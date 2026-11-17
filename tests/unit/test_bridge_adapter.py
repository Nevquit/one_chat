"""Wanchain 适配器测试：全部用 httpx.MockTransport，不访问真实网络。"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest

from wanchain_agent.adapters.bridge_wanchain import WanchainBridgeAdapter
from wanchain_agent.core.errors import BridgeValidationError, UpstreamError
from wanchain_agent.core.models import BridgeSlots, BridgeStatus, ChainId, TokenSymbol

USER = "0x4Cf0A877E906DEaD748A41aE7DA8c220E4247D9e"
TARGET = "0x2216072A246A84f7b9CE0f1415Dd239C9bF201aB"

CREATE_TX_OK = {
    "success": True,
    "data": {
        "approveCheck": {
            "from": USER,
            "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "to": TARGET,
            "amount": "100000000",
        },
        "tx": {
            "from": USER,
            "to": TARGET,
            "value": "0xde0b6b3a7640000",
            "data": "0x1234",
        },
        "receiveAmount": "99.5",
        "chainId": 56,
        "feeAndQuota": {
            "symbol": "USDT",
            "minQuota": "1000000",
            "maxQuota": "28543742384",
            "networkFee": {"value": "1000000000000000", "isPercent": False},
            "operationFee": {"value": "0", "isPercent": True},
        },
    },
}


def _slots(**overrides) -> BridgeSlots:
    data = {
        "from_chain": ChainId.ETH,
        "to_chain": ChainId.BSC,
        "token": TokenSymbol.USDT,
        "amount": Decimal(100),
        "recipient": USER,
    }
    data.update(overrides)
    return BridgeSlots(**data)


def _adapter(payload, *, status: int = 200, requests: list[httpx.Request] | None = None):
    log = requests if requests is not None else []

    def handler(request: httpx.Request) -> httpx.Response:
        log.append(request)
        return httpx.Response(status, json=payload)

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://bridge-api.test",
    )
    return WanchainBridgeAdapter(client=client)


def test_validate_route_sends_documented_create_tx_payload():
    requests: list[httpx.Request] = []
    adapter = _adapter(CREATE_TX_OK, requests=requests)

    check = asyncio.run(adapter.validate_route(_slots()))

    assert check.supported is True
    assert check.decimals == 6
    assert check.min_amount == Decimal(1)
    body = json.loads(requests[0].content)
    assert body == {
        "fromChain": "ETH",
        "toChain": "BNB",
        "fromToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "toToken": "0x55d398326f99059ff775485246999027b3197955",
        "toAccount": USER,
        "amount": "100",
    }
    assert requests[0].url.path == "/api/createTx"


def test_simulate_maps_receive_amount_and_fees():
    adapter = _adapter(CREATE_TX_OK)

    result = asyncio.run(adapter.simulate(_slots()))

    assert result.estimated_receive == Decimal("99.5")
    assert result.bridge_fee == Decimal("0.5")
    assert result.estimated_gas == Decimal("0.001")
    assert result.expires_at > datetime.now(UTC)


def test_build_unsigned_tx_maps_payload_fields():
    adapter = _adapter(CREATE_TX_OK)

    payload = asyncio.run(adapter.build_unsigned_tx(_slots()))

    assert payload.to == TARGET
    assert payload.data == "0x1234"
    assert payload.value == Decimal(1)
    assert payload.chain_id == 56
    assert payload.gas_limit is None


def test_create_tx_result_is_cached_within_ttl():
    requests: list[httpx.Request] = []
    adapter = _adapter(CREATE_TX_OK, requests=requests)

    async def scenario():
        await adapter.validate_route(_slots())
        return await adapter.simulate(_slots())

    result = asyncio.run(scenario())

    assert result.estimated_receive == Decimal("99.5")
    assert len(requests) == 1


def test_upstream_failure_surfaces_error():
    adapter = _adapter({"success": False, "error": "pair not supported"})

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(adapter.validate_route(_slots()))

    assert "pair not supported" in excinfo.value.message


def test_http_error_maps_to_upstream_error():
    adapter = _adapter({"success": False}, status=502)

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(adapter.simulate(_slots()))

    assert excinfo.value.details["status"] == 502


def test_missing_recipient_is_rejected_before_network():
    requests: list[httpx.Request] = []
    adapter = _adapter(CREATE_TX_OK, requests=requests)

    with pytest.raises(BridgeValidationError):
        asyncio.run(adapter.build_unsigned_tx(_slots(recipient=None)))

    assert requests == []


def test_poll_status_maps_processing_to_pending():
    adapter = _adapter({"success": True, "data": {"status": "Processing"}})

    status = asyncio.run(adapter.poll_status("0xabc"))

    assert status is BridgeStatus.PENDING


def test_poll_status_maps_success_to_minted():
    adapter = _adapter({"success": True, "data": {"status": "Success"}})

    assert asyncio.run(adapter.poll_status("0xabc")) is BridgeStatus.SUCCESS_MINTED


def test_poll_status_unknown_value_falls_back_to_unknown():
    adapter = _adapter({"success": True, "data": {"status": "something-new"}})

    assert asyncio.run(adapter.poll_status("0xabc")) is BridgeStatus.UNKNOWN
