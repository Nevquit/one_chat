r"""评测报告契约：统一元信息、用例结果与 JSON / Markdown 输出。

所有评测脚本共享这里的元信息字段，保证不同时间的报告可以直接比较：

- ``git_commit``：被测代码版本；
- ``dataset.sha256``：黄金集版本；
- ``index.corpus_sha256``：语料版本；
- ``mode`` / ``model``：执行方式与模型。

报告只负责记录，不参与门禁判断；是否阻断由各评测脚本自己决定。
"""

from __future__ import annotations

import hashlib
import html
import json
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_INDEX_MANIFEST = Path("data/processed/manifest.json")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def git_commit() -> str | None:
    """读取当前提交；仓库不可用时返回 ``None``，不阻断评测。"""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def index_info(path: Path = DEFAULT_INDEX_MANIFEST) -> dict[str, Any] | None:
    """读取索引清单中的语料信息；缺失或损坏时返回 ``None``。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    corpus = data.get("corpus")
    if not isinstance(corpus, dict):
        return None
    return {
        "manifest": str(path),
        "corpus_sha256": corpus.get("sha256"),
        "corpus_git_commit": corpus.get("git_commit"),
        "chunk_count": data.get("chunk_count"),
    }


def collect_meta(
    *,
    mode: str,
    dataset_path: Path,
    model: str | None = None,
    runs: int = 1,
) -> dict[str, Any]:
    dataset = Path(dataset_path)
    return {
        "generated_at": utc_now(),
        "mode": mode,
        "runs": runs,
        "model": model,
        "git_commit": git_commit(),
        "dataset": {
            "path": str(dataset),
            "sha256": sha256_file(dataset),
        },
        "index": index_info(),
    }


@dataclass
class CaseResult:
    """单个用例的执行结果。

    ``failures`` 中的条目以 ``[hard]`` 或 ``[soft]`` 开头，分别对应
    零容忍的契约违约与普通任务失败，汇总时分开计数。
    """

    case_id: str
    category: str
    status: str
    duration_ms: int = 0
    failures: list[str] = field(default_factory=list)
    turns: list[dict[str, Any]] = field(default_factory=list)
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "category": self.category,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "failures": list(self.failures),
            "turns": list(self.turns),
            "note": self.note,
        }


def summarize(results: Sequence[CaseResult]) -> dict[str, Any]:
    counts = {"passed": 0, "failed": 0, "skipped": 0}
    for item in results:
        counts[item.status] = counts.get(item.status, 0) + 1

    executed = counts["passed"] + counts["failed"]
    hard = sum(
        1 for item in results for failure in item.failures if failure.startswith("[hard]")
    )
    soft = sum(
        1 for item in results for failure in item.failures if failure.startswith("[soft]")
    )
    return {
        **counts,
        "total": len(results),
        "executed": executed,
        "pass_rate": counts["passed"] / executed if executed else 0.0,
        "hard_failures": hard,
        "soft_failures": soft,
    }


def build_report(meta: dict[str, Any], results: Sequence[CaseResult]) -> dict[str, Any]:
    return {
        "meta": meta,
        "summary": summarize(results),
        "results": [item.as_dict() for item in results],
    }


def write_json(report: dict[str, Any], report_dir: Path, prefix: str) -> Path:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{prefix}_{stamp}.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_markdown(report: dict[str, Any], report_dir: Path, prefix: str) -> Path:
    """生成与人读版本的报告，字段与 JSON 完全同源。"""
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{prefix}_{stamp}.md"
    path.write_text(render_markdown(report), encoding="utf-8")
    return path


def render_markdown(report: dict[str, Any]) -> str:
    meta = report.get("meta", {})
    summary = report.get("summary", {})
    index = meta.get("index") or {}
    dataset = meta.get("dataset") or {}

    lines = [
        "# Wanchain Agent 评测报告",
        "",
        "## 运行元信息",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| 生成时间 | {meta.get('generated_at')} |",
        f"| 模式 | `{meta.get('mode')}` |",
        f"| 模型 | `{meta.get('model') or '未使用 LLM'}` |",
        f"| 代码版本 | `{meta.get('git_commit') or 'unknown'}` |",
        f"| 数据集 | `{dataset.get('path')}` |",
        f"| 数据集哈希 | `{dataset.get('sha256')}` |",
        f"| 语料哈希 | `{index.get('corpus_sha256') or 'unknown'}` |",
        f"| 索引片段数 | {index.get('chunk_count') or 'unknown'} |",
        "",
        "## 汇总",
        "",
        "| 指标 | 值 |",
        "|---|---:|",
        f"| 用例总数 | {summary.get('total', 0)} |",
        f"| 通过 | {summary.get('passed', 0)} |",
        f"| 失败 | {summary.get('failed', 0)} |",
        f"| 跳过（pending） | {summary.get('skipped', 0)} |",
        f"| 通过率 | {summary.get('pass_rate', 0.0):.3f} |",
        f"| 硬失败 | {summary.get('hard_failures', 0)} |",
        f"| 软失败 | {summary.get('soft_failures', 0)} |",
        "",
        "## 用例结果",
        "",
        "| 用例 | 分类 | 状态 | 耗时(ms) | 失败数 |",
        "|---|---|---|---:|---:|",
    ]

    for item in report.get("results", []):
        lines.append(
            f"| `{item['case_id']}` | {item['category']} | {item['status']} | "
            f"{item['duration_ms']} | {len(item['failures'])} |"
        )

    failed = [item for item in report.get("results", []) if item["status"] == "failed"]
    if failed:
        lines += ["", "## 失败明细", ""]
        for item in failed:
            lines.append(f"### `{item['case_id']}`")
            lines.append("")
            for failure in item["failures"]:
                lines.append(f"- {failure}")
            lines.append("")

    skipped = [item for item in report.get("results", []) if item["status"] == "skipped"]
    if skipped:
        lines += ["## 跳过用例", ""]
        for item in skipped:
            reason = item.get("note") or "pending"
            lines.append(f"- `{item['case_id']}`：{reason}")
        lines.append("")

    lines += [
        "> 本报告仅为基线记录。统计门禁尚未校准，默认只告警、不阻断。",
        "",
    ]
    return "\n".join(lines)


_HTML_STYLE = """
* { box-sizing: border-box; }
body {
  margin: 0; padding: 40px 24px 72px;
  background: #f5f6f4; color: #1b2420;
  font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: 15px; line-height: 1.65;
}
.wrap { max-width: 1080px; margin: 0 auto; }
h1 { font-size: 1.9rem; margin: 0 0 6px; letter-spacing: -0.02em; }
.sub { color: #6a776f; font-size: 0.9rem; margin-bottom: 28px; }
h2 { font-size: 1.15rem; margin: 36px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #dfe3dd; }
code, pre { font-family: "Cascadia Code", Consolas, monospace; }
pre {
  margin: 0; padding: 10px 12px; background: #fbfcfa;
  border: 1px solid #e3e7e1; border-radius: 6px;
  font-size: 0.8rem; line-height: 1.55; white-space: pre-wrap; word-break: break-word;
  max-height: 420px; overflow: auto;
}
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
.card { background: #fff; border: 1px solid #e3e7e1; border-radius: 8px; padding: 14px 16px; }
.card .num { font-size: 1.5rem; font-weight: 700; color: #0c6b5b; line-height: 1.1; }
.card .lbl { font-size: 0.76rem; color: #6a776f; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; background: #fff; font-size: 0.84rem; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #edf0ea; vertical-align: top; }
th { background: #eef3f0; font-weight: 600; }
td code { word-break: break-all; }
.case {
  background: #fff; border: 1px solid #e3e7e1; border-radius: 10px;
  margin-bottom: 16px; overflow: hidden;
}
.case.failed { border-color: #e5b9a6; }
.case-head {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 12px 16px; background: #f9faf8; border-bottom: 1px solid #edf0ea;
}
.cid { font-family: "Cascadia Code", Consolas, monospace; font-weight: 700; }
.cat { font-size: 0.75rem; color: #5c6a63; background: #eef3f0; padding: 2px 8px; border-radius: 999px; }
.badge { margin-left: auto; font-size: 0.75rem; padding: 2px 10px; border-radius: 999px; font-weight: 600; }
.badge.passed { background: #e4f2ea; color: #1c6b45; }
.badge.failed { background: #f9e6de; color: #a8472a; }
.badge.skipped { background: #eceeeb; color: #6a776f; }
.dur { font-size: 0.75rem; color: #7a877f; }
.note { margin: 0; padding: 10px 16px; font-size: 0.82rem; color: #6a776f; border-bottom: 1px solid #f1f3ee; }
.turn { padding: 14px 16px; border-bottom: 1px dashed #edf0ea; }
.turn:last-of-type { border-bottom: 0; }
.turn h4 { margin: 0 0 10px; font-size: 0.9rem; }
.turn h4 .sid { font-family: "Cascadia Code", Consolas, monospace; font-size: 0.75rem; color: #7a877f; font-weight: 400; margin-left: 8px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 760px) { .cols { grid-template-columns: 1fr; } }
.cols h5, .events h5 { margin: 0 0 6px; font-size: 0.75rem; color: #5c6a63; letter-spacing: 0.04em; }
.events { margin-top: 12px; }
.ev { font-family: "Cascadia Code", Consolas, monospace; font-size: 0.78rem; font-weight: 700; color: #0c6b5b; margin-bottom: 4px; }
.ev-item + .ev-item { margin-top: 10px; }
.ev-item.error .ev { color: #a8472a; }
.fails { padding: 12px 16px 16px; background: #fdf7f3; border-top: 1px solid #f3e3d9; }
.fails h4 { margin: 0 0 8px; font-size: 0.82rem; color: #a8472a; }
.fails ul { margin: 0; padding-left: 18px; font-size: 0.82rem; }
.fails li { margin-bottom: 4px; }
.fails li.hard { color: #a8472a; font-weight: 600; }
.muted { color: #7a877f; font-size: 0.82rem; }
"""


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _block(value: Any) -> str:
    return _esc(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _render_turn(turn: dict[str, Any]) -> str:
    index = turn.get("index")
    title = f"第 {index} 轮" if isinstance(index, int) else "恢复请求"
    session = turn.get("session")
    payload = turn.get("payload")
    if payload is None:
        payload = {key: turn[key] for key in ("message",) if key in turn}

    parts = [
        '<section class="turn">',
        f'<h4>{_esc(title)}<span class="sid">session={_esc(session)}</span></h4>',
        '<div class="cols">',
        f'<div><h5>请求</h5><pre>{_block(payload)}</pre></div>',
    ]
    if "expect" in turn:
        parts.append(f'<div><h5>期望</h5><pre>{_block(turn["expect"])}</pre></div>')
    else:
        parts.append('<div><h5>期望</h5><p class="muted">旧报告未记录</p></div>')
    parts.append("</div>")

    events = turn.get("events") or []
    if events:
        parts.append('<div class="events"><h5>实际事件</h5>')
        for item in events:
            name = item.get("event")
            data = item.get("data")
            body = _block(data) if data is not None else _esc(item.get("raw") or "")
            parts.append(
                f'<div class="ev-item"><div class="ev">{_esc(name)}</div><pre>{body}</pre></div>'
            )
        parts.append("</div>")
    elif turn.get("error"):
        parts.append(
            f'<div class="events"><h5>实际事件</h5>'
            f'<div class="ev-item error"><div class="ev">请求失败</div>'
            f'<pre>{_esc(turn["error"])}</pre></div></div>'
        )
    else:
        parts.append('<p class="muted">没有收到任何事件</p>')

    parts.append("</section>")
    return "".join(parts)


def _render_case(item: dict[str, Any]) -> str:
    status = item.get("status", "")
    parts = [
        f'<article class="case {_esc(status)}">',
        '<div class="case-head">',
        f'<span class="cid">{_esc(item.get("case_id"))}</span>',
        f'<span class="cat">{_esc(item.get("category"))}</span>',
        f'<span class="badge {_esc(status)}">{_esc(status)}</span>',
        f'<span class="dur">{item.get("duration_ms", 0)} ms</span>',
        "</div>",
    ]
    if item.get("note"):
        parts.append(f'<p class="note">{_esc(item["note"])}</p>')
    for turn in item.get("turns", []):
        parts.append(_render_turn(turn))
    if item.get("failures"):
        parts.append('<div class="fails"><h4>失败断言</h4><ul>')
        for failure in item["failures"]:
            severity = "hard" if failure.startswith("[hard]") else "soft"
            parts.append(f'<li class="{severity}">{_esc(failure)}</li>')
        parts.append("</ul></div>")
    parts.append("</article>")
    return "".join(parts)


def render_html(report: dict[str, Any]) -> str:
    """生成自包含 HTML 报告：包含每个用例的请求、期望与实际输出。"""
    meta = report.get("meta") or {}
    summary = report.get("summary") or {}
    index = meta.get("index") or {}
    dataset = meta.get("dataset") or {}
    results = report.get("results") or []

    meta_rows = [
        ("生成时间", meta.get("generated_at")),
        ("模式", meta.get("mode")),
        ("模型", meta.get("model") or "未使用 LLM"),
        ("代码版本", meta.get("git_commit") or "unknown"),
        ("数据集", dataset.get("path")),
        ("数据集哈希", dataset.get("sha256")),
        ("语料哈希", index.get("corpus_sha256") or "unknown"),
        ("索引片段数", index.get("chunk_count") or "unknown"),
    ]

    cards = [
        ("用例总数", summary.get("total", 0)),
        ("通过", summary.get("passed", 0)),
        ("失败", summary.get("failed", 0)),
        ("跳过", summary.get("skipped", 0)),
        ("通过率", f"{summary.get('pass_rate', 0.0):.3f}"),
        ("硬失败", summary.get("hard_failures", 0)),
        ("软失败", summary.get("soft_failures", 0)),
    ]

    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>Wanchain Agent 评测报告</title>",
        f"<style>{_HTML_STYLE}</style>",
        "</head>",
        "<body>",
        '<div class="wrap">',
        "<h1>Wanchain Agent 评测报告</h1>",
        f'<p class="sub">生成于 {_esc(meta.get("generated_at"))} · 模式 {_esc(meta.get("mode"))}</p>',
        "<h2>运行元信息</h2>",
        "<table><thead><tr><th>字段</th><th>值</th></tr></thead><tbody>",
    ]
    for key, value in meta_rows:
        parts.append(f'<tr><td>{_esc(key)}</td><td><code>{_esc(value)}</code></td></tr>')
    parts += [
        "</tbody></table>",
        "<h2>汇总</h2>",
        '<div class="cards">',
    ]
    for label, value in cards:
        parts.append(
            f'<div class="card"><div class="num">{_esc(value)}</div>'
            f'<div class="lbl">{_esc(label)}</div></div>'
        )
    parts += [
        "</div>",
        "<h2>用例明细</h2>",
        '<p class="muted">每个用例按顺序列出：请求体 → 期望 → 实际 SSE 事件（含完整 data）。</p>',
    ]
    for item in results:
        parts.append(_render_case(item))
    parts += [
        '<p class="muted">本报告仅为基线记录。统计门禁尚未校准，默认只告警、不阻断。</p>',
        "</div>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def write_html(report: dict[str, Any], report_dir: Path, prefix: str) -> Path:
    directory = Path(report_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{prefix}_{stamp}.html"
    path.write_text(render_html(report), encoding="utf-8")
    return path
