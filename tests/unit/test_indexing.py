"""离线向量建库测试：清单校验、写入一致性、CLI 失败路径。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from wanchain_agent import indexing
from wanchain_agent.core.models import Chunk
from wanchain_agent.indexing import (
    INDEX_MANIFEST_FILENAME,
    build_vector_index,
    index_chunks,
    load_chunks,
    main,
)
from tests.unit.fakes import FakeEmbedding, FakeVectorIndex


def _chunk(chunk_id: str, text: str = "Storeman 用 sMPC 完成跨链签名。") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id="bridge/architecture",
        source_path="bridge/architecture.md",
        heading_path="Bridge > Storeman",
        text=text,
        char_start=0,
        char_end=len(text),
        token_count=8,
    )


def _processed_dir(tmp_path: Path, chunks: list[Chunk]) -> Path:
    directory = tmp_path / "processed"
    directory.mkdir()
    (directory / "chunks.jsonl").write_text(
        "".join(chunk.model_dump_json() + "\n" for chunk in chunks),
        encoding="utf-8",
    )
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "corpus": {"sha256": "corpus-sha", "git_commit": "abc123"},
                "chunker": {"max_tokens": 500, "overlap_tokens": 60},
            }
        ),
        encoding="utf-8",
    )
    return directory


def test_build_writes_index_manifest(tmp_path):
    directory = _processed_dir(tmp_path, [_chunk("a"), _chunk("b")])
    embedding = FakeEmbedding(dimension=8)
    index = FakeVectorIndex()

    result = asyncio.run(
        build_vector_index(
            directory,
            embedding=embedding,
            index=index,
            generated_at="2026-01-01T00:00:00+00:00",
        )
    )

    assert result.chunk_count == 2
    assert result.vector_dimension == 8
    assert index.count() == 2
    assert embedding.document_calls == [
        ["Storeman 用 sMPC 完成跨链签名。", "Storeman 用 sMPC 完成跨链签名。"]
    ]
    vectors = index.writes[0]["vectors"]
    assert len(vectors) == 2
    assert all(len(vector) == 8 for vector in vectors)
    assert vectors[0] == vectors[1]

    manifest = json.loads((directory / INDEX_MANIFEST_FILENAME).read_text("utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["generated_at"] == "2026-01-01T00:00:00+00:00"
    assert manifest["embedding"] == {"model_name": "fake-embedding", "dimension": 8}
    assert manifest["chunks"]["count"] == 2
    assert manifest["corpus"]["sha256"] == "corpus-sha"
    assert manifest["chunker"]["max_tokens"] == 500


def test_load_chunks_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "chunks.jsonl"
    path.write_text(
        _chunk("a").model_dump_json() + "\n" + _chunk("a").model_dump_json() + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="重复"):
        load_chunks(path)


def test_load_chunks_rejects_broken_json(tmp_path):
    path = tmp_path / "chunks.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="第 1 行"):
        load_chunks(path)


def test_missing_manifest_raises(tmp_path):
    directory = tmp_path / "processed"
    directory.mkdir()
    (directory / "chunks.jsonl").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="切分清单"):
        asyncio.run(
            build_vector_index(
                directory, embedding=FakeEmbedding(), index=FakeVectorIndex()
            )
        )


def test_index_chunks_rejects_dimension_mismatch():
    class _WrongDimension(FakeEmbedding):
        async def embed_documents(self, texts):
            return [[0.0] * 3 for _ in texts]

    with pytest.raises(ValueError, match="维度"):
        asyncio.run(
            index_chunks(
                [_chunk("a")],
                embedding=_WrongDimension(dimension=8),
                index=FakeVectorIndex(),
            )
        )


def test_index_chunks_rejects_index_count_mismatch():
    class _LyingIndex(FakeVectorIndex):
        def count(self) -> int:
            return 0

    with pytest.raises(ValueError, match="索引条数"):
        asyncio.run(
            index_chunks(
                [_chunk("a")],
                embedding=FakeEmbedding(),
                index=_LyingIndex(),
            )
        )


def test_index_chunks_with_no_chunks_is_noop():
    embedding = FakeEmbedding()
    index = FakeVectorIndex()

    assert asyncio.run(index_chunks([], embedding=embedding, index=index)) == 0
    assert embedding.document_calls == []
    assert index.writes == []


def test_cli_requires_embedding_key(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("EMBEDDING_API_KEY", raising=False)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    assert main(["--processed", str(tmp_path)]) == 1
    assert "建库失败" in capsys.readouterr().err


def test_cli_runs_with_stub_adapters(tmp_path, monkeypatch, capsys):
    directory = _processed_dir(tmp_path, [_chunk("a")])
    fake_index = FakeVectorIndex()
    monkeypatch.setattr(
        indexing, "build_embedding", lambda settings: FakeEmbedding(dimension=4)
    )
    monkeypatch.setattr(
        indexing, "ChromaVectorIndex", lambda **kwargs: fake_index
    )

    assert main(["--processed", str(directory)]) == 0

    assert "完成：1 个片段" in capsys.readouterr().out
    assert fake_index.count() == 1
    assert (directory / INDEX_MANIFEST_FILENAME).is_file()
