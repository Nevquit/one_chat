"""跨链模拟：调用只读端口，并校验返回结果内部是否自洽。

过期判定不在这里做——预览生成后可能还要等用户确认，
统一在恢复时（``preview.is_expired``）判过期，避免两处时钟口径不一致。
"""

from __future__ import annotations

from wanchain_agent.core.errors import SimulationFailedError, SlotsIncompleteError
from wanchain_agent.core.models import BridgeSlots, SimulationResult
from wanchain_agent.core.ports import BridgePort


async def simulate(slots: BridgeSlots, bridge: BridgePort) -> SimulationResult:
    if not slots.is_complete:
        raise SlotsIncompleteError("跨链槽位不完整：" + "、".join(slots.missing_slots()))

    result = await bridge.simulate(slots)
    amount = slots.amount
    if amount is None:  # pragma: no cover - is_complete 已保证
        raise SlotsIncompleteError("缺少跨链金额")

    # 手续费与到账金额之和不能超过用户输入金额，否则说明模拟结果不可信
    if result.bridge_fee + result.estimated_receive > amount:
        raise SimulationFailedError(
            "模拟结果自相矛盾：手续费与到账金额之和超过输入金额",
            details={
                "bridge_fee": format(result.bridge_fee, "f"),
                "estimated_receive": format(result.estimated_receive, "f"),
                "amount": format(amount, "f"),
            },
        )

    return result
