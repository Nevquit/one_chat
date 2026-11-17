"""相关性守卫：检索分数不达标就拒答，不把低质量上下文交给模型。

``score`` 是检索/重排的原始分数，不同后端不可直接比较；
阈值必须与所用后端一起调，不能沿用别的索引的经验值。
"""

from __future__ import annotations

from wanchain_agent.core.models import Citation

DEFAULT_MIN_RELEVANCE = 0.5

REFUSAL_TEXT = "抱歉，官方文档中没有找到足够相关的依据，我无法可靠回答这个问题。"


def guard_passed(
    citations: list[Citation],
    *,
    min_score: float = DEFAULT_MIN_RELEVANCE,
) -> bool:
    if not citations:
        return False
    return max(item.score for item in citations) >= min_score
