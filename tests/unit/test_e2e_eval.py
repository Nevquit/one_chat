"""端到端评测器的纯函数测试，全部离线，不访问网络。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation import e2e_eval
from evaluation.e2e_eval import (
    Turn,
    check_events,
    check_expect,
    load_cases,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def _token(text: str = "ok") -> dict[str, object]:
    return {"event": "token", "data": {"text": text}, "raw": ""}


def _preview() -> dict[str, object]:
    return {
        "event": "tx_preview",
        "data": {
            "preview": {
                "from_chain": "ETH",
                "to_chain": "BSC",
                "token": "USDT",
                "amount": "100",
                "bridge_fee": "0.3",
                "estimated_receive": "99.7",
                "unsigned_payload": {
                    "to": "0x1111111111111111111111111111111111111111",
                    "data": "0x",
                    "value": "0",
                    "chain_id": 1,
                },
                "expires_at": "2026-11-19T10:00:00+00:00",
            }
        },
        "raw": "",
    }


def _interrupt() -> dict[str, object]:
    return {
        "event": "interrupt",
        "data": {"session_id": "s", "type": "tx_preview"},
        "raw": "",
    }


def test_load_cases_supports_mixed_turns_and_pads_expect(tmp_path: Path) -> None:
    path = _write_jsonl(
        tmp_path / "cases.jsonl",
        [
            {
                "case_id": "c1",
                "category": "rag",
                "turns": ["第一轮", {"session": "b", "message": "第二轮"}],
                "expect": [{"events": ["token"]}],
                "status": "active",
            }
        ],
    )

    (case,) = load_cases(path)
    assert case.turns[0] == Turn(message="第一轮")
    assert case.turns[1] == Turn(message="第二轮", session="b")
    assert case.expect[1] == {}


def test_load_cases_rejects_unknown_event(tmp_path: Path) -> None:
    path = _write_jsonl(
        tmp_path / "cases.jsonl",
        [
            {
                "case_id": "c1",
                "category": "rag",
                "turns": ["x"],
                "expect": [{"events": ["done"]}],
            }
        ],
    )

    with pytest.raises(ValueError, match="未知事件"):
        load_cases(path)


def test_check_events_accepts_valid_sequence() -> None:
    events = [_token(), _preview(), _interrupt()]
    assert check_events(events, "第 1 轮") == []


def test_check_events_flags_unpaired_interrupt() -> None:
    failures = check_events([_token(), _interrupt()], "第 1 轮")
    assert any("未成对" in item for item in failures)


def test_check_events_flags_float_amount() -> None:
    event = _preview()
    event["data"]["preview"]["amount"] = 100.0  # type: ignore[index]
    failures = check_events([event, _interrupt()], "第 1 轮")
    assert any("amount 必须是十进制字符串" in item for item in failures)


def test_check_expect_flags_fabricated_address() -> None:
    events = [_token("收款地址是 0x2222222222222222222222222222222222222222")]
    failures = check_expect(events, {"no_address": True}, "第 1 轮")
    assert any(item.startswith("[hard]") for item in failures)


def test_check_expect_checks_error_code_and_preview_fields() -> None:
    error = {"event": "error", "data": {"code": "invalid_amount", "message": "x"}, "raw": ""}
    assert check_expect([error], {"events": ["error"], "error_code": "invalid_amount"}, "第 1 轮") == []

    failures = check_expect(
        [_preview(), _interrupt()], {"preview_fields": {"amount": "99"}}, "第 1 轮"
    )
    assert any("preview.amount 期望 99" in item for item in failures)


def test_check_expect_citation_traceability(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus = tmp_path / "corpus"
    (corpus / "guide").mkdir(parents=True)
    (corpus / "guide" / "intro.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr(e2e_eval, "CORPUS_ROOT", corpus)

    citations = {
        "event": "citations",
        "data": {
            "citations": [
                {
                    "doc_id": "guide/intro",
                    "source_path": "guide/intro.md",
                    "snippet": "x",
                    "score": 0.9,
                }
            ]
        },
        "raw": "",
    }
    assert check_expect([citations], {"citations_resolve": True}, "第 1 轮") == []

    citations["data"]["citations"][0]["source_path"] = "guide/missing.md"
    failures = check_expect([citations], {"citations_resolve": True}, "第 1 轮")
    assert any("无法追溯" in item for item in failures)
