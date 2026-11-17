"""Markdown 清洗：把官方文档仓库的原始文件整理成可切分的纯文本。

只做确定性的文本处理，不做语义判断：

- 统一换行与去除 BOM，剥离 YAML front matter；
- 移除非代码区的 HTML 注释与标签，并还原 HTML 实体；
- 代码块原样保留（否则代码里的 ``<address>``、``&`` 会被误伤）；
- 清理行尾空白，连续空行压缩为一行，去掉首尾空白。

导航、页脚等结构性内容不做启发式删除——误删正文的代价远高于多几个噪声块，
这一层只保证「同一份输入永远得到同一份输出」。
"""

from __future__ import annotations

import html
import re

_FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---[ \t]*\n?", re.DOTALL)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_FENCE_OPEN_RE = re.compile(r"^[ \t]*(```+|~~~+)")


def clean_markdown(raw: str) -> str:
    """清洗 Markdown 原文。幂等：对输出再清洗结果不变。"""
    text = raw.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    text = _FRONT_MATTER_RE.sub("", text, count=1)
    text = "".join(
        segment if in_code else _clean_prose(segment)
        for in_code, segment in _split_fences(text)
    )

    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_prose(segment: str) -> str:
    segment = _HTML_COMMENT_RE.sub("", segment)
    segment = _HTML_TAG_RE.sub("", segment)
    return html.unescape(segment)


def _split_fences(text: str) -> list[tuple[bool, str]]:
    """按围栏代码块切分，返回 ``(是否代码块, 片段)``。未闭合的围栏按代码处理。"""
    segments: list[tuple[bool, str]] = []
    buffer: list[str] = []
    lines = text.splitlines(keepends=True)
    index = 0

    while index < len(lines):
        line = lines[index]
        match = _FENCE_OPEN_RE.match(line)
        if match is None:
            buffer.append(line)
            index += 1
            continue

        if buffer:
            segments.append((False, "".join(buffer)))
            buffer = []

        fence = match.group(1)
        block = [line]
        index += 1
        while index < len(lines):
            block.append(lines[index])
            closed = lines[index].strip() == fence
            index += 1
            if closed:
                break
        segments.append((True, "".join(block)))

    if buffer:
        segments.append((False, "".join(buffer)))
    return segments
