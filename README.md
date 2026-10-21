# deepseek-recipe Conformance Kit

面向 [deepseek-recipe](https://github.com/deepseek-ai/deepseek-recipe) 的流式协议一致性测试工具。

目标不是重复实现协议，而是把 **chunk-split、流结束、usage 和协议输出语义** 变成可重复、可审计的测试矩阵。

对应官方问题：

- [Issue #28](https://github.com/deepseek-ai/deepseek-recipe/issues/28)：系统化 chunk-split 与 end-of-stream 覆盖
- [Issue #40](https://github.com/deepseek-ai/deepseek-recipe/issues/40)：历史工具名冲突复现
- [Issue #42](https://github.com/deepseek-ai/deepseek-recipe/issues/42)：prompt 接近上下文上限时的 output budget
- 关联 #14 / #16：JSON mode 空格语义与 U+FFFD 缓冲

> 本项目为独立社区测试工具，与 DeepSeek-AI 无隶属或背书关系。

## 当前实现

- 语言无关 JSON fixture；
- `Chat Completions`、`Responses`、`Messages` 三类协议入口；
- 所有二分字符边界；
- 逐字符分块；
- 固定种子的随机 k-way 分块；
- 输出事件规范化与 SHA-256 digest；
- 三种检查模式：
  - `chunk_transparent`：不同分块必须产生相同规范化输出；
  - `chunk_dependent_contract`：允许按契约依赖分块，但输出必须有效；
  - `end_of_stream`：流结束时不得丢失 U+FFFD 等缓冲内容；
- 官方 Python binding adapter；
- mock adapter 用于验证测试框架自身；
- JSON 报告输出。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\test.ps1
```

运行 mock 自检：

```powershell
.\.venv\Scripts\python.exe -m recipe_conformance --adapter joined-mock
```

安装官方 Python binding 后运行真实一致性检查：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,official]"
.\.venv\Scripts\python.exe -m recipe_conformance --adapter official
```

## Fixture 模式

```json
{
  "id": "chat-plain-unicode",
  "protocol": "chat_completions",
  "request": {},
  "model": "DeepSeek-V4.1-Flash",
  "model_text": "Hello, 世界!",
  "mode": "chunk_transparent",
  "issue_refs": ["deepseek-recipe#28"]
}
```

`model_text` 会按全部二分位置、逐字符和固定随机 k-way 方式重新分块，然后构造成官方 `InferenceChunk.text` 序列。

## 报告

默认输出：`reports/latest.json`

报告包含：

- adapter 名称；
- seed 和随机样本数；
- 每个 fixture 的分块计划；
- 每种分块的规范化事件 digest；
- 检查项和错误；
- 官方 Issue 引用和审计备注。

## 本机验证状态

- 核心框架和 mock adapter：测试通过；
- 本机 Windows 缺少 MSVC C++ 工具链，`deepseek-recipe` 官方 Python binding 无法在本地从 sdist 构建；
- CI 的 `official` job 在 Ubuntu 安装 Rust、Clang 和 OpenCV 后执行官方 adapter 测试。

本地缺少官方 binding 时，`tests/test_official_adapter.py` 会跳过，不会被误报为通过。

## 已知边界

- 当前先覆盖文本流；token-id 流需要官方 tokenizer 和更复杂的差分规则；
- `chunk_dependent_contract` 目前只检查输出非空和运行成功，不固定 #14 的最终空格契约；
- 工具调用和 DSML 需要后续加入真实 transcript corpus；
- 不宣称当前行为一定是正确行为，测试结果用于审计和上游讨论。

## 许可证

Apache-2.0。参见 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
