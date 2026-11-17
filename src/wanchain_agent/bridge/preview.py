"""交易预览组装与过期判定。

预览是用户签名的唯一依据，必须与模拟结果同源，不能重新计算或四舍五入。
"""

from __future__ import annotations

from datetime import UTC, datetime

from wanchain_agent.core.errors import SlotsIncompleteError
from wanchain_agent.core.models import (
    BridgeSlots,
    SimulationResult,
    TxPreview,
    UnsignedTxPayload,
)


def build_preview(
    slots: BridgeSlots,
    simulation: SimulationResult,
    payload: UnsignedTxPayload,
) -> TxPreview:
    from_chain = slots.from_chain
    to_chain = slots.to_chain
    token = slots.token
    amount = slots.amount
    if from_chain is None or to_chain is None or token is None or amount is None:
        raise SlotsIncompleteError(
            "跨链槽位不完整：" + "、".join(slots.missing_slots() or ["unknown"])
        )

    return TxPreview(
        from_chain=from_chain,
        to_chain=to_chain,
        token=token,
        amount=amount,
        bridge_fee=simulation.bridge_fee,
        estimated_receive=simulation.estimated_receive,
        estimated_gas=simulation.estimated_gas,
        unsigned_payload=payload,
        expires_at=simulation.expires_at,
    )


def is_expired(preview: TxPreview, *, now: datetime | None = None) -> bool:
    """预览过期后必须重新模拟，禁止用旧费用签名。"""
    return (now or datetime.now(UTC)) >= preview.expires_at
