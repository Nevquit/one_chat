"""图状态与检查点。

状态里只放可 JSON 序列化的纯数据（dict / str / bool），不放 Pydantic 模型实例，
否则检查点序列化与跨进程恢复都会变脆。

安全约束：状态中禁止出现私钥、助记词、完整签名材料、未脱敏的原始 prompt。
"""

from __future__ import annotations

from operator import add
from typing import Annotated, Any, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

DEFAULT_CHECKPOINT_TTL_MINUTES = 1440


class GraphState(TypedDict, total=False):
    session_id: str
    # 带 add reducer：每轮只追加新消息，历史由检查点维护
    messages: Annotated[list[dict[str, Any]], add]
    routing_decision: dict[str, Any] | None
    # 跨轮槽位记忆：跨链轮次写入，非跨链轮次清空，供下一轮续槽合并
    slots: dict[str, Any] | None
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


def make_checkpointer(
    *,
    redis_url: str | None = None,
    ttl_minutes: int = DEFAULT_CHECKPOINT_TTL_MINUTES,
) -> BaseCheckpointSaver:
    """构造检查点。

    未提供 ``redis_url`` 时退回进程内实现，只适合单进程测试与本地演示。
    Redis 实现延迟连接，可在事件循环外构造；首次使用前由应用 lifespan
    调用 ``asetup()`` 建索引，否则首轮请求会因为索引缺失而失败。
    """
    if not redis_url:
        return InMemorySaver()

    # 延迟导入：只有启用 Redis 时才要求安装该可选依赖
    from langgraph.checkpoint.redis.aio import AsyncRedisSaver

    return AsyncRedisSaver(
        redis_url=redis_url,
        ttl={"default_ttl": ttl_minutes, "refresh_on_read": True},
    )


def thread_config(session_id: str) -> dict[str, Any]:
    """``thread_id`` 必须与会话一一对应，恢复时用它定位检查点。"""
    return {"configurable": {"thread_id": session_id}}
