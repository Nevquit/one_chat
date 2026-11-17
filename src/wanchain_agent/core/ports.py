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
