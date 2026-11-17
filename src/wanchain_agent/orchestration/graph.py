"""编排拓扑。

```
entry → router ─┬─ rag     → knowledge_retrieve → guard → respond
                ├─ bridge  → validate → simulate → preview → await_approval ─┬─ approved → poll → respond
                │                                                         └─ rejected/过期 → respond
                └─ clarify → respond
```

路由只看 ``intent`` 与槽位是否齐全，不看 ``confidence``：
模型自评分未经校准，不能作为放行或拦截判据（见 ``core/models.RoutingDecision``）。
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from wanchain_agent.core.models import BridgeSlots
from wanchain_agent.core.ports import BridgePort, KnowledgePort, LLMPort, TracePort

from .nodes import (
    DEFAULT_MIN_RELEVANCE,
    NodeDeps,
    catching,
    make_await_approval_node,
    make_bridge_poll_node,
    make_bridge_preview_node,
    make_bridge_simulate_node,
    make_bridge_validate_node,
    make_clarify_node,
    make_entry_node,
    make_guard_node,
    make_knowledge_node,
    make_respond_node,
    make_router_node,
)
from .state import GraphState, make_checkpointer


def _route_after_router(state: GraphState) -> str:
    if state.get("error"):
        return "respond"
    decision = state.get("routing_decision") or {}
    intent = decision.get("intent")
    if intent == "rag":
        return "knowledge_retrieve"
    if intent == "bridge":
        slots = decision.get("slots") or {}
        if all(slots.get(field) for field in BridgeSlots.REQUIRED_FIELDS):
            return "bridge_validate"
        return "clarify"
    return "clarify"


def _continue_or_respond(next_node: str):
    def route(state: GraphState) -> str:
        return "respond" if state.get("error") else next_node

    return route


def _route_after_approval(state: GraphState) -> str:
    if state.get("error"):
        return "respond"
    if (state.get("approval") or {}).get("approved"):
        return "bridge_poll"
    return "respond"


def build_graph(
    *,
    llm: LLMPort,
    knowledge: KnowledgePort,
    bridge: BridgePort,
    trace: TracePort,
    checkpointer: Any | None = None,
    min_relevance: float = DEFAULT_MIN_RELEVANCE,
) -> CompiledStateGraph:
    """装配并编译图。``thread_id = session_id``，恢复时用 ``Command(resume=...)``。"""
    deps = NodeDeps(llm=llm, knowledge=knowledge, bridge=bridge, trace=trace)

    builder = StateGraph(GraphState)
    builder.add_node("entry", catching(make_entry_node(deps)))
    builder.add_node("router", catching(make_router_node(deps)))
    builder.add_node("clarify", catching(make_clarify_node(deps)))
    builder.add_node("knowledge_retrieve", catching(make_knowledge_node(deps)))
    builder.add_node("guard", catching(make_guard_node(deps, min_score=min_relevance)))
    builder.add_node("bridge_validate", catching(make_bridge_validate_node(deps)))
    builder.add_node("bridge_simulate", catching(make_bridge_simulate_node(deps)))
    builder.add_node("bridge_preview", catching(make_bridge_preview_node(deps)))
    builder.add_node("await_approval", catching(make_await_approval_node(deps)))
    builder.add_node("bridge_poll", catching(make_bridge_poll_node(deps)))
    builder.add_node("respond", catching(make_respond_node(deps)))

    builder.add_edge(START, "entry")
    builder.add_edge("entry", "router")
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "knowledge_retrieve": "knowledge_retrieve",
            "bridge_validate": "bridge_validate",
            "clarify": "clarify",
            "respond": "respond",
        },
    )
    builder.add_edge("knowledge_retrieve", "guard")
    builder.add_edge("guard", "respond")
    builder.add_conditional_edges(
        "bridge_validate",
        _continue_or_respond("bridge_simulate"),
        {"bridge_simulate": "bridge_simulate", "respond": "respond"},
    )
    builder.add_conditional_edges(
        "bridge_simulate",
        _continue_or_respond("bridge_preview"),
        {"bridge_preview": "bridge_preview", "respond": "respond"},
    )
    builder.add_conditional_edges(
        "bridge_preview",
        _continue_or_respond("await_approval"),
        {"await_approval": "await_approval", "respond": "respond"},
    )
    builder.add_conditional_edges(
        "await_approval",
        _route_after_approval,
        {"bridge_poll": "bridge_poll", "respond": "respond"},
    )
    builder.add_edge("bridge_poll", "respond")
    builder.add_edge("clarify", "respond")
    builder.add_edge("respond", END)

    return builder.compile(checkpointer=checkpointer or make_checkpointer())
