"""OpenAI 兼容 LLM 适配器（DeepSeek / OpenAI / 本地 vLLM 均可）。

只依赖 httpx，避免把厂商 SDK 引入业务层。

- ``complete``：普通对话补全。
- ``complete_structured``：强制 JSON 输出并用 Pydantic 校验；
  模型输出不符合 Schema 时抛 ``UpstreamError``，由编排层决定是否重试。

密钥只从构造参数读取，不写入日志与异常信息。
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from wanchain_agent.core.errors import ConfigError, UpstreamError

M = TypeVar("M", bound=BaseModel)

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"

SCHEMA_INSTRUCTION = (
    "只输出一个 JSON 对象，不要 Markdown 代码块，不要任何解释。"
    "对象必须符合以下 JSON Schema：\n{schema}"
)


class _Message(BaseModel):
    model_config = ConfigDict(extra="ignore")

    content: str | None = None


class _Choice(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message: _Message


class _ChatResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    choices: list[_Choice] = []


class OpenAICompatibleLLM:
    """实现 ``LLMPort``。异常一律转换为领域异常，不向业务层泄漏 SDK 类型。"""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise ConfigError("缺少 LLM API Key")
        self._model = model
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
    ) -> str:
        payload = await self._chat(messages, temperature=temperature)
        content = _first_content(payload)
        if not content:
            raise UpstreamError("LLM 返回了空内容")
        return content

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        schema: type[M],
        *,
        temperature: float = 0.0,
    ) -> M:
        structured_messages = [
            *messages,
            {
                "role": "system",
                "content": SCHEMA_INSTRUCTION.format(
                    schema=json.dumps(schema.model_json_schema(), ensure_ascii=False)
                ),
            },
        ]
        payload = await self._chat(
            structured_messages, temperature=temperature, json_mode=True
        )
        raw = _strip_code_fence(_first_content(payload))
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise UpstreamError(
                "LLM 未返回合法 JSON",
                details={"schema": schema.__name__},
            ) from exc

        try:
            return schema.model_validate(data)
        except ValidationError as exc:
            raise UpstreamError(
                "LLM 输出不符合 Schema",
                details={
                    "schema": schema.__name__,
                    "errors": exc.error_count(),
                },
            ) from exc

    async def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        json_mode: bool = False,
    ) -> _ChatResponse:
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.post("/chat/completions", json=body)
        except httpx.HTTPError as exc:
            raise UpstreamError(
                "LLM 请求失败", details={"reason": type(exc).__name__}
            ) from exc

        if response.status_code >= 400:
            raise UpstreamError(
                "LLM 返回错误状态", details={"status": response.status_code}
            )

        try:
            return _ChatResponse.model_validate(response.json())
        except ValueError as exc:
            raise UpstreamError("LLM 返回了非预期响应结构") from exc


def _first_content(payload: _ChatResponse) -> str:
    if not payload.choices:
        return ""
    return (payload.choices[0].message.content or "").strip()


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:])
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()
