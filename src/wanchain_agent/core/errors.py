"""领域异常体系。

约定：
- 每个异常类绑定一个机器可读的 ``ErrorCode``；
- ``to_dict()`` 输出可直接作为 API 错误响应体；
- 核心层不抛第三方异常，适配器负责把 SDK 异常转换为 ``UpstreamError``。
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """机器可读错误码。前端与评测断言依赖这些值，变更需同步契约。"""

    INTERNAL = "internal"
    CONFIG = "config"
    UNSUPPORTED_CHAIN = "unsupported_chain"
    UNSUPPORTED_TOKEN = "unsupported_token"
    INVALID_ADDRESS = "invalid_address"
    INVALID_AMOUNT = "invalid_amount"
    SAME_CHAIN = "same_chain"
    SLOTS_INCOMPLETE = "slots_incomplete"
    LOW_CONFIDENCE = "low_confidence"
    GUARDRAIL_BLOCKED = "guardrail_blocked"
    BRIDGE_VALIDATION = "bridge_validation"
    SIMULATION_FAILED = "simulation_failed"
    PREVIEW_EXPIRED = "preview_expired"
    APPROVAL_REJECTED = "approval_rejected"
    SESSION_NOT_FOUND = "session_not_found"
    UPSTREAM = "upstream"
    RATE_LIMITED = "rate_limited"
    INJECTION_DETECTED = "injection_detected"


class AgentError(Exception):
    """所有领域异常的基类。"""

    code: ErrorCode = ErrorCode.INTERNAL

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict[str, Any] = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
            }
        }

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"


class ConfigError(AgentError):
    code = ErrorCode.CONFIG


class UnsupportedChainError(AgentError):
    code = ErrorCode.UNSUPPORTED_CHAIN


class UnsupportedTokenError(AgentError):
    code = ErrorCode.UNSUPPORTED_TOKEN


class InvalidAddressError(AgentError):
    code = ErrorCode.INVALID_ADDRESS


class InvalidAmountError(AgentError):
    code = ErrorCode.INVALID_AMOUNT


class SameChainError(AgentError):
    code = ErrorCode.SAME_CHAIN


class SlotsIncompleteError(AgentError):
    code = ErrorCode.SLOTS_INCOMPLETE


class LowConfidenceError(AgentError):
    code = ErrorCode.LOW_CONFIDENCE


class GuardrailBlockedError(AgentError):
    code = ErrorCode.GUARDRAIL_BLOCKED


class BridgeValidationError(AgentError):
    code = ErrorCode.BRIDGE_VALIDATION


class SimulationFailedError(AgentError):
    code = ErrorCode.SIMULATION_FAILED


class PreviewExpiredError(AgentError):
    code = ErrorCode.PREVIEW_EXPIRED


class ApprovalRejectedError(AgentError):
    code = ErrorCode.APPROVAL_REJECTED


class SessionNotFoundError(AgentError):
    code = ErrorCode.SESSION_NOT_FOUND


class UpstreamError(AgentError):
    code = ErrorCode.UPSTREAM


class RateLimitedError(AgentError):
    code = ErrorCode.RATE_LIMITED


class PromptInjectionError(AgentError):
    code = ErrorCode.INJECTION_DETECTED
