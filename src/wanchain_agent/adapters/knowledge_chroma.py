"""Chroma 知识检索适配器：query 向量 → 向量召回 → ``Citation``。

分数约定：Chroma 返回的是余弦距离（越小越相似），这里统一转换为
``1 - distance`` 的相似度，保证与 ``knowledge.guard`` 的"分数越高越相关"
约定一致。阈值仍需与 bge-m3 + cosine 这组配置一起调，不能沿用其他后端经验值。

启动时可传入 ``index_manifest_path`` 校验索引与当前 Embedding 配置是否一致：
模型名或维度不一致直接抛 ``ConfigError``，避免"不报错但不准"的检索。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from wanchain_agent.core.errors import ConfigError, UpstreamError
from wanchain_agent.core.models import Citation
from wanchain_agent.core.ports import EmbeddingPort

DEFAULT_COLLECTION_NAME = "wanchain_docs"
DEFAULT_INDEX_MANIFEST = "data/processed/index_manifest.json"


class ChromaKnowledge:
    """实现 ``KnowledgePort``。只做检索与结果映射，不做生成。"""

    def __init__(
        self,
        *,
        embedding: EmbeddingPort,
        persist_path: str,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        manifest_path: str | Path | None = None,
        document_store: ChromaDocumentStore | None = None,
    ) -> None:
        self._embedding = embedding
        if manifest_path is not None:
            _check_manifest(Path(manifest_path), embedding)
        self._store = document_store or ChromaDocumentStore(
            collection_name=collection_name,
            persist_path=persist_path,
            client_settings={"anonymized_telemetry": False},
        )

    async def retrieve(self, query: str, top_k: int = 5) -> list[Citation]:
        text = query.strip()
        if not text or top_k < 1:
            return []

        vector = await self._embedding.embed_query(text)
        try:
            results = self._store.search_embeddings([vector], top_k=top_k)
        except Exception as exc:  # SDK 异常统一转为领域异常
            raise UpstreamError(
                "向量检索失败", details={"reason": type(exc).__name__}
            ) from exc

        citations: list[Citation] = []
        for document in results[0] if results else []:
            if not document.content:
                continue
            meta = document.meta or {}
            citations.append(
                Citation(
                    doc_id=str(meta.get("doc_id") or document.id),
                    source_path=str(meta.get("source_path") or "unknown"),
                    heading_path=str(meta.get("heading_path") or ""),
                    snippet=document.content,
                    score=_similarity(document.score),
                )
            )
        return citations

    async def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "chunks": self._store.count_documents(),
            "model": self._embedding.model_name,
            "dimension": self._embedding.dimension,
        }

    async def aclose(self) -> None:
        self._store.close()
        closer = getattr(self._embedding, "aclose", None)
        if closer is not None:
            await closer()


def _similarity(distance: float | None) -> float:
    if distance is None:
        return 0.0
    return max(-1.0, min(1.0, 1.0 - distance))


def _check_manifest(path: Path, embedding: EmbeddingPort) -> None:
    if not path.is_file():
        raise ConfigError(
            f"找不到索引清单：{path}，请先运行 wanchain_agent.indexing",
            details={"path": str(path)},
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"索引清单不是合法 JSON：{path}") from exc

    info = data.get("embedding") if isinstance(data, dict) else None
    if not isinstance(info, dict):
        raise ConfigError(f"索引清单缺少 embedding 信息：{path}")

    if info.get("model_name") != embedding.model_name:
        raise ConfigError(
            "索引模型与当前 Embedding 配置不一致",
            details={
                "index_model": info.get("model_name"),
                "config_model": embedding.model_name,
            },
        )
    if info.get("dimension") != embedding.dimension:
        raise ConfigError(
            "索引维度与当前 Embedding 配置不一致",
            details={
                "index_dimension": info.get("dimension"),
                "config_dimension": embedding.dimension,
            },
        )
