"""LLM 适配器测试：httpx.MockTransport，不发真实请求。"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from wanchain_agent.adapters.llm_openai import OpenAICompatibleLLM
from wanchain_agent.core.errors import ConfigError, UpstreamError
from wanchain_agent.core.models import RoutingDecision

CHAT_OK = {
    "choices": [{"message": {"role": "assistant", "content": "Wanchain 使用 Storeman。"}}]
}


def _llm(payload, *, status: int = 200, requests: list[httpx.Request] | None = None):
    log = requests if requests is not None else []

    def handler(request: httpx.Request) -> httpx.Response:
        log.append(request)
        return httpx.Response(status, json=payload)

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://llm.test/v1",
        headers={"Authorization": "Bearer test-key"},
    )
    return OpenAICompatibleLLM(api_key="test-key", client=client)


def test_missing_api_key_fails_fast():
    with pytest.raises(ConfigError):
        OpenAICompatibleLLM(api_key="")


def test_complete_returns_content_and_sends_auth():
    requests: list[httpx.Request] = []
    llm = _llm(CHAT_OK, requests=requests)

    answer = asyncio.run(llm.complete([{"role": "user", "content": "hi"}]))

    assert answer == "Wanchain 使用 Storeman。"
    assert requests[0].headers["Authorization"] == "Bearer test-key"
    body = json.loads(requests[0].content)
    assert body["model"] == "deepseek-chat"
    assert "response_format" not in body


def test_empty_choices_raise_upstream_error():
    llm = _llm({"choices": []})

    with pytest.raises(UpstreamError):
        asyncio.run(llm.complete([{"role": "user", "content": "hi"}]))


def test_http_error_maps_to_upstream_error_without_leaking_key():
    llm = _llm({"error": "unauthorized"}, status=401)

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(llm.complete([{"role": "user", "content": "hi"}]))

    assert excinfo.value.details["status"] == 401
    assert "test-key" not in str(excinfo.value)


def test_complete_structured_validates_json_into_schema():
    requests: list[httpx.Request] = []
    llm = _llm(
        {
            "choices": [
                {"message": {"content": '{"intent": "rag", "confidence": 0.9}'}}
            ]
        },
        requests=requests,
    )

    decision = asyncio.run(
        llm.complete_structured(
            [{"role": "user", "content": "Storeman 是什么"}], RoutingDecision
        )
    )

    assert decision.intent == "rag"
    assert decision.confidence == 0.9
    body = json.loads(requests[0].content)
    assert body["response_format"] == {"type": "json_object"}
    assert "JSON Schema" in body["messages"][-1]["content"]


def test_complete_structured_strips_code_fence():
    llm = _llm(
        {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"intent": "clarify", "confidence": 0.3}\n```'
                    }
                }
            ]
        }
    )

    decision = asyncio.run(
        llm.complete_structured([{"role": "user", "content": "?"}], RoutingDecision)
    )

    assert decision.intent == "clarify"


def test_complete_structured_rejects_invalid_json():
    llm = _llm({"choices": [{"message": {"content": "not json"}}]})

    with pytest.raises(UpstreamError):
        asyncio.run(
            llm.complete_structured(
                [{"role": "user", "content": "?"}], RoutingDecision
            )
        )


def test_complete_structured_rejects_schema_mismatch():
    llm = _llm(
        {
            "choices": [
                {"message": {"content": '{"intent": "bridge", "confidence": 2.0}'}}
            ]
        }
    )

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(
            llm.complete_structured(
                [{"role": "user", "content": "?"}], RoutingDecision
            )
        )

    assert excinfo.value.details["schema"] == "RoutingDecision"
