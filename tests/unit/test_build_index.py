"""离线建库测试：产物结构、幂等、清单与 CLI 退出码。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wanchain_agent.knowledge.build_index import (
    CHUNKS_FILENAME,
    MANIFEST_FILENAME,
    build_index,
    main,
)


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "bridge").mkdir(parents=True)
    (root / "bridge" / "architecture.md").write_text(
        "# Bridge\n\nStoreman 节点用 sMPC 签名跨链交易。\n", encoding="utf-8"
    )
    (root / "faq.md").write_text(
        "# FAQ\n\nWanchain 是什么？\n", encoding="utf-8"
    )
    (root / "notes.txt").write_text("不是 Markdown，应被忽略", encoding="utf-8")
    return root


def test_build_writes_chunks_and_manifest(tmp_path):
    result = build_index(_corpus(tmp_path), tmp_path / "out")

    assert result.file_count == 2
    assert result.chunk_count == 2

    lines = result.chunks_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["doc_id"] == "bridge/architecture"
    assert first["source_path"] == "bridge/architecture.md"
    assert first["text"].startswith("Storeman")

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["chunk_count"] == 2
    assert manifest["chunker"]["max_tokens"] == 500
    assert manifest["chunker"]["token_estimator"] == "cjk+word/v1"
    assert [item["path"] for item in manifest["corpus"]["files"]] == [
        "bridge/architecture.md",
        "faq.md",
    ]
    assert all(item["chunk_count"] == 1 for item in manifest["corpus"]["files"])


def test_rebuild_is_idempotent(tmp_path):
    corpus = _corpus(tmp_path)
    stamp = "2026-01-01T00:00:00+00:00"

    first = build_index(corpus, tmp_path / "out-a", generated_at=stamp)
    second = build_index(corpus, tmp_path / "out-b", generated_at=stamp)

    assert first.chunks_path.read_bytes() == second.chunks_path.read_bytes()
    assert first.manifest == second.manifest


def test_manifest_records_git_commit(tmp_path):
    result = build_index(
        _corpus(tmp_path), tmp_path / "out", git_commit="0" * 40
    )

    assert result.manifest["corpus"]["git_commit"] == "0" * 40


def test_empty_corpus_raises(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(ValueError):
        build_index(empty, tmp_path / "out")


def test_non_utf8_file_raises(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "broken.md").write_bytes(b"\xff\xfe# broken")

    with pytest.raises(ValueError):
        build_index(root, tmp_path / "out")


def test_cli_writes_artifacts(tmp_path, capsys):
    corpus = _corpus(tmp_path)
    out = tmp_path / "out"

    assert main(["--corpus", str(corpus), "--out", str(out)]) == 0

    assert (out / CHUNKS_FILENAME).is_file()
    assert (out / MANIFEST_FILENAME).is_file()
    assert "完成" in capsys.readouterr().out


def test_cli_missing_corpus_returns_exit_code_1(tmp_path, capsys):
    assert main(["--corpus", str(tmp_path / "missing"), "--out", str(tmp_path / "out")]) == 1

    assert "构建失败" in capsys.readouterr().err
