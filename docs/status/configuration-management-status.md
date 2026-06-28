# 配置管理规则落地状态

## 已完成范围

- 新增根目录 `.gitignore`，明确禁止提交真实 `.env` 配置文件。
- 新增后端本地开发配置模板：`backend/.env.example`。
- 新增后端生产部署配置模板：`backend/.env.prod.example`。
- 新增前端本地开发配置模板：`frontend/.env.example`。
- 新增前端生产部署配置模板：`frontend/.env.prod.example`。
- 新增根目录 `docker-compose.yml`，用于本地启动 MySQL、Redis 和 Qdrant 依赖服务。
- 所有配置模板均按类别分组，并为每个配置项补充中文注释说明。
- 项目级规则 `AGENTS.md` 已补充配置管理长期规则。
- 架构设计文档已补充配置管理设计章节。
- 后端大模型配置已简化为单组通用 `LLM_*` 配置，避免在配置层暴露多套 provider 专用 API Key。
- 后端 `pyproject.toml` 已显式配置 setuptools 只发现 `app*` Python 包，避免 `backend/knowledge/` 这类资料沉淀目录被误识别为顶层包并导致 editable install 失败。

## 重要约束

- 后端真实配置必须从 `backend/.env` 读取。
- 前端真实配置必须从 `frontend/.env` 读取。
- 真实 `.env` 文件包含密钥、数据库密码、API Token、本地服务地址等信息，禁止提交到 Git。
- 示例配置文件只提供配置项说明和占位值，可以提交到 Git。
- 前端配置只能使用 `VITE_` 前缀变量，不能放任何私密密钥。
- `backend/knowledge/` 是 RAG 资料沉淀目录，不是 Python package；后端打包只应包含 `app*`。
- 新增配置项时，必须同步更新本地和生产示例配置文件，并添加中文注释。
- 大模型接入统一使用 `LLM_MODEL`、`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_TEMPERATURE`、`LLM_MAX_TOKENS`、`LLM_TIMEOUT_SECONDS` 和 `LLM_MAX_RETRIES`。
- 不再维护 provider 专用 API Key 配置项。
- AI 安全拦截统一使用 `GUARDRAILS_ENABLED`、`GUARDRAILS_AUDIT_ENABLED` 和 `GUARDRAILS_DEFAULT_BLOCK_MESSAGE`。
- 本地开发默认通过 `docker compose up -d mysql redis qdrant` 启动 MySQL、Redis 和 Qdrant，`backend/.env.example` 中的 `DATABASE_URL`、`REDIS_URL`、`CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND` 和 `QDRANT_URL` 已对齐容器映射端口。
- Qdrant 使用官方 `qdrant/qdrant:latest` 镜像，暴露 REST `6333` 和 gRPC `6334`，并通过 Docker 命名卷 `ai_agent_qdrant_data` 持久化 `/qdrant/storage`。

## 验证方式

- 已执行 `git diff --check` 检查 Markdown 和配置模板空白格式。
- 已执行 `docker compose config` 校验本地 MySQL/Redis/Qdrant compose 配置。
- 已执行 `backend/.venv/bin/python -m pip install -e ".[dev]"` 验证 editable install 不再受 `backend/knowledge/` 目录影响。
- 已通过 `git status --short` 核对新增文件范围。
- 已新增 `Settings` 测试，覆盖通用大模型配置读取。
- 已新增 `Settings` 测试，覆盖通用 Guardrails 配置读取。

## 后续建议

- 实现后端 `Settings` 配置类时，按当前模板分类映射配置项。
- 实现前端配置读取时，集中封装 `src/shared/config/`，避免业务页面直接散落读取 `import.meta.env`。
- 后续接入部署时，用平台密钥管理或 CI/CD Secret 注入生产 `.env`。
