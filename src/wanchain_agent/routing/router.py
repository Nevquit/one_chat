"""路由管道：规则优先，LLM 兜底。

规则命中是确定性的，不消耗 token；只有规则无法判断时才调用 LLM。
LLM 只负责分类与槽位抽取，不做任何链上操作。
"""

from __future__ import annotations

from wanchain_agent.core.models import RoutingDecision
from wanchain_agent.core.ports import LLMPort

from .rules import match_rules

CLASSIFIER_SYSTEM_PROMPT = (
    "你是 Wanchain 助手的意图分类器。把用户请求分类为 rag（官方文档问答）、"
    "bridge（跨链转账）或 clarify（信息不足需追问）。"
    "抽取跨链槽位：from_chain / to_chain 只能取 ETH、BSC、WAN，"
    "token 只能取 USDT、USDC、WAN，amount 用十进制数字字符串。"
    "严禁编造用户没有给出的参数：用户没有明确说出的链、代币、金额一律留空，"
    "不要用 Wanchain 或任何默认值补全。"
)


async def route(message: str, llm: LLMPort) -> RoutingDecision:
    """先跑规则，未命中的请求交给 LLM 做结构化分类。"""
    decision = match_rules(message)
    if decision is not None:
        return decision

    return await llm.complete_structured(
        [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        RoutingDecision,
    )
