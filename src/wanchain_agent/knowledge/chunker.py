"""标题感知的 Markdown 切分。

产物是 ``core.models.Chunk``，供后续 embedding 与向量库写入使用。

切分规则（与架构文档 §7.1 对齐）：

- 以 Markdown 标题划分章节，标题层级以 ``" > "`` 记入 ``heading_path``；
- 段落、表格、围栏代码块各自作为不可分割的原子；
- 表格与代码块绝不跨块切断；单个原子超过 ``max_tokens`` 时独占一个块，
  宁可超大也不破坏结构；
- 相邻块之间按 ``overlap_tokens`` 回带尾部原子，避免语义被边界割裂。

``token_count`` 由 ``estimate_tokens`` 估算：中日韩字符按 1 token、英文单词按
1 token 计。它只用于切分与成本控制，不是模型真实计费值。没有引入 tokenizer
依赖，换用真实分词器时递增 ``CHUNKER_VERSION`` 并重建索引即可。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from wanchain_agent.core.models import Chunk

DEFAULT_MAX_TOKENS = 500
DEFAULT_OVERLAP_TOKENS = 60
CHUNKER_VERSION = 1
TOKEN_ESTIMATOR = "cjk+word/v1"

_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE_RE = re.compile(r"^[ \t]*(```+|~~~+)")


@dataclass(frozen=True)
class _Atom:
    """不可再分的文本片段及其在原文中的区间。"""

    start: int
    end: int
    tokens: int
    heading_path: str


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数。只保证同一输入结果稳定，不保证与模型分词一致。"""
    return len(_CJK_RE.findall(text)) + len(_WORD_RE.findall(text))


def chunk_markdown(
    text: str,
    *,
    doc_id: str,
    source_path: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[Chunk]:
    """切分清洗后的 Markdown。``doc_id`` 必须跨构建稳定。"""
    if max_tokens < 1:
        raise ValueError("max_tokens 必须为正整数")
    if not 0 <= overlap_tokens < max_tokens:
        raise ValueError("overlap_tokens 必须在 [0, max_tokens) 区间内")

    chunks: list[Chunk] = []
    for group in _group_by_heading(_collect_atoms(text)):
        chunks.extend(
            _pack(
                text,
                group,
                doc_id=doc_id,
                source_path=source_path,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
            )
        )
    return chunks


def _collect_atoms(text: str) -> list[_Atom]:
    """把文档拆成原子片段，同时维护标题栈。标题行本身不进入正文。"""
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    atoms: list[_Atom] = []
    stack: list[tuple[int, str]] = []
    block_start: int | None = None
    index = 0

    def current_path() -> str:
        return " > ".join(title for _, title in stack)

    def flush(end: int) -> None:
        nonlocal block_start
        if block_start is None:
            return
        start, block_start = block_start, None
        fragment = text[start:end]
        atoms.append(_Atom(start, end, estimate_tokens(fragment), current_path()))

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        start = offsets[index]
        end = offsets[index + 1]

        fence = _FENCE_RE.match(line)
        if fence is not None:
            flush(start)
            marker = fence.group(1)
            code_end = end
            index += 1
            while index < len(lines):
                code_end = offsets[index + 1]
                closed = lines[index].strip() == marker
                index += 1
                if closed:
                    break
            fragment = text[start:code_end]
            atoms.append(
                _Atom(start, code_end, estimate_tokens(fragment), current_path())
            )
            continue

        if stripped.startswith("|"):
            flush(start)
            table_end = end
            index += 1
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_end = offsets[index + 1]
                index += 1
            fragment = text[start:table_end]
            atoms.append(
                _Atom(start, table_end, estimate_tokens(fragment), current_path())
            )
            continue

        heading = _HEADING_RE.match(stripped)
        if heading is not None:
            flush(start)
            level = len(heading.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading.group(2).strip()))
            index += 1
            continue

        if not stripped:
            flush(start)
            index += 1
            continue

        if block_start is None:
            block_start = start
        index += 1

    flush(len(text))
    return atoms


def _group_by_heading(atoms: list[_Atom]) -> list[list[_Atom]]:
    groups: list[list[_Atom]] = []
    current: list[_Atom] = []
    for atom in atoms:
        if current and current[-1].heading_path != atom.heading_path:
            groups.append(current)
            current = []
        current.append(atom)
    if current:
        groups.append(current)
    return groups


def _pack(
    text: str,
    atoms: list[_Atom],
    *,
    doc_id: str,
    source_path: str,
    max_tokens: int,
    overlap_tokens: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    current: list[_Atom] = []
    current_tokens = 0

    for atom in atoms:
        if current and current_tokens + atom.tokens > max_tokens:
            _emit(chunks, text, current, doc_id=doc_id, source_path=source_path)
            current = _overlap_tail(current, overlap_tokens)
            current_tokens = sum(item.tokens for item in current)
            while current and current_tokens + atom.tokens > max_tokens:
                current_tokens -= current[0].tokens
                current.pop(0)

        current.append(atom)
        current_tokens += atom.tokens
        if len(current) == 1 and atom.tokens >= max_tokens:
            _emit(chunks, text, current, doc_id=doc_id, source_path=source_path)
            current = []
            current_tokens = 0

    if current:
        _emit(chunks, text, current, doc_id=doc_id, source_path=source_path)
    return chunks


def _overlap_tail(atoms: list[_Atom], budget: int) -> list[_Atom]:
    """回带尾部原子，只在预算内整块带回，避免复制超大代码块。"""
    if budget <= 0:
        return []
    tail: list[_Atom] = []
    used = 0
    for atom in reversed(atoms):
        if used + atom.tokens > budget:
            break
        tail.insert(0, atom)
        used += atom.tokens
    return tail


def _emit(
    chunks: list[Chunk],
    text: str,
    atoms: list[_Atom],
    *,
    doc_id: str,
    source_path: str,
) -> None:
    start = atoms[0].start
    end = atoms[-1].end
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1

    body = text[start:end]
    if not body:
        return

    fingerprint = f"{doc_id}\0{start}\0{end}\0{body}"
    chunks.append(
        Chunk(
            chunk_id=hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
            doc_id=doc_id,
            source_path=source_path,
            heading_path=atoms[0].heading_path,
            text=body,
            char_start=start,
            char_end=end,
            token_count=max(1, estimate_tokens(body)),
        )
    )
