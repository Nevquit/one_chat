---
title: Wanchain Agent
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# Wanchain Agent

Wanchain 跨链与知识问答智能体，FastAPI + LangGraph + Chroma。

## 运行前提

在 Space 的 Settings → Variables and secrets 中配置：

- `LLM_API_KEY`（必填，OpenAI 兼容接口）
- `EMBEDDING_API_KEY`（必填，SiliconFlow）

可选变量：`LLM_API_BASE`、`LLM_MODEL`、`EMBEDDING_API_BASE`、`EMBEDDING_MODEL`、`MIN_RELEVANCE`。

## 免费实例限制

- 使用内存检查点，仅支持单实例；休眠或重启后会话丢失。
- 空闲 48 小时后休眠，下次请求需要冷启动。
- 向量索引已随镜像打包，不依赖外部数据库。
