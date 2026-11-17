"""节点实现：薄封装，只做协议调用与状态拼装。

真正的业务规则（规则路由、重排、纯函数校验）后续落在
``routing/``、``knowledge/``、``bridge/``，这里不做重复实现。
每个节点都包了 ``AgentError`` 捕获：领域异常转成 ``state["error"]``，
由图的条件边决定是否直接跳到 ``respond``。
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from wanchain_agent.core.errors import (
    AgentError,
    BridgeValidationError,
    PreviewExpiredError,
    SlotsIncompleteError,
)
from wanchain_agent.core.models import (
    BridgeSlots,
    SimulationResult,
    TxPreview,
)
from wanchain_agent.core.ports import BridgePort, KnowledgePort, LLMPort, TracePort
from wanchain_agent.routing.router import route

from .state import GraphState

DEFAULT_MIN_RELEVANCE = 0.5

REFUSAL_TEXT = "抱歉，官方文档中没有找到足够相关的依据，我无法可靠回答这个问题。"
CANCELLED_TEXT = "已取消本次跨链操作，没有生成任何待签名交易。"

CLARIFY_SYSTEM_PROMPT = (
    "你是 Wanchain 助手。用户想发起跨链转账但槽位不完整，"
    "请用一句中文追问缺失的信息，不要编造参数。"
)

ANSWER_SYSTEM_PROMPT = (
    "你是 Wanchain 文档助手。只能依据给定文档片段回答，"
    "片段不足时明确说明无法回答，不要编造。\n\n文档片段：\n{context}"
)

NodeFn = Callable[[GraphState], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class NodeDeps:
    """节点依赖的四个端口。"""

    llm: LLMPort
    knowledge: KnowledgePort
    bridge: BridgePort
    trace: TracePort


def catching(node: NodeFn) -> NodeFn:
    """把领域异常收敛为 ``state["error"]``，交给条件边决定去向。"""

    @wraps(node)
    async def wrapper(state: GraphState) -> dict[str, Any]:
        try:
            return await node(state)
        except AgentError as exc:
            return {"error": exc.to_dict()}

    return wrapper


def _last_user_content(state: GraphState) -> str:
    for message in reversed(state.get("messages") or []):
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


def _slots(state: GraphState) -> BridgeSlots:
    raw = (state.get("routing_decision") or {}).get("slots")
    if not raw:
        raise SlotsIncompleteError("缺少跨链槽位，无法继续")
    slots = BridgeSlots.model_validate(raw)
    if not slots.is_complete:
        raise SlotsIncompleteError("跨链槽位不完整：" + "、".join(slots.missing_slots()))
    return slots


def _compose_error(state: GraphState) -> str:
    error = (state.get("error") or {}).get("error", {})
    return f"处理失败：{error.get('message', '未知错误')}（{error.get('code', 'internal')}）"


def make_entry_node(deps: NodeDeps) -> NodeFn:
    async def entry(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("entry", session_id=state.get("session_id", "")):
            # 逐轮清理上一轮的瞬时字段，避免旧预览/旧错误泄漏到新问题
            return {
                "trace_id": state.get("trace_id") or uuid.uuid4().hex,
                "routing_decision": None,
                "rag_context": None,
                "guard_passed": None,
                "simulation": None,
                "tx_preview": None,
                "approval": None,
                "clarification": None,
                "tx_hash": None,
                "bridge_status": None,
                "error": None,
            }

    return entry


def make_router_node(deps: NodeDeps) -> NodeFn:
    async def router(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("router", session_id=state.get("session_id", "")):
            decision = await route(_last_user_content(state), deps.llm)
            return {"routing_decision": decision.model_dump(mode="json")}

    return router


def make_clarify_node(deps: NodeDeps) -> NodeFn:
    async def clarify(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("clarify", session_id=state.get("session_id", "")):
            raw = (state.get("routing_decision") or {}).get("slots") or {}
            missing = [
                field for field in BridgeSlots.REQUIRED_FIELDS if not raw.get(field)
            ]
            question = await deps.llm.complete(
                [
                    {"role": "system", "content": CLARIFY_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": "缺失字段：" + ("、".join(missing) or "意图不明"),
                    },
                ]
            )
            return {"clarification": question}

    return clarify


def make_knowledge_node(deps: NodeDeps) -> NodeFn:
    async def knowledge_retrieve(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("knowledge_retrieve", session_id=state.get("session_id", "")):
            citations = await deps.knowledge.retrieve(_last_user_content(state), top_k=5)
            return {"rag_context": [item.model_dump(mode="json") for item in citations]}

    return knowledge_retrieve


def make_guard_node(deps: NodeDeps, *, min_score: float) -> NodeFn:
    async def guard(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("guard", session_id=state.get("session_id", "")):
            context = state.get("rag_context") or []
            top_score = max((float(item.get("score", 0.0)) for item in context), default=0.0)
            return {"guard_passed": bool(context) and top_score >= min_score}

    return guard


def make_bridge_validate_node(deps: NodeDeps) -> NodeFn:
    async def bridge_validate(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("bridge_validate", session_id=state.get("session_id", "")):
            check = await deps.bridge.validate_route(_slots(state))
            if not check.supported:
                raise BridgeValidationError(check.reason or "该跨链路由不受支持")
            return {}

    return bridge_validate


def make_bridge_simulate_node(deps: NodeDeps) -> NodeFn:
    async def bridge_simulate(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("bridge_simulate", session_id=state.get("session_id", "")):
            simulation = await deps.bridge.simulate(_slots(state))
            return {"simulation": simulation.model_dump(mode="json")}

    return bridge_simulate


def make_bridge_preview_node(deps: NodeDeps) -> NodeFn:
    async def bridge_preview(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("bridge_preview", session_id=state.get("session_id", "")):
            slots = _slots(state)
            simulation = SimulationResult.model_validate(state["simulation"])
            payload = await deps.bridge.build_unsigned_tx(slots)
            preview = TxPreview(
                from_chain=slots.from_chain,
                to_chain=slots.to_chain,
                token=slots.token,
                amount=slots.amount,
                bridge_fee=simulation.bridge_fee,
                estimated_receive=simulation.estimated_receive,
                estimated_gas=simulation.estimated_gas,
                unsigned_payload=payload,
                expires_at=simulation.expires_at,
            )
            return {"tx_preview": preview.model_dump(mode="json")}

    return bridge_preview


def make_await_approval_node(deps: NodeDeps) -> NodeFn:
    from langgraph.types import interrupt

    async def await_approval(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("await_approval", session_id=state.get("session_id", "")):
            preview = TxPreview.model_validate(state["tx_preview"])
            decision = interrupt({"type": "tx_preview", "data": state["tx_preview"]})
            # 恢复时先校验过期，再采信用户决定；过期预览一律作废重来
            if datetime.now(UTC) >= preview.expires_at:
                raise PreviewExpiredError("交易预览已过期，请重新发起跨链")
            approval = decision if isinstance(decision, dict) else {}
            if not approval.get("approved"):
                return {"approval": {"approved": False}, "tx_hash": None}
            return {
                "approval": {"approved": True},
                "tx_hash": approval.get("tx_hash"),
            }

    return await_approval


def make_bridge_poll_node(deps: NodeDeps) -> NodeFn:
    async def bridge_poll(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("bridge_poll", session_id=state.get("session_id", "")):
            tx_hash = state.get("tx_hash")
            if not tx_hash:
                raise BridgeValidationError("用户已确认但缺少交易哈希，无法查询跨链状态")
            status = await deps.bridge.poll_status(tx_hash)
            return {"bridge_status": status.value}

    return bridge_poll


def make_respond_node(deps: NodeDeps) -> NodeFn:
    async def respond(state: GraphState) -> dict[str, Any]:
        with deps.trace.span("respond", session_id=state.get("session_id", "")):
            text = await _compose_answer(state, deps)
            return {"messages": [{"role": "assistant", "content": text}]}

    return respond


async def _compose_answer(state: GraphState, deps: NodeDeps) -> str:
    if state.get("error"):
        return _compose_error(state)

    if state.get("clarification"):
        return state["clarification"]

    intent = (state.get("routing_decision") or {}).get("intent")

    if intent == "rag":
        if not state.get("guard_passed"):
            return REFUSAL_TEXT
        context = "\n\n".join(
            f"[{item.get('source_path', '')}] {item.get('snippet', '')}"
            for item in state.get("rag_context") or []
        )
        return await deps.llm.complete(
            [
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT.format(context=context)},
                *(state.get("messages") or []),
            ]
        )

    # bridge 分支的三种终态
    if (state.get("approval") or {}).get("approved"):
        return f"跨链状态：{state.get('bridge_status') or 'UNKNOWN'}"
    if state.get("approval") is not None:
        return CANCELLED_TEXT
    return "交易预览已生成，请在钱包中确认并签名后回传交易哈希。"
