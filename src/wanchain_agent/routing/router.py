"""路由管道：规则优先，LLM 兜底。

规则命中是确定性的，不消耗 token；只有规则无法判断时才调用 LLM。
LLM 只负责分类与槽位抽取，不做任何链上操作。
"""

from __future__ import annotations

from typing import Any

from wanchain_agent.core.models import BridgeSlots, RoutingDecision
from wanchain_agent.core.ports import LLMPort

from .rules import extract_slots, is_question, match_rules

# 槽位字段全集：REQUIRED_FIELDS 之外的 recipient 也要参与跨轮合并
SLOT_FIELDS: tuple[str, ...] = (*BridgeSlots.REQUIRED_FIELDS, "recipient")

# 明确「改上一笔」的措辞。只有出现这些词时，才允许完整槽位的上一轮被覆盖。
MODIFY_KEYWORDS = ("改成", "改为", "换成", "换为", "调整", "修改")

CLASSIFIER_SYSTEM_PROMPT = (
    "你是 Wanchain 助手的意图分类器。把用户请求分类为 rag（官方文档问答）、"
    "bridge（跨链转账）或 clarify（信息不足需追问）。"
    "抽取跨链槽位：from_chain / to_chain 只能取 ETH、BSC、WAN，"
    "token 只能取 USDT、USDC、WAN，amount 用十进制数字字符串。"
    "严禁编造用户没有给出的参数：用户没有明确说出的链、代币、金额一律留空，"
    "不要用 Wanchain 或任何默认值补全。"
)


def merge_slots(
    previous: dict[str, Any] | None, current: BridgeSlots | None
) -> BridgeSlots:
    """本轮显式值覆盖旧值，未提及的字段保留上一轮结果。"""
    base = BridgeSlots.model_validate(previous) if previous else BridgeSlots()
    if current is None:
        return base

    merged: dict[str, Any] = {
        name: getattr(current, name)
        if getattr(current, name) is not None
        else getattr(base, name)
        for name in SLOT_FIELDS
    }

    # 改槽后两侧相同：以本轮显式指定的一侧为准，清掉另一侧交给图转澄清，
    # 而不是在路由层静默猜测用户想去哪条链。
    if merged["from_chain"] is not None and merged["from_chain"] == merged["to_chain"]:
        if current.from_chain is not None:
            merged["to_chain"] = None
        else:
            merged["from_chain"] = None

    return BridgeSlots(**merged)


def _has_modify_signal(message: str) -> bool:
    return any(keyword in message for keyword in MODIFY_KEYWORDS)


def _merge_decision(
    message: str,
    decision: RoutingDecision,
    previous_slots: dict[str, Any] | None,
) -> RoutingDecision:
    """把本轮规则结果与上一轮槽位合并。

    只有上一轮跨链尚未完成，或用户明确说「改成 / 换成」时才合并；
    否则一个全新的完整请求不应继承上一个话题的旧槽位。
    """
    if not previous_slots or decision.slots is None:
        return decision

    previous = BridgeSlots.model_validate(previous_slots)
    if previous.is_complete and not _has_modify_signal(message):
        return decision

    merged = merge_slots(previous_slots, decision.slots)
    return decision.model_copy(update={"slots": merged, "reason": "rule:bridge+merge"})


def _continuation_decision(
    message: str, previous_slots: dict[str, Any] | None
) -> RoutingDecision | None:
    """规则未命中时，判断本轮是否只是在给上一轮跨链补槽。"""
    if not previous_slots or is_question(message):
        return None

    fragment = extract_slots(message)
    if not any(getattr(fragment, name) is not None for name in SLOT_FIELDS):
        return None

    return RoutingDecision(
        intent="bridge",
        confidence=1.0,
        slots=merge_slots(previous_slots, fragment),
        reason="rule:resume_slots",
    )


async def route(
    message: str,
    llm: LLMPort,
    *,
    previous_slots: dict[str, Any] | None = None,
) -> RoutingDecision:
    """先跑规则，未命中的请求交给 LLM 做结构化分类。

    ``previous_slots`` 是同一会话上一轮的跨链槽位。本轮显式给出的字段覆盖旧值，
    未提及的保留；这样「100 USDT 跨到 BSC」+「从 ETH」可以拼成完整请求。
    """
    decision = match_rules(message)
    if decision is not None:
        if decision.intent == "bridge":
            return _merge_decision(message, decision, previous_slots)
        return decision

    continuation = _continuation_decision(message, previous_slots)
    if continuation is not None:
        return continuation

    return await llm.complete_structured(
        [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        RoutingDecision,
    )
