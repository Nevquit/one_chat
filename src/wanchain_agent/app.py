"""FastAPI 网关：HTTP / SSE 与图执行之间的转换层。

职责边界：
- 只做入参校验、SSE 编码、中断恢复的会话校验；
- 不包含任何业务规则，图返回什么就推送什么；
- 服务端不接触私钥与签名材料，``/chat/resume`` 只接收已广播后的交易哈希。

事件约定（见 ``core.models.SSEEvent``）：

| 事件 | 触发时机 | ``data`` |
|---|---|---|
| ``token`` | 本轮生成完毕 | ``{"text": 回答文本}`` |
| ``tx_preview`` | 进入人工确认 | ``{"preview": TxPreview}`` |
| ``interrupt`` | 同一时刻的暂停信号 | ``{"session_id": ..., "type": "tx_preview"}`` |
| ``error`` | 领域异常被捕获 | ``{"code": ..., "message": ..., "details": ...}`` |

当前 LLM 端口没有流式接口，``token`` 事件一次性推完整段文本；
接入流式生成后只需改这里的事件拆分，图与端口不变。

**生产环境必须使用共享检查点**（如 Redis）：``InMemorySaver`` 是进程内实现，
多副本部署时 ``/chat/resume`` 可能落到没有该会话的实例上。否则只能单进程运行。
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from langgraph.types import Command
from pydantic import BaseModel, ConfigDict, Field

from .adapters.trace_noop import NoopTrace
from .core.errors import AgentError, ErrorCode, SessionNotFoundError
from .core.models import ChatRequest, SSEEvent
from .core.ports import BridgePort, KnowledgePort, LLMPort, TracePort
from .knowledge.guard import DEFAULT_MIN_RELEVANCE
from .orchestration import build_graph, initial_state, thread_config

logger = logging.getLogger(__name__)

SSE_MEDIA_TYPE = "text/event-stream"
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

# 领域错误码 → HTTP 状态码；未列出的按客户端错误处理
_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.INTERNAL: 500,
    ErrorCode.CONFIG: 500,
    ErrorCode.UPSTREAM: 502,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.SESSION_NOT_FOUND: 404,
}


class ResumeRequest(BaseModel):
    """中断恢复入参。``approved=False`` 时忽略 ``tx_hash``。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_id: str = Field(min_length=1, max_length=64)
    approved: bool
    tx_hash: str | None = None


def _encode(event: SSEEvent) -> str:
    data = json.dumps(event.data, ensure_ascii=False)
    return f"event: {event.event}\ndata: {data}\n\n"


def _state_events(state: dict[str, Any], *, session_id: str) -> list[SSEEvent]:
    """把图的一次执行结果映射成事件序列。"""
    if state.get("error"):
        details = state["error"].get("error", state["error"])
        return [SSEEvent(event="error", data=details)]

    preview = state.get("tx_preview")
    if "__interrupt__" in state and preview:
        return [
            SSEEvent(event="tx_preview", data={"preview": preview}),
            SSEEvent(
                event="interrupt",
                data={"session_id": session_id, "type": "tx_preview"},
            ),
        ]

    messages = state.get("messages") or []
    last = messages[-1] if messages else None
    if last and last.get("role") == "assistant":
        return [SSEEvent(event="token", data={"text": str(last.get("content", ""))})]
    return []


async def _stream(
    graph: Any,
    *,
    session_id: str,
    run_input: Any,
) -> AsyncIterator[str]:
    """执行一次图并推送事件。

    执行前协议层的 ``AgentError`` 已在端点内同步抛出（如会话不存在），
    这里只需要兜住图内部的异常，保证连接不会因为未捕获异常而裸断。
    """
    try:
        state = await graph.ainvoke(run_input, thread_config(session_id))
    except AgentError as exc:
        yield _encode(SSEEvent(event="error", data=exc.to_dict()["error"]))
        return
    except Exception:
        # 网关必须把未知异常转成可读事件，避免 SSE 连接裸断
        logger.exception("图执行失败 session_id=%s", session_id)
        yield _encode(
            SSEEvent(
                event="error",
                data={"code": ErrorCode.INTERNAL.value, "message": "内部错误", "details": {}},
            )
        )
        return

    for event in _state_events(state, session_id=session_id):
        yield _encode(event)


def create_app(
    *,
    llm: LLMPort,
    knowledge: KnowledgePort,
    bridge: BridgePort,
    trace: TracePort | None = None,
    min_relevance: float = DEFAULT_MIN_RELEVANCE,
    checkpointer: Any | None = None,
    resources: Sequence[Any] = (),
) -> FastAPI:
    """装配网关。端口全部注入，测试可直接传入 Fake。

    ``resources`` 是需要在应用关闭时释放的对象（适配器连接池等），
    只要求实现可选的 ``aclose()``。
    """
    graph = build_graph(
        llm=llm,
        knowledge=knowledge,
        bridge=bridge,
        trace=trace or NoopTrace(),
        checkpointer=checkpointer,
        min_relevance=min_relevance,
    )
    closables = [*resources, llm, knowledge, bridge, trace]

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        for resource in closables:
            closer = getattr(resource, "aclose", None)
            if closer is not None:
                await closer()

    app = FastAPI(title="Wanchain Agent", version="0.1.0", lifespan=lifespan)

    @app.exception_handler(AgentError)
    async def _handle_agent_error(_: Request, exc: AgentError) -> JSONResponse:
        return JSONResponse(
            status_code=_HTTP_STATUS.get(exc.code, 400),
            content=exc.to_dict(),
        )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "knowledge": await knowledge.health()}

    @app.post("/chat")
    async def chat(payload: ChatRequest) -> StreamingResponse:
        return StreamingResponse(
            _stream(
                graph,
                session_id=payload.session_id,
                run_input=initial_state(
                    session_id=payload.session_id, message=payload.message
                ),
            ),
            media_type=SSE_MEDIA_TYPE,
            headers=SSE_HEADERS,
        )

    @app.post("/chat/resume")
    async def resume(payload: ResumeRequest) -> StreamingResponse:
        config = thread_config(payload.session_id)
        snapshot = await graph.aget_state(config)
        if not snapshot.values:
            raise SessionNotFoundError("会话不存在或已过期")
        if not snapshot.next:
            raise SessionNotFoundError("该会话没有等待确认的交易预览")

        return StreamingResponse(
            _stream(
                graph,
                session_id=payload.session_id,
                run_input=Command(
                    resume={"approved": payload.approved, "tx_hash": payload.tx_hash}
                ),
            ),
            media_type=SSE_MEDIA_TYPE,
            headers=SSE_HEADERS,
        )

    return app
