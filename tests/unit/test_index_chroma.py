"""Chroma 索引适配器测试：临时持久化目录，不联网。"""

from __future__ import annotations

import pytest
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from wanchain_agent.adapters.index_chroma import ChromaVectorIndex
from wanchain_agent.core.models import Chunk


def _chunk(chunk_id: str, text: str = "Storeman 节点用 sMPC 签名跨链交易。") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=f"doc-{chunk_id}",
        source_path=f"bridge/{chunk_id}.md",
        heading_path="Bridge > Storeman",
        text=text,
        char_start=0,
        char_end=len(text),
        token_count=5,
    )


def test_write_then_read_metadata_and_embedding(tmp_path):
    path = str(tmp_path / "chroma")
    index = ChromaVectorIndex(persist_path=path)
    try:
        written = index.write(
            [_chunk("a"), _chunk("b")],
            [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        )
        assert written == 2
        assert index.count() == 2
    finally:
        index.close()

    store = ChromaDocumentStore(
        collection_name="wanchain_docs",
        persist_path=path,
        client_settings={"anonymized_telemetry": False},
    )
    try:
        documents = {document.id: document for document in store.filter_documents()}
    finally:
        store.close()

    assert set(documents) == {"a", "b"}
    first = documents["a"]
    assert first.content == "Storeman 节点用 sMPC 签名跨链交易。"
    assert first.meta["doc_id"] == "doc-a"
    assert first.meta["source_path"] == "bridge/a.md"
    assert first.meta["heading_path"] == "Bridge > Storeman"
    assert first.meta["token_count"] == 5
    assert first.embedding == pytest.approx([0.1, 0.2, 0.3])


def test_rewrite_replaces_whole_index(tmp_path):
    index = ChromaVectorIndex(persist_path=str(tmp_path / "chroma"))
    try:
        index.write([_chunk("a"), _chunk("b")], [[0.1, 0.2], [0.3, 0.4]])
        assert index.count() == 2

        index.write([_chunk("b")], [[0.3, 0.4]])

        assert index.count() == 1
    finally:
        index.close()


def test_length_mismatch_is_rejected_before_writing(tmp_path):
    index = ChromaVectorIndex(persist_path=str(tmp_path / "chroma"))
    try:
        with pytest.raises(ValueError):
            index.write([_chunk("a")], [])
        assert index.count() == 0
    finally:
        index.close()
