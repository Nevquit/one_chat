# 待办事项

> 用途：记录本项目的待办与后续计划，按优先级排序。  
> 维护方式：新增事项请分配唯一编号（`TODO-NNN`）、优先级与验收标准；完成后勾选并移入「已完成」。  
> 最后更新：2026-11-20

## 图例

| 标记 | 含义 |
|---|---|
| P0 | 阻塞发布或影响正确性，优先处理 |
| P1 | 本阶段应完成 |
| P2 | 可排期，不阻塞当前阶段 |
| `- [ ]` | 未开始 |
| `- [x]` | 已完成 |

---

## 进行中

（暂无）

---

## 待办

### TODO-001 补齐传统 API 测试

- **优先级**：P1
- **状态**：`- [ ]` 未开始
- **背景**：当前仅有一层 API 回归测试（`tests/e2e/test_api.py`，11 条，进程内 ASGI + Fake 适配器），覆盖健康检查、422、404、SSE 主路径与生命周期，缺少系统化的参数边界、错误码矩阵与契约校验。
- **定位**：这是**接口契约测试**，不是质量评测。要求快、稳定、零网络，与 `evaluation/` 下的真实链路评测分开维护。

#### 范围

- [ ] **参数边界矩阵**：`session_id` 长度 1 / 64 / 65，`message` 长度 4000 / 4001，空字符串，未知字段，非 JSON 请求体，错误 `Content-Type`
- [ ] **错误码矩阵**：每个 `ErrorCode` 至少一条可触发用例，断言 `error.code` 稳定、`message` 非空、不泄漏内部堆栈
- [ ] **幂等与重复操作**：重复 `resume`、重复 `chat`、同一会话连续恢复
- [ ] **SSE 协议边界**：断连、超时、非法帧、空流、事件顺序
- [ ] **契约快照**：响应结构与 OpenAPI / JSON Schema 一致，字段增删可被发现
- [ ] **并发与会话隔离**：同一 `session_id` 并发请求、不同 `session_id` 并发不串状态

#### 落地位置

```text
tests/api/
├── test_validation.py      # 参数边界
├── test_error_codes.py     # 错误码矩阵
├── test_idempotency.py     # 重复操作
├── test_sse_protocol.py    # SSE 边界
└── test_contract.py        # 契约快照
```

#### 验收标准

1. 新增用例全部使用 Fake 适配器，不访问网络，单文件运行时间 < 5 s；
2. 每个 `ErrorCode` 都有对应用例，无遗漏；
3. 参数边界覆盖上界、下界与越界；
4. `pytest` 全绿，且不依赖 `.env` 或外部服务；
5. 与 `evaluation/e2e_eval.py` 职责不重叠：后者不再补这类确定性断言。

#### 不做什么

- 不在此处验证回答质量、检索召回、语义忠实度；
- 不在此处调用真实 LLM / Chroma / 跨链接口；
- 不替代 `evaluation/` 下的端到端评测。

---

### TODO-009 打通 trace_id 与结构化日志

- **优先级**：P1（其中 P0 子项建议优先）
- **状态**：`- [ ]` 未开始
- **背景**：
  - 被测系统已有 `TracePort` 抽象与节点级 `span()` 埋点，但装配的是 `NoopTrace`，实际不采集；
  - 服务端日志仅 `app.py` 一句 `logger.exception("图执行失败 ...")`，无结构化字段；
  - 评测器 `e2e_eval.py` 只有 `print`，证据落在 JSON/HTML，但缺事件时间戳、HTTP 状态与 `trace_id` 关联。
- **目标**：失败用例可以从报告跳转到服务端链路，且能区分“检索慢 / 模型慢 / 上游慢”。

#### 现状

| 能力 | 被测系统 | 评测器 |
|---|---|---|
| span 埋点 | 有（10 个节点） | 无 |
| span 导出 | 无（NoopTrace） | 无 |
| 结构化日志 | 无 | 无 |
| `trace_id` 贯穿 | 有字段，未写入日志 | 未记录 |
| 事件时间戳 | — | 未记录 |
| token / 耗时统计 | 未记录 | 仅有整轮耗时 |

#### 范围

**P0 — 关联 ID（最小闭环）**

- [ ] 评测器每次请求带 `X-Request-ID`（建议 `case_id + 轮次`）
- [ ] 服务端读取该头，写入 `state.trace_id` 与日志上下文
- [ ] 报告中记录 `trace_id`，失败用例可直接检索服务端日志

**P1 — 结构化日志**

- [ ] 服务端输出 JSON 行日志：`ts / level / trace_id / session_id / node / duration_ms / outcome`
- [ ] 节点进出统一埋点（装饰器或 span 内记录），避免逐节点手写
- [ ] LLM 适配器记录 `model / tokens / latency`，失败记录错误码
- [ ] 日志脱敏：不输出 API Key、完整交易载荷、用户地址

**P2 — 真 trace 与评测增强**

- [ ] 用 OTel 实现替换 `NoopTrace`，`span()` 开真实 span，本地接 Jaeger/Tempo
- [ ] 评测器记录每个事件的到达时间，报告增加“首事件耗时”
- [ ] 评测器记录 HTTP 状态码、重试次数
- [ ] 报告用例表增加 `trace_id` 列

#### 落地位置

```text
src/wanchain_agent/adapters/trace_otel.py     # 新增：OTel 实现
src/wanchain_agent/logging.py                 # 新增：结构化日志配置
src/wanchain_agent/app.py                     # 读取 X-Request-ID，绑定上下文
evaluation/e2e_eval.py                        # 透传请求头、记录时间戳
evaluation/report.py                          # 报告增加 trace_id / 耗时列
```

#### 验收标准

1. 同一次 e2e 运行内，报告中的 `trace_id` 能在服务端日志中检索到完整节点链路；
2. 任一失败用例可指出耗时最长的节点；
3. 日志为单行 JSON，含 `trace_id` 与 `session_id`，不含密钥与完整载荷；
4. 未配置 OTel 时，`NoopTrace` 路径仍可正常启动，行为与现在一致；
5. 不改变 SSE 事件契约与现有断言。

#### 不做什么

- 不引入完整 APM 平台或商业监控；
- 不在此项里做指标聚合与告警规则；
- 不为日志增加业务判断逻辑。

---

## 已识别待排期

| 编号 | 事项 | 优先级 | 来源 |
|---|---|---|---|
| TODO-002 | 实现多轮槽位合并，修复路由只读当前轮消息的问题 | P0 | 评测计划已知缺口 |
| TODO-003 | 槽位合并落地后启用 `e2e-09` / `e2e-16`，各至少通过 1 条 | P1 | 评测计划 P1 退出条件 |
| TODO-004 | 校准 `MIN_RELEVANCE`（数据建议 0.5 → 0.6）并重跑端到端基线 | P1 | 首轮基线 e2e-03 失败 |
| TODO-005 | `e2e-20` 故障注入用例（非法帧 / 断连） | P2 | 当前标记 pending |
| TODO-006 | RAG 检索专项评测：Recall@5、MRR、Context Precision | P2 | 评测计划 L2 |
| TODO-007 | 生成专项评测：Faithfulness、Answer Relevancy、LLM Judge 校准 | P2 | 评测计划 L3 |
| TODO-008 | 统一归档文档并提交 | P2 | 工作区存在未提交改动 |

---

## 已完成

（暂无）
