"""配置层测试：环境变量读取、默认值、缺失密钥的失败方式。"""

from __future__ import annotations

import asyncio

import pytest

from wanchain_agent.adapters.bridge_wanchain import WanchainBridgeAdapter
from wanchain_agent.adapters.llm_openai import OpenAICompatibleLLM
from wanchain_agent.config import Adapters, Settings, build_adapters
from wanchain_agent.core.errors import ConfigError


def test_settings_defaults_when_env_is_empty():
    settings = Settings.from_env({})

    assert settings.llm_api_key == ""
    assert settings.llm_model == "deepseek-chat"
    assert settings.bridge_from_account is None
    assert settings.min_relevance == 0.5


def test_settings_reads_all_overrides():
    settings = Settings.from_env(
        {
            "LLM_API_KEY": "sk-test",
            "LLM_API_BASE": "https://llm.test/v1",
            "LLM_MODEL": "test-model",
            "BRIDGE_API_BASE": "https://bridge.test",
            "BRIDGE_FROM_ACCOUNT": "0x" + "2" * 40,
            "MIN_RELEVANCE": "0.7",
        }
    )

    assert settings.llm_api_key == "sk-test"
    assert settings.llm_api_base == "https://llm.test/v1"
    assert settings.llm_model == "test-model"
    assert settings.bridge_api_base == "https://bridge.test"
    assert settings.bridge_from_account == "0x" + "2" * 40
    assert settings.min_relevance == 0.7


def test_invalid_min_relevance_raises_config_error():
    with pytest.raises(ConfigError):
        Settings.from_env({"MIN_RELEVANCE": "1.5"})


def test_build_adapters_requires_api_key():
    with pytest.raises(ConfigError):
        build_adapters(Settings())


def test_build_adapters_wires_real_implementations():
    adapters = build_adapters(
        Settings(
            llm_api_key="sk-test",
            llm_api_base="https://llm.test/v1",
            bridge_api_base="https://bridge.test",
        )
    )

    assert isinstance(adapters, Adapters)
    assert isinstance(adapters.llm, OpenAICompatibleLLM)
    assert isinstance(adapters.bridge, WanchainBridgeAdapter)
    asyncio.run(adapters.aclose())
