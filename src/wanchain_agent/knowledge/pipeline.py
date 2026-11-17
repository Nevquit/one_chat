"""检索管道：召回结果去重、排序、截断。

重试策略由适配器负责（端口不定义重试与降级），这里只做纯数据处理，
保证同一 ``doc_id`` 只保留最高分片段，避免引用列表里出现重复来源。
"""

from __future__ import annotations

from wanchain_agent.core.models import Citation
from wanchain_agent.core.ports import KnowledgePort

DEFAULT_TOP_K = 5


async def retrieve(
    query: str,
    knowledge: KnowledgePort,
    *,
    top_k: int = DEFAULT_TOP_K,
) -> list[Citation]:
    text = query.strip()
    if not text:
        return []
    citations = await knowledge.retrieve(text, top_k=top_k)
    return rank(citations, top_k=top_k)


def rank(citations: list[Citation], *, top_k: int = DEFAULT_TOP_K) -> list[Citation]:
    """按分数降序，同一文档只保留最高分片段。"""
    best: dict[str, Citation] = {}
    for citation in citations:
        current = best.get(citation.doc_id)
        if current is None or citation.score > current.score:
            best[citation.doc_id] = citation
    return sorted(best.values(), key=lambda item: item.score, reverse=True)[:top_k]
