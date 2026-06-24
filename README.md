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

## 后端开发

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python -m uvicorn app.main:app --reload
```

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
- `docs/api/health.md`
- `docs/status/project-initialization-status.md`
