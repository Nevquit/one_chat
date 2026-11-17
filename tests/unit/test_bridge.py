"""跨链纯逻辑测试：校验、模拟、预览，全部离线。"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tests.unit.fakes import FAKE_ADDRESS, FakeBridge
from wanchain_agent.bridge import build_preview, is_expired, simulate, validate_slots
from wanchain_agent.core.errors import (
    InvalidAmountError,
    SimulationFailedError,
    SlotsIncompleteError,
    UnsupportedTokenError,
)
from wanchain_agent.core.models import (
    BridgeSlots,
    ChainId,
    SimulationResult,
    TokenSymbol,
    UnsignedTxPayload,
)


def _slots(**overrides) -> BridgeSlots:
    data = {
        "from_chain": ChainId.ETH,
        "to_chain": ChainId.BSC,
        "token": TokenSymbol.USDT,
        "amount": Decimal(100),
    }
    data.update(overrides)
    return BridgeSlots(**data)


def _simulation(**overrides) -> SimulationResult:
    data = {
        "bridge_fee": Decimal("0.5"),
        "estimated_receive": Decimal("99.5"),
        "expires_at": datetime.now(UTC) + timedelta(minutes=5),
    }
    data.update(overrides)
    return SimulationResult(**data)


def _payload() -> UnsignedTxPayload:
    return UnsignedTxPayload(to=FAKE_ADDRESS, data="0x", value=Decimal(0), chain_id=1)


def test_validate_returns_route_check_for_valid_slots():
    check = validate_slots(_slots())

    assert check.supported is True
    assert check.decimals == 6
    assert check.min_amount == Decimal(1)


def test_validate_rejects_incomplete_slots():
    with pytest.raises(SlotsIncompleteError):
        validate_slots(_slots(token=None))


def test_validate_rejects_too_many_decimals():
    with pytest.raises(InvalidAmountError) as excinfo:
        validate_slots(_slots(amount=Decimal("1.1234567")))

    assert excinfo.value.details["decimals"] == 6


def test_validate_rejects_amount_below_minimum():
    with pytest.raises(InvalidAmountError) as excinfo:
        validate_slots(_slots(amount=Decimal("0.5")))

    assert excinfo.value.details["min_amount"] == "1"


def test_validate_rejects_usdc_on_wanchain():
    with pytest.raises(UnsupportedTokenError):
        validate_slots(_slots(to_chain=ChainId.WAN, token=TokenSymbol.USDC))


def test_validate_rejects_wan_token_outside_wanchain():
    with pytest.raises(UnsupportedTokenError):
        validate_slots(_slots(token=TokenSymbol.WAN))


def test_simulate_passes_through_consistent_result():
    result = asyncio.run(simulate(_slots(), FakeBridge()))

    assert result.bridge_fee == Decimal("0.5")
    assert result.estimated_receive == Decimal("99.5")


class _InconsistentBridge(FakeBridge):
    async def simulate(self, slots):
        return _simulation(bridge_fee=Decimal(60), estimated_receive=Decimal(60))


def test_simulate_rejects_inconsistent_result():
    with pytest.raises(SimulationFailedError):
        asyncio.run(simulate(_slots(), _InconsistentBridge()))


def test_build_preview_reuses_simulation_values():
    simulation = _simulation()
    preview = build_preview(_slots(), simulation, _payload())

    assert preview.from_chain is ChainId.ETH
    assert preview.to_chain is ChainId.BSC
    assert preview.amount == Decimal(100)
    assert preview.bridge_fee == simulation.bridge_fee
    assert preview.estimated_receive == simulation.estimated_receive
    assert preview.expires_at == simulation.expires_at


def test_build_preview_requires_complete_slots():
    with pytest.raises(SlotsIncompleteError):
        build_preview(_slots(amount=None), _simulation(), _payload())


def test_is_expired_uses_expiry_boundary():
    simulation = _simulation()

    assert is_expired(build_preview(_slots(), simulation, _payload())) is False
    assert (
        is_expired(
            build_preview(_slots(), simulation, _payload()),
            now=simulation.expires_at,
        )
        is True
    )
