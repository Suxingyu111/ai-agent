# AI 恋爱大师智能体实现状态

## 已完成范围

- 新增独立智能体目录 `backend/app/agents/love_master_agent/`。
- 新增系统提示词 `prompts/system.md`，明确角色定位为恋爱关系教练和情感沟通助手。
- 新增 `manifest.yaml`，配置：
  - `key: love_master_agent`
  - `allowed_tools: []`
  - `memory_namespace: agent.love_master`
- 新增 `LangChainChatModelClient`，通过通用 `LLM_*` 配置接入 OpenAI-compatible 大模型接口。
- `LangChainChatModelClient.generate_structured(...)` 已增加兼容回退：当模型网关不支持原生 `response_format` 结构化输出时，会自动改用 JSON 输出指令并在本地执行 Pydantic 校验。
- `LangChainChatModelClient.generate_structured(...)` 会把 JSON fallback 解析失败或 schema 校验失败包装为通用 `StructuredOutputError`，供所有智能体统一识别结构化输出失败。
- `LoveMasterAgent` 已支持真实大模型生成；未配置 `LLM_API_KEY` 时保留规则型本地兜底，便于测试和无密钥环境启动。
- `LoveMasterAgent` 已改为优先使用通用结构化输出能力，模型返回会校验为 `LoveMasterModelOutput`；如果模型返回不可解析 JSON，会降级为普通文本回复并继续返回 201，避免聊天接口 500。
- 新增恋爱报告结构化输出能力：
  - 新增 `prompts/report.md`，报告提示词与普通聊天提示词分离。
  - 新增 `LoveReportOutput`，用于校验关系阶段、局面总结、积极信号、风险信号、下一步行动和沟通话术。
  - 新增 `LoveMasterAgent.generate_report(...)`，通过通用 `ChatModelClient.generate_structured(...)` 生成报告。
- 新增 SQLAlchemy 业务持久化能力：
  - 新增 `db/base.py`、`db/models.py` 和 `db/session.py`。
  - 新增 `ConversationRepository`，持久化会话、消息、记忆候选和恋爱报告。
  - 服务重启后可通过同一 `conversation_id` 恢复消息历史和 `memory_summary`。
- 会话链路已接入通用 AI Guardrails，用户输入和模型输出都会经过 `agent_kernel/guardrails` 统一拦截。
- 更新 `LoveMasterAgent`，支持：
  - 暧昧阶段推进建议。
  - 把系统提示词、会话记忆摘要和完整多轮消息历史传给大模型。
  - 从结构化输出中读取 `reply`、`memory_candidates`、`safety_flags`、`relationship_stage`、`needs_clarification` 和 `suggested_next_questions`。
  - 跟踪、监视、骚扰、操控、报复等请求的安全转向。
  - 输出 `memory_candidates` 和 `safety_flags`。
- 新增 `modules/conversations`，提供多轮会话 API：
  - `POST /api/v1/conversations`
  - `GET /api/v1/conversations`
  - `GET /api/v1/conversations/{conversation_id}`
  - `POST /api/v1/conversations/{conversation_id}/messages`
  - `POST /api/v1/conversations/{conversation_id}/love-report`
  - `GET /api/v1/conversations/{conversation_id}/messages`
- 前端 `ChatWorkspacePage.vue` 已从占位页升级为最小可用聊天工作台：
  - 首次发送时自动创建 `love_master_agent` 会话。
  - 展示用户消息和助手消息。
  - 展示当前会话记忆摘要。
  - 页面刷新时通过 localStorage 中的会话 id 恢复会话详情、历史消息和记忆摘要。
  - 当本地缓存的会话 id 在后端不存在时，恢复阶段会清理旧 id；发送阶段会自动重建会话并重试当前消息一次，避免 Docker 数据库重建或页面长期打开后一直发送失败。
  - 支持创建新会话并清理本地会话 id。
  - 支持基于当前会话生成并展示结构化恋爱报告。
  - 支持发送中和错误状态。
- 新增前端聊天 API 封装 `frontend/src/modules/chat/api.ts`。

## 核心业务约束

- AI 恋爱大师是恋爱关系教练，不是用户的 AI 伴侣、治疗师、律师或现实关系替代品。
- 智能体不能调用外部工具，`allowed_tools` 保持为空。
- 智能体只能使用 `agent.love_master` 记忆命名空间。
- 当前多轮消息和会话级 `memory_summary` 已通过 SQLAlchemy 业务表持久化，服务重启后可按 `conversation_id` 恢复。
- 当前长期记忆暂未实现跨会话检索、用户授权确认和更细粒度敏感信息过滤。
- 安全策略优先拒绝或转向以下请求：
  - 跟踪、监视、偷拍。
  - 骚扰、威胁、报复。
  - PUA、操控、欺骗对方。
- 通用 Guardrails 会在请求进入模型前拦截上述输入，并在模型输出保存前拦截危险输出。

## 涉及模块

- 后端智能体：
  - `backend/app/agent_kernel/contracts/model.py`
  - `backend/app/agent_kernel/runtime/chat_model.py`
  - `backend/app/agents/love_master_agent/agent.py`
  - `backend/app/agents/love_master_agent/prompts/report.md`
  - `backend/app/agents/love_master_agent/prompts/system.md`
  - `backend/app/agents/love_master_agent/manifest.yaml`
  - `backend/app/agents/love_master_agent/schemas.py`
  - `backend/app/agents/love_master_agent/memory.py`
  - `backend/app/agents/love_master_agent/tools.py`
- 后端接口：
  - `backend/app/db/base.py`
  - `backend/app/db/models.py`
  - `backend/app/db/session.py`
  - `backend/app/modules/conversations/api.py`
  - `backend/app/modules/conversations/repository.py`
  - `backend/app/modules/conversations/service.py`
  - `backend/app/modules/conversations/schemas.py`
  - `backend/app/api/v1/router.py`
  - `backend/app/main.py`
- 前端：
  - `frontend/src/modules/chat/api.ts`
  - `frontend/src/modules/chat/pages/ChatWorkspacePage.vue`
  - `frontend/src/shared/api/http.ts`
  - `frontend/src/styles/global.css`
- 测试：
  - `backend/tests/test_chat_model.py`
  - `backend/tests/test_love_master_agent.py`
  - `backend/tests/test_conversations_api.py`
  - `frontend/src/modules/chat/api.test.ts`

## 已执行验证

- `backend/.venv/bin/python -m pytest backend/tests/test_love_master_agent.py backend/tests/test_conversations_api.py -q`
  - 结果：通过，`11 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_chat_model.py backend/tests/test_love_master_agent.py backend/tests/test_conversations_api.py -q`
  - 结果：通过，`18 passed, 1 warning`。
- `backend/.venv/bin/python -m py_compile backend/app/agent_kernel/contracts/model.py backend/app/agent_kernel/runtime/chat_model.py backend/app/agents/love_master_agent/agent.py`
  - 结果：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_conversations_api.py -q`
  - 结果：通过，`7 passed, 1 warning`。
- `npm test -- --run src/modules/chat/api.test.ts`
  - 目录：`frontend/`
  - 结果：通过，`6 passed`。
- `npm run build`
  - 目录：`frontend/`
  - 结果：通过。

## 当前限制

- 已接入真实大模型，但当前仍使用普通 HTTP POST 返回完整回复，尚未实现 token 级流式输出。
- 普通聊天消息 API 暂未把 `relationship_stage`、`needs_clarification` 和 `suggested_next_questions` 暴露给前端；恋爱报告接口会单独返回结构化关系阶段和行动建议。
- 恋爱报告已保存到 `love_reports` 表，但当前还没有报告历史查询接口，前端刷新后仍只恢复对话和记忆摘要。
- 尚未接入 LangGraph checkpointer；当前先用数据库中的会话消息和 `memory_summary` 支撑 thread-level memory 行为。
- 尚未提供 SSE 流式输出，当前前端使用普通 HTTP POST 获取完整回复。
- 已接入 SQLAlchemy 业务数据库；尚未接入用户登录态、会话归属、软删除、审计日志、会员额度和 CSRF。
- 记忆候选当前由服务端自动合并到会话摘要，后续应增加用户授权确认和敏感信息过滤。

## 下一步建议

- 使用 LangGraph `checkpointer + thread_id` 替换当前内存摘要，实现可恢复的短期记忆。
- 增加会话列表 UI 和报告历史查询接口。
- 增加 `POST /runs` 和 SSE 流式输出接口，提升聊天体验。
- 扩展安全策略，覆盖未成年人、家暴、自伤、他伤、性胁迫和严重心理危机场景。
