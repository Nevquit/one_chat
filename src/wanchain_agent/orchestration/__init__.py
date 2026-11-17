"""LangGraph 编排层：节点调度、状态持久化、中断恢复。

只做薄封装，业务规则留在 ``routing/``、``knowledge/``、``bridge/``。
"""

from wanchain_agent.knowledge.guard import DEFAULT_MIN_RELEVANCE

from .graph import build_graph
from .nodes import (
    CANCELLED_TEXT,
    REFUSAL_TEXT,
    NodeDeps,
)
from .state import GraphState, initial_state, make_checkpointer, thread_config

__all__ = [
    "CANCELLED_TEXT",
    "DEFAULT_MIN_RELEVANCE",
    "REFUSAL_TEXT",
    "GraphState",
    "NodeDeps",
    "build_graph",
    "initial_state",
    "make_checkpointer",
    "thread_config",
]
