r"""端到端评测：通过 HTTP + SSE 验证事件契约与任务结果。

设计约束：

- 只通过公开接口观察系统，不导入业务流程内部函数；
- 事件契约违约、金额错误、编造地址记为 ``[hard]``，其余任务失败记为 ``[soft]``；
- 默认只告警，``--strict`` 时才用失败数决定退出码。

用法::

    python -m evaluation.e2e_eval --base-url http://127.0.0.1:8000
    python -m evaluation.e2e_eval --filter e2e-06,e2e-12 --strict
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from evaluation.report import (
    CaseResult,
    build_report,
    collect_meta,
    write_html,
    write_json,
    write_markdown,
)

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_DATASET = Path("evaluation/datasets/e2e_cases.jsonl")
DEFAULT_REPORT_DIR = Path("evals")
CORPUS_ROOT = Path("corpus")

EVENT_NAMES = {"token", "citations", "tx_preview", "interrupt", "error"}
PREVIEW_FIELDS = (
    "from_chain",
    "to_chain",
    "token",
    "amount",
    "bridge_fee",
    "estimated_receive",
    "unsigned_payload",
    "expires_at",
)
PAYLOAD_FIELDS = ("to", "data", "value", "chain_id")
FORBIDDEN_PAYLOAD_KEYS = {
    "private_key",
    "privateKey",
    "raw_transaction",
    "rawTransaction",
    "signed_tx",
    "signature",
}
ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}\b")
STATUSES = {"active", "pending"}


class StreamError(RuntimeError):
    """HTTP 层失败，区别于事件契约违约。"""


@dataclass(frozen=True)
class Turn:
    message: str
    session: str = "main"


@dataclass(frozen=True)
class Resume:
    approved: bool
    tx_hash: str | None
    session: str = "main"
    expect: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class E2ECase:
    case_id: str
    category: str
    turns: tuple[Turn, ...]
    expect: tuple[dict[str, Any], ...]
    resume: Resume | None
    status: str
    note: str | None


def load_cases(path: Path) -> list[E2ECase]:
    """读取 JSONL；结构错误直接抛 ``ValueError`` / ``TypeError``。"""
    dataset = Path(path)
    if not dataset.is_file():
        raise ValueError(f"数据集不存在：{dataset}")

    cases: list[E2ECase] = []
    seen: set[str] = set()
    for line_no, line in enumerate(dataset.read_text(encoding="utf-8").splitlines(), start=1):
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
        raise ValueError(f"数据集为空：{dataset}")
    return cases


def _parse_case(raw: Any, line_no: int) -> E2ECase:
    if not isinstance(raw, dict):
        raise TypeError(f"第 {line_no} 行必须是 JSON 对象")

    case_id = raw.get("case_id")
    category = raw.get("category")
    status = raw.get("status", "active")
    note = raw.get("note")
    turns_raw = raw.get("turns")
    expect_raw = raw.get("expect") or []

    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError(f"第 {line_no} 行缺少 case_id")
    if not isinstance(category, str) or not category.strip():
        raise ValueError(f"第 {line_no} 行缺少 category")
    if status not in STATUSES:
        raise ValueError(f"第 {line_no} 行 status 非法：{status}")
    if note is not None and not isinstance(note, str):
        raise ValueError(f"第 {line_no} 行 note 必须是字符串")
    if not isinstance(turns_raw, list) or not turns_raw:
        raise ValueError(f"第 {line_no} 行 turns 必须是非空数组")

    turns = tuple(_parse_turn(item, line_no, index) for index, item in enumerate(turns_raw, 1))

    if not isinstance(expect_raw, list):
        raise TypeError(f"第 {line_no} 行 expect 必须是数组")
    if len(expect_raw) > len(turns):
        raise ValueError(f"第 {line_no} 行 expect 条数多于 turns")
    expect = tuple(_parse_expect(item, line_no) for item in expect_raw)
    expect = expect + tuple({} for _ in range(len(turns) - len(expect)))

    resume_raw = raw.get("resume")
    resume = _parse_resume(resume_raw, line_no) if resume_raw is not None else None

    return E2ECase(
        case_id=case_id.strip(),
        category=category.strip(),
        turns=turns,
        expect=expect,
        resume=resume,
        status=status,
        note=note,
    )


def _parse_turn(raw: Any, line_no: int, index: int) -> Turn:
    if isinstance(raw, str):
        if not raw.strip():
            raise ValueError(f"第 {line_no} 行第 {index} 轮消息为空")
        return Turn(message=raw.strip())
    if not isinstance(raw, dict):
        raise TypeError(f"第 {line_no} 行第 {index} 轮必须是字符串或对象")

    message = raw.get("message")
    session = raw.get("session", "main")
    if not isinstance(message, str) or not message.strip():
        raise ValueError(f"第 {line_no} 行第 {index} 轮缺少 message")
    if not isinstance(session, str) or not session.strip():
        raise ValueError(f"第 {line_no} 行第 {index} 轮 session 非法")
    return Turn(message=message.strip(), session=session.strip())


def _parse_expect(raw: Any, line_no: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError(f"第 {line_no} 行 expect 项必须是对象")

    checked = dict(raw)
    for key in ("events", "forbidden"):
        value = checked.get(key, [])
        if not isinstance(value, list) or any(not isinstance(name, str) for name in value):
            raise ValueError(f"第 {line_no} 行 expect.{key} 必须是字符串数组")
        unknown = set(value) - EVENT_NAMES
        if unknown:
            raise ValueError(f"第 {line_no} 行 expect.{key} 含未知事件：{sorted(unknown)}")
        checked[key] = value

    for key in ("no_citations", "citations_resolve", "no_address"):
        if key in checked and not isinstance(checked[key], bool):
            raise ValueError(f"第 {line_no} 行 expect.{key} 必须是布尔值")

    error_code = checked.get("error_code")
    if error_code is not None and not isinstance(error_code, str):
        raise ValueError(f"第 {line_no} 行 expect.error_code 必须是字符串")

    contains = checked.get("text_contains_any", [])
    if not isinstance(contains, list) or any(not isinstance(item, str) for item in contains):
        raise ValueError(f"第 {line_no} 行 expect.text_contains_any 必须是字符串数组")
    checked["text_contains_any"] = contains

    preview_fields = checked.get("preview_fields", {})
    if not isinstance(preview_fields, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in preview_fields.items()
    ):
        raise ValueError(f"第 {line_no} 行 expect.preview_fields 必须是字符串映射")
    checked["preview_fields"] = preview_fields
    return checked


def _parse_resume(raw: Any, line_no: int) -> Resume:
    if not isinstance(raw, dict):
        raise TypeError(f"第 {line_no} 行 resume 必须是对象")

    approved = raw.get("approved")
    if not isinstance(approved, bool):
        raise TypeError(f"第 {line_no} 行 resume.approved 必须是布尔值")

    tx_hash = raw.get("tx_hash")
    if tx_hash is not None and not isinstance(tx_hash, str):
        raise ValueError(f"第 {line_no} 行 resume.tx_hash 必须是字符串或 null")

    session = raw.get("session", "main")
    if not isinstance(session, str) or not session.strip():
        raise ValueError(f"第 {line_no} 行 resume.session 非法")

    expect = _parse_expect(raw.get("expect") or {}, line_no)
    return Resume(
        approved=approved,
        tx_hash=tx_hash,
        session=session.strip(),
        expect=expect,
    )


async def _read_stream(response: httpx.Response) -> list[dict[str, Any]]:
    """解析 SSE 帧；坏帧保留为 ``json_error``，交由契约检查判失败。"""
    events: list[dict[str, Any]] = []
    name: str | None = None
    data_lines: list[str] = []

    def flush() -> None:
        nonlocal name, data_lines
        if name is None:
            data_lines = []
            return
        raw = "\n".join(data_lines)
        events.append(_decode_event(name, raw))
        name = None
        data_lines = []

    async for line in response.aiter_lines():
        if line == "":
            flush()
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        value = value.removeprefix(" ")
        if field == "event":
            name = value
        elif field == "data":
            data_lines.append(value)
    flush()
    return events


def _decode_event(name: str, raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        return {"event": name, "data": None, "raw": raw, "json_error": str(exc)}
    return {"event": name, "data": data, "raw": raw}


async def _post_stream(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    timeout: float,
) -> list[dict[str, Any]]:
    try:
        async with client.stream(
            "POST", url, json=payload, timeout=httpx.Timeout(timeout, connect=10.0)
        ) as response:
            if response.status_code != 200:
                body = (await response.aread()).decode("utf-8", "replace")
                raise StreamError(f"HTTP {response.status_code}: {body[:300]}")
            return await _read_stream(response)
    except httpx.HTTPError as exc:
        raise StreamError(f"{type(exc).__name__}: {exc}") from exc


def check_events(events: Sequence[dict[str, Any]], label: str) -> list[str]:
    """与用例无关的契约检查：事件名、字段类型、预览与中断配对。"""
    failures: list[str] = []
    if not events:
        failures.append(f"[soft] {label} 没有收到任何 SSE 事件")
        return failures

    for index, item in enumerate(events, start=1):
        name = item.get("event")
        data = item.get("data")
        prefix = f"{label} 第 {index} 个事件"
        if name not in EVENT_NAMES:
            failures.append(f"[hard] {prefix} 事件名非法：{name}")
            continue
        if item.get("json_error"):
            failures.append(f"[hard] {prefix} data 不是合法 JSON：{item['json_error']}")
            continue
        if not isinstance(data, dict):
            failures.append(f"[hard] {prefix} data 必须是对象")
            continue
        failures.extend(_check_payload(name, data, prefix))

    names = [item.get("event") for item in events]
    previews = names.count("tx_preview")
    interrupts = names.count("interrupt")
    if previews != interrupts:
        failures.append(
            f"[hard] {label} tx_preview={previews} 与 interrupt={interrupts} 未成对"
        )
    if previews and names.index("tx_preview") > names.index("interrupt"):
        failures.append(f"[hard] {label} interrupt 出现在 tx_preview 之前")
    return failures


def _check_payload(name: str, data: dict[str, Any], prefix: str) -> list[str]:
    failures: list[str] = []
    if name == "token":
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            failures.append(f"[hard] {prefix} token.text 必须是非空字符串")
    elif name == "citations":
        citations = data.get("citations")
        if not isinstance(citations, list) or not citations:
            failures.append(f"[hard] {prefix} citations 必须是非空数组")
            return failures
        for item in citations:
            if not isinstance(item, dict):
                failures.append(f"[hard] {prefix} citations 项必须是对象")
                continue
            for key in ("doc_id", "source_path", "snippet", "score"):
                if key not in item:
                    failures.append(f"[hard] {prefix} citations 缺字段 {key}")
            if not isinstance(item.get("score"), (int, float)):
                failures.append(f"[hard] {prefix} citations.score 必须是数字")
    elif name == "tx_preview":
        preview = data.get("preview")
        if not isinstance(preview, dict):
            failures.append(f"[hard] {prefix} tx_preview.preview 必须是对象")
            return failures
        for key in PREVIEW_FIELDS:
            if key not in preview:
                failures.append(f"[hard] {prefix} preview 缺字段 {key}")
        if not isinstance(preview.get("amount"), str):
            failures.append(f"[hard] {prefix} preview.amount 必须是十进制字符串")
        payload = preview.get("unsigned_payload")
        if not isinstance(payload, dict):
            failures.append(f"[hard] {prefix} preview.unsigned_payload 必须是对象")
        else:
            for key in PAYLOAD_FIELDS:
                if key not in payload:
                    failures.append(f"[hard] {prefix} unsigned_payload 缺字段 {key}")
            leaked = FORBIDDEN_PAYLOAD_KEYS & set(payload)
            if leaked:
                failures.append(f"[hard] {prefix} 载荷含签名材料：{sorted(leaked)}")
    elif name == "interrupt":
        if data.get("type") != "tx_preview":
            failures.append(f"[hard] {prefix} interrupt.type 必须是 tx_preview")
        if not isinstance(data.get("session_id"), str):
            failures.append(f"[hard] {prefix} interrupt.session_id 缺失")
    elif name == "error" and (
        not isinstance(data.get("code"), str) or not isinstance(data.get("message"), str)
    ):
        failures.append(f"[hard] {prefix} error 必须含 code 与 message")
    return failures


def check_expect(events: Sequence[dict[str, Any]], expect: dict[str, Any], label: str) -> list[str]:
    """用例级期望：必需/禁止事件、错误码、引用可追溯、文本约束。"""
    failures: list[str] = []
    names = [item.get("event") for item in events]
    token_text = "\n".join(
        str(item.get("data", {}).get("text", ""))
        for item in events
        if item.get("event") == "token" and isinstance(item.get("data"), dict)
    )

    for required in expect.get("events", []):
        if required not in names:
            failures.append(f"[soft] {label} 缺少事件 {required}")
    for forbidden in expect.get("forbidden", []):
        if forbidden in names:
            failures.append(f"[soft] {label} 出现禁止事件 {forbidden}")

    if "error_code" in expect:
        codes = [
            item.get("data", {}).get("code")
            for item in events
            if item.get("event") == "error" and isinstance(item.get("data"), dict)
        ]
        if not codes:
            failures.append(f"[soft] {label} 期望 error，但没有任何 error 事件")
        elif expect["error_code"] not in codes:
            failures.append(
                f"[soft] {label} error.code 期望 {expect['error_code']}，实际 {codes}"
            )

    if expect.get("no_citations") and "citations" in names:
        failures.append(f"[soft] {label} 不应出现 citations")

    if expect.get("citations_resolve"):
        for item in events:
            if item.get("event") != "citations" or not isinstance(item.get("data"), dict):
                continue
            for citation in item["data"].get("citations", []):
                path = citation.get("source_path") if isinstance(citation, dict) else None
                if not isinstance(path, str) or not (CORPUS_ROOT / path).is_file():
                    failures.append(f"[soft] {label} 引用无法追溯：{path}")

    if expect.get("no_address"):
        found = ADDRESS_RE.search(token_text)
        if found:
            failures.append(f"[hard] {label} 输出中编造了地址：{found.group(0)}")

    for value in expect.get("text_contains_any", []):
        if value not in token_text:
            failures.append(f"[soft] {label} 回答未包含期望文本：{value}")

    preview_fields = expect.get("preview_fields", {})
    if preview_fields:
        preview = next(
            (
                item["data"].get("preview")
                for item in events
                if item.get("event") == "tx_preview" and isinstance(item.get("data"), dict)
            ),
            None,
        )
        if not isinstance(preview, dict):
            failures.append(f"[soft] {label} 期望交易预览，但没有 preview")
        else:
            for key, expected in preview_fields.items():
                actual = preview.get(key)
                if str(actual) != expected:
                    severity = "hard" if key == "amount" else "soft"
                    failures.append(
                        f"[{severity}] {label} preview.{key} 期望 {expected}，实际 {actual}"
                    )
    return failures


def _session_id(prefix: str, case_id: str, slot: str) -> str:
    return f"{prefix}-{case_id}-{slot}"[:64]


async def run_case(
    client: httpx.AsyncClient,
    base_url: str,
    case: E2ECase,
    *,
    run_prefix: str,
    timeout: float,
) -> CaseResult:
    if case.status != "active":
        return CaseResult(
            case_id=case.case_id,
            category=case.category,
            status="skipped",
            note=case.note or "pending",
        )

    started = time.perf_counter()
    failures: list[str] = []
    turns: list[dict[str, Any]] = []
    sessions: dict[str, str] = {}

    for index, (turn, expect) in enumerate(zip(case.turns, case.expect), start=1):
        session_id = sessions.setdefault(
            turn.session, _session_id(run_prefix, case.case_id, turn.session)
        )
        payload = {"session_id": session_id, "message": turn.message}
        try:
            events = await _post_stream(client, f"{base_url}/chat", payload, timeout)
        except StreamError as exc:
            failures.append(f"[hard] 第 {index} 轮请求失败：{exc}")
            turns.append(
                {
                    "index": index,
                    "session": turn.session,
                    "message": turn.message,
                    "payload": payload,
                    "expect": expect,
                    "events": [],
                    "error": str(exc),
                }
            )
            break

        failures.extend(check_events(events, f"第 {index} 轮"))
        failures.extend(check_expect(events, expect, f"第 {index} 轮"))
        turns.append(
            {
                "index": index,
                "session": turn.session,
                "message": turn.message,
                "payload": payload,
                "expect": expect,
                "events": events,
            }
        )

    if case.resume is not None and not failures:
        session_id = sessions.get(case.resume.session)
        if session_id is None:
            failures.append("[hard] resume 指向的会话没有对应轮次")
        else:
            resume_payload = {
                "session_id": session_id,
                "approved": case.resume.approved,
                "tx_hash": case.resume.tx_hash,
            }
            try:
                events = await _post_stream(
                    client,
                    f"{base_url}/chat/resume",
                    resume_payload,
                    timeout,
                )
            except StreamError as exc:
                failures.append(f"[hard] 恢复请求失败：{exc}")
                turns.append(
                    {
                        "index": "resume",
                        "session": case.resume.session,
                        "payload": resume_payload,
                        "expect": case.resume.expect,
                        "error": str(exc),
                    }
                )
            else:
                failures.extend(check_events(events, "恢复"))
                failures.extend(check_expect(events, case.resume.expect, "恢复"))
                turns.append(
                    {
                        "index": "resume",
                        "session": case.resume.session,
                        "payload": resume_payload,
                        "expect": case.resume.expect,
                        "events": events,
                    }
                )

    elapsed = int((time.perf_counter() - started) * 1000)
    return CaseResult(
        case_id=case.case_id,
        category=case.category,
        status="passed" if not failures else "failed",
        duration_ms=elapsed,
        failures=failures,
        turns=turns,
        note=case.note,
    )


async def run_all(
    cases: Sequence[E2ECase],
    *,
    base_url: str,
    run_prefix: str,
    timeout: float,
    concurrency: int,
) -> list[CaseResult]:
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async with httpx.AsyncClient(follow_redirects=False) as client:

        async def _one(case: E2ECase) -> CaseResult:
            async with semaphore:
                return await run_case(
                    client,
                    base_url,
                    case,
                    run_prefix=run_prefix,
                    timeout=timeout,
                )

        return list(await asyncio.gather(*(_one(case) for case in cases)))


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wanchain Agent 端到端评测（HTTP + SSE）")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    parser.add_argument("--filter", default="", help="逗号分隔的 case_id 子串")
    parser.add_argument("--timeout", type=float, default=90.0, help="单次请求超时秒数")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument(
        "--mode",
        default="http",
        choices=("http",),
        help="执行方式；当前仅支持真实 HTTP + SSE",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="有失败用例时返回非零；默认只告警",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        cases = load_cases(Path(args.dataset))
    except (TypeError, ValueError) as exc:
        print(f"评测失败：{exc}", file=sys.stderr)
        return 1

    filters = [item.strip() for item in args.filter.split(",") if item.strip()]
    if filters:
        cases = [case for case in cases if any(item in case.case_id for item in filters)]
        if not cases:
            print("评测失败：过滤后没有用例", file=sys.stderr)
            return 1

    base_url = args.base_url.rstrip("/")
    run_prefix = "ev" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    try:
        results = asyncio.run(
            run_all(
                cases,
                base_url=base_url,
                run_prefix=run_prefix,
                timeout=args.timeout,
                concurrency=args.concurrency,
            )
        )
    except KeyboardInterrupt:
        print("评测中断", file=sys.stderr)
        return 130

    meta = collect_meta(mode=args.mode, dataset_path=Path(args.dataset))
    report = build_report(meta, results)

    prefix = f"e2e_{args.mode}"
    json_path = write_json(report, Path(args.report_dir), prefix)
    md_path = write_markdown(report, Path(args.report_dir), prefix)
    html_path = write_html(report, Path(args.report_dir), prefix)

    summary = report["summary"]
    print(
        f"cases={summary['total']} passed={summary['passed']} failed={summary['failed']} "
        f"skipped={summary['skipped']} pass_rate={summary['pass_rate']:.3f} "
        f"hard={summary['hard_failures']} soft={summary['soft_failures']}"
    )
    for item in results:
        if item.status == "failed":
            print(f"  FAIL {item.case_id}: {item.failures[0]}")
    print(f"report={json_path}")
    print(f"report={md_path}")
    print(f"report={html_path}")

    if args.strict and summary["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
