# AI API 综合测试项目（P024）

被测对象：DeepSeek Chat Completions API（`POST /chat/completions`）

## 项目简介

- 定位：个人实战项目（AI 应用测试 / 接口自动化），2026-09 完成。
- 测试范围：接口契约与参数异常、AI 输出质量（指令遵循 / 幻觉 / 边界）、AI 安全（提示词注入 / 敏感信息 / 越权 / 拒答）、多轮对话（记忆 / 指代 / 指令冲突 / 长上下文）。
- 用例规模：42 条（参数化驱动）。
- 执行结果：`41 passed + 1 xfailed`，耗时约 110 秒（`pytest-html` 报告见 `reports/pytest_report.html`）。
- 工程化要点：测试数据与代码分离、公共请求封装、`@pytest.mark.parametrize`、4 个 marker 分组、断言逻辑抽取、`xfail(strict=True)` 管理已知缺陷、API Key 改为环境变量读取。

## 执行结果与缺陷

| 项目 | 结论 |
| --- | --- |
| 用例执行 | 42 条：41 passed、1 xfailed（已知缺陷，用于跟踪服务端行为） |
| 安全复核 | 7 种提示词注入 / 诱导手法（含 Base64 变形注入）全部被拒绝 |
| AI-BUG-001 | 空 `content` 未被拒绝，接口返回 200（Minor，当前以 `xfail(strict=True)` 跟踪） |
| AI-RISK-001 | V1/V2 源码硬编码 API Key（Major，V3 已改为环境变量读取） |

## 关键结论（可面试展开）

同一类提示词注入，在裸模型 API 上被稳定拒绝，却在 RAG 应用（见 RAG 应用测试项目）里成功绕过知识库约束。
说明风险来源是**应用层的提示词编排**，而不是基础模型的安全边界，修复重点应放在应用侧。

## 项目结构

```
AI_API综合测试/
├─ conftest.py            公共 fixture 与用例数据加载
├─ pytest.ini             pytest 配置（marker、默认参数）
├─ utils/api_client.py    接口请求封装（统一 base_url / 鉴权 / 超时）
├─ data/                  测试数据（与代码分离）
│  ├─ cases_api_basic.json    正常请求与 Response 结构
│  ├─ cases_api_errors.json   认证与参数异常
│  ├─ cases_quality.json      AI 输出质量（指令遵循/幻觉/边界）
│  ├─ cases_safety.json       AI 安全（注入/泄露/越权/拒答）
│  └─ cases_multi_turn.json   多轮对话（记忆/切换/冲突/长上下文）
└─ tests/
   ├─ test_01_api_basic.py
   ├─ test_02_api_errors.py
   ├─ test_03_output_quality.py
   ├─ test_04_safety.py
   └─ test_05_multi_turn.py
```

## 运行方式

API Key 通过环境变量传入，不再写死在代码里：

```powershell
$env:DEEPSEEK_API_KEY = "<你的 key>"
python -m pytest                       # 全量
python -m pytest -m safety             # 只跑安全用例
python -m pytest --html=reports/report.html --self-contained-html   # 生成 HTML 报告
```

可选环境变量：`AI_API_BASE_URL`（默认 `https://api.deepseek.com`）、`AI_API_MODEL`（默认 `deepseek-flash`）。

## 用例编号

- `API-0xx`：接口契约与参数异常
- `QUAL-0xx`：AI 输出质量
- `SAFE-0xx`：AI 安全
- `MT-0xx`：多轮对话

新增用例只改 `data/*.json`，不需要改测试代码。

## 环境依赖

```
python -m pip install -r requirements.txt
```

- Python 3.12+（开发环境为 3.14）
- `requests` / `pytest` / `pytest-html`
- 需要在本地设置环境变量 `DEEPSEEK_API_KEY`（不要写入代码或提交到仓库）

## 报告与文档

- `reports/pytest_report.html`：pytest-html 自包含报告（41 passed / 1 xfailed）
- `reports/AI_API综合测试项目_测试报告_V3.docx` / `.pdf`：正式测试报告（5 页）
- `reports/AI_API综合测试项目_测试用例_V3.docx` / `.pdf`：测试用例文档（4 页）
- `reports/png/`：上述文档逐页渲染图，用于版面复核
