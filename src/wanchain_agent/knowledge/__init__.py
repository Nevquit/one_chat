"""知识问答：检索管道与相关性守卫。"""

from .guard import DEFAULT_MIN_RELEVANCE, REFUSAL_TEXT, guard_passed
from .pipeline import DEFAULT_TOP_K, rank, retrieve

__all__ = [
    "DEFAULT_MIN_RELEVANCE",
    "DEFAULT_TOP_K",
    "REFUSAL_TEXT",
    "guard_passed",
    "rank",
    "retrieve",
]
