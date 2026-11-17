"""异常体系测试：错误码是前端契约，变更必须被测试挡住。"""

import pytest

from wanchain_agent.core import errors
from wanchain_agent.core.errors import AgentError, ErrorCode


def test_error_to_dict_shape():
    err = errors.UnsupportedChainError("链不支持", details={"chain": "SOL"})
    assert err.to_dict() == {
        "error": {
            "code": "unsupported_chain",
            "message": "链不支持",
            "details": {"chain": "SOL"},
        }
    }


def test_error_str_contains_code():
    assert str(errors.InvalidAddressError("地址非法")) == "[invalid_address] 地址非法"


def test_base_error_defaults_to_internal():
    err = AgentError("boom")
    assert err.code is ErrorCode.INTERNAL
    assert err.details == {}
    assert isinstance(err, Exception)


@pytest.mark.parametrize(
    ("exc_type", "code"),
    [
        (errors.ConfigError, ErrorCode.CONFIG),
        (errors.UnsupportedChainError, ErrorCode.UNSUPPORTED_CHAIN),
        (errors.UnsupportedTokenError, ErrorCode.UNSUPPORTED_TOKEN),
        (errors.InvalidAddressError, ErrorCode.INVALID_ADDRESS),
        (errors.InvalidAmountError, ErrorCode.INVALID_AMOUNT),
        (errors.SameChainError, ErrorCode.SAME_CHAIN),
        (errors.SlotsIncompleteError, ErrorCode.SLOTS_INCOMPLETE),
        (errors.LowConfidenceError, ErrorCode.LOW_CONFIDENCE),
        (errors.GuardrailBlockedError, ErrorCode.GUARDRAIL_BLOCKED),
        (errors.BridgeValidationError, ErrorCode.BRIDGE_VALIDATION),
        (errors.SimulationFailedError, ErrorCode.SIMULATION_FAILED),
        (errors.PreviewExpiredError, ErrorCode.PREVIEW_EXPIRED),
        (errors.ApprovalRejectedError, ErrorCode.APPROVAL_REJECTED),
        (errors.SessionNotFoundError, ErrorCode.SESSION_NOT_FOUND),
        (errors.UpstreamError, ErrorCode.UPSTREAM),
        (errors.RateLimitedError, ErrorCode.RATE_LIMITED),
        (errors.PromptInjectionError, ErrorCode.INJECTION_DETECTED),
    ],
)
def test_subclass_binds_expected_code(exc_type, code):
    err = exc_type("x")
    assert err.code is code
    assert err.to_dict()["error"]["code"] == code.value


def test_error_codes_are_unique():
    values = [member.value for member in ErrorCode]
    assert len(values) == len(set(values))
