"""Chroma 向量索引适配器（基于 Haystack ``ChromaDocumentStore``）。

写入时显式携带 embedding：``ChromaDocumentStore`` 的内置 ONNX 模型只在
``embedding_function`` 被真正调用时才加载，这里从不调用它，因此建库过程
不需要下载模型，也不会偷偷用另一个 embedding 模型。

``write`` 采用全量重建语义：先清空 collection 再逐条 upsert。离线建库的输入
是完整的 ``chunks.jsonl``，全量重建能保证"索引条数 == 片段条数"，避免语料
缩减后残留旧片段导致检索命中已删除内容。
"""

from __future__ import annotations

from typing import Any, Final, Literal

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from wanchain_agent.core.models import Chunk

DEFAULT_COLLECTION_NAME = "wanchain_docs"

# 文档向量已做归一化时，余弦距离与内积等价；显式指定避免不同版本默认值漂移。
DEFAULT_DISTANCE_FUNCTION: Final[Literal["l2", "cosine", "ip"]] = "cosine"


class ChromaVectorIndex:
    """实现 ``VectorIndexPort``。只负责持久化，不做 embedding。"""

    def __init__(
        self,
        *,
        persist_path: str,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        distance_function: Literal["l2", "cosine", "ip"] = DEFAULT_DISTANCE_FUNCTION,
        metadata: dict[str, Any] | None = None,
        document_store: ChromaDocumentStore | None = None,
    ) -> None:
        self._store = document_store or ChromaDocumentStore(
            collection_name=collection_name,
            persist_path=persist_path,
            distance_function=distance_function,
            metadata=metadata,
            client_settings={"anonymized_telemetry": False},
        )

    def write(self, chunks: list[Chunk], vectors: list[list[float]]) -> int:
        if len(chunks) != len(vectors):
            raise ValueError(
                f"片段数与向量数不一致：{len(chunks)} != {len(vectors)}"
            )

        self._store.delete_all_documents()
        if not chunks:
            return 0

        documents = [
            _to_document(chunk, vector) for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        return self._store.write_documents(documents, policy=DuplicatePolicy.OVERWRITE)

    def count(self) -> int:
        return self._store.count_documents()

    def close(self) -> None:
        self._store.close()


def _to_document(chunk: Chunk, vector: list[float]) -> Document:
    meta: dict[str, Any] = {
        "doc_id": chunk.doc_id,
        "source_path": chunk.source_path,
        "heading_path": chunk.heading_path,
        "char_start": chunk.char_start,
        "char_end": chunk.char_end,
        "token_count": chunk.token_count,
    }
    return Document(
        id=chunk.chunk_id,
        content=chunk.text,
        meta=meta,
        embedding=vector,
    )
