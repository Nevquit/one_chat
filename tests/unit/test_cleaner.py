"""Markdown 清洗测试：确定性、幂等、不误伤代码块。"""

from __future__ import annotations

from wanchain_agent.knowledge.cleaner import clean_markdown


def test_removes_bom_front_matter_and_normalizes_newlines():
    raw = "\ufeff---\ntitle: bridge\ntags: [a, b]\n---\r\n\r\n# 标题  \r\n正文\r\n"

    assert clean_markdown(raw) == "# 标题\n正文"


def test_strips_html_outside_code_but_keeps_fence():
    raw = (
        "<!-- 导航 -->\n"
        "<div>hello &amp; world</div>\n\n"
        "```html\n<div>keep</div> &amp;\n```\n"
    )

    cleaned = clean_markdown(raw)

    assert "hello & world" in cleaned
    assert "导航" not in cleaned
    assert "<div>keep</div> &amp;" in cleaned


def test_collapses_extra_blank_lines_and_trims_edges():
    raw = "\n\nA\n\n\n\nB\n\n\n"

    assert clean_markdown(raw) == "A\n\nB"


def test_preserves_tables_and_inline_markup():
    raw = "| 链 | 状态 |\n| --- | --- |\n| ETH | 支持 |\n"

    assert clean_markdown(raw) == "| 链 | 状态 |\n| --- | --- |\n| ETH | 支持 |"


def test_cleaning_is_idempotent():
    raw = "# T\n\n<div>a &lt; b</div>\n\n\n```\nx = 1 < 2\n```\n"

    once = clean_markdown(raw)

    assert clean_markdown(once) == once
