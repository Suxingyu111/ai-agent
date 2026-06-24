# 项目级开发规则

## 语言规则

- 默认使用简体中文进行沟通、文档编写、提交说明和变更总结。
- 代码标识符、API 名称、日志、协议字段、第三方错误信息保持原文。

## 架构总原则

本项目是多智能体平台，不是单智能体应用。所有开发必须遵守以下原则：

- 智能体独立。
- 目录解耦。
- 文件解耦。
- 工具解耦。
- 记忆隔离。
- 权限隔离。
- 契约优先。
- 默认拒绝。
- 可测试。
- 可版本化。
- 可观测。
- 可恢复。

## 智能体解耦规则

- 每个智能体必须拥有独立目录、独立 `manifest.yaml`、独立 `agent.py`、独立 `schemas.py`、独立 `prompts/`、独立 `tools.py`、独立 `memory.py` 和独立测试。
- 每个智能体只完成自己的职责，不允许把多个智能体职责混在一个智能体里。
- 智能体之间禁止直接 import、直接调用、直接读写状态。
- 智能体之间只能通过 Orchestrator、Workflow、Event、TaskResult、Artifact 或 ToolGateway 协作。
- 新增某个智能体功能时，默认只允许修改该智能体自己的目录。
- 修改公共契约或 Agent Kernel 前，必须说明影响范围，并补充兼容性验证。

## 目录和文件解耦规则

- `agent_kernel/` 只放平台运行内核，不放具体智能体业务逻辑。
- `agents/` 下每个子目录只属于一个智能体。
- `workflows/` 只负责编排，不写具体智能体内部业务。
- `modules/` 只放业务领域 API、service、repository、model。
- `integrations/` 只放第三方系统适配，不写业务规则。
- `shared/` 只放真正稳定、通用、无业务倾向的基础能力。
- 禁止创建不断膨胀的万能文件，例如无边界的 `common.py`、`utils.py`、`helpers.py`。
- Prompt、schema、工具绑定、记忆策略必须按智能体隔离。

## 工具和权限规则

- 智能体不能直接访问外部 API、MCP server、数据库、文件系统、终端或浏览器。
- 所有工具调用必须经过 `ToolGateway`。
- 工具权限默认拒绝，只允许调用 manifest 和 policy 明确授权的工具。
- 高风险工具必须具备审批、审计、超时、重试和熔断。
- API key、OAuth token 等凭证必须由平台服务注入，智能体不能直接读取明文凭证。

## 配置管理规则

- 后端所有运行配置必须从 `backend/.env` 读取。
- 前端所有运行配置必须从 `frontend/.env` 读取。
- 真实 `.env` 文件包含密钥、数据库密码、API Token、本地服务地址等敏感或环境相关信息，禁止提交到 Git。
- `.gitignore` 必须持续忽略根目录、`backend/` 和 `frontend/` 下的真实 `.env` 文件。
- 配置项必须按类别规整，例如基础服务、认证安全、数据库、Redis、任务队列、大模型、向量数据库、对象存储、工具、MCP、可观测性等。
- 每一个配置项都必须使用中文注释说明用途、影响范围和注意事项。
- `backend/.env.example` 和 `frontend/.env.example` 用于本地开发环境配置模板。
- `backend/.env.prod.example` 和 `frontend/.env.prod.example` 用于生产部署环境配置模板。
- 新增、删除或修改任何配置项时，必须同步更新对应的 example 配置文件，并保持中文注释完整。
- 前端只允许使用 `VITE_` 前缀变量，不能在前端配置中放置任何私密密钥。

## 记忆和知识库规则

- 每个智能体只能读写自己的 memory namespace。
- 跨智能体共享记忆必须通过 `MemoryService` 授权。
- 访问知识库必须经过权限过滤。
- 知识库回答必须保留引用来源。
- 敏感信息默认不写入长期记忆。

## 测试和验证规则

- 每个智能体必须有 contract test、permission test、memory isolation test 和 golden task test。
- 平台必须有 workflow 集成测试、ToolGateway 权限测试、checkpoint 恢复测试和 human-in-the-loop 测试。
- 新增或修改后端接口后，必须同步接口文档。
- 完成独立功能后，必须同步状态文档。
- 提交前必须执行与变更风险匹配的测试和验证。

## 设计文档

详细设计方案见：

- `docs/architecture/multi-agent-platform-design.md`
