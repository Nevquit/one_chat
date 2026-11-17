"""知识层测试：检索去重排序与相关性守卫。"""

from __future__ import annotations

import asyncio

from tests.unit.fakes import FakeKnowledge
from wanchain_agent.core.models import Citation
from wanchain_agent.knowledge import guard_passed, rank, retrieve


def _citation(doc_id: str, score: float, snippet: str = "片段") -> Citation:
    return Citation(
        doc_id=doc_id,
        source_path=f"docs/{doc_id}.md",
        snippet=snippet,
        score=score,
    )


def test_rank_keeps_best_chunk_per_document():
    ranked = rank(
        [
            _citation("bridge", 0.3),
            _citation("bridge", 0.9, snippet="更相关"),
            _citation("storeman", 0.6),
        ]
    )

    assert [item.doc_id for item in ranked] == ["bridge", "storeman"]
    assert ranked[0].snippet == "更相关"


def test_rank_caps_results_at_top_k():
    ranked = rank([_citation(f"doc-{i}", 0.1 * i) for i in range(1, 8)], top_k=3)

    assert len(ranked) == 3
    assert ranked[0].score >= ranked[-1].score


def test_retrieve_skips_blank_query_without_calling_port():
    knowledge = FakeKnowledge()

    result = asyncio.run(retrieve("   ", knowledge))

    assert result == []
    assert knowledge.queries == []


def test_retrieve_passes_trimmed_query_and_top_k():
    knowledge = FakeKnowledge([_citation("bridge", 0.9)])

    result = asyncio.run(retrieve("  Storeman 是什么  ", knowledge, top_k=2))

    assert knowledge.queries == [("Storeman 是什么", 2)]
    assert [item.doc_id for item in result] == ["bridge"]


def test_guard_passes_at_threshold_boundary():
    assert guard_passed([_citation("bridge", 0.5)], min_score=0.5) is True
    assert guard_passed([_citation("bridge", 0.49)], min_score=0.5) is False


def test_guard_fails_without_context():
    assert guard_passed([]) is False
