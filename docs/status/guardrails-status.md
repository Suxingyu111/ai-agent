# 通用 AI Guardrails 实现状态

## 已完成范围

- 新增 `backend/app/agent_kernel/guardrails/` 通用拦截器模块。
- 新增 Guardrails 基础契约：
  - `GuardrailDecision`
  - `GuardrailFinding`
  - `GuardrailResult`
  - `GuardrailContext`
  - `GuardrailInterceptor`
- 新增默认拦截管线 `build_default_guardrail_pipeline()`，当前覆盖：
  - prompt injection / jailbreak 请求。
  - 请求泄露系统提示词、内部规则、API key、token 等敏感信息。
  - 手机号、邮箱、密钥和 token 脱敏。
  - 跟踪、监视、偷拍、骚扰、报复、威胁、PUA、操控等高风险请求。
  - 模型输出中的系统提示词、内部规则和配置泄露风险。
- 输出侧已区分“危险建议”和“安全边界说明”：例如“不能帮助你跟踪、监视”会放行，“你可以跟踪她下班”会拦截。
- 已接入 `ConversationService`：
  - 用户输入保存和调用模型前执行输入拦截。
  - 输入被拦截时不调用大模型，直接返回安全提示。
  - 模型输出保存和返回前执行输出拦截。
  - 输出被拦截时不保存原始危险内容，只保存安全替换文案。
- 已接入 `LangChainChatModelClient`：
  - 所有通过通用模型客户端返回的大模型输出都会经过 Guardrails 后置检查。
  - 通用结构化输出会对返回的字符串字段执行 Guardrails 后置检查。
  - 当 OpenAI-compatible 模型网关不支持原生 `response_format` 时，通用结构化输出会回退到 JSON 输出指令和本地 Pydantic 校验，校验后的字符串字段仍会经过 Guardrails。
- 新增配置项：
  - `GUARDRAILS_ENABLED`
  - `GUARDRAILS_AUDIT_ENABLED`
  - `GUARDRAILS_DEFAULT_BLOCK_MESSAGE`

## 当前默认处理策略

| 风险类型 | 输入处理 | 输出处理 |
|---|---|---|
| Prompt Injection / Jailbreak | 拦截 | 不适用 |
| 请求泄露系统提示词或密钥 | 拦截 | 拦截 |
| 手机号 / 邮箱 | 脱敏后继续 | 脱敏后返回 |
| API Key / token / secret | 脱敏后继续 | 脱敏后返回或拦截 |
| 跟踪、监视、骚扰、操控 | 拦截 | 危险建议拦截，安全拒绝说明放行 |
| 系统提示词泄露 | 不适用 | 拦截 |

## 涉及模块

- Guardrails：
  - `backend/app/agent_kernel/guardrails/contracts.py`
  - `backend/app/agent_kernel/guardrails/pipeline.py`
  - `backend/app/agent_kernel/guardrails/pii.py`
  - `backend/app/agent_kernel/guardrails/prompt_injection.py`
  - `backend/app/agent_kernel/guardrails/safety.py`
- 模型调用：
  - `backend/app/agent_kernel/runtime/chat_model.py`
- 会话接口：
  - `backend/app/modules/conversations/service.py`
- 配置：
  - `backend/app/core/config.py`
  - `backend/.env.example`
  - `backend/.env.prod.example`
- 测试：
  - `backend/tests/test_guardrails.py`
  - `backend/tests/test_chat_model.py`
  - `backend/tests/test_conversations_api.py`
  - `backend/tests/test_config.py`

## 已执行验证

- `backend/.venv/bin/python -m pytest backend/tests -q`
  - 结果：通过，`25 passed`。
- `backend/.venv/bin/python -m ruff check backend/app backend/tests`
  - 结果：通过。
- `npm test`
  - 目录：`frontend/`
  - 结果：通过，`7 passed`。
- `npm run build`
  - 目录：`frontend/`
  - 结果：通过。

## 当前限制

- 当前拦截器以规则和正则为主，尚未接入独立模型分类器或 OpenAI Moderation。
- `GUARDRAILS_AUDIT_ENABLED` 已保留配置，但尚未落地数据库审计表。
- 当前 Guardrails 已接入会话链路和通用模型客户端；未来新增 ToolGateway 后，还需要接入工具调用前后拦截。
- 当前 `AgentRunner` 尚未统一承载所有智能体任务的输入输出拦截；随着更多智能体接入真实模型，应将 Guardrails 下沉到 `AgentRunner` 或统一 runtime。
- 脱敏规则会继续扩展，当前只覆盖常见手机号、邮箱、`sk-*` 密钥和 labeled token/API key。

## 下一步建议

- 为 Guardrails 增加审计日志模型，记录 `agent_key`、`direction`、`decision`、`categories` 和 `trace_id`。
- 接入 ToolGateway 后，新增 `tool_input` 和 `tool_output` 拦截。
- 增加模型分类器可选路径，用于识别更隐蔽的 prompt injection、编码绕过和多语言攻击。
- 增加管理端配置页面，支持按智能体安全画像查看命中统计。
