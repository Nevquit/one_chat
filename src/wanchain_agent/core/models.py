"""领域数据契约。

核心层铁律：仅依赖 Python 标准库与 Pydantic，
禁止导入 LangChain / httpx / chromadb / redis / langfuse 等第三方运行时库。

两条容易出错的约定：

1. 金额一律使用 ``Decimal``，禁止 ``float``（浮点误差会变成链上真实损失）；
   序列化为普通十进制字符串，不使用科学计数法。
2. 地址在本层只做结构校验（``0x`` + 40 位十六进制）；
   EIP-55 校验和依赖 Keccak-256，由适配器层负责，核心层不做密码学校验。
"""

from __future__ import annotations

import re
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, ClassVar, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    computed_field,
    model_validator,
)

# ---------------------------------------------------------------------------
# 基础类型
# ---------------------------------------------------------------------------

_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
_HEX_RE = re.compile(r"^0x[0-9a-fA-F]*$")


def _validate_address(value: str) -> str:
    if not _ADDRESS_RE.match(value):
        raise ValueError("地址必须为 0x 开头的 40 位十六进制字符串")
    return value


def _validate_hex_data(value: str) -> str:
    if not _HEX_RE.match(value) or len(value) % 2 != 0:
        raise ValueError("交易 data 必须为偶数长度的 0x 十六进制字符串")
    return value


def _reject_float(value: Any) -> Any:
    if isinstance(value, float):
        raise ValueError("金额禁止使用 float，请传 Decimal 或字符串")
    return value


def _serialize_amount(value: Decimal) -> str:
    return format(value, "f")


Address = Annotated[str, AfterValidator(_validate_address)]
HexData = Annotated[str, AfterValidator(_validate_hex_data)]
PositiveAmount = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    Field(gt=0),
    PlainSerializer(_serialize_amount, return_type=str),
]
NonNegativeAmount = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    Field(ge=0),
    PlainSerializer(_serialize_amount, return_type=str),
]


class ChainId(str, Enum):
    """内部链标识。与外部 API 链名的映射由适配器维护，不在核心层硬编码。"""

    ETH = "ETH"
    BSC = "BSC"
    WAN = "WAN"


class TokenSymbol(str, Enum):
    USDT = "USDT"
    USDC = "USDC"
    WAN = "WAN"


class BridgeStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS_MINTED = "SUCCESS_MINTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


Intent = Literal["rag", "bridge", "clarify"]

# ---------------------------------------------------------------------------
# 入参与流式输出
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=4000)
    wallet_address: Address | None = None


class SSEEvent(BaseModel):
    """SSE 事件。流结束由连接关闭表示，不额外定义终止事件。"""

    model_config = ConfigDict(extra="forbid")

    event: Literal["token", "citations", "tx_preview", "interrupt", "error"]
    data: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------


class BridgeSlots(BaseModel):
    """跨链槽位。允许部分缺失，由 router 的确定性检查决定是否转澄清。"""

    model_config = ConfigDict(extra="forbid")

    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = ("from_chain", "to_chain", "token", "amount")

    from_chain: ChainId | None = None
    to_chain: ChainId | None = None
    token: TokenSymbol | None = None
    amount: PositiveAmount | None = None
    recipient: Address | None = None

    def missing_slots(self) -> list[str]:
        return [name for name in self.REQUIRED_FIELDS if getattr(self, name) is None]

    @property
    def is_complete(self) -> bool:
        return not self.missing_slots()

    @model_validator(mode="after")
    def _check_distinct_chains(self) -> BridgeSlots:
        if self.from_chain is not None and self.from_chain == self.to_chain:
            raise ValueError("源链与目标链不能相同")
        return self


class RoutingDecision(BaseModel):
    """路由结果。

    ``confidence`` 来自模型自评，未经过概率校准，不能作为放行判据；
    是否进入跨链分支由 ``slots.is_complete`` 等确定性检查决定。
    """

    model_config = ConfigDict(extra="forbid")

    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    slots: BridgeSlots | None = None
    reason: str = ""


# ---------------------------------------------------------------------------
# 跨链
# ---------------------------------------------------------------------------


class RouteCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supported: bool
    reason: str = ""
    min_amount: PositiveAmount | None = None
    decimals: int | None = Field(default=None, ge=0, le=36)


class SimulationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bridge_fee: NonNegativeAmount
    estimated_receive: PositiveAmount
    estimated_gas: NonNegativeAmount | None = None
    expires_at: AwareDatetime


class UnsignedTxPayload(BaseModel):
    """待签名交易载荷。服务端只生产它，不消费签名结果。"""

    model_config = ConfigDict(extra="forbid")

    to: Address
    data: HexData
    value: NonNegativeAmount
    chain_id: int = Field(ge=1)
    gas_limit: int | None = Field(default=None, ge=0)


class TxPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_chain: ChainId
    to_chain: ChainId
    token: TokenSymbol
    amount: PositiveAmount
    bridge_fee: NonNegativeAmount
    estimated_receive: PositiveAmount
    estimated_gas: NonNegativeAmount | None = None
    unsigned_payload: UnsignedTxPayload
    expires_at: AwareDatetime

    @model_validator(mode="after")
    def _check_distinct_chains(self) -> TxPreview:
        if self.from_chain == self.to_chain:
            raise ValueError("源链与目标链不能相同")
        return self


# ---------------------------------------------------------------------------
# 知识问答
# ---------------------------------------------------------------------------


class Citation(BaseModel):
    """引用片段。``score`` 为检索/重排原始分数，不同后端不可直接比较。"""

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    heading_path: str = ""
    snippet: str = Field(min_length=1)
    score: float


class Chunk(BaseModel):
    """离线切分产物。``char_start`` / ``char_end`` 指向清洗后文档的字符区间。

    ``heading_path`` 用 ``" > "`` 连接标题层级；``token_count`` 是估算值，
    仅供切分与成本控制使用，不是模型真实计费 token 数。
    """

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)
    doc_id: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    heading_path: str = ""
    text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    token_count: int = Field(ge=1)


class RAGResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    citations: list[Citation] = Field(default_factory=list)
    faithfulness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    guard_passed: bool


# ---------------------------------------------------------------------------
# 可观测性与评测
# ---------------------------------------------------------------------------


class TokenUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class TraceSpan(BaseModel):
    """``metadata`` 中禁止写入完整 prompt 或未脱敏地址。"""

    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(min_length=1)
    node_name: str = Field(min_length=1)
    latency_ms: float = Field(ge=0.0)
    token_usage: TokenUsage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    expected: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
