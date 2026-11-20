"""Wanchain 官方 Bridge API 适配器（只读 + 未签名载荷）。

端点（官方文档）：

- ``POST https://bridge-api.wanchain.org/api/createTx``  组装跨链交易
- ``GET  https://bridge-api.wanchain.org/api/status/{hash}``  查询跨链状态

安全边界：本适配器只返回未签名载荷，永不接触私钥、永不广播交易。

已知取舍：

- ``fromAccount`` 是 createTx 的必填字段，未配置时直接抛
  ``BridgeValidationError``，避免把 400 变成难以定位的 ``upstream`` 错误。
- ``bridge_fee`` 取 ``amount - receiveAmount`` 的差额，仅当源/目标代币精度
  一致时精确；精度不同时只作展示用途，不作为对账依据。
- createTx 结果按请求键做短 TTL 缓存，避免同一轮 validate / simulate /
  preview 重复打三次网络。
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator

from wanchain_agent.core.errors import (
    BridgeValidationError,
    SlotsIncompleteError,
    UnsupportedChainError,
    UnsupportedTokenError,
    UpstreamError,
)
from wanchain_agent.core.models import (
    BridgeSlots,
    BridgeStatus,
    ChainId,
    RouteCheck,
    SimulationResult,
    TokenSymbol,
    UnsignedTxPayload,
)

DEFAULT_BASE_URL = "https://bridge-api.wanchain.org"

# 官方文档中的 chainType（注意 BSC 的 chainType 是 BNB）
CHAIN_TYPES: dict[ChainId, str] = {
    ChainId.ETH: "ETH",
    ChainId.BSC: "BNB",
    ChainId.WAN: "WAN",
}

# 官方文档中的代币合约地址；WAN 在 Wanchain 上是原生币，用零地址表示
TOKEN_ADDRESSES: dict[ChainId, dict[TokenSymbol, str]] = {
    ChainId.ETH: {
        TokenSymbol.USDT: "0xdac17f958d2ee523a2206206994597c13d831ec7",
        TokenSymbol.USDC: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    },
    ChainId.BSC: {
        TokenSymbol.USDT: "0x55d398326f99059ff775485246999027b3197955",
        TokenSymbol.USDC: "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
    },
    ChainId.WAN: {
        TokenSymbol.WAN: "0x0000000000000000000000000000000000000000",
    },
}

TOKEN_DECIMALS: dict[TokenSymbol, int] = {
    TokenSymbol.USDT: 6,
    TokenSymbol.USDC: 6,
    TokenSymbol.WAN: 18,
}

_STATUS_MAP: dict[str, BridgeStatus] = {
    "processing": BridgeStatus.PENDING,
    "pending": BridgeStatus.PENDING,
    "initiated": BridgeStatus.PENDING,
    "success": BridgeStatus.SUCCESS_MINTED,
    "completed": BridgeStatus.SUCCESS_MINTED,
    "success_minted": BridgeStatus.SUCCESS_MINTED,
    "failed": BridgeStatus.FAILED,
    "refunded": BridgeStatus.FAILED,
}


class _TxBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    to: str
    data: str = "0x"
    value: str = "0x0"
    from_address: str | None = Field(default=None, alias="from")


class _Fee(BaseModel):
    model_config = ConfigDict(extra="ignore")

    value: str
    isPercent: bool = False


class _FeeAndQuota(BaseModel):
    model_config = ConfigDict(extra="ignore")

    symbol: str = ""
    minQuota: str = "0"
    maxQuota: str = "0"
    networkFee: _Fee | None = None
    operationFee: _Fee | None = None


class _CreateTxData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tx: _TxBody
    receiveAmount: str
    chainId: int
    feeAndQuota: _FeeAndQuota | None = None

    @field_validator("chainId", mode="before")
    @classmethod
    def _parse_chain_id(cls, value: Any) -> Any:
        """官方接口可能返回 ``"0x1"`` 形式的链 ID。"""
        if isinstance(value, str):
            text = value.strip()
            if text.lower().startswith("0x"):
                return int(text, 16)
        return value


class _CreateTxResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool
    error: str | None = None
    data: _CreateTxData | None = None


class _StatusData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str = ""
    lockHash: str | None = None
    redeemHash: str | None = None


class _StatusResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool
    error: str | None = None
    data: _StatusData | None = None


class WanchainBridgeAdapter:
    """实现 ``BridgePort``。所有方法只读或构建载荷。"""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        from_account: str | None = None,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
        cache_ttl_seconds: float = 60.0,
        quote_ttl_seconds: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._from_account = from_account
        self._timeout = timeout
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout
        )
        self._cache_ttl = cache_ttl_seconds
        self._quote_ttl = timedelta(seconds=quote_ttl_seconds)
        self._cache: dict[tuple[Any, ...], tuple[float, _CreateTxData]] = {}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def validate_route(self, slots: BridgeSlots) -> RouteCheck:
        data = await self._create_tx(slots)
        return RouteCheck(
            supported=True,
            reason="createTx accepted",
            min_amount=_smallest_to_decimal(
                data.feeAndQuota.minQuota if data.feeAndQuota else "0",
                TOKEN_DECIMALS[_require_token(slots)],
            ),
            decimals=TOKEN_DECIMALS[_require_token(slots)],
        )

    async def simulate(self, slots: BridgeSlots) -> SimulationResult:
        data = await self._create_tx(slots)
        amount = _require_amount(slots)
        try:
            receive = Decimal(data.receiveAmount)
        except InvalidOperation as exc:
            raise UpstreamError(
                "createTx 返回的 receiveAmount 不是十进制数"
            ) from exc

        fee = amount - receive if amount > receive else Decimal(0)
        return SimulationResult(
            bridge_fee=fee,
            estimated_receive=receive,
            estimated_gas=_network_fee(data.feeAndQuota),
            expires_at=datetime.now(UTC) + self._quote_ttl,
        )

    async def build_unsigned_tx(self, slots: BridgeSlots) -> UnsignedTxPayload:
        data = await self._create_tx(slots)
        try:
            return UnsignedTxPayload(
                to=data.tx.to,
                data=data.tx.data or "0x",
                value=_wei_to_native(data.tx.value),
                chain_id=data.chainId,
            )
        except ValueError as exc:  # Pydantic 校验失败
            raise UpstreamError("createTx 返回的载荷字段不合法") from exc

    async def poll_status(self, tx_hash: str) -> BridgeStatus:
        if not tx_hash:
            raise BridgeValidationError("缺少交易哈希")
        raw = await self._request("GET", f"/api/status/{tx_hash}")
        payload = _StatusResponse.model_validate(raw)
        if not payload.success or payload.data is None:
            raise UpstreamError(payload.error or "状态查询未返回数据")
        return _STATUS_MAP.get(payload.data.status.strip().lower(), BridgeStatus.UNKNOWN)

    # -- 内部实现 ---------------------------------------------------------

    async def _create_tx(self, slots: BridgeSlots) -> _CreateTxData:
        body = self._build_create_tx_body(slots)
        key = (
            body["fromChain"],
            body["toChain"],
            body["fromToken"],
            body["toToken"],
            body["toAccount"],
            body["amount"],
        )

        cached = self._cache.get(key)
        now = time.monotonic()
        if cached is not None and now - cached[0] < self._cache_ttl:
            return cached[1]

        raw = await self._request("POST", "/api/createTx", json=body)
        payload = _CreateTxResponse.model_validate(raw)
        if not payload.success or payload.data is None:
            raise UpstreamError(payload.error or "createTx 未返回交易数据")

        self._cache[key] = (now, payload.data)
        return payload.data

    def _build_create_tx_body(self, slots: BridgeSlots) -> dict[str, str]:
        from_chain = slots.from_chain
        to_chain = slots.to_chain
        token = slots.token
        amount = slots.amount

        if from_chain is None or to_chain is None or token is None or amount is None:
            raise SlotsIncompleteError(
                "跨链槽位不完整：" + "、".join(slots.missing_slots() or ["unknown"])
            )
        if slots.recipient is None:
            raise BridgeValidationError("缺少收款地址，无法构建跨链交易")
        if not self._from_account:
            raise BridgeValidationError("未配置发起账户，无法构建跨链交易")

        return {
            "fromChain": _chain_type(from_chain),
            "toChain": _chain_type(to_chain),
            "fromToken": _token_address(from_chain, token),
            "toToken": _token_address(to_chain, token),
            "fromAccount": self._from_account,
            "toAccount": slots.recipient,
            "amount": format(amount, "f"),
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise UpstreamError(
                "Wanchain API 请求失败",
                details={"reason": type(exc).__name__},
            ) from exc

        if response.status_code >= 400:
            raise UpstreamError(
                "Wanchain API 返回错误状态",
                details={"status": response.status_code},
            )

        try:
            return response.json()
        except ValueError as exc:
            raise UpstreamError("Wanchain API 返回了非 JSON 响应") from exc


def _chain_type(chain: ChainId) -> str:
    try:
        return CHAIN_TYPES[chain]
    except KeyError as exc:
        raise UnsupportedChainError(f"不支持的链：{chain.value}") from exc


def _token_address(chain: ChainId, token: TokenSymbol) -> str:
    try:
        return TOKEN_ADDRESSES[chain][token]
    except KeyError as exc:
        raise UnsupportedTokenError(
            f"{token.value} 在 {chain.value} 上没有配置代币地址"
        ) from exc


def _require_token(slots: BridgeSlots) -> TokenSymbol:
    if slots.token is None:  # pragma: no cover - 调用前已校验
        raise SlotsIncompleteError("缺少代币")
    return slots.token


def _require_amount(slots: BridgeSlots) -> Decimal:
    if slots.amount is None:  # pragma: no cover - 调用前已校验
        raise SlotsIncompleteError("缺少金额")
    return slots.amount


def _smallest_to_decimal(raw: str, decimals: int) -> Decimal:
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise UpstreamError("返回的金额不是十进制数", details={"raw": raw}) from exc
    return value / (Decimal(10) ** decimals)


def _network_fee(fee_and_quota: _FeeAndQuota | None) -> Decimal | None:
    """networkFee 以 wei 计价；百分比费用无法折算成绝对值，返回 None。"""
    if fee_and_quota is None or fee_and_quota.networkFee is None:
        return None
    fee = fee_and_quota.networkFee
    if fee.isPercent:
        return None
    return _wei_to_native(fee.value)


def _parse_number(raw: str) -> Decimal:
    text = raw.strip()
    if not text:
        raise UpstreamError("返回的数值为空字符串")
    if text.startswith(("0x", "0X")):
        try:
            return Decimal(int(text, 16))
        except ValueError as exc:
            raise UpstreamError(
                "返回的数值不是合法十六进制", details={"raw": raw}
            ) from exc
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise UpstreamError("返回的数值不是十进制数", details={"raw": raw}) from exc


def _wei_to_native(raw: str) -> Decimal:
    """wei → 原生币数量（18 位小数）。"""
    return _parse_number(raw) / (Decimal(10) ** 18)
