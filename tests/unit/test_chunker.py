"""切分测试：标题路径、结构保护、重叠、区间与幂等。"""

from __future__ import annotations

import pytest

from wanchain_agent.knowledge.chunker import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_OVERLAP_TOKENS,
    chunk_markdown,
    estimate_tokens,
)
from wanchain_agent.knowledge.cleaner import clean_markdown

DOC = """# Bridge

Intro paragraph about Wanchain bridge.

## Storeman

Storeman nodes use sMPC to sign cross-chain transactions.

### Rotation

Rotating keys periodically keeps the group secure.
"""


def _chunks(text: str = DOC, **kwargs):
    return chunk_markdown(
        clean_markdown(text), doc_id="bridge/architecture", source_path="bridge/architecture.md", **kwargs
    )


def test_estimate_tokens_counts_cjk_and_words():
    assert estimate_tokens("Wanchain 跨链") == 3
    assert estimate_tokens("") == 0


def test_heading_path_follows_hierarchy():
    chunks = _chunks()

    assert [chunk.heading_path for chunk in chunks] == [
        "Bridge",
        "Bridge > Storeman",
        "Bridge > Storeman > Rotation",
    ]


def test_heading_lines_are_not_part_of_body():
    chunks = _chunks()

    assert all(not chunk.text.startswith("#") for chunk in chunks)
    assert chunks[1].text.startswith("Storeman nodes")


def test_char_span_slices_cleaned_text_exactly():
    cleaned = clean_markdown(DOC)
    chunks = _chunks()

    for chunk in chunks:
        assert cleaned[chunk.char_start : chunk.char_end] == chunk.text


def test_default_params_are_documented_values():
    assert DEFAULT_MAX_TOKENS == 500
    assert DEFAULT_OVERLAP_TOKENS == 60


def test_code_fence_is_never_split():
    text = (
        "# T\n\nintro words here\n\n"
        "```solidity\ncontract A {\n    function f() {}\n}\n```\n\n"
        "after words here\n"
    )
    chunks = _chunks(text, max_tokens=5, overlap_tokens=0)

    fenced = [chunk for chunk in chunks if "```" in chunk.text]
    assert len(fenced) == 1
    assert "function f" in fenced[0].text
    assert fenced[0].text.count("```") == 2


def test_table_is_never_split():
    text = "# T\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\ntail paragraph\n"
    chunks = _chunks(text, max_tokens=2, overlap_tokens=0)

    tables = [chunk for chunk in chunks if chunk.text.startswith("|")]
    assert len(tables) == 1
    assert tables[0].text.count("\n") == 2


def test_overlap_repeats_tail_atom_in_next_chunk():
    text = (
        "# T\n\n"
        "alpha beta gamma delta\n\n"
        "echo foxtrot golf hotel\n\n"
        "india juliet kilo lima\n"
    )
    chunks = _chunks(text, max_tokens=8, overlap_tokens=4)

    assert len(chunks) == 2
    assert chunks[0].text.endswith("echo foxtrot golf hotel")
    assert chunks[1].text.startswith("echo foxtrot golf hotel")
    assert chunks[1].text.endswith("india juliet kilo lima")


def test_oversized_atom_is_kept_whole():
    text = "# T\n\n" + " ".join(f"w{index}" for index in range(20)) + "\n"
    chunks = _chunks(text, max_tokens=5, overlap_tokens=0)

    assert len(chunks) == 1
    assert chunks[0].token_count == 20


def test_chunk_ids_are_stable_and_unique():
    first = _chunks(max_tokens=10, overlap_tokens=2)
    second = _chunks(max_tokens=10, overlap_tokens=2)

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert len({chunk.chunk_id for chunk in first}) == len(first)


def test_empty_or_heading_only_documents_produce_no_chunks():
    assert _chunks("") == []
    assert _chunks("# Only title\n\n## Another\n") == []


def test_invalid_parameters_raise_value_error():
    with pytest.raises(ValueError):
        _chunks(max_tokens=0)
    with pytest.raises(ValueError):
        _chunks(max_tokens=10, overlap_tokens=10)
    with pytest.raises(ValueError):
        _chunks(overlap_tokens=-1)
