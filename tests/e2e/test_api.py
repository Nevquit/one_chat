"""API 网关端到端测试：ASGI 进程内调用，全部使用 Fake 适配器，无网络。"""

from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Any

import httpx

from tests.unit.fakes import FakeBridge, FakeKnowledge, FakeLLM, FakeTrace
from wanchain_agent.app import create_app
from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    Citation,
    RoutingDecision,
    TokenSymbol,
)
from wanchain_agent.orchestration import CANCELLED_TEXT, REFUSAL_TEXT

SESSION = "sess-api"


def _rag_decision() -> RoutingDecision:
    return RoutingDecision(intent="rag", confidence=0.9)


def _bridge_decision() -> RoutingDecision:
    return RoutingDecision(
        intent="bridge",
        confidence=0.9,
        slots=BridgeSlots(
            from_chain=ChainId.ETH,
            to_chain=ChainId.BSC,
            token=TokenSymbol.USDT,
            amount=Decimal(100),
        ),
    )


def _make_app(
    decision: RoutingDecision,
    *,
    responses: list[str] | None = None,
    citations: list[Citation] | None = None,
    bridge: FakeBridge | None = None,
):
    llm = FakeLLM(responses=responses)
    llm.register_structured(RoutingDecision, decision)
    knowledge = FakeKnowledge(citations=citations)
    bridge = bridge or FakeBridge()
    app = create_app(
        llm=llm,
        knowledge=knowledge,
        bridge=bridge,
        trace=FakeTrace(),
        min_relevance=0.5,
    )
    return app, llm, knowledge, bridge


async def _call(app, method: str, path: str, payload: dict[str, Any] | None = None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, json=payload)


def _post(app, path: str, payload: dict[str, Any]):
    return asyncio.run(_call(app, "POST", path, payload))


def _parse_sse(raw: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for block in raw.strip().split("\n\n"):
        name: str | None = None
        data: Any = None
        for line in block.splitlines():
            if line.startswith("event: "):
                name = line.removeprefix("event: ")
            elif line.startswith("data: "):
                data = json.loads(line.removeprefix("data: "))
        if name is not None:
            events.append({"event": name, "data": data})
    return events


def test_health_reports_knowledge_status():
    app, _, _, _ = _make_app(_rag_decision())
    response = asyncio.run(_call(app, "GET", "/health"))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["knowledge"]["status"] == "ok"


def test_rag_chat_streams_token_and_citations():
    app, _, knowledge, _ = _make_app(
        _rag_decision(), responses=["Wanchain 通过 Storeman 完成跨链。"]
    )
    response = _post(
        app, "/chat", {"session_id": SESSION, "message": "Storeman 是什么？"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = _parse_sse(response.text)
    assert events == [
        {"event": "token", "data": {"text": "Wanchain 通过 Storeman 完成跨链。"}},
        {
            "event": "citations",
            "data": {
                "citations": [
                    {
                        "doc_id": "bridge_architecture",
                        "source_path": "docs/bridge/architecture.md",
                        "heading_path": "Bridge > Architecture > Storeman",
                        "snippet": "Wanchain 采用 Storeman 节点组与 sMPC 实现跨链。",
                        "score": 0.91,
                    }
                ]
            },
        },
    ]
    assert knowledge.queries == [("Storeman 是什么？", 5)]


def test_rag_low_relevance_refuses_without_calling_llm():
    citations = [
        Citation(
            doc_id="noise",
            source_path="docs/noise.md",
            snippet="无关内容",
            score=0.05,
        )
    ]
    app, llm, _, _ = _make_app(_rag_decision(), citations=citations)
    response = _post(app, "/chat", {"session_id": SESSION, "message": "随便聊聊"})

    events = _parse_sse(response.text)
    assert events == [{"event": "token", "data": {"text": REFUSAL_TEXT}}]
    assert [call for call in llm.calls if "schema" not in call] == []


def test_bridge_chat_emits_preview_then_interrupt():
    app, _, _, bridge = _make_app(_bridge_decision())
    response = _post(
        app,
        "/chat",
        {"session_id": SESSION, "message": "把 100 USDT 从 ETH 跨到 BSC"},
    )

    events = _parse_sse(response.text)
    assert [event["event"] for event in events] == ["tx_preview", "interrupt"]
    preview = events[0]["data"]["preview"]
    assert preview["from_chain"] == "ETH"
    assert preview["amount"] == "100"
    assert events[1]["data"] == {"session_id": SESSION, "type": "tx_preview"}
    assert bridge.polls == []


def test_resume_approved_streams_bridge_status():
    app, _, _, bridge = _make_app(_bridge_decision())
    _post(app, "/chat", {"session_id": SESSION, "message": "把 100 USDT 从 ETH 跨到 BSC"})

    response = _post(
        app,
        "/chat/resume",
        {"session_id": SESSION, "approved": True, "tx_hash": "0xdeadbeef"},
    )

    assert response.status_code == 200
    assert _parse_sse(response.text) == [
        {"event": "token", "data": {"text": "跨链状态：SUCCESS_MINTED"}}
    ]
    assert bridge.polls == ["0xdeadbeef"]


def test_resume_rejected_returns_cancel_text():
    app, _, _, bridge = _make_app(_bridge_decision())
    _post(app, "/chat", {"session_id": SESSION, "message": "把 100 USDT 从 ETH 跨到 BSC"})

    response = _post(
        app, "/chat/resume", {"session_id": SESSION, "approved": False}
    )

    assert _parse_sse(response.text) == [
        {"event": "token", "data": {"text": CANCELLED_TEXT}}
    ]
    assert bridge.polls == []


def test_resume_unknown_session_returns_404():
    app, *_ = _make_app(_bridge_decision())
    response = _post(
        app, "/chat/resume", {"session_id": "missing", "approved": True}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "session_not_found"


def test_resume_without_pending_interrupt_returns_404():
    app, *_ = _make_app(_rag_decision(), responses=["已经答完了"])
    _post(app, "/chat", {"session_id": SESSION, "message": "Storeman 是什么？"})

    response = _post(
        app, "/chat/resume", {"session_id": SESSION, "approved": True}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "session_not_found"


def test_bridge_validation_failure_emits_error_event():
    app, *_ = _make_app(
        _bridge_decision(), bridge=FakeBridge(supported=False)
    )
    response = _post(
        app, "/chat", {"session_id": SESSION, "message": "把 100 USDT 从 ETH 跨到 BSC"}
    )

    events = _parse_sse(response.text)
    assert [event["event"] for event in events] == ["error"]
    assert events[0]["data"]["code"] == "bridge_validation"


def test_invalid_chat_request_is_rejected_before_graph_runs():
    app, _, knowledge, _ = _make_app(_rag_decision())
    response = _post(app, "/chat", {"session_id": SESSION, "message": ""})

    assert response.status_code == 422
    assert knowledge.queries == []
