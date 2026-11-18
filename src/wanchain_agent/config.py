"""配置加载与适配器装配。

配置只从环境变量读取，不读取配置文件，也不在代码里写默认密钥。
``Settings`` 允许缺少 ``LLM_API_KEY``（便于测试与健康检查），
真正构造 LLM 适配器时由 ``build_adapters`` 统一校验并抛 ``ConfigError``。

知识层适配器依赖离线索引；``build_knowledge`` 可按配置装配 Chroma 检索，
也可以继续由调用方注入（测试与自定义向量库）。
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from fastapi import FastAPI
from langgraph.checkpoint.base import BaseCheckpointSaver
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .adapters import bridge_wanchain, embedding_siliconflow, llm_openai
from .adapters.knowledge_chroma import DEFAULT_INDEX_MANIFEST, ChromaKnowledge
from .adapters.trace_noop import NoopTrace
from .app import create_app
from .core.errors import ConfigError
from .core.ports import BridgePort, EmbeddingPort, KnowledgePort, LLMPort, TracePort
from .knowledge.guard import DEFAULT_MIN_RELEVANCE
from .orchestration.state import make_checkpointer


class Settings(BaseModel):
    """运行期配置。字段名与架构文档第 12.1 节的环境变量一一对应。"""

    model_config = ConfigDict(extra="ignore")

    llm_api_key: str = ""
    llm_api_base: str = llm_openai.DEFAULT_BASE_URL
    llm_model: str = llm_openai.DEFAULT_MODEL
    embedding_api_key: str = ""
    embedding_api_base: str = embedding_siliconflow.DEFAULT_BASE_URL
    embedding_model: str = embedding_siliconflow.DEFAULT_MODEL
    embedding_dimension: int = Field(
        default=embedding_siliconflow.DEFAULT_DIMENSION, ge=1
    )
    chroma_path: str = "data/chroma"
    chroma_collection: str = "wanchain_docs"
    index_manifest_path: str = DEFAULT_INDEX_MANIFEST
    bridge_api_base: str = bridge_wanchain.DEFAULT_BASE_URL
    bridge_from_account: str | None = None
    min_relevance: float = Field(default=DEFAULT_MIN_RELEVANCE, ge=0.0, le=1.0)
    checkpointer: Literal["memory", "redis"] = "memory"
    checkpoint_url: str = ""
    checkpoint_ttl_minutes: int = Field(default=1440, ge=1)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        raw: dict[str, Any] = {
            "llm_api_key": source.get("LLM_API_KEY", ""),
            "llm_api_base": source.get("LLM_API_BASE", llm_openai.DEFAULT_BASE_URL),
            "llm_model": source.get("LLM_MODEL", llm_openai.DEFAULT_MODEL),
            # 兼容 SiliconFlow 官方文档里的变量名。
            "embedding_api_key": source.get("EMBEDDING_API_KEY")
            or source.get("SILICONFLOW_API_KEY", ""),
            "embedding_api_base": source.get(
                "EMBEDDING_API_BASE", embedding_siliconflow.DEFAULT_BASE_URL
            ),
            "embedding_model": source.get(
                "EMBEDDING_MODEL", embedding_siliconflow.DEFAULT_MODEL
            ),
            "embedding_dimension": source.get(
                "EMBEDDING_DIMENSION", embedding_siliconflow.DEFAULT_DIMENSION
            ),
            "chroma_path": source.get("CHROMA_PATH", "data/chroma"),
            "chroma_collection": source.get("CHROMA_COLLECTION", "wanchain_docs"),
            "index_manifest_path": source.get(
                "INDEX_MANIFEST_PATH", DEFAULT_INDEX_MANIFEST
            ),
            "bridge_api_base": source.get(
                "BRIDGE_API_BASE", bridge_wanchain.DEFAULT_BASE_URL
            ),
            "bridge_from_account": source.get("BRIDGE_FROM_ACCOUNT") or None,
            "min_relevance": source.get("MIN_RELEVANCE", DEFAULT_MIN_RELEVANCE),
            "checkpointer": (source.get("CHECKPOINTER") or "memory").strip().lower(),
            # 本地 Redis 与 Upstash 都可用；显式 CHECKPOINT_URL 优先级最高。
            "checkpoint_url": (
                source.get("CHECKPOINT_URL")
                or source.get("REDIS_URL")
                or source.get("UPSTASH_REDIS_URL")
                or ""
            ).strip(),
            "checkpoint_ttl_minutes": source.get("CHECKPOINT_TTL_MINUTES", 1440),
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


def build_embedding(settings: Settings | None = None) -> EmbeddingPort:
    """按配置构造 Embedding 适配器。密钥缺失直接失败，不做静默降级。"""
    resolved = settings or Settings.from_env()
    if not resolved.embedding_api_key:
        raise ConfigError(
            "缺少 EMBEDDING_API_KEY（或 SILICONFLOW_API_KEY），无法初始化 Embedding 适配器"
        )

    return embedding_siliconflow.SiliconFlowEmbedding(
        api_key=resolved.embedding_api_key,
        base_url=resolved.embedding_api_base,
        model=resolved.embedding_model,
        dimension=resolved.embedding_dimension,
    )


def build_knowledge(settings: Settings | None = None) -> KnowledgePort:
    """按配置装配 Chroma 检索适配器，并校验索引与 Embedding 配置一致。"""
    resolved = settings or Settings.from_env()
    return ChromaKnowledge(
        embedding=build_embedding(resolved),
        persist_path=resolved.chroma_path,
        collection_name=resolved.chroma_collection,
        manifest_path=resolved.index_manifest_path,
    )


def build_checkpointer(settings: Settings | None = None) -> BaseCheckpointSaver:
    """按配置构造会话检查点。

    选择 redis 但缺少连接地址时直接失败，不回退到内存实现：静默降级会让
    多副本部署看起来正常，实际在实例切换时丢失会话。
    """
    resolved = settings or Settings.from_env()
    if resolved.checkpointer == "redis":
        if not resolved.checkpoint_url:
            raise ConfigError(
                "CHECKPOINTER=redis 需要配置 CHECKPOINT_URL、REDIS_URL 或 UPSTASH_REDIS_URL"
            )
        return make_checkpointer(
            redis_url=resolved.checkpoint_url,
            ttl_minutes=resolved.checkpoint_ttl_minutes,
        )
    return make_checkpointer()


def build_app(
    settings: Settings | None = None,
    *,
    knowledge: KnowledgePort | None = None,
) -> FastAPI:
    """生产装配入口：配置 + 知识适配器 + 会话检查点 → FastAPI 应用。

    ``knowledge`` 省略时按配置构造 Chroma 检索；测试或自定义向量库可直接注入。
    注入的适配器由 ``create_app`` 在应用关闭时统一释放。
    """
    resolved = settings or Settings.from_env()
    adapters = build_adapters(resolved)
    knowledge = knowledge or build_knowledge(resolved)
    checkpointer = build_checkpointer(resolved)
    return create_app(
        llm=adapters.llm,
        knowledge=knowledge,
        bridge=adapters.bridge,
        trace=adapters.trace,
        min_relevance=resolved.min_relevance,
        checkpointer=checkpointer,
        resources=(adapters,),
    )
