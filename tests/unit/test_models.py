"""契约层测试：只验证 core 的数据约束，不启动任何外部依赖。"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    ChatRequest,
    EvalCase,
    RouteCheck,
    RoutingDecision,
    SimulationResult,
    SSEEvent,
    TokenSymbol,
    TokenUsage,
    TraceSpan,
    TxPreview,
    UnsignedTxPayload,
)

VALID_ADDR = "0x" + "1" * 40


def _unsigned_tx() -> UnsignedTxPayload:
    return UnsignedTxPayload(to=VALID_ADDR, data="0x", value=Decimal("0"), chain_id=1)


# ---------------------------------------------------------------------------
# 金额精度
# ---------------------------------------------------------------------------


def test_amount_rejects_float():
    with pytest.raises(ValidationError):
        BridgeSlots(amount=0.1)


def test_amount_rejects_non_positive():
    for bad in ("0", "-1"):
        with pytest.raises(ValidationError):
            BridgeSlots(amount=bad)


def test_amount_arithmetic_is_exact():
    a = BridgeSlots(amount="0.1").amount
    b = BridgeSlots(amount="0.2").amount
    assert a is not None and b is not None
    assert a + b == Decimal("0.3")


def test_amount_serializes_as_plain_decimal_string():
    slots = BridgeSlots(amount="1234567890.123456789")
    assert slots.model_dump(mode="json")["amount"] == "1234567890.123456789"


def test_amount_never_uses_scientific_notation():
    payload = UnsignedTxPayload(
        to=VALID_ADDR,
        data="0x",
        value=Decimal("1E+3"),
        chain_id=1,
    )
    assert payload.model_dump(mode="json")["value"] == "1000"


# ---------------------------------------------------------------------------
# 地址与十六进制
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "0x",
        "0X" + "1" * 40,
        "0x" + "1" * 39,
        "0x" + "g" * 40,
        "1" * 40,
    ],
)
def test_address_rejects_invalid(bad: str):
    with pytest.raises(ValidationError):
        ChatRequest(session_id="s1", message="hi", wallet_address=bad)


def test_address_accepts_lower_and_mixed_case_structure():
    # 核心层只做语法校验；EIP-55 校验和由适配器负责，因此大小写混合也放行
    for addr in ("0x" + "a" * 40, "0x" + "aB" * 20):
        assert ChatRequest(session_id="s1", message="hi", wallet_address=addr).wallet_address == addr


def test_unsigned_tx_data_must_be_even_length_hex():
    with pytest.raises(ValidationError):
        UnsignedTxPayload(to=VALID_ADDR, data="0xabc", value="0", chain_id=1)


# ---------------------------------------------------------------------------
# 槽位
# ---------------------------------------------------------------------------


def test_slots_missing_and_complete():
    partial = BridgeSlots(from_chain="ETH")
    assert partial.missing_slots() == ["to_chain", "token", "amount"]
    assert not partial.is_complete

    full = BridgeSlots(from_chain="ETH", to_chain="BSC", token="USDT", amount="100")
    assert full.is_complete
    assert full.missing_slots() == []


def test_slots_reject_same_chain():
    with pytest.raises(ValidationError):
        BridgeSlots(from_chain=ChainId.ETH, to_chain=ChainId.ETH)


def test_slots_recipient_is_optional():
    full = BridgeSlots(
        from_chain="ETH",
        to_chain="BSC",
        token=TokenSymbol.USDT,
        amount="100",
    )
    assert full.recipient is None


# ---------------------------------------------------------------------------
# 交易预览
# ---------------------------------------------------------------------------


def test_preview_requires_timezone_aware_expiry():
    with pytest.raises(ValidationError):
        TxPreview(
            from_chain="ETH",
            to_chain="BSC",
            token="USDT",
            amount="100",
            bridge_fee="0.5",
            estimated_receive="99.5",
            unsigned_payload=_unsigned_tx(),
            expires_at=datetime(2026, 1, 1, 12, 0, 0),
        )


def test_preview_rejects_same_chain():
    with pytest.raises(ValidationError):
        TxPreview(
            from_chain="ETH",
            to_chain="ETH",
            token="USDT",
            amount="100",
            bridge_fee="0.5",
            estimated_receive="99.5",
            unsigned_payload=_unsigned_tx(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )


def test_simulation_result_requires_positive_receive():
    with pytest.raises(ValidationError):
        SimulationResult(
            bridge_fee="0.5",
            estimated_receive="0",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )


# ---------------------------------------------------------------------------
# 路由与流式事件
# ---------------------------------------------------------------------------


def test_routing_confidence_bounds():
    with pytest.raises(ValidationError):
        RoutingDecision(intent="rag", confidence=1.2)
    with pytest.raises(ValidationError):
        RoutingDecision(intent="rag", confidence=-0.1)


def test_sse_event_rejects_unknown_event():
    with pytest.raises(ValidationError):
        SSEEvent(event="unknown")


def test_models_forbid_extra_fields():
    with pytest.raises(ValidationError):
        ChatRequest(session_id="s1", message="hi", unexpected=1)


def test_blank_message_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(session_id="s1", message="   ")


def test_empty_session_id_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(session_id="", message="hi")


# ---------------------------------------------------------------------------
# 观测与评测
# ---------------------------------------------------------------------------


def test_token_usage_total_is_serialized():
    usage = TokenUsage(prompt_tokens=10, completion_tokens=5)
    assert usage.total_tokens == 15
    assert usage.model_dump()["total_tokens"] == 15


def test_trace_span_requires_non_negative_latency():
    with pytest.raises(ValidationError):
        TraceSpan(trace_id="t1", node_name="router", latency_ms=-1)


def test_eval_case_defaults():
    case = EvalCase(case_id="c1", input="Wanchain 跨链原理？")
    assert case.tags == []
    assert case.expected == {}


def test_route_check_decimals_bounds():
    with pytest.raises(ValidationError):
        RouteCheck(supported=True, decimals=37)
