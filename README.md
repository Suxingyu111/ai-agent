# AI 多智能体平台

这是一个面向多智能体协作的 AI 超级智能体平台。项目当前处于初始化阶段，已建立后端 FastAPI、前端 Vue 3/Vite、Agent Kernel、独立智能体插件目录和配置模板。

## 目录

```text
backend/   后端 FastAPI 服务、Agent Kernel、智能体插件和业务模块
frontend/  前端 Vue 3 + Vite 工作台
docs/      架构设计、接口文档和状态文档
```

## 配置

真实配置文件不提交到 Git。

后端本地开发：

```bash
cp backend/.env.example backend/.env
```

前端本地开发：

```bash
cp frontend/.env.example frontend/.env
```

生产部署时分别参考：

```text
backend/.env.prod.example
frontend/.env.prod.example
```

## 本地依赖服务

MySQL、Redis 和 Qdrant 使用 Docker 启动：

```bash
docker compose up -d mysql redis qdrant
docker compose ps
```

默认暴露端口：

```text
MySQL: 127.0.0.1:3307
Redis: 127.0.0.1:6379
Qdrant REST: 127.0.0.1:6333
Qdrant gRPC: 127.0.0.1:6334
```

Qdrant 数据通过 Docker 命名卷 `ai_agent_qdrant_data` 持久化到容器内 `/qdrant/storage`，容器重建后已入库的向量数据仍会保留。

本地 `backend/.env.example` 已和 `docker-compose.yml` 的账号、密码、数据库名、Redis 地址和 Qdrant 地址保持一致。

## 后端开发

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python -m uvicorn app.main:app --reload
```

通用大模型配置位于 `backend/.env` 的 `LLM_*` 配置项。所有智能体可通过 `ChatModelClient.generate_structured(...)` 使用 Pydantic schema 获取结构化输出；如果 OpenAI-compatible 网关暂不支持原生 `response_format`，公共客户端会自动回退到 JSON 输出指令和本地 Pydantic 校验。

AI 恋爱大师聊天工作台已支持多轮对话、SQLAlchemy 会话记忆持久化、页面刷新恢复和结构化恋爱报告生成。

健康检查：

```text
GET http://127.0.0.1:8000/api/v1/health
```

## 前端开发

```bash
cd frontend
npm install
npm test
npm run build
npm run dev
```

## 设计文档

- `docs/architecture/multi-agent-platform-design.md`
- `docs/architecture/love-master-rag-knowledge-base-design.md`
- `docs/api/health.md`
- `docs/api/conversations.md`
- `docs/api/knowledge-bases.md`
- `docs/status/project-initialization-status.md`
- `docs/status/love-master-agent-status.md`
- `docs/status/guardrails-status.md`
