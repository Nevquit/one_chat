"""意图路由：规则优先、LLM 兜底。"""

from .router import CLASSIFIER_SYSTEM_PROMPT, route
from .rules import match_rules

__all__ = ["CLASSIFIER_SYSTEM_PROMPT", "match_rules", "route"]
