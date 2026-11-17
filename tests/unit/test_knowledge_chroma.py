"""Chroma 知识检索适配器测试：临时索引与 FakeEmbedding，不联网。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from wanchain_agent.adapters.index_chroma import ChromaVectorIndex
from wanchain_agent.adapters.knowledge_chroma import ChromaKnowledge
from wanchain_agent.core.errors import ConfigError, UpstreamError
from wanchain_agent.core.models import Chunk
from tests.unit.fakes import FakeEmbedding

COLLECTION = "test_docs"
STOREMAN = "Storeman 节点使用 sMPC 签名跨链交易。"
WANBRIDGE = "WanBridge 支持多条链之间的资产转移。"


def _chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=f"doc-{chunk_id}",
        source_path=f"guide/{chunk_id}.md",
        heading_path="Guide > Overview",
        text=text,
        char_start=0,
        char_end=len(text),
        token_count=6,
    )


def _write_index(tmp_path: Path, embedding: FakeEmbedding) -> str:
    """用与 query 相同的向量写入两个片段，保证 query 能精确命中。"""
    path = str(tmp_path / "chroma")
    chunks = [_chunk("a", STOREMAN), _chunk("b", WANBRIDGE)]
    vectors = [asyncio.run(embedding.embed_query(chunk.text)) for chunk in chunks]
    index = ChromaVectorIndex(persist_path=path, collection_name=COLLECTION)
    try:
        index.write(chunks, vectors)
    finally:
        index.close()
    return path


def _knowledge(embedding: FakeEmbedding, path: str, **kwargs) -> ChromaKnowledge:
    return ChromaKnowledge(
        embedding=embedding,
        persist_path=path,
        collection_name=COLLECTION,
        **kwargs,
    )


def test_retrieve_maps_documents_to_citations(tmp_path):
    embedding = FakeEmbedding(dimension=4)
    path = _write_index(tmp_path, embedding)
    knowledge = _knowledge(embedding, path)

    try:
        citations = asyncio.run(knowledge.retrieve(STOREMAN, top_k=2))
        health = asyncio.run(knowledge.health())
    finally:
        asyncio.run(knowledge.aclose())

    assert len(citations) == 2
    top = citations[0]
    assert top.doc_id == "doc-a"
    assert top.source_path == "guide/a.md"
    assert top.heading_path == "Guide > Overview"
    assert top.snippet == STOREMAN
    assert top.score == pytest.approx(1.0, abs=1e-3)

    assert health["status"] == "ok"
    assert health["chunks"] == 2
    assert health["model"] == "fake-embedding"
    assert health["dimension"] == 4


def test_blank_query_skips_embedding(tmp_path):
    embedding = FakeEmbedding()
    path = _write_index(tmp_path, embedding)
    embedding.query_calls.clear()
    knowledge = _knowledge(embedding, path)

    try:
        assert asyncio.run(knowledge.retrieve("   ", top_k=3)) == []
    finally:
        asyncio.run(knowledge.aclose())

    assert embedding.query_calls == []


def test_search_failure_maps_to_upstream_error(tmp_path):
    class _BrokenStore:
        def search_embeddings(self, *args, **kwargs):
            raise RuntimeError("boom")

        def close(self) -> None:
            pass

    knowledge = ChromaKnowledge(
        embedding=FakeEmbedding(),
        persist_path=str(tmp_path / "unused"),
        document_store=_BrokenStore(),
    )

    with pytest.raises(UpstreamError) as excinfo:
        asyncio.run(knowledge.retrieve("Storeman"))

    assert excinfo.value.details["reason"] == "RuntimeError"


def _manifest(tmp_path: Path, *, model: str, dimension: int) -> Path:
    path = tmp_path / "index_manifest.json"
    path.write_text(
        json.dumps({"embedding": {"model_name": model, "dimension": dimension}}),
        encoding="utf-8",
    )
    return path


def test_manifest_model_mismatch_raises(tmp_path):
    manifest = _manifest(tmp_path, model="BAAI/other", dimension=8)

    with pytest.raises(ConfigError) as excinfo:
        _knowledge(
            FakeEmbedding(model_name="fake-embedding", dimension=8),
            str(tmp_path / "chroma"),
            manifest_path=manifest,
        )

    assert excinfo.value.details["index_model"] == "BAAI/other"


def test_manifest_dimension_mismatch_raises(tmp_path):
    manifest = _manifest(tmp_path, model="fake-embedding", dimension=512)

    with pytest.raises(ConfigError) as excinfo:
        _knowledge(
            FakeEmbedding(dimension=8),
            str(tmp_path / "chroma"),
            manifest_path=manifest,
        )

    assert excinfo.value.details["index_dimension"] == 512


def test_missing_manifest_raises(tmp_path):
    with pytest.raises(ConfigError):
        _knowledge(
            FakeEmbedding(dimension=8),
            str(tmp_path / "chroma"),
            manifest_path=tmp_path / "missing.json",
        )


def test_matching_manifest_is_accepted(tmp_path):
    manifest = _manifest(tmp_path, model="fake-embedding", dimension=8)

    knowledge = _knowledge(
        FakeEmbedding(dimension=8),
        str(tmp_path / "chroma"),
        manifest_path=manifest,
    )
    asyncio.run(knowledge.aclose())
