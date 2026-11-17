"""编排图测试：全部使用 Fake 适配器，无网络、无外部存储。"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from langgraph.types import Command

from tests.unit.fakes import FakeBridge, FakeKnowledge, FakeLLM, FakeTrace
from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    Citation,
    RoutingDecision,
    TokenSymbol,
)
from wanchain_agent.orchestration import (
    CANCELLED_TEXT,
    REFUSAL_TEXT,
    build_graph,
    initial_state,
    thread_config,
)

SESSION = "sess-1"


def _run(coro):
    return asyncio.run(coro)


def _text_calls(llm: FakeLLM) -> list[dict]:
    """FakeLLM 同时记录结构化调用，这里只取纯文本生成。"""
    return [call for call in llm.calls if "schema" not in call]


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


def _citation(score: float = 0.91) -> Citation:
    return Citation(
        doc_id="bridge_architecture",
        source_path="docs/bridge/architecture.md",
        snippet="Wanchain 使用 Storeman 与 sMPC 完成跨链。",
        score=score,
    )


def _make_graph(
    decision: RoutingDecision,
    *,
    responses: list[str] | None = None,
    citations: list[Citation] | None = None,
    bridge: FakeBridge | None = None,
    min_relevance: float = 0.5,
):
    llm = FakeLLM(responses=responses)
    llm.register_structured(RoutingDecision, decision)
    knowledge = FakeKnowledge(citations=citations)
    bridge = bridge or FakeBridge()
    trace = FakeTrace()
    graph = build_graph(
        llm=llm,
        knowledge=knowledge,
        bridge=bridge,
        trace=trace,
        min_relevance=min_relevance,
    )
    return graph, llm, knowledge, bridge, trace


def test_graph_contains_expected_nodes():
    graph, *_ = _make_graph(_rag_decision())
    nodes = set(graph.get_graph().nodes)
    assert nodes == {
        "__start__",
        "entry",
        "router",
        "clarify",
        "knowledge_retrieve",
        "guard",
        "bridge_validate",
        "bridge_simulate",
        "bridge_preview",
        "await_approval",
        "bridge_poll",
        "respond",
        "__end__",
    }


def test_rag_branch_answers_and_traces_nodes():
    graph, llm, knowledge, _, trace = _make_graph(
        _rag_decision(), responses=["Wanchain 通过 Storeman 完成跨链。"]
    )
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="Storeman 是什么？"),
            thread_config(SESSION),
        )
    )

    assert state["guard_passed"] is True
    assert state["messages"][-1] == {
        "role": "assistant",
        "content": "Wanchain 通过 Storeman 完成跨链。",
    }
    assert len(state["rag_context"]) == 1
    assert knowledge.queries == [("Storeman 是什么？", 5)]
    assert [span["name"] for span in trace.spans] == [
        "entry",
        "router",
        "knowledge_retrieve",
        "guard",
        "respond",
    ]
    assert state["trace_id"]
    assert len(_text_calls(llm)) == 1  # 只有生成回答时调用一次 LLM


def test_rag_guard_blocks_and_refuses_without_calling_llm():
    graph, llm, _, _, _ = _make_graph(
        _rag_decision(), citations=[_citation(score=0.05)]
    )
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="随便聊聊"),
            thread_config(SESSION),
        )
    )

    assert state["guard_passed"] is False
    assert state["messages"][-1]["content"] == REFUSAL_TEXT
    assert _text_calls(llm) == []


def test_bridge_missing_slots_routes_to_clarify():
    decision = RoutingDecision(
        intent="bridge",
        confidence=0.9,
        slots=BridgeSlots(from_chain=ChainId.ETH, to_chain=ChainId.BSC),
    )
    graph, llm, _, _, _ = _make_graph(decision, responses=["请补充代币和金额。"])
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="帮我跨链"),
            thread_config(SESSION),
        )
    )

    assert state["messages"][-1]["content"] == "请补充代币和金额。"
    assert state["tx_preview"] is None
    assert len(_text_calls(llm)) == 1


def test_clarify_intent_uses_llm_question():
    graph, _, _, _, _ = _make_graph(
        RoutingDecision(intent="clarify", confidence=0.4),
        responses=["你想问的是哪条链上的问题？"],
    )
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="这个怎么弄"),
            thread_config(SESSION),
        )
    )

    assert state["messages"][-1]["content"] == "你想问的是哪条链上的问题？"


def test_bridge_flow_interrupts_then_polls_after_approval():
    graph, _, _, bridge, trace = _make_graph(_bridge_decision())
    config = thread_config(SESSION)

    paused = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="把 100 USDT 从 ETH 跨到 BSC"),
            config,
        )
    )

    assert "__interrupt__" in paused
    assert paused["tx_preview"]["from_chain"] == "ETH"
    assert paused["tx_preview"]["amount"] == "100"
    assert paused["tx_preview"]["bridge_fee"] == "0.5"
    assert bridge.polls == []

    resumed = _run(
        graph.ainvoke(
            Command(resume={"approved": True, "tx_hash": "0xdeadbeef"}), config
        )
    )

    assert resumed["approval"] == {"approved": True}
    assert resumed["tx_hash"] == "0xdeadbeef"
    assert resumed["bridge_status"] == "SUCCESS_MINTED"
    assert bridge.polls == ["0xdeadbeef"]
    assert resumed["messages"][-1]["content"] == "跨链状态：SUCCESS_MINTED"
    assert [span["name"] for span in trace.spans] == [
        "entry",
        "router",
        "bridge_validate",
        "bridge_simulate",
        "bridge_preview",
        "await_approval",
        "await_approval",
        "bridge_poll",
        "respond",
    ]


def test_bridge_rejection_cancels_without_polling():
    graph, _, _, bridge, _ = _make_graph(_bridge_decision())
    config = thread_config(SESSION)

    _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="把 100 USDT 从 ETH 跨到 BSC"),
            config,
        )
    )
    state = _run(graph.ainvoke(Command(resume={"approved": False}), config))

    assert state["approval"] == {"approved": False}
    assert state["tx_hash"] is None
    assert state["messages"][-1]["content"] == CANCELLED_TEXT
    assert bridge.polls == []


class _ExpiredFakeBridge(FakeBridge):
    """模拟预览在用户确认前过期。"""

    async def simulate(self, slots):
        result = await super().simulate(slots)
        return result.model_copy(
            update={"expires_at": datetime.now(UTC) - timedelta(seconds=1)}
        )


def test_expired_preview_rejects_resume():
    graph, _, _, bridge, _ = _make_graph(
        _bridge_decision(), bridge=_ExpiredFakeBridge()
    )
    config = thread_config(SESSION)

    _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="把 100 USDT 从 ETH 跨到 BSC"),
            config,
        )
    )
    state = _run(
        graph.ainvoke(
            Command(resume={"approved": True, "tx_hash": "0xdeadbeef"}), config
        )
    )

    assert state["error"]["error"]["code"] == "preview_expired"
    assert state["messages"][-1]["content"].startswith("处理失败")
    assert bridge.polls == []


def test_unsupported_route_returns_error_message():
    graph, _, _, bridge, _ = _make_graph(
        _bridge_decision(), bridge=FakeBridge(supported=False)
    )
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="把 100 USDT 从 ETH 跨到 BSC"),
            thread_config(SESSION),
        )
    )

    assert state["error"]["error"]["code"] == "bridge_validation"
    assert state["tx_preview"] is None
    assert state["messages"][-1]["content"].startswith("处理失败")
    assert bridge.polls == []


def test_multi_turn_keeps_conversation_history():
    graph, *_ = _make_graph(_rag_decision(), responses=["第一轮回答"])
    config = thread_config(SESSION)

    _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="第一个问题"), config
        )
    )
    state = _run(
        graph.ainvoke(
            initial_state(session_id=SESSION, message="第二个问题"), config
        )
    )

    assert [message["role"] for message in state["messages"]] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert state["messages"][0]["content"] == "第一个问题"
