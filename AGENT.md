# AGENT.md

给 AI 编码助手与协作者的项目约定。新增规则追加到对应章节，不删除已有约束。

## 1. 运行环境

- Python 版本：**3.12**。本机 `python` 命令指向 Python 2.7，禁止使用。
- 虚拟环境：项目根目录 `.venv/`（已创建并安装依赖）。
- 解释器路径：`.venv\Scripts\python.exe`
- 安装/更新依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## 2. 每次改动代码后的固定流程

代码改动完成即执行，顺序不可跳过：

1. **跑测试**：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

2. **测试全绿才允许提交**。有失败先修复；不允许带着失败或跳过用例提交。
3. **提交**：

```powershell
git add <本次改动的文件>
git commit -m "<中文提交信息>"
```

4. 提交信息格式：`<type>(<scope>): <简述>`，正文说明「改了什么、为什么」。
5. 禁止 `--no-verify`，禁止空提交，禁止把 `.venv/`、`__pycache__/`、缓存目录纳入版本库。

## 3. 架构约束（改动前必读）

- `core/` 只依赖 Python 标准库与 Pydantic，禁止导入任何第三方 SDK。
- 业务模块（`routing/`、`knowledge/`、`bridge/`、`orchestration/`）只依赖 `core/ports.py` 定义的 Protocol。
- 所有第三方 SDK 与网络 I/O 只允许出现在 `adapters/`。
- `src/` 不得导入 `evaluation/`、`deepeval`、`ragas`。
- 金额一律使用 `Decimal`，禁止 `float`；序列化为十进制字符串，不使用科学计数法。
- 地址在核心层只做结构校验（`0x` + 40 位十六进制），EIP-55 校验和由适配器层负责。
- 服务端永不接触私钥、助记词或签名材料。

## 4. 参考文档

- 架构设计：[docs/architecture.md](docs/architecture.md)
- 领域契约：[src/wanchain_agent/core/models.py](src/wanchain_agent/core/models.py)
- 端口定义：[src/wanchain_agent/core/ports.py](src/wanchain_agent/core/ports.py)
- 测试替身：[tests/unit/fakes.py](tests/unit/fakes.py)
