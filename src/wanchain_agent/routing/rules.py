"""规则路由：关键词与正则的确定性匹配，毫秒级返回。

设计取舍：

- 命中即返回决策，不调用 LLM；未命中返回 ``None`` 交由 LLM 兜底。
- 规则命中时 ``confidence`` 固定为 1.0，只用于填充契约字段，
  **不参与任何放行判定**（放行只依据槽位是否齐全）。
- 收款地址只在出现「收款地址 / 接收地址 / 到地址 / recipient」等显式提示时抽取，
  绝不把消息里出现的第一个地址猜成收款方。
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    RoutingDecision,
    TokenSymbol,
)

BRIDGE_KEYWORDS = ("跨链", "bridge", "跨到", "跨过去", "跨入")

RAG_KEYWORDS = ("是什么", "什么是", "什么", "如何", "为什么", "介绍", "解释", "区别", "文档")

_CHAIN_ALIASES: dict[ChainId, tuple[str, ...]] = {
    ChainId.ETH: ("ethereum", "eth", "以太坊", "以太"),
    ChainId.BSC: ("bnb chain", "bsc", "bnb", "币安智能链", "币安链", "币安"),
    ChainId.WAN: ("wanchain", "万维链", "wan"),
}

_ALIAS_TO_CHAIN: dict[str, ChainId] = {
    alias.lower(): chain for chain, aliases in _CHAIN_ALIASES.items() for alias in aliases
}

# 长别名优先，避免 "eth" 抢先匹配 "ethereum"、"wan" 抢先匹配 "wanchain"
_CHAIN_RE = re.compile(
    "|".join(re.escape(alias) for alias in sorted(_ALIAS_TO_CHAIN, key=len, reverse=True)),
    re.IGNORECASE,
)

_AMOUNT_WITH_TOKEN_RE = re.compile(
    r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:个)?\s*(usdt|usdc|wan)(?![a-z0-9])",
    re.IGNORECASE,
)
_AMOUNT_ONLY_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
_TOKEN_RE = re.compile(r"(?<![a-z0-9])(usdt|usdc|wan)(?![a-z0-9])", re.IGNORECASE)
_RECIPIENT_RE = re.compile(
    r"(?:收款地址|接收地址|到地址|recipient)\s*[:：]?\s*(0x[0-9a-fA-F]{40})",
    re.IGNORECASE,
)
_TO_PREFIX_RE = re.compile(r"(?:到|至|to)\s*$", re.IGNORECASE)


def match_rules(message: str) -> RoutingDecision | None:
    """命中规则返回决策；无法确定时返回 ``None``。"""
    text = message.strip()
    if not text:
        return None

    lowered = text.lower()
    mentions = _extract_chains(text)
    amount, token, _ = _extract_amount(text)
    transfer_signal = any(keyword in lowered for keyword in BRIDGE_KEYWORDS)
    has_params = amount is not None or token is not None

    # 只有「转账类关键词 + 交易参数」或「两条链 + 明确转账意图」才算跨链请求。
    # 否则「Storeman 如何保证跨链安全？」「WanBridge 是什么？」这类文档问题
    # 会因为出现「跨链 / bridge」而被误送进交易分支。
    bridge_signal = (
        len(mentions) >= 2 and (has_params or transfer_signal)
    ) or (has_params and transfer_signal)

    if bridge_signal:
        return RoutingDecision(
            intent="bridge",
            confidence=1.0,
            slots=_build_slots(text, mentions),
            reason="rule:bridge",
        )

    if _is_question(text):
        return RoutingDecision(intent="rag", confidence=1.0, reason="rule:rag")

    return None


def is_question(text: str) -> bool:
    """是否为文档问答口吻，供多轮续槽判断使用。"""
    return _is_question(text.strip())


def extract_slots(text: str) -> BridgeSlots:
    """只抽取单条消息里的槽位，不判断意图。

    多轮续槽时用它拿到本轮新增/覆盖的字段，再与历史槽位合并。
    """
    cleaned = text.strip()
    return _build_slots(cleaned, _extract_chains(cleaned))


def _is_question(text: str) -> bool:
    if text.rstrip().endswith(("?", "？")):
        return True
    return any(keyword in text for keyword in RAG_KEYWORDS)


def _extract_chains(text: str) -> list[tuple[int, ChainId]]:
    return [
        (match.start(), _ALIAS_TO_CHAIN[match.group(0).lower()])
        for match in _CHAIN_RE.finditer(text)
    ]


def _build_slots(text: str, mentions: list[tuple[int, ChainId]]) -> BridgeSlots:
    amount, token, amount_span = _extract_amount(text)
    # "100 WAN" 里的 WAN 是代币不是链名，落在金额片段内的链别名要排除
    if amount_span is not None:
        mentions = [
            item for item in mentions if not amount_span[0] <= item[0] < amount_span[1]
        ]

    # 反过来，"从 WAN 跨" 里的 WAN 是链名不是代币。只有当 WAN 没有被金额片段
    # 排除、仍作为链出现时，才清掉代币槽位，避免把源链误记成代币。
    if token is TokenSymbol.WAN and any(
        chain is ChainId.WAN for _, chain in mentions
    ):
        token = None

    from_chain: ChainId | None = None
    to_chain: ChainId | None = None

    if len(mentions) >= 2:
        from_chain, to_chain = mentions[0][1], mentions[1][1]
    elif len(mentions) == 1:
        position, chain = mentions[0]
        prefix = text[max(0, position - 3) : position]
        if _TO_PREFIX_RE.search(prefix):
            to_chain = chain
        else:
            from_chain = chain

    # 同链只能留一侧，交给图的槽位检查转澄清，而不是静默改写用户意图
    if from_chain is not None and from_chain == to_chain:
        to_chain = None

    return BridgeSlots(
        from_chain=from_chain,
        to_chain=to_chain,
        token=token,
        amount=amount,
        recipient=_extract_recipient(text),
    )


def _extract_amount(
    text: str,
) -> tuple[Decimal | None, TokenSymbol | None, tuple[int, int] | None]:
    paired = _AMOUNT_WITH_TOKEN_RE.search(text)
    if paired:
        return (
            _to_amount(paired.group(1)),
            TokenSymbol(paired.group(2).upper()),
            paired.span(),
        )

    token_match = _TOKEN_RE.search(text)
    token = TokenSymbol(token_match.group(1).upper()) if token_match else None
    amount_match = _AMOUNT_ONLY_RE.search(text)
    amount = _to_amount(amount_match.group(1)) if amount_match else None
    return amount, token, None


def _to_amount(raw: str) -> Decimal | None:
    try:
        value = Decimal(raw)
    except InvalidOperation:  # pragma: no cover - 正则已限制为纯数字
        return None
    return value if value > 0 else None


def _extract_recipient(text: str) -> str | None:
    match = _RECIPIENT_RE.search(text)
    return match.group(1) if match else None
