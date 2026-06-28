# 知识库接口

当前知识库接口用于 AI 恋爱大师默认 RAG 知识库的本地文档入库和检索调试。知识库元数据、文档和 chunk 写入业务数据库，chunk embedding 会写入向量存储；本地开发在 Qdrant 不可用时会使用内存向量兜底，避免阻断验证。

## 获取默认知识库

- 路径：`GET /api/v1/knowledge-bases/love-master-default`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：返回 AI 恋爱大师默认知识库信息；如果不存在会自动创建。

### 成功响应

```json
{
  "knowledge_base_id": "kb_love_master_default",
  "name": "AI 恋爱大师默认知识库",
  "domain": "love_relationship",
  "status": "active"
}
```

## 写入 Markdown 文档

- 路径：`POST /api/v1/knowledge-bases/love-master-default/documents`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：写入一篇 Markdown 知识卡片，服务端会解析 frontmatter、按标题和段落切块、生成 embedding，并写入向量存储。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `source_uri` | `string` | 是 | 无 | 文档来源标识，可使用 `local://...`。 |
| `markdown` | `string` | 是 | 无 | 带 frontmatter 的 Markdown 知识卡片。 |

### Markdown frontmatter 建议

```yaml
---
title: 暧昧期低压力邀约原则
relationship_stage: ambiguous
primary_category: meeting_dating
topic_tags:
  - communication
  - boundaries
intent_tags:
  - strategy
  - script
safety_level: normal
source_urls:
  - https://www.loveisrespect.org/resources/creating-boundaries-in-romantic-relationships/
---
```

### 成功响应

```json
{
  "document_id": "doc_...",
  "knowledge_base_id": "kb_love_master_default",
  "title": "暧昧期低压力邀约原则",
  "source_uri": "local://love-master/curated/ambiguous_invitation.md",
  "status": "indexed",
  "chunk_count": 2
}
```

## 查看已入库文档和切片

- 路径：`GET /api/v1/knowledge-bases/love-master-default/documents`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：用业务语义查看已经入库的原始知识文档和切割后的 chunk。相比直接查询 Qdrant point，该接口会按文档聚合 chunk，并展示标题、来源、元数据、正文、token 数和 `qdrant_point_id`。

### 成功响应

```json
{
  "knowledge_base_id": "kb_love_master_default",
  "document_count": 2,
  "chunk_count": 4,
  "documents": [
    {
      "document_id": "doc_...",
      "knowledge_base_id": "kb_love_master_default",
      "title": "暧昧期低压力邀约原则",
      "source_type": "markdown",
      "source_uri": "local://love-master/curated/ambiguous_invitation.md",
      "version": "v1",
      "status": "indexed",
      "metadata": {
        "relationship_stage": "ambiguous",
        "primary_category": "meeting_dating",
        "topic_tags": ["communication", "boundaries", "invitation"],
        "intent_tags": ["strategy", "script"],
        "safety_level": "normal"
      },
      "chunks": [
        {
          "chunk_id": "chunk_...",
          "chunk_index": 1,
          "title": "暧昧期低压力邀约原则",
          "title_path": "暧昧期低压力邀约原则 / 核心原则",
          "content": "标题：暧昧期低压力邀约原则\n章节：...",
          "token_count": 64,
          "qdrant_point_id": "11bd2f05-c173-53ef-8bf2-be75e3dcf68a",
          "status": "indexed",
          "metadata": {
            "relationship_stage": "ambiguous",
            "primary_category": "meeting_dating",
            "safety_level": "normal"
          }
        }
      ]
    }
  ]
}
```

## 重建默认知识库索引

- 路径：`POST /api/v1/knowledge-bases/love-master-default/documents/reindex`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：重新确保默认知识库存在、重新扫描项目内 Markdown 资料，并对项目内 `curated/` 和 `collected/` 文档执行强制重切。服务会按 `source_uri` 或 `source_hash` 找到历史文档，删除旧 chunk 和旧 Qdrant point，再按当前切片策略重新写入 chunk 与向量。适合切片策略变更、Qdrant 刚启动、collection 被清空、或新增本地资料后手动刷新索引。

### 成功响应

```json
{
  "knowledge_base_id": "kb_love_master_default",
  "collection_name": "ai_agent_dev_love_master_v1",
  "document_count": 34,
  "chunk_count": 34
}
```

## 查看资料来源清单

- 路径：`GET /api/v1/knowledge-bases/love-master-default/sources`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：按资料维度查看来源 URL、审核状态、主分类、关系阶段、安全等级和切片数量，用于人工巡检资料覆盖面。

### 成功响应

```json
{
  "knowledge_base_id": "kb_love_master_default",
  "source_count": 1,
  "sources": [
    {
      "document_id": "doc_...",
      "title": "数字边界沟通原则",
      "source_uri": "local://love-master/curated/safety_boundaries/digital_boundaries.md",
      "source_urls": [
        "https://www.loveisrespect.org/resources/creating-boundaries-in-romantic-relationships/"
      ],
      "source_type": "markdown",
      "review_status": "reviewed",
      "primary_category": "safety_boundaries",
      "relationship_stage": "general",
      "safety_level": "normal",
      "chunk_count": 2
    }
  ]
}
```

## 采集 URL 并整理入库

- 路径：`POST /api/v1/knowledge-bases/love-master-default/sources/collect`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：抓取一个网页 URL，提取标题、摘要和正文段落，整理成统一 Markdown 知识卡片，再复用 Markdown 入库流程完成切块、embedding 和向量写入。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `source_url` | `string` | 是 | 无 | 需要采集的网页地址。 |
| `title` | `string | null` | 否 | 网页标题 | 手动覆盖知识卡片标题。 |
| `relationship_stage` | `string | null` | 否 | 自动推断 | 关系阶段，例如 `general`、`ambiguous`、`conflict`、`breakup`、`marriage`。 |
| `primary_category` | `string | null` | 否 | 自动推断 | 主分类，例如 `safety_boundaries`、`meeting_dating`、`conflict_repair`。 |
| `topic_tags` | `string[]` | 否 | `[]` | 主题标签，例如 `boundaries`、`communication`。 |
| `intent_tags` | `string[]` | 否 | `[]` | 意图标签，例如 `explain`、`strategy`、`script`。 |
| `safety_level` | `string` | 否 | `normal` | 安全等级，`blocked` 内容不会进入聊天回答证据。 |

### 成功响应

```json
{
  "source_url": "https://example.com/healthy-boundaries",
  "markdown_path": "./knowledge/love_master/collected/example-com-healthy-boundaries-0f3a....md",
  "markdown": "---\ntitle: Healthy boundaries\n...",
  "document": {
    "document_id": "doc_...",
    "knowledge_base_id": "kb_love_master_default",
    "title": "Healthy boundaries",
    "source_uri": "https://example.com/healthy-boundaries",
    "status": "indexed",
    "chunk_count": 3
  }
}
```

## 批量采集 URL 并整理入库

- 路径：`POST /api/v1/knowledge-bases/love-master-default/sources/batch-collect`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：一次提交 1-20 个 URL 采集任务，服务端逐条抓取、整理 Markdown、沉淀到 `collected/` 并入库。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `sources` | `KnowledgeSourceCollectRequest[]` | 是 | 无 | 每项字段与单 URL 采集接口一致，数量范围 1-20。 |

### 成功响应

```json
{
  "collected_count": 2,
  "sources": [
    {
      "source_url": "https://example.com/digital-boundaries",
      "markdown_path": "./knowledge/love_master/collected/example-com-digital-boundaries-....md",
      "markdown": "---\ntitle: Digital boundaries\n...",
      "document": {
        "document_id": "doc_...",
        "knowledge_base_id": "kb_love_master_default",
        "title": "Digital boundaries",
        "source_uri": "https://example.com/digital-boundaries",
        "status": "indexed",
        "chunk_count": 2
      }
    }
  ]
}
```

## 检索调试

- 路径：`POST /api/v1/knowledge-bases/love-master-default/query`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：调试 AI 恋爱大师知识库召回效果；正式聊天接口会自动调用检索，不要求前端或用户手动选择目录。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `query` | `string` | 是 | 无 | 用户问题或检索语句。 |
| `limit` | `integer | null` | 否 | `RAG_FINAL_TOP_N` | 最大返回证据数量，范围 1-20。 |

### 成功响应

```json
{
  "knowledge_used": true,
  "evidence": [
    {
      "chunk_id": "chunk_...",
      "document_id": "doc_...",
      "knowledge_base_id": "kb_love_master_default",
      "title": "暧昧期低压力邀约原则",
      "source_uri": "local://love-master/curated/ambiguous_invitation.md",
      "content": "标题：暧昧期低压力邀约原则...",
      "score": 0.82,
      "relationship_stage": "ambiguous",
      "primary_category": "meeting_dating",
      "topic_tags": ["communication", "boundaries"],
      "intent_tags": ["strategy", "script"],
      "safety_level": "normal"
    }
  ],
  "citations": [
    {
      "chunk_id": "chunk_...",
      "title": "暧昧期低压力邀约原则",
      "source_uri": "local://love-master/curated/ambiguous_invitation.md",
      "score": 0.82
    }
  ]
}
```

## 查看召回调试详情

- 路径：`GET /api/v1/knowledge-bases/love-master-default/retrieval-debug`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：查看服务端对自然语言问题的自动分类、实际召回证据和引用，供调试知识切片、分类过滤和向量召回质量使用。

### Query 参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `query` | `string` | 是 | 无 | 用户问题或检索语句。 |
| `limit` | `integer | null` | 否 | `RAG_FINAL_TOP_N` | 最大返回证据数量，范围 1-20。 |

### 成功响应

```json
{
  "query": "如何沟通手机隐私？",
  "classification": {
    "relationship_stage": "general",
    "primary_category": "safety_boundaries"
  },
  "knowledge_used": true,
  "candidate_count": 2,
  "selected_evidence": [
    {
      "chunk_id": "chunk_...",
      "document_id": "doc_...",
      "knowledge_base_id": "kb_love_master_default",
      "title": "数字边界沟通原则",
      "source_uri": "local://love-master/curated/safety_boundaries/digital_boundaries.md",
      "content": "亲密关系不等于放弃隐私...",
      "score": 0.91,
      "relationship_stage": "general",
      "primary_category": "safety_boundaries",
      "topic_tags": ["privacy", "boundaries"],
      "intent_tags": ["strategy"],
      "safety_level": "normal"
    }
  ],
  "citations": [
    {
      "chunk_id": "chunk_...",
      "title": "数字边界沟通原则",
      "source_uri": "local://love-master/curated/safety_boundaries/digital_boundaries.md",
      "score": 0.91
    }
  ]
}
```

## 运行检索评估

- 路径：`POST /api/v1/knowledge-bases/love-master-default/retrieval-evaluations`
- 权限：当前项目尚未接入登录态，暂不校验用户权限。
- 用途：用一个问题、期望命中的标题和禁止命中的标题验证召回质量，适合作为人工维护知识卡片后的快速回归检查。

### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `query` | `string` | 是 | 无 | 需要评估的用户问题。 |
| `expected_titles` | `string[]` | 否 | `[]` | 至少应命中的知识标题，全部命中才算通过该项。 |
| `forbidden_titles` | `string[]` | 否 | `[]` | 不应命中的知识标题，命中任一项即失败。 |
| `limit` | `integer | null` | 否 | `RAG_FINAL_TOP_N` | 最大返回证据数量，范围 1-20。 |

### 成功响应

```json
{
  "query": "如何沟通手机隐私？",
  "passed": true,
  "matched_expected_titles": ["数字边界沟通原则"],
  "missing_expected_titles": [],
  "forbidden_title_hits": [],
  "retrieved_titles": ["数字边界沟通原则"],
  "result": {
    "knowledge_used": true,
    "evidence": [],
    "citations": []
  }
}
```

## TypeScript 类型建议

```ts
interface KnowledgeBase {
  knowledgeBaseId: string
  name: string
  domain: 'love_relationship'
  status: 'active' | 'disabled'
}

interface KnowledgeDocument {
  documentId: string
  knowledgeBaseId: string
  title: string
  sourceUri: string
  status: 'indexed' | 'failed' | 'deleted'
  chunkCount: number
}

interface KnowledgeChunkReadable {
  chunkId: string
  chunkIndex: number
  title: string
  titlePath: string
  content: string
  tokenCount: number
  qdrantPointId?: string
  status: 'indexed' | 'pending' | 'failed' | 'deleted'
  metadata: Record<string, unknown>
}

interface KnowledgeDocumentReadable {
  documentId: string
  knowledgeBaseId: string
  title: string
  sourceType: string
  sourceUri: string
  version: string
  status: 'indexed' | 'indexing' | 'failed' | 'deleted'
  metadata: Record<string, unknown>
  chunks: KnowledgeChunkReadable[]
}

interface KnowledgeDocumentsReadableResponse {
  knowledgeBaseId: string
  documentCount: number
  chunkCount: number
  documents: KnowledgeDocumentReadable[]
}

interface KnowledgeCollectedSource {
  sourceUrl: string
  markdownPath: string
  markdown: string
  document: KnowledgeDocument
}

interface KnowledgeSourceReadable {
  documentId: string
  title: string
  sourceUri: string
  sourceUrls: string[]
  sourceType: string
  reviewStatus: 'draft' | 'reviewed' | 'rejected'
  primaryCategory: string
  relationshipStage: string
  safetyLevel: 'normal' | 'sensitive' | 'crisis' | 'blocked'
  chunkCount: number
}

interface KnowledgeReindexResult {
  knowledgeBaseId: string
  collectionName: string
  documentCount: number
  chunkCount: number
}

interface KnowledgeEvidence {
  chunkId: string
  documentId: string
  knowledgeBaseId: string
  title: string
  sourceUri: string
  content: string
  score: number
  relationshipStage?: string
  primaryCategory?: string
  topicTags: string[]
  intentTags: string[]
  safetyLevel: 'normal' | 'sensitive' | 'crisis' | 'blocked'
}

interface KnowledgeQueryResult {
  knowledgeUsed: boolean
  evidence: KnowledgeEvidence[]
  citations: Array<{
    chunkId: string
    title: string
    sourceUri: string
    score: number
  }>
}

interface KnowledgeRetrievalDebugResult {
  query: string
  classification: {
    relationshipStage?: string
    primaryCategory?: string
    [key: string]: unknown
  }
  knowledgeUsed: boolean
  candidateCount: number
  selectedEvidence: KnowledgeEvidence[]
  citations: KnowledgeQueryResult['citations']
}

interface KnowledgeRetrievalEvaluationResult {
  query: string
  passed: boolean
  matchedExpectedTitles: string[]
  missingExpectedTitles: string[]
  forbiddenTitleHits: string[]
  retrievedTitles: string[]
  result: KnowledgeQueryResult
}
```

## 特殊行为说明

- 默认知识库：服务启动时会确保 `kb_love_master_default` 存在，并优先从 `KNOWLEDGE_DOCUMENTS_PATH/curated/` 和 `KNOWLEDGE_DOCUMENTS_PATH/collected/` 读取项目内 Markdown 知识卡片；当前项目已在 `backend/knowledge/love_master/curated/` 沉淀 34 份资料，覆盖关系基础、沟通、边界安全、约会推进、冲突修复、信任嫉妒、亲密节奏、长期承诺、分手恢复、风险安全和异地关系。
- URL 采集：当前使用后端标准库抓取 HTML，过滤 `script`、`style`、`nav`、`header`、`footer` 等噪声节点，提取 `title`、`meta description`、标题、段落和列表项并整理为 Markdown 知识卡片。
- 文档沉淀：人工整理资料放在 `KNOWLEDGE_DOCUMENTS_PATH/curated/`；URL 采集整理出的 Markdown 知识卡片会写入 `KNOWLEDGE_DOCUMENTS_PATH/collected/`，默认本地路径为 `backend/knowledge/love_master/collected/`，便于人工审核后提交到 Git。
- 采集限制：当前不执行 JavaScript 渲染，不处理需要登录或强反爬的网站；抓取超时由 `KNOWLEDGE_COLLECTION_TIMEOUT_SECONDS` 控制，单页整理长度由 `KNOWLEDGE_COLLECTION_MAX_CHARS` 控制。
- 切片策略：Markdown 会先按标题识别章节；短章节会自动与相邻章节合并，避免“适用场景”“核心原则”“步骤”“话术”被拆成过短的孤立句子。
- 历史切片迁移：调用重建索引接口时，项目内 Markdown 对应的历史短 chunk 会从业务数据库删除，对应 Qdrant point 也会按 `document_id` 删除，然后按当前切片策略重新生成。
- 元数据过滤：检索会固定过滤 `tenant_id=default`、`project_id=default`、`agent_key=love_master_agent`、`active=true` 和默认知识库 id。
- 安全过滤：`safety_level=blocked` 的 chunk 不会进入回答证据。
- 上下文扩展：检索命中某个 chunk 后，会从业务数据库补充同一文档的相邻 chunk 作为 evidence 上下文；向量召回仍看命中片段，发送给 LLM 时给更完整的同文档语境。
- 去重截断：同一文档默认只取最相关 chunk，并受 `RAG_FINAL_TOP_N` 和 `RAG_CONTEXT_MAX_CHARS` 控制。
- Qdrant 兜底：本地开发如果 Qdrant 不可用，服务会使用内存向量存储完成测试；生产环境应使用真实 Qdrant 服务，并确保 embedding 维度与 collection 保持一致。
- 登录态：当前尚未接入用户系统、CSRF、会员额度、软删除或审计日志。后续接入后需要补充租户隔离、知识库归属和操作审计。
