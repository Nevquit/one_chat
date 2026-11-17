"""路由层测试：规则优先、LLM 兜底，全部离线。"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from tests.unit.fakes import FakeLLM
from wanchain_agent.core.models import ChainId, RoutingDecision, TokenSymbol
from wanchain_agent.routing import match_rules, route

ADDRESS = "0x" + "1" * 40


def test_rules_extract_english_bridge_slots():
    decision = match_rules("把 100 USDT 从 ETH 跨到 BSC")

    assert decision is not None
    assert decision.intent == "bridge"
    assert decision.slots is not None
    assert (decision.slots.from_chain, decision.slots.to_chain) == (ChainId.ETH, ChainId.BSC)
    assert decision.slots.token is TokenSymbol.USDT
    assert decision.slots.amount == Decimal(100)
    assert decision.slots.is_complete


def test_rules_understand_chinese_chain_aliases():
    decision = match_rules("从以太坊跨 50 USDC 到币安链")

    assert decision is not None and decision.slots is not None
    assert (decision.slots.from_chain, decision.slots.to_chain) == (ChainId.ETH, ChainId.BSC)
    assert decision.slots.token is TokenSymbol.USDC
    assert decision.slots.amount == Decimal(50)


def test_rules_keep_partial_slots_instead_of_guessing():
    decision = match_rules("把 100 从 ETH 跨到 BSC")

    assert decision is not None and decision.slots is not None
    assert decision.slots.amount == Decimal(100)
    assert decision.slots.token is None
    assert decision.slots.missing_slots() == ["token"]


def test_rules_extract_recipient_only_with_explicit_hint():
    with_hint = match_rules(f"把 100 USDT 从 ETH 跨到 BSC，收款地址 {ADDRESS}")
    without_hint = match_rules(f"把 100 USDT 从 ETH 跨到 BSC {ADDRESS}")

    assert with_hint is not None and with_hint.slots is not None
    assert with_hint.slots.recipient == ADDRESS
    assert without_hint is not None and without_hint.slots is not None
    assert without_hint.slots.recipient is None


def test_rules_do_not_confuse_wan_token_with_wanchain():
    decision = match_rules("把 100 WAN 从 ETH 跨到 BSC")

    assert decision is not None and decision.slots is not None
    assert decision.slots.token is TokenSymbol.WAN
    assert (decision.slots.from_chain, decision.slots.to_chain) == (ChainId.ETH, ChainId.BSC)


def test_rules_drop_same_chain_and_leave_slot_missing():
    decision = match_rules("从 ETH 跨到 Ethereum")

    assert decision is not None and decision.slots is not None
    assert decision.slots.from_chain is ChainId.ETH
    assert decision.slots.to_chain is None
    assert "to_chain" in decision.slots.missing_slots()


def test_rules_reject_zero_amount():
    decision = match_rules("把 0 USDT 从 ETH 跨到 BSC")

    assert decision is not None and decision.slots is not None
    assert decision.slots.amount is None


def test_rules_answer_documentation_questions():
    decision = match_rules("Wanchain 的 Storeman 是什么？")

    assert decision is not None
    assert decision.intent == "rag"
    assert decision.slots is None


def test_rules_return_none_for_vague_messages():
    assert match_rules("这个怎么弄") is None
    assert match_rules("随便聊聊") is None
    assert match_rules("   ") is None


def test_route_prefers_rules_without_calling_llm():
    llm = FakeLLM()

    decision = asyncio.run(route("把 100 USDT 从 ETH 跨到 BSC", llm))

    assert decision.intent == "bridge"
    assert decision.reason == "rule:bridge"
    assert llm.calls == []


def test_route_falls_back_to_llm_once_for_unmatched_input():
    llm = FakeLLM()
    expected = RoutingDecision(intent="clarify", confidence=0.6)
    llm.register_structured(RoutingDecision, expected)

    decision = asyncio.run(route("这个怎么弄", llm))

    assert decision is expected
    assert len(llm.calls) == 1
    assert llm.calls[0]["schema"] is RoutingDecision
