# 会话接口

## 接口概览

当前会话接口用于 AI 恋爱大师智能体的多轮对话。会话、消息、会话记忆摘要和恋爱报告已通过 SQLAlchemy 持久化到 `DATABASE_URL` 指向的数据库；前端会保存当前会话 id，用于页面刷新后恢复对话。后续接入 LangGraph checkpointer 后，可继续复用当前 `thread_id`。

## 创建会话

- 路径：`POST /api/v1/conversations`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：创建一个绑定 `love_master_agent` 的恋爱咨询会话。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `agent_key` | `string` | 否 | `love_master_agent` | 当前仅支持 `love_master_agent`。 |
| `title` | `string | null` | 否 | `恋爱咨询` | 会话标题。 |

### 成功响应

```json
{
  "conversation_id": "conv_6f0b...",
  "thread_id": "thread_12ab...",
  "agent_key": "love_master_agent",
  "title": "暧昧推进",
  "memory_namespace": "agent.love_master"
}
```

### 错误响应

```json
{
  "detail": "当前仅支持 love_master_agent 会话。"
}
```

## 获取会话列表

- 路径：`GET /api/v1/conversations`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：获取当前可恢复的会话列表，按更新时间倒序返回。

### 成功响应

```json
{
  "conversations": [
    {
      "conversation_id": "conv_6f0b...",
      "thread_id": "thread_12ab...",
      "agent_key": "love_master_agent",
      "title": "暧昧推进",
      "memory_namespace": "agent.love_master",
      "memory_summary": "用户当前关系阶段可能是暧昧期。"
    }
  ]
}
```

## 获取会话详情

- 路径：`GET /api/v1/conversations/{conversation_id}`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：页面刷新后根据本地保存的 `conversation_id` 恢复会话元信息和记忆摘要。

### 成功响应

```json
{
  "conversation_id": "conv_6f0b...",
  "thread_id": "thread_12ab...",
  "agent_key": "love_master_agent",
  "title": "暧昧推进",
  "memory_namespace": "agent.love_master",
  "memory_summary": "用户当前关系阶段可能是暧昧期。"
}
```

### 常见错误

| 状态码 | `detail` | 说明 |
|---|---|---|
| `404` | `会话不存在。` | `conversation_id` 不存在或已被删除。 |

## 发送消息

- 路径：`POST /api/v1/conversations/{conversation_id}/messages`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：向指定会话发送一条用户消息，并返回 AI 恋爱大师回复。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `content` | `string` | 是 | 无 | 用户本轮恋爱问题或需要润色的消息。 |

### 成功响应

```json
{
  "conversation_id": "conv_6f0b...",
  "user_message": {
    "message_id": "msg_1",
    "role": "user",
    "content": "我和她暧昧两个月了，想推进关系但怕太主动。",
    "safety_flags": []
  },
  "assistant_message": {
    "message_id": "msg_2",
    "role": "assistant",
    "content": "你现在的难点是想推进暧昧关系...",
    "safety_flags": []
  },
  "memory_summary": "用户当前关系阶段可能是暧昧期。",
  "safety_flags": []
}
```

### 安全转向响应示例

当用户请求跟踪、监视、骚扰、操控、报复等行为时，接口仍返回 `201`，但助手消息会转向边界和安全建议：

```json
{
  "conversation_id": "conv_6f0b...",
  "user_message": {
    "message_id": "msg_1",
    "role": "user",
    "content": "教我怎么跟踪她下班。",
    "safety_flags": []
  },
  "assistant_message": {
    "message_id": "msg_2",
    "role": "assistant",
    "content": "我不能帮助你跟踪、监视、骚扰或操控对方...",
    "safety_flags": ["unsafe_control_or_harassment"]
  },
  "memory_summary": "",
  "safety_flags": ["unsafe_control_or_harassment"]
}
```

### 常见错误

| 状态码 | `detail` | 说明 |
|---|---|---|
| `404` | `会话不存在。` | `conversation_id` 不存在或已被删除。 |
| `422` | FastAPI 校验错误 | `content` 为空或请求体格式不正确。 |

## 生成恋爱报告

- 路径：`POST /api/v1/conversations/{conversation_id}/love-report`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：基于当前会话历史和 `memory_summary` 生成结构化恋爱报告。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `focus` | `string | null` | 否 | `null` | 报告分析重点，例如“推进关系”。最长 80 字符。 |
| `style` | `string | null` | 否 | `null` | 报告表达风格，例如“温和直接”。最长 80 字符。 |

### 成功响应

```json
{
  "conversation_id": "conv_6f0b...",
  "report": {
    "report_title": "暧昧期推进分析报告",
    "relationship_stage": "暧昧期",
    "user_goal": "希望推进关系，但担心显得太主动。",
    "situation_summary": "用户和对方暧昧两个月，正在寻找低压力推进方式。",
    "positive_signals": ["关系已经持续互动两个月"],
    "risk_signals": ["用户担心节奏过快"],
    "emotional_needs": ["需要确定感"],
    "next_steps": ["先用轻量邀约测试对方投入度"],
    "communication_script": "这周有个地方我觉得你会喜欢，要不要一起去？",
    "questions_to_clarify": ["你们最近一次单独互动是什么时候？"],
    "memory_candidates": [
      {
        "type": "relationship_stage",
        "content": "用户当前关系阶段可能是暧昧期。",
        "confidence": 0.9,
        "requires_user_consent": true
      }
    ],
    "safety_flags": [],
    "confidence": 0.78
  },
  "memory_summary": "用户当前关系阶段可能是暧昧期。",
  "safety_flags": []
}
```

### 常见错误

| 状态码 | `detail` | 说明 |
|---|---|---|
| `400` | `请先发送至少一条消息，再生成恋爱报告。` | 当前会话还没有任何消息。 |
| `400` | `报告偏好包含安全风险。` | `focus` 或 `style` 命中安全拦截。 |
| `404` | `会话不存在。` | `conversation_id` 不存在或已被删除。 |
| `422` | FastAPI 校验错误 | 请求体格式不正确，或字段超出长度限制。 |

## 获取会话消息

- 路径：`GET /api/v1/conversations/{conversation_id}/messages`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：获取指定会话的用户和助手消息列表。

### 成功响应

```json
{
  "conversation_id": "conv_6f0b...",
  "memory_summary": "用户当前关系阶段可能是暧昧期。",
  "messages": [
    {
      "message_id": "msg_1",
      "role": "user",
      "content": "我和她暧昧两个月了，想推进关系但怕太主动。",
      "safety_flags": []
    },
    {
      "message_id": "msg_2",
      "role": "assistant",
      "content": "你现在的难点是想推进暧昧关系...",
      "safety_flags": []
    }
  ]
}
```

## 前端 TypeScript 类型建议

```ts
type ConversationRole = 'user' | 'assistant'

interface ConversationMessage {
  messageId: string
  role: ConversationRole
  content: string
  safetyFlags: string[]
}

interface LoveConversation {
  conversationId: string
  threadId: string
  agentKey: 'love_master_agent'
  title: string
  memoryNamespace: 'agent.love_master'
  memorySummary: string
}

interface LoveConversationMessageResult {
  conversationId: string
  userMessage: ConversationMessage
  assistantMessage: ConversationMessage
  memorySummary: string
  safetyFlags: string[]
}

interface LoveConversationMessagesResult {
  conversationId: string
  memorySummary: string
  messages: ConversationMessage[]
}

interface LoveReport {
  reportTitle: string
  relationshipStage: string
  userGoal: string
  situationSummary: string
  positiveSignals: string[]
  riskSignals: string[]
  emotionalNeeds: string[]
  nextSteps: string[]
  communicationScript: string
  questionsToClarify: string[]
  confidence: number
  safetyFlags: string[]
}

interface LoveReportResult {
  conversationId: string
  report: LoveReport
  memorySummary: string
  safetyFlags: string[]
}

interface LoveReportOptions {
  focus?: string
  style?: string
}
```

## 特殊行为说明

- 多轮记忆：当前通过同一会话内的 `memory_summary` 保存关系阶段摘要，例如“用户当前关系阶段可能是暧昧期”。摘要会持久化到数据库，服务重启后仍可继续使用。
- 前端恢复：聊天工作台会把当前 `conversation_id` 写入 `localStorage.ai-agent.love-master.current-conversation-id`，刷新页面时读取会话详情和历史消息；如果恢复阶段后端返回 `404`，前端会清理本地会话 id；如果发送消息阶段遇到旧会话 `404`，前端会清理旧会话、自动创建新会话并重试本次消息一次。
- 记忆隔离：AI 恋爱大师只使用 `agent.love_master` 命名空间，不读取其他智能体记忆。
- 安全边界：接口已接入通用 AI Guardrails，用户输入和模型输出都会经过安全拦截。
- 结构化输出降级：聊天回复和恋爱报告会优先通过通用 `ChatModelClient.generate_structured(...)` 生成并由 Pydantic schema 校验；如果模型服务不支持结构化输出，或 JSON fallback 仍返回不可解析内容，服务端会降级为普通回复或规则报告，避免接口 500。
- 输入拦截：prompt injection、请求泄露系统提示词或密钥、跟踪、监视、骚扰、操控、报复等请求不会进入大模型，会直接返回安全提示。
- 输出拦截：模型输出如果包含系统提示词泄露、疑似密钥、骚扰操控建议等内容，会被安全替换或脱敏后再保存和返回。
- 脱敏行为：手机号、邮箱、API key、token、`sk-*` 等疑似敏感信息会被替换为 `[已脱敏...]`。
- 登录态：当前尚未接入用户系统、CSRF、会员额度、软删除或审计日志。后续接入后需要补充用户隔离、会话归属和审计字段。
- 持久化限制：当前业务会话已落库，但尚未接入用户登录态和租户隔离；生产版本需要补充会话归属、权限过滤、软删除和审计日志。LangGraph/Redis checkpoint 仍属于后续 Agent Runtime 持久化能力。
