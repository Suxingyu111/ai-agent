# AI 超级智能体多智能体平台详细设计方案

## 1. 文档信息

- 文档状态：设计方案
- 适用项目：AI 超级智能体多智能体平台
- 技术主线：Python、FastAPI、LangChain、LangGraph、Vue 3、Vite、MySQL、Redis、向量数据库、MCP
- 设计目标：构建一个支持多个独立智能体、知识库问答、工具调用、自主规划、自主执行、可审计、可扩展、可高可用部署的 AI 智能体平台
- 重要约束：本项目从第一天开始必须坚持智能体解耦、目录解耦、文件解耦、工具解耦、运行状态解耦和权限解耦

## 2. 背景与目标

本项目不是单一聊天机器人，也不是把多个角色混在一个大智能体里的简单应用，而是一个面向长期演进的多智能体运行平台。平台需要支持多个智能体独立完成各自职责，并能在受控编排下协同完成复杂目标。

核心目标如下：

- 支持多个独立智能体，每个智能体只负责自己的任务边界。
- 支持多轮对话、会话记忆、长期记忆和项目级记忆。
- 支持基于自定义知识库的 RAG 问答。
- 支持通过 LangChain 接入多种大模型。
- 支持通过 MCP、LangChain Tools、自定义工具、沙箱工具接入联网搜索、网页抓取、文件操作、终端操作、地图服务、资源下载、PDF 生成等能力。
- 支持自主规划、自主推理、自主执行、反思评估、失败重试、人工审批和任务恢复。
- 支持高扩展性：新增一个智能体或新增某个智能体功能时，不影响其他智能体和既有功能。
- 支持高维护性：目录、文件、模块边界清晰，职责单一，接口稳定，测试完整。
- 支持高可用性：任务可恢复，服务可水平扩展，工具可熔断，运行全程可观测。

## 3. 非目标

第一阶段不追求完全开放的自治 swarm，也不允许模型无限制调用工具或无限循环执行。平台应先实现可控、可审计、可恢复的多智能体能力，再逐步增强自治程度。

非目标包括：

- 不把所有智能体 prompt 混在一个文件中。
- 不把所有智能体逻辑写在一个 Python 类或一个 service 中。
- 不让一个智能体直接调用另一个智能体的内部实现。
- 不让智能体绕过工具网关直接访问外部系统。
- 不让智能体共享一份无边界的全局记忆。
- 不在 MVP 阶段实现完全自由的多智能体 swarm。

## 4. 总体设计原则

### 4.1 智能体独立原则

每个智能体必须是独立模块，拥有独立的职责、输入输出契约、工具权限、记忆命名空间、知识库范围、prompt、测试和版本。

智能体之间禁止直接依赖：

- 禁止 `research_agent` 直接 import `writer_agent`。
- 禁止 `code_agent` 直接读取 `knowledge_agent` 的私有状态。
- 禁止任意智能体直接访问其他智能体的 prompt、memory、tools 或 internal state。
- 禁止通过共享全局变量传递智能体状态。

智能体之间只能通过以下方式协作：

- `Orchestrator` 分派任务。
- `Workflow Engine` 进行编排。
- `Event Bus` 发布和消费标准事件。
- `TaskResult` 传递结构化结果。
- `Artifact` 传递文件或产物。
- `ToolGateway` 调用共享工具。

### 4.2 平台内核与智能体插件分离

平台分为两层：

- `Agent Kernel`：稳定运行内核，负责契约、注册、运行、权限、工具、记忆、审计、checkpoint、事件流。
- `Agent Plugin`：具体智能体插件，只实现某个智能体自己的业务能力。

普通功能开发优先修改对应智能体插件。只有当多个智能体共同需要同一种平台能力时，才允许修改 `Agent Kernel`。

### 4.3 目录和文件解耦原则

目录结构必须表达架构边界。文件不允许变成跨领域的大杂烩。

规则如下：

- 每个智能体一个独立目录。
- 每个领域模块一个独立目录。
- 每个工具适配器一个独立文件或子目录。
- prompt 按智能体隔离存放。
- schema 按领域或智能体隔离存放。
- 测试文件与被测模块对应。
- 禁止建立 `common.py`、`utils.py`、`helpers.py` 这类无限膨胀的万能文件。
- 公共能力必须先证明至少两个模块稳定复用，再抽入 shared 或 kernel。

### 4.4 契约优先原则

智能体不是通过内部代码互相认识，而是通过契约协作。

核心契约包括：

- `AgentManifest`
- `AgentContract`
- `TaskInput`
- `TaskResult`
- `AgentEvent`
- `ToolRequest`
- `ToolResult`
- `MemoryScope`
- `Artifact`

任何智能体输入输出结构变更，都必须考虑版本兼容。

### 4.5 默认拒绝原则

工具、知识库、记忆和外部 API 权限必须默认拒绝。智能体只能访问 manifest 或 policy 明确授权的能力。

默认拒绝范围包括：

- 未授权工具。
- 未授权知识库。
- 非本智能体 memory namespace。
- 非本项目文件空间。
- 高风险外部操作。
- 需要用户授权的 OAuth 资源。

## 5. 技术选型

| 层级 | 技术 | 说明 |
|---|---|---|
| 后端 API | FastAPI | API 网关、认证、任务、工具、知识库、智能体管理 |
| Agent 框架 | LangChain | 模型接入、工具抽象、RAG、MCP tools 集成 |
| Agent 编排 | LangGraph | 多智能体 graph、subgraph、checkpoint、human-in-the-loop、可恢复执行 |
| 前端 | Vue 3 + Vite | 智能体工作台、任务时间线、知识库、工具市场 |
| 关系数据库 | MySQL | 用户、项目、会话、任务、智能体配置、审计日志 |
| 缓存和队列 | Redis | 缓存、锁、事件中转、限流、异步状态 |
| 向量数据库 | Qdrant | MVP 推荐，后续可替换 Milvus/Zilliz/TiDB Vector |
| 对象存储 | MinIO / S3 | 文件、产物、PDF、下载资源 |
| 工具协议 | MCP | 标准化接入外部工具和上下文 |
| 任务执行 | Celery / Dramatiq / Arq | 异步长任务执行 |
| 可观测性 | OpenTelemetry、LangSmith 或 Langfuse | trace、工具调用、模型调用、任务事件 |
| 沙箱 | Docker / E2B / Browserbase | 终端、代码、浏览器等高风险能力隔离 |

## 6. 总体架构

```text
Vue 3 / Vite 前端
  ├─ 对话工作台
  ├─ 智能体管理
  ├─ Workflow 编排
  ├─ 任务运行时间线
  ├─ 工具市场 / MCP Server 管理
  ├─ 知识库管理
  ├─ 记忆管理
  └─ 产物中心

FastAPI API Gateway
  ├─ Auth / User / Project
  ├─ Agent Registry API
  ├─ Workflow API
  ├─ Agent Run API
  ├─ Conversation API
  ├─ Knowledge API
  ├─ Tool / MCP API
  ├─ Artifact API
  ├─ Approval API
  └─ Audit API

Agent Platform Core
  ├─ Agent Kernel
  ├─ Workflow Engine
  ├─ Tool Gateway
  ├─ Memory Service
  ├─ Knowledge Service
  ├─ Event Bus
  ├─ Checkpoint Service
  ├─ Approval Service
  └─ Observability

Independent Agent Plugins
  ├─ supervisor_agent
  ├─ planner_agent
  ├─ research_agent
  ├─ knowledge_agent
  ├─ writer_agent
  ├─ reviewer_agent
  ├─ file_agent
  ├─ browser_agent
  ├─ code_agent
  ├─ map_agent
  └─ pdf_agent

Infrastructure
  ├─ MySQL
  ├─ Redis
  ├─ Qdrant
  ├─ MinIO / S3
  ├─ MCP Servers
  ├─ Sandbox Workers
  └─ Observability Stack
```

## 7. 后端目录结构设计

```text
backend/
  pyproject.toml
  alembic.ini
  app/
    main.py
    api/
      v1/
        router.py
        deps.py
    core/
      config.py
      security.py
      logging.py
      errors.py
      pagination.py
      rate_limit.py
      observability.py

    db/
      base.py
      session.py
      migrations/

    shared/
      enums.py
      types.py
      time.py
      id_generator.py
      schemas/
        base.py
        pagination.py

    agent_kernel/
      contracts/
        agent.py
        task.py
        message.py
        result.py
        tool.py
        memory.py
        event.py
        artifact.py
      runtime/
        compiler.py
        context.py
        runner.py
        streaming.py
        checkpoints.py
        cancellation.py
      registry/
        loader.py
        manifest.py
        validator.py
      policies/
        tool_policy.py
        memory_policy.py
        knowledge_policy.py
        budget_policy.py
        safety_policy.py
      events/
        bus.py
        publisher.py
        subscribers.py
      testing/
        contract_test.py
        fake_model.py
        fake_tools.py

    workflows/
      supervisor/
        graph.py
        state.py
        router.py
      planner_executor/
        graph.py
        state.py
      pipeline/
        graph.py
        state.py
      handoff/
        graph.py
        state.py

    agents/
      supervisor_agent/
        manifest.yaml
        agent.py
        schemas.py
        prompts/
          system.md
          planning.md
        tools.py
        memory.py
        tests/
      planner_agent/
      research_agent/
      knowledge_agent/
      writer_agent/
      reviewer_agent/
      file_agent/
      browser_agent/
      code_agent/
      map_agent/
      pdf_agent/

    modules/
      auth/
        api.py
        models.py
        schemas.py
        service.py
        repository.py
      users/
      projects/
      conversations/
      agent_definitions/
      agent_runs/
      workflows/
      tools/
      mcp_servers/
      knowledge/
      memory/
      artifacts/
      approvals/
      audit/

    integrations/
      llms/
        router.py
        providers/
          openai.py
          anthropic.py
          deepseek.py
          qwen.py
          openrouter.py
          ollama.py
      mcp/
        client.py
        server_registry.py
      search/
        firecrawl.py
        tavily.py
        brave.py
      vectorstores/
        qdrant.py
        milvus.py
      storage/
        s3.py
        local.py
      sandbox/
        docker_runner.py
        browser_runner.py
        code_runner.py

    workers/
      celery_app.py
      tasks/
        agent_run_tasks.py
        knowledge_ingestion_tasks.py
        artifact_tasks.py

  tests/
    contract/
    integration/
    e2e/
```

### 7.1 后端目录规则

- `agent_kernel/` 只放平台内核，不放具体业务智能体逻辑。
- `agents/` 下每个目录只属于一个智能体。
- `workflows/` 只负责编排，不写具体智能体业务逻辑。
- `modules/` 只放业务领域 API、service、repository、model。
- `integrations/` 只放第三方系统适配，不写业务规则。
- `shared/` 只放真正稳定、通用、无业务倾向的基础能力。

## 8. 前端目录结构设计

```text
frontend/
  package.json
  vite.config.ts
  src/
    main.ts
    app/
      router.ts
      stores.ts
      layouts/
        MainLayout.vue
        WorkspaceLayout.vue

    shared/
      api/
        http.ts
        sse.ts
        websocket.ts
      components/
        EmptyState.vue
        ConfirmDialog.vue
        DataTable.vue
      composables/
        useAsyncState.ts
        useEventStream.ts
      types/
        api.ts
        pagination.ts
      utils/

    modules/
      chat/
        pages/
        components/
        stores/
        api.ts
        types.ts
      agents/
        pages/
          AgentListPage.vue
          AgentDetailPage.vue
          AgentBuilderPage.vue
        components/
        stores/
        api.ts
        types.ts
      workflows/
        pages/
        components/
        stores/
        api.ts
        types.ts
      agent-runs/
        pages/
          RunDetailPage.vue
          RunTimelinePage.vue
        components/
          StepTimeline.vue
          AgentStepCard.vue
          ToolCallPanel.vue
          ApprovalPanel.vue
        stores/
        api.ts
        types.ts
      knowledge/
      tools/
      mcp-servers/
      memory/
      artifacts/
      approvals/
      audit/
      settings/

    styles/
      tokens.css
      global.css

  tests/
    unit/
    e2e/
```

### 8.1 前端目录规则

- 每个业务模块必须独立维护自己的 `api.ts`、`types.ts`、`stores/` 和页面组件。
- `shared/components` 只放跨模块稳定复用的 UI 组件。
- 禁止某个模块直接 import 另一个模块的内部组件，跨模块能力必须通过 shared 或显式导出的 public API。
- 智能体运行时间线、工具调用面板、审批面板必须作为独立模块维护。

## 9. 智能体插件标准

每个智能体必须使用统一插件结构：

```text
agents/{agent_key}/
  manifest.yaml
  agent.py
  schemas.py
  prompts/
    system.md
  tools.py
  memory.py
  tests/
    test_contract.py
    test_permissions.py
    test_memory_isolation.py
    test_golden_tasks.py
```

### 9.1 manifest 示例

```yaml
key: research_agent
version: 1.0.0
display_name: 研究智能体
description: 负责联网检索、网页抓取、资料归纳和来源整理
responsibility: 只完成研究相关任务，不负责最终写作、代码执行或文件修改
input_schema: ResearchTaskInput
output_schema: ResearchTaskResult
model_policy: research_default
memory_namespace: agent.research
allowed_tools:
  - firecrawl.search
  - firecrawl.scrape
  - web.fetch
knowledge_scopes: []
requires_approval_for:
  - external_download
max_iterations: 6
max_runtime_seconds: 180
```

### 9.2 智能体契约

每个智能体必须实现统一契约：

```python
class AgentContract(Protocol):
    key: str
    version: str

    async def run(
        self,
        task: AgentTask,
        context: AgentContext,
    ) -> AgentTaskResult:
        ...
```

智能体返回值必须是结构化结果，不允许只返回自由文本：

```python
class AgentTaskResult(BaseModel):
    status: Literal["succeeded", "failed", "needs_approval", "needs_clarification"]
    summary: str
    data: dict[str, Any]
    artifacts: list[ArtifactRef] = []
    citations: list[Citation] = []
    events: list[AgentEvent] = []
    next_suggested_tasks: list[AgentTask] = []
```

## 10. 内置智能体设计

| 智能体 | 职责边界 | 禁止行为 |
|---|---|---|
| `supervisor_agent` | 识别任务类型、选择智能体、分配子任务 | 不直接执行业务工具 |
| `planner_agent` | 拆解目标、制定计划、定义完成标准 | 不直接调用外部 API |
| `research_agent` | 联网搜索、网页抓取、资料整理 | 不写最终报告、不修改文件 |
| `knowledge_agent` | 查询私有知识库、返回引用证据 | 不访问未授权知识库 |
| `writer_agent` | 汇总材料、生成报告、组织表达 | 不自行联网检索 |
| `reviewer_agent` | 审核事实、风险、格式、完成标准 | 不修改原始产物，只给审查结果 |
| `file_agent` | 在授权工作区内读写文件 | 不访问工作区外路径 |
| `browser_agent` | 浏览器访问、页面交互、网页验证 | 不执行终端命令 |
| `code_agent` | 代码分析、生成、运行沙箱测试 | 不绕过沙箱访问宿主机 |
| `map_agent` | 地图、地理编码、路线、位置服务 | 不处理非地图任务 |
| `pdf_agent` | PDF 生成、模板渲染、版式检查 | 不负责内容事实判断 |

## 11. 多智能体编排设计

### 11.1 Supervisor 模式

适合大多数任务。主管智能体只负责分派和汇总，不直接干子智能体的工作。

```text
User Goal
  -> SupervisorAgent
  -> PlannerAgent
  -> ResearchAgent / KnowledgeAgent / FileAgent / CodeAgent
  -> ReviewerAgent
  -> WriterAgent
  -> Final Result
```

### 11.2 Pipeline 模式

适合固定流程，例如知识库报告生成：

```text
KnowledgeAgent
  -> ResearchAgent
  -> WriterAgent
  -> ReviewerAgent
  -> PdfAgent
```

每一步只接收上一步的结构化输出。

### 11.3 Handoff 模式

适合动态移交，例如用户提出地图任务时，从通用助手移交给 `map_agent`。Handoff 只能通过父级 workflow 完成，不允许智能体直接调用另一个智能体。

### 11.4 Event-driven 模式

适合长任务和异步任务。智能体发布事件，其他模块按契约消费。

```text
research.completed
knowledge.evidence_found
approval.required
artifact.created
review.failed
run.completed
```

## 12. LangGraph 落地方式

LangGraph 用于实现运行时编排：

- 每个智能体可被编译为独立 subgraph。
- 每个 subgraph 使用唯一 node name，保证 namespace isolation。
- 每个 subgraph 可以有自己的 checkpointer。
- 父 graph 只负责路由、汇总、审批和生命周期控制。
- 子 graph 如需返回父 graph，使用 `Command.PARENT`。
- human-in-the-loop 使用 `interrupt()` 暂停，并通过 `Command(resume=...)` 恢复。
- checkpoint 用于任务恢复、回放、fork 和失败重试。

## 13. 工具系统设计

### 13.1 工具类型

| 类型 | 示例 | 说明 |
|---|---|---|
| Builtin Tool | 文件、PDF、内部查询 | 平台内置能力 |
| MCP Tool | GitHub、数据库、地图、浏览器 | 标准协议接入 |
| HTTP Tool | 外部 REST API | 用户配置或平台配置 |
| Search Tool | Firecrawl、Tavily、Brave | 联网搜索和抓取 |
| Sandbox Tool | 终端、代码运行、浏览器自动化 | 高风险能力，必须隔离 |

### 13.2 Tool Gateway

所有工具调用必须经过 `ToolGateway`：

```text
Agent
  -> ToolGateway
  -> ToolPolicy
  -> CredentialResolver
  -> Adapter
  -> ResultNormalizer
  -> AuditLogger
```

智能体禁止直接持有 API key，禁止直接调用 MCP server，禁止直接启动终端或浏览器。

### 13.3 工具权限

工具权限按智能体、项目、租户、用户四层判断：

- 智能体是否声明该工具能力。
- 项目是否启用该工具。
- 用户是否有调用权限。
- 当前操作是否需要人工审批。

## 14. MCP 设计

MCP 是工具生态主协议。平台需要提供 MCP Gateway 和 MCP Registry。

MCP server 元数据包括：

- server key
- transport：`stdio`、`sse`、`streamable_http`
- command 或 remote URL
- tool list
- credential profile
- health status
- tenant scope
- allowed agent list

MCP Gateway 负责：

- 工具发现。
- 工具过滤。
- 凭证隔离。
- 参数校验。
- 调用审计。
- 超时和熔断。
- 返回结果标准化。

## 15. 记忆系统设计

记忆必须按作用域隔离：

| 记忆类型 | 作用域 | 用途 |
|---|---|---|
| thread memory | 单次会话或任务 | 当前上下文 |
| agent memory | 单个智能体 | 专家经验和偏好 |
| project memory | 项目 | 项目背景和约束 |
| user memory | 用户 | 用户稳定偏好 |
| organization memory | 组织 | 团队规范和企业知识 |

规则：

- 智能体只能读写自己的 `agent memory namespace`。
- 跨智能体共享记忆必须通过 `MemoryService` 授权。
- 重要记忆需要来源、时间、可信度、过期策略。
- 敏感信息默认不写入长期记忆。
- 用户必须能查看、删除、禁用记忆。

## 16. 知识库系统设计

知识库流程：

```text
上传或导入
  -> 文件解析
  -> 内容清洗
  -> 结构化切块
  -> embedding
  -> 写入向量数据库
  -> metadata 写入 MySQL
  -> 检索时按权限过滤
  -> rerank
  -> 返回 evidence
```

知识库访问规则：

- 只有 `knowledge_agent` 直接访问检索服务。
- 其他智能体需要知识证据时，必须请求 `knowledge_agent` 或调用受控 RAG tool。
- 检索必须带 `tenant_id`、`project_id`、`knowledge_base_id`。
- 回答必须包含引用来源。
- 文档分块必须保存来源、页码、标题层级、版本和权限信息。

## 17. 数据模型设计

核心表：

```text
users
projects
project_members

agent_definitions
agent_versions
agent_instances
agent_capabilities
agent_tool_permissions
agent_memory_scopes
agent_knowledge_scopes

workflows
workflow_versions
workflow_nodes
workflow_edges

agent_runs
agent_tasks
agent_task_events
agent_task_results
agent_handoffs
agent_private_states

conversation_sessions
conversation_messages

knowledge_bases
documents
document_chunks

tool_definitions
tool_servers
tool_credentials
tool_invocations

memory_entries
artifacts
approval_requests
audit_logs
```

### 17.1 agent_private_states

用于保存单个智能体私有状态：

```text
id
tenant_id
project_id
agent_instance_id
agent_version
run_id
namespace
schema_version
state_json
created_at
updated_at
```

其他智能体不能直接读取该表。

### 17.2 tool_invocations

用于审计所有工具调用：

```text
id
tenant_id
project_id
run_id
task_id
agent_instance_id
tool_key
request_json
response_json
status
latency_ms
cost
error_message
created_at
```

## 18. API 设计

```text
POST   /api/v1/agents
GET    /api/v1/agents
GET    /api/v1/agents/{id}
PATCH  /api/v1/agents/{id}
POST   /api/v1/agents/{id}/versions

POST   /api/v1/workflows
GET    /api/v1/workflows
GET    /api/v1/workflows/{id}
POST   /api/v1/workflows/{id}/versions

POST   /api/v1/agent-runs
GET    /api/v1/agent-runs/{id}
GET    /api/v1/agent-runs/{id}/events
POST   /api/v1/agent-runs/{id}/cancel
POST   /api/v1/agent-runs/{id}/resume
POST   /api/v1/agent-runs/{id}/fork

POST   /api/v1/approvals/{id}/approve
POST   /api/v1/approvals/{id}/reject

POST   /api/v1/tools
GET    /api/v1/tools
POST   /api/v1/tools/{id}/test

POST   /api/v1/mcp-servers
GET    /api/v1/mcp-servers
GET    /api/v1/mcp-servers/{id}/tools

POST   /api/v1/knowledge-bases
GET    /api/v1/knowledge-bases
POST   /api/v1/knowledge-bases/{id}/documents
POST   /api/v1/knowledge-bases/{id}/query

GET    /api/v1/artifacts/{id}
GET    /api/v1/audit-logs
```

## 19. 事件流设计

长任务通过 SSE 或 WebSocket 向前端推送事件。

事件类型：

```text
run.created
run.started
plan.created
task.created
agent.started
agent.message
tool.requested
tool.started
tool.succeeded
tool.failed
approval.required
approval.approved
approval.rejected
handoff.created
artifact.created
review.failed
run.completed
run.failed
run.cancelled
```

所有事件必须包含：

```text
event_id
event_type
run_id
task_id
agent_instance_id
timestamp
payload
trace_id
```

## 20. 高可用设计

- FastAPI 服务无状态，可水平扩容。
- Agent Run 使用 worker 异步执行。
- 每个 run 和 task 都持久化状态。
- LangGraph checkpointer 保存可恢复 checkpoint。
- Redis 只作为缓存、锁和事件通道，最终状态写 MySQL。
- 工具调用设置超时、重试、熔断和限流。
- MCP server 做健康检查和隔离部署。
- 高风险工具通过沙箱执行。
- 每个智能体有独立并发限制。
- 某个智能体不可用时，workflow 可降级、暂停、重试或人工接管。

## 21. 安全设计

### 21.1 权限边界

- 用户权限控制项目、知识库、工具、智能体实例。
- 智能体权限控制工具、记忆、知识库和文件空间。
- 工具权限控制外部 API、凭证、风险动作。
- 所有高风险动作必须支持人工审批。

### 21.2 高风险工具审批

以下操作默认需要审批：

- 终端命令执行。
- 文件删除、覆盖、批量修改。
- 数据库写操作。
- 外部资源下载。
- 发送邮件、消息、通知。
- 调用地图服务提交真实路线、下单、预约等真实世界动作。
- 任何涉及支付、账号、权限变更的操作。

### 21.3 凭证管理

- API key 和 OAuth token 必须加密存储。
- 智能体不能直接读取明文凭证。
- 凭证只在 ToolGateway 执行时短暂注入。
- 每次凭证使用必须记录审计日志。

## 22. 可观测性设计

必须观测：

- 每次模型调用。
- 每次工具调用。
- 每个智能体任务步骤。
- 每次 handoff。
- 每次审批。
- 每个 checkpoint。
- 每个 artifact。
- 每次失败和重试。

推荐接入：

- OpenTelemetry：系统 trace。
- LangSmith 或 Langfuse：LLM trace、prompt、tool call、评测。
- Prometheus + Grafana：系统指标。
- 结构化日志：排查任务执行链路。

## 23. 配置管理设计

项目必须从第一天开始区分真实配置和示例配置。真实配置不允许提交到 Git，示例配置必须提交到 Git，用于说明本地开发和生产部署需要哪些配置项。

### 23.1 配置文件位置

```text
backend/
  .env              # 后端真实配置，禁止提交
  .env.example      # 后端本地开发配置模板，允许提交
  .env.prod.example # 后端生产部署配置模板，允许提交

frontend/
  .env              # 前端真实配置，禁止提交
  .env.example      # 前端本地开发配置模板，允许提交
  .env.prod.example # 前端生产部署配置模板，允许提交
```

### 23.2 配置分类

后端配置必须按以下类别规整：

- 基础服务配置。
- 安全与认证配置。
- MySQL 数据库配置。
- Redis 配置。
- 异步任务配置。
- 大模型与 LangChain 配置。
- 向量数据库配置。
- 对象存储配置。
- 工具与 MCP 配置。
- 可观测性配置。

前端配置必须按以下类别规整：

- 基础应用配置。
- 后端接口配置。
- 功能开关配置。
- 静态资源和产物配置。
- 可观测性配置。

### 23.3 配置注释规则

- 每一个配置项都必须有中文注释。
- 注释必须说明配置用途、影响范围和重要注意事项。
- 涉及密钥、Token、密码、OAuth 凭证的配置，注释必须明确禁止提交真实值。
- 生产配置模板必须使用占位值，不允许出现真实域名、真实密钥或真实账号密码。

### 23.4 前后端读取规则

- 后端所有配置必须集中从 `backend/.env` 读取，再映射到统一 `Settings` 配置对象。
- 后端业务代码不得直接散落读取环境变量。
- 前端所有配置必须从 `frontend/.env` 读取。
- 前端必须通过集中配置模块读取 `import.meta.env`，页面和组件不得散落读取配置。
- 前端只能使用 `VITE_` 前缀变量，不能放置任何私密密钥。

### 23.5 Git 跟踪规则

- `.gitignore` 必须忽略根目录、`backend/` 和 `frontend/` 下的真实 `.env` 文件。
- `.env.example` 和 `.env.prod.example` 是可提交模板，必须持续维护。
- 新增配置项时，必须同步更新本地和生产示例配置文件。
- 删除配置项时，必须同步删除示例配置文件中的对应项。

## 24. 测试策略

### 24.1 智能体测试

每个智能体必须包含：

- contract test：输入输出契约稳定。
- permission test：不能调用未授权工具。
- memory isolation test：不能读写其他智能体记忆。
- golden task test：典型任务输出符合预期。
- regression test：历史任务行为不被破坏。

### 24.2 平台测试

平台必须包含：

- workflow 集成测试。
- ToolGateway 权限测试。
- MCP server 发现和调用测试。
- checkpoint 恢复测试。
- human-in-the-loop 中断和恢复测试。
- 任务取消和重试测试。
- 并发任务测试。

### 24.3 目录解耦测试

建议增加静态检查：

- 禁止 `agents/*` 互相 import。
- 禁止智能体 import `db.session`。
- 禁止智能体绕过 `ToolGateway`。
- 禁止跨 namespace 访问 memory。
- 禁止 prompt 文件跨智能体复用。

## 25. 版本和发布策略

智能体必须独立版本化：

- bugfix：`1.0.1`
- 兼容新增能力：`1.1.0`
- 破坏性 schema 或行为变化：`2.0.0`

Workflow 绑定具体智能体版本。升级智能体时，不自动影响历史 workflow 和正在运行的任务。

发布流程：

```text
修改某个智能体
  -> 更新该智能体版本
  -> 跑该智能体测试
  -> 跑平台 contract regression
  -> 灰度到部分 workflow
  -> 观察 trace 和失败率
  -> 全量启用
```

## 26. MVP 分期

### 第一期：基础平台

- FastAPI 项目结构。
- Vue 3 基础工作台。
- 用户、项目、会话。
- 模型路由。
- SSE 事件流。
- MySQL、Redis 基础设施。

### 第二期：独立智能体内核

- Agent Kernel。
- Agent Manifest。
- Agent Registry。
- Agent Contract。
- Supervisor、Planner、Writer、Reviewer 四个基础智能体。
- 智能体隔离测试。

### 第三期：知识库和 RAG

- 文档上传。
- PDF、Markdown、TXT、网页解析。
- Qdrant 向量检索。
- KnowledgeAgent。
- 引用回答。
- 权限过滤。

### 第四期：工具和 MCP

- ToolGateway。
- MCP Server Registry。
- Firecrawl 搜索和抓取。
- 文件工具。
- PDF 生成工具。
- 人工审批。
- 工具审计。

### 第五期：高级多智能体编排

- Workflow Builder。
- Handoff。
- Checkpoint 恢复。
- 任务 fork。
- BrowserAgent、CodeAgent、MapAgent。
- 智能体评测和回归集。

## 27. 项目全局强制规则

以下规则从项目开始到后续所有开发阶段都必须遵守：

1. 每个智能体必须独立目录、独立 manifest、独立 schema、独立 prompt、独立测试。
2. 智能体之间不得直接 import、直接调用、直接读写状态。
3. 新增某个智能体功能时，不得修改其他智能体文件，除非修改的是稳定公共契约并完成兼容评估。
4. 智能体不能直接访问数据库、外部 API、MCP server、文件系统或终端，必须通过平台服务或 ToolGateway。
5. 每个智能体只能访问授权工具、授权知识库和自己的 memory namespace。
6. 目录结构必须体现架构边界，禁止把多个领域混在一个文件中。
7. 公共能力不能过早抽象，只有明确被多个模块稳定复用时才能进入 shared 或 kernel。
8. 所有输入输出契约必须可测试、可版本化、可回归。
9. 高风险工具必须支持审批、审计、超时、重试和熔断。
10. 每个任务运行必须有 trace、事件、步骤、工具调用记录和最终状态。
11. 所有新增后端接口必须同步接口文档。
12. 所有独立功能完成后必须同步状态文档。
13. 所有修改必须通过与风险匹配的测试和验证。
14. 前后端真实配置必须分别从 `backend/.env` 和 `frontend/.env` 读取，并且真实 `.env` 文件不得提交到 Git。
15. 新增、删除或修改配置项时，必须同步更新 `.env.example` 和 `.env.prod.example`，并补充中文注释。

## 28. 资料依据

本设计参考了以下资料和文档：

- LangGraph subgraphs：`https://docs.langchain.com/oss/python/langgraph/use-subgraphs`
- LangGraph graph API / `Command.PARENT`：`https://docs.langchain.com/oss/python/langgraph/graph-api`
- LangGraph checkpointers：`https://docs.langchain.com/oss/python/langgraph/checkpointers`
- LangGraph human-in-the-loop / interrupt：`https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph`
- LangChain multi-agent：`https://docs.langchain.com/oss/python/langchain/multi-agent`
- LangGraph Supervisor Reference：`https://reference.langchain.com/python/langgraph-supervisor`
- MCP 官方介绍：`https://modelcontextprotocol.io/docs/getting-started/intro`
- MCP Tools 规范：`https://modelcontextprotocol.io/specification/2025-06-18/server/tools`
- MCP Gateway Registry：`https://www.truefoundry.com/blog/mcp-gateway-registry`
- MCP Tool Governance：`https://konghq.com/blog/engineering/mcp-tool-governance-security-meets-context-efficiency`
