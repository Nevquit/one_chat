"""跨链参数校验：100% 确定性纯函数，不访问网络。

这一层只做本地可判定的检查；链上路由是否真实可用由 ``BridgePort`` 确认。
两者顺序是：本地校验先挡住明显非法输入，再调用外部接口。
"""

from __future__ import annotations

from decimal import Decimal

from wanchain_agent.core.errors import (
    InvalidAmountError,
    SameChainError,
    SlotsIncompleteError,
    UnsupportedTokenError,
)
from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    RouteCheck,
    TokenSymbol,
)

TOKEN_DECIMALS: dict[TokenSymbol, int] = {
    TokenSymbol.USDT: 6,
    TokenSymbol.USDC: 6,
    TokenSymbol.WAN: 18,
}

MIN_AMOUNTS: dict[TokenSymbol, Decimal] = {
    TokenSymbol.USDT: Decimal(1),
    TokenSymbol.USDC: Decimal(1),
    TokenSymbol.WAN: Decimal(10),
}


def validate_slots(slots: BridgeSlots) -> RouteCheck:
    """校验槽位。非法输入抛领域异常，合法返回 ``RouteCheck``。"""
    from_chain = slots.from_chain
    to_chain = slots.to_chain
    token = slots.token
    amount = slots.amount

    if from_chain is None or to_chain is None or token is None or amount is None:
        raise SlotsIncompleteError(
            "跨链槽位不完整：" + "、".join(slots.missing_slots() or ["unknown"])
        )

    if from_chain == to_chain:
        raise SameChainError("源链与目标链不能相同")

    _check_token_chain(token, from_chain, to_chain)

    decimals = TOKEN_DECIMALS[token]
    exponent = amount.as_tuple().exponent
    if not isinstance(exponent, int) or -exponent > decimals:
        raise InvalidAmountError(
            f"{token.value} 最多支持 {decimals} 位小数",
            details={"decimals": decimals},
        )

    min_amount = MIN_AMOUNTS[token]
    if amount < min_amount:
        raise InvalidAmountError(
            f"{token.value} 最小跨链金额为 {min_amount}",
            details={"min_amount": format(min_amount, "f")},
        )

    return RouteCheck(supported=True, min_amount=min_amount, decimals=decimals)


def _check_token_chain(token: TokenSymbol, from_chain: ChainId, to_chain: ChainId) -> None:
    chains = (from_chain, to_chain)
    if token is TokenSymbol.USDC and ChainId.WAN in chains:
        raise UnsupportedTokenError("USDC 暂不支持与 WAN 链互通")
    if token is TokenSymbol.WAN and ChainId.WAN not in chains:
        raise UnsupportedTokenError("WAN 代币只能与 WAN 链组合")
