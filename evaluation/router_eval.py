r"""路由离线评测：意图准确率、槽位 F1、澄清准确率。

两种模式：

- ``rules``：只跑确定性规则，零 token 成本，适合每次提交；
- ``llm``：走完整 ``route()``（规则 + LLM 兜底），需要 ``LLM_API_KEY``。

门禁阈值与架构文档 §11.2 对齐。报告写入 ``evals/``，包含数据集哈希、
模型名、语料哈希与 git commit，保证不同时间的报告可比较。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evaluation.report import git_commit as _git_commit
from evaluation.report import index_info as _index_info
from evaluation.report import sha256_file as _sha256_file
from wanchain_agent.core.errors import ConfigError
from wanchain_agent.core.models import BridgeSlots, RoutingDecision
from wanchain_agent.core.ports import LLMPort
from wanchain_agent.routing.router import route
from wanchain_agent.routing.rules import match_rules

DEFAULT_DATASET = Path("evaluation/datasets/router_cases.jsonl")
DEFAULT_REPORT_DIR = Path("evals")

INTENTS = ("rag", "bridge", "clarify")
REQUIRED_FIELDS = ("from_chain", "to_chain", "token", "amount")
GATES = {
    "intent_accuracy": 0.90,
    "slot_f1": 0.85,
    "clarify_accuracy": 0.85,
}


@dataclass(frozen=True)
class RouterCase:
    case_id: str
    message: str
    expected_intent: str
    expected_slots: dict[str, str | None]
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Prediction:
    intent: str
    slots: dict[str, str | None]
    error: str | None = None


@dataclass(frozen=True)
class Metrics:
    intent_accuracy: float
    slot_precision: float
    slot_recall: float
    slot_f1: float
    clarify_accuracy: float
    intent_correct: int
    intent_total: int
    slot_tp: int
    slot_fp: int
    slot_fn: int
    clarify_correct: int
    clarify_total: int

    def as_dict(self) -> dict[str, float]:
        return {
            "intent_accuracy": self.intent_accuracy,
            "slot_precision": self.slot_precision,
            "slot_recall": self.slot_recall,
            "slot_f1": self.slot_f1,
            "clarify_accuracy": self.clarify_accuracy,
        }


def load_cases(path: Path) -> list[RouterCase]:
    """读取 JSONL 黄金集。结构错误一律抛 ``ValueError`` / ``TypeError``，不带病评测。"""
    if not path.is_file():
        raise ValueError(f"数据集不存在：{path}")

    cases: list[RouterCase] = []
    seen: set[str] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"第 {line_no} 行不是合法 JSON") from exc
        case = _parse_case(raw, line_no)
        if case.case_id in seen:
            raise ValueError(f"第 {line_no} 行 case_id 重复：{case.case_id}")
        seen.add(case.case_id)
        cases.append(case)

    if not cases:
        raise ValueError(f"数据集为空：{path}")
    return cases


def decision_to_prediction(decision: RoutingDecision | None) -> Prediction:
    """把路由结果归一成用户可见意图。

    规则路由会对信息不足的跨链请求返回 ``bridge`` 并附带残缺槽位，
    真正对用户表现为追问，因此统一归一为 ``clarify``。
    """
    if decision is None:
        return Prediction(intent="unknown", slots=_empty_slots())

    intent = decision.intent
    if intent == "bridge" and (decision.slots is None or not decision.slots.is_complete):
        intent = "clarify"
    return Prediction(intent=intent, slots=_slot_values(decision.slots))


async def evaluate_async(
    cases: Sequence[RouterCase],
    *,
    llm: LLMPort | None,
    concurrency: int = 5,
) -> list[Prediction]:
    """``llm=None`` 时只跑规则；否则跑完整路由并按并发限制调用 LLM。"""
    if llm is None:
        return [_safe_rules(case.message) for case in cases]

    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def _one(case: RouterCase) -> Prediction:
        async with semaphore:
            try:
                decision = await route(case.message, llm)
            except Exception as exc:  # noqa: BLE001 - 单条失败不拖垮整批评测
                return Prediction(
                    intent="error",
                    slots=_empty_slots(),
                    error=f"{type(exc).__name__}: {exc}",
                )
        return decision_to_prediction(decision)

    return list(await asyncio.gather(*(_one(case) for case in cases)))


def compute_metrics(
    cases: Sequence[RouterCase], predictions: Sequence[Prediction]
) -> Metrics:
    if len(cases) != len(predictions):
        raise ValueError("cases 与 predictions 数量不一致")

    intent_correct = sum(
        case.expected_intent == prediction.intent
        for case, prediction in zip(cases, predictions)
    )

    tp = fp = fn = 0
    clarify_correct = clarify_total = 0
    for case, prediction in zip(cases, predictions):
        if case.expected_intent not in ("bridge", "clarify"):
            continue
        clarify_total += 1
        if case.expected_intent == prediction.intent:
            clarify_correct += 1
        for field in REQUIRED_FIELDS:
            expected = case.expected_slots.get(field)
            actual = prediction.slots.get(field)
            if expected is not None and actual is not None:
                if expected == actual:
                    tp += 1
                else:
                    fp += 1
                    fn += 1
            elif expected is not None:
                fn += 1
            elif actual is not None:
                fp += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    total = len(cases)
    return Metrics(
        intent_accuracy=intent_correct / total if total else 0.0,
        slot_precision=precision,
        slot_recall=recall,
        slot_f1=f1,
        clarify_accuracy=clarify_correct / clarify_total if clarify_total else 0.0,
        intent_correct=intent_correct,
        intent_total=total,
        slot_tp=tp,
        slot_fp=fp,
        slot_fn=fn,
        clarify_correct=clarify_correct,
        clarify_total=clarify_total,
    )


def build_report(
    cases: Sequence[RouterCase],
    predictions: Sequence[Prediction],
    *,
    mode: str,
    dataset_path: Path,
    dataset_sha256: str,
    model: str | None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    metrics = compute_metrics(cases, predictions)
    gates = {
        name: {
            "threshold": threshold,
            "passed": getattr(metrics, name) >= threshold,
        }
        for name, threshold in GATES.items()
    }
    return {
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "mode": mode,
        "model": model,
        "git_commit": _git_commit(),
        "dataset": {
            "path": str(dataset_path),
            "sha256": dataset_sha256,
            "case_count": len(cases),
        },
        "index": _index_info(),
        "metrics": metrics.as_dict(),
        "counts": {
            "intent_correct": metrics.intent_correct,
            "intent_total": metrics.intent_total,
            "slot_tp": metrics.slot_tp,
            "slot_fp": metrics.slot_fp,
            "slot_fn": metrics.slot_fn,
            "clarify_correct": metrics.clarify_correct,
            "clarify_total": metrics.clarify_total,
        },
        "gates": gates,
        "passed": all(gate["passed"] for gate in gates.values()),
        "failures": _collect_failures(cases, predictions),
    }


def write_report(report: dict[str, Any], report_dir: Path) -> Path:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"router_{report['mode']}_{stamp}.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    dataset = Path(args.dataset)
    try:
        cases = load_cases(dataset)
    except (TypeError, ValueError) as exc:
        print(f"评测失败：{exc}", file=sys.stderr)
        return 1

    dataset_sha = _sha256_file(dataset)
    try:
        if args.mode == "llm":
            report = asyncio.run(
                _run_llm(cases, args, dataset_path=dataset, dataset_sha256=dataset_sha)
            )
        else:
            predictions = asyncio.run(evaluate_async(cases, llm=None))
            report = build_report(
                cases,
                predictions,
                mode="rules",
                dataset_path=dataset,
                dataset_sha256=dataset_sha,
                model=None,
            )
    except ConfigError as exc:
        print(f"评测失败：{exc}", file=sys.stderr)
        return 1

    path = write_report(report, Path(args.report_dir))
    _print_summary(report, path)
    return 0 if report["passed"] else 1


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="路由离线评测（意图 / 槽位 / 澄清）")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="JSONL 黄金集")
    parser.add_argument("--mode", choices=("rules", "llm"), default="rules")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    parser.add_argument("--concurrency", type=int, default=5, help="LLM 模式并发数")
    return parser.parse_args(argv)


async def _run_llm(
    cases: Sequence[RouterCase],
    args: argparse.Namespace,
    *,
    dataset_path: Path,
    dataset_sha256: str,
) -> dict[str, Any]:
    # 延迟导入，rules 模式不加载 FastAPI / 适配器依赖
    from wanchain_agent.config import Settings, build_adapters

    settings = Settings.from_env()
    adapters = build_adapters(settings)
    try:
        predictions = await evaluate_async(
            cases, llm=adapters.llm, concurrency=args.concurrency
        )
    finally:
        await adapters.aclose()

    return build_report(
        cases,
        predictions,
        mode="llm",
        dataset_path=dataset_path,
        dataset_sha256=dataset_sha256,
        model=settings.llm_model,
    )


def _safe_rules(message: str) -> Prediction:
    try:
        decision = match_rules(message)
    except Exception as exc:  # noqa: BLE001 - 规则异常同样记录为失败用例
        return Prediction(
            intent="error",
            slots=_empty_slots(),
            error=f"{type(exc).__name__}: {exc}",
        )
    return decision_to_prediction(decision)


def _parse_case(raw: Any, line_no: int) -> RouterCase:
    if not isinstance(raw, dict):
        raise TypeError(f"第 {line_no} 行必须是 JSON 对象")

    case_id = raw.get("case_id")
    message = raw.get("input")
    expected = raw.get("expected")
    tags = raw.get("tags") or []

    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError(f"第 {line_no} 行缺少 case_id")
    if not isinstance(message, str) or not message.strip():
        raise ValueError(f"第 {line_no} 行缺少 input")
    if not isinstance(expected, dict):
        raise TypeError(f"第 {line_no} 行缺少 expected 对象")

    intent = expected.get("intent")
    if intent not in INTENTS:
        raise ValueError(f"第 {line_no} 行 intent 非法：{intent}")

    slots = expected.get("slots") or {}
    if not isinstance(slots, dict):
        raise TypeError(f"第 {line_no} 行 slots 必须是对象")
    unknown = set(slots) - set(REQUIRED_FIELDS)
    if unknown:
        raise ValueError(f"第 {line_no} 行存在未知槽位：{sorted(unknown)}")
    normalized: dict[str, str | None] = {}
    for field in REQUIRED_FIELDS:
        value = slots.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"第 {line_no} 行槽位 {field} 必须是字符串或 null")
        normalized[field] = value

    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError(f"第 {line_no} 行 tags 必须是字符串数组")

    return RouterCase(
        case_id=case_id.strip(),
        message=message.strip(),
        expected_intent=intent,
        expected_slots=normalized,
        tags=tuple(tags),
    )


def _slot_values(slots: BridgeSlots | None) -> dict[str, str | None]:
    if slots is None:
        return _empty_slots()
    return {
        "from_chain": slots.from_chain.value if slots.from_chain else None,
        "to_chain": slots.to_chain.value if slots.to_chain else None,
        "token": slots.token.value if slots.token else None,
        "amount": str(slots.amount) if slots.amount is not None else None,
    }


def _empty_slots() -> dict[str, str | None]:
    return {field: None for field in REQUIRED_FIELDS}


def _collect_failures(
    cases: Sequence[RouterCase], predictions: Sequence[Prediction]
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for case, prediction in zip(cases, predictions):
        slot_diff: dict[str, Any] = {}
        if case.expected_intent in ("bridge", "clarify"):
            for field in REQUIRED_FIELDS:
                expected = case.expected_slots.get(field)
                actual = prediction.slots.get(field)
                if expected != actual:
                    slot_diff[field] = {"expected": expected, "predicted": actual}

        if case.expected_intent == prediction.intent and not slot_diff:
            continue
        failures.append(
            {
                "case_id": case.case_id,
                "input": case.message,
                "expected_intent": case.expected_intent,
                "predicted_intent": prediction.intent,
                "slot_diff": slot_diff,
                "error": prediction.error,
            }
        )
    return failures


def _print_summary(report: dict[str, Any], path: Path) -> None:
    metrics = report["metrics"]
    print(
        f"mode={report['mode']} cases={report['dataset']['case_count']} "
        f"intent_accuracy={metrics['intent_accuracy']:.3f} "
        f"slot_f1={metrics['slot_f1']:.3f} "
        f"clarify_accuracy={metrics['clarify_accuracy']:.3f}"
    )
    print(f"gate={'PASS' if report['passed'] else 'FAIL'} report={path}")


if __name__ == "__main__":
    raise SystemExit(main())
