"""Embedding 适配器测试：httpx.MockTransport，不发真实请求。"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from wanchain_agent.adapters.embedding_siliconflow import (
    DEFAULT_MODEL,
    SiliconFlowEmbedding,
)
from wanchain_agent.core.errors import ConfigError, UpstreamError

DIMENSION = 4


def _ok_response(request: httpx.Request, *, dimension: int = DIMENSION) -> httpx.Response:
    count = len(json.loads(request.content)["input"])
    return httpx.Response(
        200,
        json={
            "data": [
                {"index": index, "embedding": [float(index)] * dimension}
                for index in range(count)
            ]
        },
    )


def _ok_handler(requests: list[httpx.Request], *, dimension: int = DIMENSION):
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _ok_response(request, dimension=dimension)

    return handler


def _embedding(handler, **kwargs) -> SiliconFlowEmbedding:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://embed.test/v1",
        headers={"Authorization": "Bearer test-key"},
    )
    options = {"dimension": DIMENSION, "retry_delay": 0.0, **kwargs}
    return SiliconFlowEmbedding(api_key="test-key", client=client, **options)


def test_missing_api_key_fails_fast():
    with pytest.raises(ConfigError):
        SiliconFlowEmbedding(api_key="")


def test_defaults_target_bge_m3():
    embedding = _embedding(_ok_handler([]))

    assert embedding.model_name == DEFAULT_MODEL == "BAAI/bge-m3"
    assert embedding.dimension == DIMENSION


def test_embed_query_sends_auth_and_model():
    requests: list[httpx.Request] = []
    embedding = _embedding(_ok_handler(requests))

    vector = asyncio.run(embedding.embed_query("Storeman 是什么"))

    assert vector == [0.0] * DIMENSION
    assert requests[0].headers["Authorization"] == "Bearer test-key"
    body = json.loads(requests[0].content)
    assert body["model"] == "BAAI/bge-m3"
    assert body["input"] == ["Storeman 是什么"]


def test_embed_documents_splits_batches():
    requests: list[httpx.Request] = []
    embedding = _embedding(_ok_handler(requests), batch_size=2)

    vectors = asyncio.run(embedding.embed_documents(["a", "b", "c", "d", "e"]))

    assert len(vectors) == 5
    assert [len(json.loads(item.content)["input"]) for item in requests] == [2, 2, 1]


def test_embed_documents_returns_vectors_in_input_order():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 2, "embedding": [3.0] * DIMENSION},
                    {"index": 0, "embedding": [1.0] * DIMENSION},
                    {"index": 1, "embedding": [2.0] * DIMENSION},
                ]
            },
        )

    vectors = asyncio.run(_embedding(handler).embed_documents(["a", "b", "c"]))

    assert vectors == [[1.0] * DIMENSION, [2.0] * DIMENSION, [3.0] * DIMENSION]


def test_empty_input_skips_network():
    requests: list[httpx.Request] = []

    assert asyncio.run(_embedding(_ok_handler(requests)).embed_documents([])) == []
    assert requests == []


def test_blank_text_is_rejected():
    with pytest.raises(ValueError):
        asyncio.run(_embedding(_ok_handler([])).embed_documents(["ok", "  "]))


def test_rate_limit_is_retried():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(429, json={"error": "slow down"})
        return _ok_response(request)

    embedding = _embedding(handler, max_retries=2)

    vectors = asyncio.run(embedding.embed_documents(["a"]))

    assert len(vectors) == 1
    assert len(requests) == 2


def test_retries_exhausted_raises_upstream_error():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503, json={"error": "unavailable"})

    embedding = _embedding(handler, max_retries=2)

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(embedding.embed_documents(["a"]))

    assert excinfo.value.details["status"] == 503
    assert len(requests) == 3


def test_network_error_is_retried_then_mapped():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ConnectError("boom", request=request)

    embedding = _embedding(handler, max_retries=1)

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(embedding.embed_documents(["a"]))

    assert excinfo.value.details["reason"] == "ConnectError"
    assert len(requests) == 2


def test_client_error_is_not_retried():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(401, json={"error": "unauthorized"})

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(_embedding(handler, max_retries=2).embed_documents(["a"]))

    assert excinfo.value.details["status"] == 401
    assert len(requests) == 1


def test_count_mismatch_raises_upstream_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"data": [{"index": 0, "embedding": [0.0] * DIMENSION}]}
        )

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(_embedding(handler).embed_documents(["a", "b"]))

    assert excinfo.value.details == {"expected": 2, "actual": 1}


def test_dimension_mismatch_raises_upstream_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"data": [{"index": 0, "embedding": [0.0] * (DIMENSION - 1)}]}
        )

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(_embedding(handler).embed_documents(["a"]))

    assert excinfo.value.details == {"expected": DIMENSION, "actual": DIMENSION - 1}


def test_invalid_response_structure_raises_upstream_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    with pytest.raises(UpstreamError):
        asyncio.run(_embedding(handler).embed_documents(["a"]))
