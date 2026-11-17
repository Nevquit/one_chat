"""图状态与检查点。

状态里只放可 JSON 序列化的纯数据（dict / str / bool），不放 Pydantic 模型实例，
否则检查点序列化与跨进程恢复都会变脆。

安全约束：状态中禁止出现私钥、助记词、完整签名材料、未脱敏的原始 prompt。
"""

from __future__ import annotations

from operator import add
from typing import Annotated, Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver


class GraphState(TypedDict, total=False):
    session_id: str
    # 带 add reducer：每轮只追加新消息，历史由检查点维护
    messages: Annotated[list[dict[str, Any]], add]
    routing_decision: dict[str, Any] | None
    rag_context: list[dict[str, Any]] | None
    guard_passed: bool | None
    simulation: dict[str, Any] | None
    tx_preview: dict[str, Any] | None
    approval: dict[str, Any] | None
    clarification: str | None
    tx_hash: str | None
    bridge_status: str | None
    trace_id: str | None
    error: dict[str, Any] | None


def initial_state(*, session_id: str, message: str) -> GraphState:
    """单轮入口状态。同一 ``thread_id`` 的历史由检查点负责合并。"""
    return GraphState(
        session_id=session_id,
        messages=[{"role": "user", "content": message}],
    )


def make_checkpointer() -> InMemorySaver:
    """测试与本地开发用内存检查点；生产替换为 Upstash Redis 实现。"""
    return InMemorySaver()


def thread_config(session_id: str) -> dict[str, Any]:
    """``thread_id`` 必须与会话一一对应，恢复时用它定位检查点。"""
    return {"configurable": {"thread_id": session_id}}
