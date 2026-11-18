"""路由评测器的纯函数与报告测试，全部离线。"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from evaluation.router_eval import (
    REQUIRED_FIELDS,
    Prediction,
    RouterCase,
    compute_metrics,
    decision_to_prediction,
    load_cases,
    main,
)
from wanchain_agent.core.models import BridgeSlots, ChainId, RoutingDecision, TokenSymbol


def _write_cases(path: Path, cases: list[dict[str, object]]) -> Path:
    path.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
        encoding="utf-8",
    )
    return path


def test_load_cases_rejects_duplicate_ids(tmp_path):
    case = {
        "case_id": "dup",
        "input": "WanBridge 是什么？",
        "expected": {"intent": "rag", "slots": {}},
        "tags": [],
    }
    path = _write_cases(tmp_path / "cases.jsonl", [case, case])

    with pytest.raises(ValueError, match="重复"):
        load_cases(path)


def test_load_cases_rejects_unknown_intent(tmp_path):
    case = {
        "case_id": "bad",
        "input": "随便聊聊",
        "expected": {"intent": "chat", "slots": {}},
        "tags": [],
    }
    path = _write_cases(tmp_path / "cases.jsonl", [case])

    with pytest.raises(ValueError, match="intent 非法"):
        load_cases(path)


def test_decision_to_prediction_normalizes_incomplete_bridge():
    decision = RoutingDecision(
        intent="bridge",
        confidence=1.0,
        slots=BridgeSlots(
            from_chain=ChainId.ETH,
            token=TokenSymbol.USDT,
            amount=Decimal(100),
        ),
    )

    prediction = decision_to_prediction(decision)

    assert prediction.intent == "clarify"
    assert prediction.slots["from_chain"] == "ETH"
    assert prediction.slots["to_chain"] is None
    assert prediction.slots["amount"] == "100"


def test_decision_to_prediction_keeps_complete_bridge():
    decision = RoutingDecision(
        intent="bridge",
        confidence=1.0,
        slots=BridgeSlots(
            from_chain=ChainId.ETH,
            to_chain=ChainId.BSC,
            token=TokenSymbol.USDT,
            amount=Decimal(100),
        ),
    )

    prediction = decision_to_prediction(decision)

    assert prediction.intent == "bridge"
    assert prediction.slots == {
        "from_chain": "ETH",
        "to_chain": "BSC",
        "token": "USDT",
        "amount": "100",
    }


def test_compute_metrics_counts_slot_errors():
    cases = [
        RouterCase(
            case_id="bridge",
            message="x",
            expected_intent="bridge",
            expected_slots={
                "from_chain": "ETH",
                "to_chain": "BSC",
                "token": "USDT",
                "amount": "100",
            },
            tags=(),
        ),
        RouterCase(
            case_id="rag",
            message="y",
            expected_intent="rag",
            expected_slots={field: None for field in REQUIRED_FIELDS},
            tags=(),
        ),
    ]
    predictions = [
        Prediction(
            intent="bridge",
            slots={
                "from_chain": "ETH",
                "to_chain": None,
                "token": "USDT",
                "amount": "100",
            },
        ),
        Prediction(
            intent="rag",
            slots={field: None for field in REQUIRED_FIELDS},
        ),
    ]

    metrics = compute_metrics(cases, predictions)

    assert metrics.intent_accuracy == 1.0
    assert metrics.slot_tp == 3
    assert metrics.slot_fp == 0
    assert metrics.slot_fn == 1
    assert metrics.slot_f1 == pytest.approx(6 / 7)
    assert metrics.clarify_accuracy == 1.0


def test_rules_mode_passes_and_writes_report(tmp_path):
    dataset = _write_cases(
        tmp_path / "cases.jsonl",
        [
            {
                "case_id": "rag",
                "input": "WanBridge 是什么？",
                "expected": {"intent": "rag", "slots": {}},
                "tags": ["rag"],
            },
            {
                "case_id": "complete",
                "input": "把 100 USDT 从 ETH 跨到 BSC",
                "expected": {
                    "intent": "bridge",
                    "slots": {
                        "from_chain": "ETH",
                        "to_chain": "BSC",
                        "token": "USDT",
                        "amount": "100",
                    },
                },
                "tags": ["bridge"],
            },
            {
                "case_id": "clarify",
                "input": "帮我把 100 USDT 跨到 BSC",
                "expected": {
                    "intent": "clarify",
                    "slots": {
                        "from_chain": None,
                        "to_chain": "BSC",
                        "token": "USDT",
                        "amount": "100",
                    },
                },
                "tags": ["clarify"],
            },
        ],
    )
    report_dir = tmp_path / "evals"

    exit_code = main(
        [
            "--dataset",
            str(dataset),
            "--mode",
            "rules",
            "--report-dir",
            str(report_dir),
        ]
    )

    assert exit_code == 0
    reports = list(report_dir.glob("router_rules_*.json"))
    assert len(reports) == 1
    report = json.loads(reports[0].read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["metrics"]["intent_accuracy"] == 1.0
    assert report["metrics"]["slot_f1"] == 1.0
    assert report["dataset"]["case_count"] == 3
