# AI 恋爱大师 RAG 知识库完善设计方案

## 1. 文档信息

- 文档状态：设计方案
- 适用范围：AI 恋爱大师智能体默认 RAG 本地知识库
- 适用模块：
  - `backend/app/modules/knowledge/`
  - `backend/app/modules/conversations/`
  - `backend/app/agents/love_master_agent/`
  - `backend/knowledge/love_master/`
- 相关接口文档：`docs/api/knowledge-bases.md`
- 相关状态文档：`docs/status/love-master-agent-status.md`
- 设计目标：扩展 AI 恋爱大师的恋爱关系知识面，建立可采集、可审核、可入库、可检索、可引用、可持续维护的 RAG 知识库体系。

## 2. 背景与问题

当前 AI 恋爱大师已经具备基础 RAG 能力：

- 支持 Markdown 知识卡片入库。
- 支持 URL 网页采集并整理为 Markdown。
- 支持将 chunk embedding 写入 Qdrant。
- 支持基于用户问题自动检索默认知识库。
- 支持返回 `citations`。
- 支持通过调试接口查看已入库文档和 chunk。

但当前项目内 `backend/knowledge/love_master/curated/` 仅沉淀了少量知识卡片，主要覆盖：

- 暧昧期低压力邀约。
- 冲突后的修复沟通。

这只能支撑本地 smoke 验证，无法覆盖真实用户在恋爱关系中的多样化问题。AI 恋爱大师要稳定回答用户问题，知识库需要从“少量示例卡片”升级为“分层、可审查、可扩展的关系知识体系”。

## 3. 设计目标

### 3.1 用户体验目标

- 用户不需要选择“单身篇、恋爱篇、已婚篇”等目录。
- 用户只需要提出自然语言问题。
- 系统自动识别关系阶段、问题领域、风险等级和回答意图。
- 回答中尽量给出可执行建议、沟通话术、风险提醒和引用来源。
- 当问题涉及安全风险时，优先给安全转向和求助建议，而不是普通恋爱技巧。

### 3.2 知识库目标

- 覆盖单身、认识、暧昧、恋爱、长期关系、婚姻、分手、复合、安全风险等常见场景。
- 每个知识片段都有明确来源、适用场景、元数据和安全等级。
- 支持人工整理资料和 URL 采集资料共同进入知识库。
- 支持后续批量采集、审核、重建索引、版本管理和质量评估。
- 支持 Qdrant payload filter、语义检索、去重、rerank 和引用返回。

### 3.3 工程目标

- 保持智能体解耦：AI 恋爱大师只访问自己的知识库范围。
- 保持目录解耦：资料沉淀在 `backend/knowledge/love_master/`，业务代码在 `backend/app/modules/knowledge/`。
- 保持权限默认拒绝：后续接入用户系统后，知识库必须按租户、项目、智能体和用户权限过滤。
- 保持可测试：采集、切割、入库、检索、引用、安全过滤都需要测试覆盖。

## 4. 非目标

- 不在前端要求用户手动选择知识目录。
- 不把公开网页原文大段复制进知识库。
- 不把心理治疗、法律建议、医疗建议包装成恋爱建议。
- 不提供跟踪、骚扰、操控、报复、胁迫等危险内容。
- 不在第一阶段实现完整知识库后台管理系统。
- 不在第一阶段实现所有格式解析，PDF、登录页面、JavaScript 渲染页面可以后续扩展。

## 5. 总体架构

```text
资料来源
  ├─ 人工整理 Markdown
  ├─ URL 网页采集
  ├─ 后续 PDF / 文档导入
  └─ 后续批量采集任务

资料沉淀目录
  ├─ backend/knowledge/love_master/curated/
  └─ backend/knowledge/love_master/collected/

Knowledge Service
  ├─ 解析 frontmatter
  ├─ 标准化元数据
  ├─ 标题和段落切块
  ├─ 生成 embedding
  ├─ 写入业务数据库
  ├─ 写入 Qdrant
  └─ 提供调试查看接口

Conversation Service
  ├─ 接收用户问题
  ├─ 识别关系阶段和问题领域
  ├─ 检索 RAG 知识库
  ├─ 去重和截断 evidence
  ├─ 注入 LLM
  └─ 返回回答和 citations
```

## 6. 知识主题体系

前端不展示这些分类，但后端知识库必须用这些分类做元数据管理和检索过滤。

### 6.1 关系阶段

| 阶段 | 建议枚举值 | 说明 |
|---|---|---|
| 通用关系 | `general` | 不依赖具体阶段的关系原则、边界、安全提醒。 |
| 单身准备 | `single_preparation` | 自我认知、择偶标准、关系期待、情绪准备。 |
| 认识破冰 | `first_contact` | 开场、聊天、兴趣表达、邀约前信号判断。 |
| 暧昧推进 | `ambiguous` | 低压力邀约、升温、确认关系、模糊关系处理。 |
| 确定关系 | `early_relationship` | 建立关系规则、沟通频率、边界确认。 |
| 稳定恋爱 | `stable_relationship` | 冲突、亲密、信任、长期规划。 |
| 异地恋 | `long_distance` | 见面频率、信任、沟通安排、未来计划。 |
| 同居婚姻 | `marriage` | 家务、金钱、家庭边界、长期承诺。 |
| 分手恢复 | `breakup` | 断联、复盘、恢复、共同好友边界。 |
| 复合评估 | `reconciliation` | 复合条件、风险判断、关系重建。 |
| 安全危机 | `safety_crisis` | 亲密伴侣暴力、控制、威胁、胁迫。 |

### 6.2 问题领域

| 领域 | 建议枚举值 | 覆盖内容 |
|---|---|---|
| 关系基础 | `relationship_basics` | 健康关系、不健康关系、平等、尊重、信任。 |
| 沟通表达 | `communication` | 表达需求、倾听、确认感、非防御回应。 |
| 边界尊重 | `safety_boundaries` | 数字边界、身体边界、情绪边界、金钱边界、隐私边界。 |
| 邀约约会 | `meeting_dating` | 聊天、邀约、约会安排、推进节奏。 |
| 冲突修复 | `conflict_repair` | 道歉、复盘、降温、修复尝试、争吵升级。 |
| 信任嫉妒 | `trust_jealousy` | 不安全感、查手机、社交边界、信任重建。 |
| 亲密关系 | `intimacy` | 亲密沟通、同意、节奏差异、尊重拒绝。 |
| 长期承诺 | `long_term_commitment` | 同居、婚姻、未来规划、家庭系统。 |
| 分手复盘 | `breakup_recovery` | 分手后恢复、复合判断、情绪照顾。 |
| 风险护栏 | `risk_safety` | 控制、跟踪、骚扰、威胁、暴力、危机转介。 |

### 6.3 意图类型

| 意图 | 建议枚举值 | 说明 |
|---|---|---|
| 概念解释 | `explain` | 解释某个关系概念或行为。 |
| 局势判断 | `diagnose` | 判断用户描述中的关系信号和风险。 |
| 行动策略 | `strategy` | 给出下一步处理策略。 |
| 沟通话术 | `script` | 给出可直接参考的话术。 |
| 决策树 | `decision_tree` | 帮用户判断是否继续、表白、分手、复合。 |
| 风险提醒 | `risk_warning` | 提醒边界、安全、操控、暴力等风险。 |
| 情绪支持 | `emotional_support` | 帮用户稳定情绪、降低自责和冲动。 |

### 6.4 安全等级

| 等级 | 建议枚举值 | 处理方式 |
|---|---|---|
| 普通 | `normal` | 可进入普通回答证据。 |
| 敏感 | `sensitive` | 可检索，但回答需要更保守。 |
| 危机 | `crisis` | 优先安全建议、求助资源和离开危险场景。 |
| 禁用 | `blocked` | 不进入回答证据。 |

## 7. 知识卡片规范

### 7.1 Markdown frontmatter

每张知识卡片必须包含结构化元数据：

```yaml
---
title: 数字边界沟通原则
relationship_stage: general
primary_category: safety_boundaries
topic_tags:
  - boundaries
  - communication
  - privacy
intent_tags:
  - explain
  - strategy
  - script
safety_level: normal
evidence_level: authoritative_public
audience: general
locale: zh-CN
content_type: principle
source_urls:
  - https://www.loveisrespect.org/resources/creating-boundaries-in-romantic-relationships/
review_status: reviewed
last_reviewed_at: 2026-06-28
version: v1
---
```

### 7.2 正文结构

正文建议统一使用以下结构：

```markdown
# 数字边界沟通原则

## 适用场景

## 核心原则

## 可执行步骤

## 可参考话术

## 风险提醒

## 来源说明
```

这样切块后，每个 chunk 都更容易保留语义，不会只截出孤立句子。

### 7.3 资料目录

```text
backend/knowledge/love_master/
  README.md
  curated/
    relationship_basics/
    communication/
    safety_boundaries/
    meeting_dating/
    conflict_repair/
    trust_jealousy/
    intimacy/
    long_term_commitment/
    breakup_recovery/
    risk_safety/
  collected/
    pending_review/
    reviewed/
    rejected/
```

第一阶段可以继续使用当前扁平 `curated/*.md`，但当卡片超过 30 篇后，应切换到子目录分组。

## 8. 首批知识库扩展清单

建议第一批扩展到 80 到 120 张知识卡片。优先级如下。

### 8.1 P0 核心安全和边界

| 主题 | 建议卡片 |
|---|---|
| 健康关系 | 健康关系特征、不健康关系特征、关系中的平等与尊重。 |
| 边界 | 数字边界、身体边界、情绪边界、金钱边界、社交边界、隐私边界。 |
| 安全 | 控制行为识别、跟踪骚扰识别、威胁和胁迫、亲密伴侣暴力求助建议。 |
| 同意 | 亲密关系中的同意、拒绝权、压力和胁迫识别。 |

### 8.2 P1 高频恋爱咨询

| 主题 | 建议卡片 |
|---|---|
| 单身准备 | 择偶标准、关系期待、自我价值感、脱单焦虑。 |
| 认识破冰 | 开场聊天、兴趣表达、回复节奏、判断对方投入度。 |
| 暧昧推进 | 低压力邀约、升温节奏、表白时机、模糊关系处理。 |
| 恋爱沟通 | 表达需求、倾听、确认感、沟通频率差异、冷淡回应。 |
| 冲突修复 | 道歉、复盘、暂停争吵、修复尝试、避免升级。 |

### 8.3 P2 长期关系和分手恢复

| 主题 | 建议卡片 |
|---|---|
| 长期关系 | 同居规则、家务分工、金钱观、未来规划、双方家庭边界。 |
| 异地恋 | 联系频率、见面安排、信任维护、长期计划。 |
| 分手恢复 | 断联、情绪恢复、共同好友、社交媒体边界。 |
| 复合评估 | 是否适合复合、问题是否改变、复合沟通、二次伤害预防。 |

## 9. 数据采集和整理流程

### 9.1 资料来源分级

| 等级 | 来源类型 | 用途 |
|---|---|---|
| A 级 | 公共机构、安全教育组织、官方健康关系资料 | 安全护栏、边界、亲密伴侣暴力、危机处理。 |
| B 级 | 关系研究机构、专家方法论 | 沟通、冲突修复、长期关系方法论。 |
| C 级 | 项目原创总结和中文本地化改写 | 话术模板、场景决策树、中文咨询体验优化。 |

### 9.2 采集流程

```text
候选 URL
  -> 抓取网页
  -> 提取正文
  -> 过滤导航和广告噪声
  -> 生成 Markdown 草稿
  -> 人工审核和中文改写
  -> 写入 curated 或 reviewed
  -> 入库切块
  -> 写入业务数据库
  -> 写入 Qdrant
  -> 检索评估
```

### 9.3 采集原则

- 不直接大段搬运网页原文。
- 保留 `source_urls`，回答时可返回 citation。
- 对英文来源应整理成中文知识卡片。
- 安全相关内容优先使用权威来源，不用社交平台帖子作为主证据。
- 每张卡片只解决一个明确问题，避免一篇文档覆盖过多主题。

## 10. 切割、向量化和存储设计

### 10.1 切割策略

当前项目按 Markdown 标题和段落切块，并已加入短章节合并和同文档上下文扩展：

- 短知识卡片优先合并相邻章节，避免“适用场景”“核心原则”“步骤”“话术”被拆成多个一句话 chunk。
- 长章节超过窗口时再按 700 字左右切割，并保留 overlap。
- 检索命中单个 chunk 后，返回给 LLM 的 evidence 会补充同一文档相邻 chunk，形成“小块召回、大块注入”的效果。
- 切片策略升级后，项目内 Markdown 通过重建索引执行迁移：按 `document_id` 删除旧 chunk 与旧 Qdrant point，再按新策略重切和写入向量。
- 对长文资料，每个 chunk 目标长度建议控制在 500 到 900 中文字符。
- chunk overlap：80 到 150 字。
- 每个 chunk 自动补充：
  - 文档标题。
  - 章节路径。
  - 适用阶段。
  - 主分类。
  - 安全等级。
- 对“话术模板”和“风险提醒”不要和普通原则混在同一 chunk。

### 10.2 业务数据库

业务数据库继续作为知识库事实来源：

- `knowledge_bases`：知识库定义。
- `knowledge_documents`：原始 Markdown 文档记录、来源、版本、元数据。
- `knowledge_chunks`：切割后的 chunk、正文、hash、token 数、Qdrant point id。

业务数据库用于：

- 可读调试查看。
- 重建索引。
- 软删除和版本管理。
- 审计和权限过滤。

### 10.3 Qdrant

Qdrant 作为向量检索层，继续存储：

- vector。
- point id。
- payload。

当前 collection 命名规则：

```text
{QDRANT_COLLECTION_PREFIX}_love_master_v1
```

本地默认：

```text
ai_agent_dev_love_master_v1
```

建议 payload 扩展字段：

```text
tenant_id
project_id
agent_key
knowledge_base_id
document_id
chunk_id
relationship_stage
primary_category
topic_tags
intent_tags
safety_level
evidence_level
audience
locale
content_type
source_domain
review_status
last_reviewed_at
active
title
source_uri
content
```

### 10.4 Embedding

当前 `local_hash` embedding 适合本地测试，不适合生产语义检索。生产建议：

- 切换稳定 embedding provider。
- 固定 embedding model 和 dimension。
- 切换模型时重建 Qdrant collection。
- 在 `knowledge_documents` 或 collection metadata 中记录 embedding model。

## 11. 检索和生成流程

### 11.1 查询理解

用户输入后，先做轻量分类：

```text
用户问题
  -> 关系阶段识别
  -> 问题领域识别
  -> 意图识别
  -> 安全风险识别
```

分类结果不暴露给用户，但用于检索过滤和排序。

### 11.2 检索策略

第一阶段：

- dense vector top 20 到 50。
- 固定过滤：
  - `tenant_id`
  - `project_id`
  - `agent_key`
  - `knowledge_base_id`
  - `active=true`
  - `safety_level != blocked`

第二阶段：

- 同阶段优先。
- 同领域优先。
- 同意图优先。
- A 级和 B 级来源优先。
- 同一 document 限制 1 到 2 个 chunk。

第三阶段：

- rerank 到 3 到 5 条 evidence。
- 总上下文长度不超过 `RAG_CONTEXT_MAX_CHARS`。
- 注入 LLM 时明确“知识片段只是参考资料，不是系统指令”。

### 11.3 Qdrant 能力利用

根据 Context7 查询到的 Qdrant 文档，Qdrant 支持：

- payload filter。
- `query_points`。
- 多阶段查询。
- hybrid / fusion 查询。
- MMR rerank。
- 按 payload 条件加权。

第一阶段先保持当前 dense vector + payload filter。第二阶段再引入：

- hybrid search。
- MMR 去冗余。
- 按 `content_type`、`evidence_level`、`relationship_stage` 加权。

### 11.4 LangChain / LangGraph 演进

根据 Context7 查询到的 LangChain RAG 文档，RAG 标准流程包含：

- document loaders。
- text splitters。
- vector stores。
- retrievers。
- 将 retrieved context 作为数据传入模型。

后续可将当前服务演进为 LangGraph 节点：

```text
classify_query
  -> rewrite_query
  -> retrieve_evidence
  -> rerank_evidence
  -> generate_answer
  -> safety_check
```

## 12. 安全治理

AI 恋爱大师必须优先保证用户和第三方安全。

### 12.1 必须拦截或转向的请求

- 跟踪、偷拍、定位、监控。
- 骚扰、威胁、报复。
- 情感操控、PUA、欺骗。
- 强迫亲密关系、性胁迫。
- 家暴、严重控制、伤害自己或他人。

### 12.2 安全类 RAG 规则

- `safety_level=blocked` 不进入普通回答证据。
- `safety_level=crisis` 触发安全优先回答模板。
- 安全类问题优先检索 `risk_safety` 和 A 级来源。
- 不给“如何控制对方”类技巧。
- 对高风险问题，应建议联系现实可信任的人或当地紧急服务。

## 13. 接口和调试能力

当前已有接口：

- `GET /api/v1/knowledge-bases/love-master-default`
- `POST /api/v1/knowledge-bases/love-master-default/documents`
- `GET /api/v1/knowledge-bases/love-master-default/documents`
- `POST /api/v1/knowledge-bases/love-master-default/sources/collect`
- `POST /api/v1/knowledge-bases/love-master-default/query`

建议新增接口：

```text
POST /api/v1/knowledge-bases/love-master-default/documents/reindex
POST /api/v1/knowledge-bases/love-master-default/sources/batch-collect
GET  /api/v1/knowledge-bases/love-master-default/sources
GET  /api/v1/knowledge-bases/love-master-default/retrieval-debug
POST /api/v1/knowledge-bases/love-master-default/retrieval-evaluations
```

调试页面建议展示：

- 文档列表。
- chunk 列表。
- 元数据筛选。
- Qdrant point id。
- 输入 query 后展示召回顺序、score、过滤原因、最终注入 evidence。

## 14. 质量评估

### 14.1 知识覆盖评估

每个主题至少有：

- 1 张原则卡片。
- 1 张行动步骤卡片。
- 1 张话术模板卡片。
- 1 张风险提醒卡片。

### 14.2 检索评估

建立 golden query 集合：

```text
暧昧两个月怎么推进？
她总是不回消息是不是不喜欢我？
吵架后怎么道歉？
对象要查我手机怎么办？
分手后还要不要复合？
对方威胁我怎么办？
```

每条 golden query 记录：

- 期望召回文档。
- 不应召回文档。
- 期望安全等级。
- 期望回答方向。

### 14.3 回答质量评估

评估维度：

- 是否回答了用户问题。
- 是否引用了合适证据。
- 是否避免过度确定。
- 是否提供可执行步骤。
- 是否有合适话术。
- 是否识别安全风险。
- 是否避免操控和伤害。

## 15. 实施计划

### 15.1 第一批：知识面扩充

- 新增 30 张 `curated` 知识卡片。
- 覆盖关系基础、边界、沟通、暧昧、冲突、分手、安全。
- 每张卡片统一 frontmatter 和正文结构。
- 补充入库测试和检索 smoke。

### 15.2 第二批：采集和审核流程

- 支持批量 URL 采集。
- 增加 `review_status`。
- 将 `collected/` 分为 `pending_review`、`reviewed`、`rejected`。
- 支持重新入库和重建索引。

### 15.3 第三批：检索增强

- 增强 query classification。
- 增加 payload boost。
- 增加 MMR 去冗余。
- 引入生产 embedding provider。
- 增加 retrieval debug 接口。

### 15.4 第四批：管理页面和评估

- 增加知识库调试页面。
- 增加检索评估集。
- 增加知识质量评分。
- 增加版本回滚和软删除审计。

## 16. 风险和约束

| 风险 | 说明 | 应对 |
|---|---|---|
| 知识来源质量不稳定 | 网页内容可能营销化或缺乏证据 | 来源分级，安全类优先权威来源。 |
| 版权风险 | 直接复制网页原文可能不合适 | 只保留要点和原创中文整理，保留来源链接。 |
| 检索误召回 | 用户问题复杂时可能召回错阶段内容 | 加强元数据、query classification 和 rerank。 |
| 安全风险 | 用户可能提出操控、威胁、跟踪请求 | Guardrails + `safety_level` + 风险类知识优先。 |
| embedding 迁移 | 切换模型会导致旧向量不可比 | collection 版本化，重建索引。 |
| 资料过期 | 外部关系教育资料可能更新 | 增加 `last_reviewed_at` 和定期审核。 |

## 17. 外部参考

- Qdrant 文档：payload filter、query points、多阶段查询、hybrid/fusion、MMR rerank，参考 [Qdrant API Reference](https://api.qdrant.tech/) 和 [Qdrant Documentation](https://qdrant.tech/documentation/)。
- LangChain 文档：RAG loaders、text splitters、retriever、retrieved context 作为数据而不是指令，参考 [LangChain RAG](https://docs.langchain.com/oss/python/langchain/rag)。
- love is respect：健康关系、边界、数字边界和安全关系教育资料，参考 [Creating Boundaries in Romantic Relationships](https://www.loveisrespect.org/resources/creating-boundaries-in-romantic-relationships/)。
- Gottman Institute：冲突修复、修复尝试、关系沟通方法论，参考 [R is for Repair](https://www.gottman.com/blog/r-is-for-repair/) 和 [The Four Horsemen: The Antidotes](https://www.gottman.com/blog/the-four-horsemen-the-antidotes/)。
- CDC：亲密伴侣暴力、关系安全和风险识别资料，参考 [About Intimate Partner Violence](https://www.cdc.gov/intimate-partner-violence/about/index.html)。
