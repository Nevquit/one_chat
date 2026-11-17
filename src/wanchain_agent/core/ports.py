"""端口定义（依赖倒置接口）。

业务模块只依赖这里的 ``Protocol``，具体实现全部放在 ``adapters/``。
端口只返回纯数据结构（Pydantic 模型），不暴露任何第三方 SDK 对象。
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol, TypeVar, runtime_checkable

from .models import (
    BridgeSlots,
    BridgeStatus,
    Chunk,
    Citation,
    RouteCheck,
    SimulationResult,
    UnsignedTxPayload,
)

T = TypeVar("T")


@runtime_checkable
class LLMPort(Protocol):
    """大模型能力。实现方负责把 SDK 异常转换为 ``UpstreamError``。"""

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
    ) -> str: ...

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        schema: type[T],
        *,
        temperature: float = 0.0,
    ) -> T: ...


@runtime_checkable
class KnowledgePort(Protocol):
    """知识检索。返回结果必须带引用元数据，供回答标注来源。"""

    async def retrieve(self, query: str, top_k: int = 5) -> list[Citation]: ...

    async def health(self) -> dict[str, Any]: ...


@runtime_checkable
class EmbeddingPort(Protocol):
    """文本向量化。query 与文档必须使用同一模型、同一维度。

    ``dimension`` 由实现方声明，建库时用它校验向量长度；
    ``model_name`` 会写入索引清单，启动时与配置比对。
    """

    @property
    def model_name(self) -> str: ...

    @property
    def dimension(self) -> int: ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


@runtime_checkable
class VectorIndexPort(Protocol):
    """向量索引写入。``write`` 负责全量重建，保证索引与传入片段一一对应。"""

    def write(self, chunks: list[Chunk], vectors: list[list[float]]) -> int: ...

    def count(self) -> int: ...

    def close(self) -> None: ...


@runtime_checkable
class BridgePort(Protocol):
    """跨链能力。全部方法都是只读或载荷构建，不含签名与广播。"""

    async def validate_route(self, slots: BridgeSlots) -> RouteCheck: ...

    async def simulate(self, slots: BridgeSlots) -> SimulationResult: ...

    async def build_unsigned_tx(self, slots: BridgeSlots) -> UnsignedTxPayload: ...

    async def poll_status(self, tx_hash: str) -> BridgeStatus: ...


@runtime_checkable
class TracePort(Protocol):
    """链路追踪。实现方必须异步上报，失败不得影响主链路。"""

    def span(
        self,
        name: str,
        **attributes: Any,
    ) -> AbstractContextManager[None]: ...
