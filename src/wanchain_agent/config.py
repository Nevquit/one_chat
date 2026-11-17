"""配置加载与适配器装配。

配置只从环境变量读取，不读取配置文件，也不在代码里写默认密钥。
``Settings`` 允许缺少 ``LLM_API_KEY``（便于测试与健康检查），
真正构造 LLM 适配器时由 ``build_adapters`` 统一校验并抛 ``ConfigError``。

知识层适配器依赖离线索引，暂由调用方注入；这里只装配 LLM、Bridge 与追踪。
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .adapters import bridge_wanchain, llm_openai
from .adapters.trace_noop import NoopTrace
from .app import create_app
from .core.errors import ConfigError
from .core.ports import BridgePort, KnowledgePort, LLMPort, TracePort
from .knowledge.guard import DEFAULT_MIN_RELEVANCE


class Settings(BaseModel):
    """运行期配置。字段名与架构文档第 12.1 节的环境变量一一对应。"""

    model_config = ConfigDict(extra="ignore")

    llm_api_key: str = ""
    llm_api_base: str = llm_openai.DEFAULT_BASE_URL
    llm_model: str = llm_openai.DEFAULT_MODEL
    bridge_api_base: str = bridge_wanchain.DEFAULT_BASE_URL
    bridge_from_account: str | None = None
    min_relevance: float = Field(default=DEFAULT_MIN_RELEVANCE, ge=0.0, le=1.0)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        raw: dict[str, Any] = {
            "llm_api_key": source.get("LLM_API_KEY", ""),
            "llm_api_base": source.get("LLM_API_BASE", llm_openai.DEFAULT_BASE_URL),
            "llm_model": source.get("LLM_MODEL", llm_openai.DEFAULT_MODEL),
            "bridge_api_base": source.get(
                "BRIDGE_API_BASE", bridge_wanchain.DEFAULT_BASE_URL
            ),
            "bridge_from_account": source.get("BRIDGE_FROM_ACCOUNT") or None,
            "min_relevance": source.get("MIN_RELEVANCE", DEFAULT_MIN_RELEVANCE),
        }
        try:
            return cls.model_validate(raw)
        except ValidationError as exc:
            raise ConfigError(
                "环境变量配置不合法", details={"errors": exc.error_count()}
            ) from exc


@dataclass(frozen=True)
class Adapters:
    """已装配的端口实现。释放由调用方负责（FastAPI lifespan 已处理）。"""

    llm: LLMPort
    bridge: BridgePort
    trace: TracePort

    async def aclose(self) -> None:
        for adapter in (self.llm, self.bridge):
            closer = getattr(adapter, "aclose", None)
            if closer is not None:
                await closer()


def build_adapters(settings: Settings | None = None) -> Adapters:
    """按配置构造真实适配器。密钥缺失直接失败，不做静默降级。"""
    resolved = settings or Settings.from_env()
    if not resolved.llm_api_key:
        raise ConfigError("缺少 LLM_API_KEY，无法初始化 LLM 适配器")

    return Adapters(
        llm=llm_openai.OpenAICompatibleLLM(
            api_key=resolved.llm_api_key,
            base_url=resolved.llm_api_base,
            model=resolved.llm_model,
        ),
        bridge=bridge_wanchain.WanchainBridgeAdapter(
            base_url=resolved.bridge_api_base,
            from_account=resolved.bridge_from_account,
        ),
        trace=NoopTrace(),
    )


def build_app(
    settings: Settings | None = None,
    *,
    knowledge: KnowledgePort,
) -> FastAPI:
    """生产装配入口：配置 + 知识适配器 → FastAPI 应用。"""
    resolved = settings or Settings.from_env()
    adapters = build_adapters(resolved)
    return create_app(
        llm=adapters.llm,
        knowledge=knowledge,
        bridge=adapters.bridge,
        trace=adapters.trace,
        min_relevance=resolved.min_relevance,
        resources=(adapters,),
    )
