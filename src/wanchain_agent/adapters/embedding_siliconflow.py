"""SiliconFlow Embedding 适配器（OpenAI 兼容 ``/embeddings``）。

默认模型 ``BAAI/bge-m3``：中英跨语言检索，输出 1024 维向量。

- 文档与 query 走同一模型、同一维度，混用会导致"不报错但不准"；
- 按 ``batch_size`` 分批请求，429 / 5xx / 网络错误指数退避；
- 返回数量或维度不符合预期时抛 ``UpstreamError``，不把半成品写入索引；
- 密钥只从构造参数读取，不写入日志与异常信息。
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from wanchain_agent.core.errors import ConfigError, UpstreamError

DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_DIMENSION = 1024
DEFAULT_BATCH_SIZE = 32


class _EmbeddingItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    index: int = Field(default=0, ge=0)
    embedding: list[float]


class _EmbeddingResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[_EmbeddingItem] = []


class SiliconFlowEmbedding:
    """实现 ``EmbeddingPort``。异常一律转换为领域异常，不泄漏 SDK 类型。"""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        dimension: int = DEFAULT_DIMENSION,
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise ConfigError("缺少 Embedding API Key")
        if dimension < 1:
            raise ConfigError("Embedding 维度必须为正整数")
        if batch_size < 1:
            raise ConfigError("Embedding batch_size 必须为正整数")
        if max_retries < 0:
            raise ConfigError("Embedding max_retries 不能为负数")

        self._model = model
        self._dimension = dimension
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    async def aclose(self) -> None:
        await self._client.aclose()

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self._check_texts(texts)
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            vectors.extend(await self._embed_batch(batch))
        return vectors

    async def embed_query(self, text: str) -> list[float]:
        self._check_texts([text])
        vectors = await self._embed_batch([text])
        return vectors[0]

    def _check_texts(self, texts: list[str]) -> None:
        for position, text in enumerate(texts):
            if not text.strip():
                raise ValueError(f"Embedding 输入不能为空：第 {position} 条")

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        body: dict[str, Any] = {
            "model": self._model,
            "input": texts,
            "encoding_format": "float",
        }

        response = await self._post_with_retry(body)

        try:
            payload = _EmbeddingResponse.model_validate(response.json())
        except ValueError as exc:
            raise UpstreamError("Embedding 返回了非预期响应结构") from exc

        items = sorted(payload.data, key=lambda item: item.index)
        if len(items) != len(texts):
            raise UpstreamError(
                "Embedding 返回数量与输入不一致",
                details={"expected": len(texts), "actual": len(items)},
            )

        vectors: list[list[float]] = []
        for item in items:
            if len(item.embedding) != self._dimension:
                raise UpstreamError(
                    "Embedding 维度不符合配置",
                    details={"expected": self._dimension, "actual": len(item.embedding)},
                )
            vectors.append(item.embedding)
        return vectors

    async def _post_with_retry(self, body: dict[str, Any]) -> httpx.Response:
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.post("/embeddings", json=body)
            except httpx.HTTPError as exc:
                if attempt >= self._max_retries:
                    raise UpstreamError(
                        "Embedding 请求失败", details={"reason": type(exc).__name__}
                    ) from exc
                await self._backoff(attempt)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt >= self._max_retries:
                    raise UpstreamError(
                        "Embedding 返回错误状态",
                        details={"status": response.status_code},
                    )
                await self._backoff(attempt)
                continue

            if response.status_code >= 400:
                raise UpstreamError(
                    "Embedding 返回错误状态",
                    details={"status": response.status_code},
                )
            return response

        raise UpstreamError("Embedding 重试次数耗尽")  # pragma: no cover - 循环必然返回或抛错

    async def _backoff(self, attempt: int) -> None:
        if self._retry_delay > 0:
            await asyncio.sleep(self._retry_delay * (2**attempt))
