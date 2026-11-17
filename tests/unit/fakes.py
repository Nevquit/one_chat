"""测试替身：满足各 Port 的内存实现。

单元测试必须只依赖这些 Fake，禁止访问网络、向量库或链上接口。
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, TypeVar

from wanchain_agent.core.models import (
    BridgeSlots,
    BridgeStatus,
    Citation,
    RouteCheck,
    SimulationResult,
    UnsignedTxPayload,
)

T = TypeVar("T")

FAKE_ADDRESS = "0x" + "1" * 40


class FakeLLM:
    """按调用顺序返回预设文本；结构化输出需显式注册。"""

    def __init__(self, responses: list[str] | None = None) -> None:
        self._responses = list(responses or ["fake answer"])
        self.calls: list[dict[str, Any]] = []
        self._structured: dict[type, Any] = {}

    def register_structured(self, schema: type, value: Any) -> None:
        self._structured[schema] = value

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
    ) -> str:
        self.calls.append({"messages": messages, "temperature": temperature})
        index = min(len(self.calls) - 1, len(self._responses) - 1)
        return self._responses[index]

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        schema: type[T],
        *,
        temperature: float = 0.0,
    ) -> T:
        self.calls.append({"messages": messages, "temperature": temperature, "schema": schema})
        if schema not in self._structured:
            raise LookupError(f"FakeLLM 未注册结构化响应：{schema.__name__}")
        return self._structured[schema]


class FakeKnowledge:
    def __init__(self, citations: list[Citation] | None = None) -> None:
        self.citations = citations or [
            Citation(
                doc_id="bridge_architecture",
                source_path="docs/bridge/architecture.md",
                heading_path="Bridge > Architecture > Storeman",
                snippet="Wanchain 采用 Storeman 节点组与 sMPC 实现跨链。",
                score=0.91,
            )
        ]
        self.queries: list[tuple[str, int]] = []

    async def retrieve(self, query: str, top_k: int = 5) -> list[Citation]:
        self.queries.append((query, top_k))
        return self.citations[:top_k]

    async def health(self) -> dict[str, Any]:
        return {"status": "ok", "chunks": len(self.citations)}


class FakeBridge:
    def __init__(
        self,
        *,
        supported: bool = True,
        status: BridgeStatus = BridgeStatus.SUCCESS_MINTED,
    ) -> None:
        self.supported = supported
        self.status = status
        self.polls: list[str] = []

    async def validate_route(self, slots: BridgeSlots) -> RouteCheck:
        return RouteCheck(
            supported=self.supported,
            reason="fake validator",
            min_amount=Decimal("1"),
            decimals=6,
        )

    async def simulate(self, slots: BridgeSlots) -> SimulationResult:
        amount = slots.amount if slots.amount is not None else Decimal("1")
        fee = Decimal("0.5")
        return SimulationResult(
            bridge_fee=fee,
            estimated_receive=amount - fee if amount > fee else amount,
            estimated_gas=Decimal("0.001"),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    async def build_unsigned_tx(self, slots: BridgeSlots) -> UnsignedTxPayload:
        return UnsignedTxPayload(
            to=FAKE_ADDRESS,
            data="0x",
            value=Decimal("0"),
            chain_id=1,
        )

    async def poll_status(self, tx_hash: str) -> BridgeStatus:
        self.polls.append(tx_hash)
        return self.status


class FakeTrace:
    """记录 span 名称与属性，便于断言节点流转轨迹。"""

    def __init__(self) -> None:
        self.spans: list[dict[str, Any]] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[None]:
        record: dict[str, Any] = {"name": name, "attributes": attributes}
        self.spans.append(record)
        try:
            yield
        except Exception as exc:  # noqa: BLE001 - 测试替身需要记录任意异常
            record["error"] = type(exc).__name__
            raise
