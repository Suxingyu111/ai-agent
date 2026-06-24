# 项目初始化状态

## 已完成范围

- 初始化后端 FastAPI 项目骨架。
- 初始化前端 Vue 3 + Vite + TypeScript 项目骨架。
- 后端实现 `GET /api/v1/health` 健康检查接口。
- 后端配置集中从 `backend/.env` 读取，并保留可提交的 `.env.example` 与 `.env.prod.example`。
- 前端配置集中通过 `src/shared/config/appConfig.ts` 读取 `VITE_` 环境变量。
- 初始化 `agent_kernel` 目录，包含契约、运行时、注册、策略、事件和测试辅助模块。
- 初始化独立智能体插件目录：
  - `supervisor_agent`
  - `planner_agent`
  - `research_agent`
  - `knowledge_agent`
  - `writer_agent`
  - `reviewer_agent`
  - `file_agent`
  - `browser_agent`
  - `code_agent`
  - `map_agent`
  - `pdf_agent`
- 初始化基础 workflow 目录：
  - `supervisor`
  - `planner_executor`
  - `pipeline`
  - `handoff`
- 新增健康检查接口文档。

## 当前边界

- 当前只完成项目骨架和最小健康检查，不包含真实数据库连接、模型调用、MCP 调用、RAG 检索或工具执行。
- 每个智能体当前是独立占位实现，后续功能必须只在对应智能体目录内演进。
- 所有工具调用必须继续通过未来的 `ToolGateway` 实现，不允许智能体直接访问外部工具。

## 已执行验证

- `backend/.venv/bin/python -m pytest backend/tests -q`
  - 结果：通过，`3 passed`。
  - 说明：FastAPI/Starlette 当前对 `httpx` 测试客户端有上游弃用提示，不影响当前健康检查测试。
- `backend/.venv/bin/python -m ruff check backend/app backend/tests`
  - 结果：通过。
- `npm test`
  - 目录：`frontend/`
  - 结果：通过，`1 passed`。
- `npm run build`
  - 目录：`frontend/`
  - 结果：通过，Vite 成功生成生产构建产物。
- `git diff --check`
  - 结果：通过。

## 启动错误修复记录

- 问题：后端启动时读取 `backend/.env`，`CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173` 被 `pydantic-settings` 当作复杂列表字段解析，触发 JSON 解析失败。
- 根因：`cors_allowed_origins` 字段原本声明为 `list[str]`，`.env` 中的逗号分隔字符串在进入 validator 前就被 `pydantic-settings` 按 JSON 解码。
- 修复：将原始配置改为字符串字段 `cors_allowed_origins_raw`，再通过 `cors_allowed_origins` 属性统一转换为列表。
- 回归：新增 `.env` 逗号分隔 CORS 配置读取测试，确保后续不会再次破坏启动。

## 依赖安装说明

- 后端已创建本地虚拟环境 `backend/.venv`，该目录不提交到 Git。
- 前端已执行 `npm install --cache .npm-cache`，避免使用存在权限问题的用户全局 npm cache。
- `npm install` 当前报告 1 个低危依赖审计提示，后续可在锁定功能范围后单独执行依赖审计和升级评估。

## 下一步建议

- 实现数据库 session、Alembic 迁移和基础模型。
- 实现 Agent Registry 读取 manifest 的真实加载逻辑。
- 实现 ToolGateway 的权限校验和审计记录。
- 为每个智能体补充 contract test、permission test、memory isolation test 和 golden task test。
