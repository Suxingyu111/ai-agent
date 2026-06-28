import { apiGet, apiPost } from '@/shared/api/http'

const CURRENT_LOVE_CONVERSATION_ID_KEY = 'ai-agent.love-master.current-conversation-id'

export interface ConversationMessage {
  messageId: string
  role: 'user' | 'assistant'
  content: string
  safetyFlags: string[]
  citations: KnowledgeCitation[]
}

export interface KnowledgeCitation {
  chunkId: string
  title: string
  sourceUri: string
  score: number
}

export interface KnowledgeChunk {
  chunkId: string
  chunkIndex: number
  title: string
  titlePath: string
  content: string
  tokenCount: number
  qdrantPointId: string | null
  status: string
  metadata: Record<string, unknown>
}

export interface KnowledgeDocument {
  documentId: string
  knowledgeBaseId: string
  title: string
  sourceType: string
  sourceUri: string
  version: string
  status: string
  metadata: Record<string, unknown>
  chunks: KnowledgeChunk[]
}

export interface KnowledgeDocumentsResult {
  knowledgeBaseId: string
  documentCount: number
  chunkCount: number
  documents: KnowledgeDocument[]
}

export interface KnowledgeEvidence {
  chunkId: string
  documentId: string
  knowledgeBaseId: string
  title: string
  sourceUri: string
  content: string
  score: number
  relationshipStage: string | null
  primaryCategory: string | null
  topicTags: string[]
  intentTags: string[]
  safetyLevel: string
}

export interface KnowledgeRetrievalDebugResult {
  query: string
  classification: {
    relationshipStage?: string
    primaryCategory?: string
    [key: string]: unknown
  }
  knowledgeUsed: boolean
  candidateCount: number
  selectedEvidence: KnowledgeEvidence[]
  citations: KnowledgeCitation[]
}

export interface KnowledgeReindexResult {
  knowledgeBaseId: string
  collectionName: string
  documentCount: number
  chunkCount: number
}

export interface KnowledgeRetrievalEvaluationOptions {
  query: string
  expectedTitles: string[]
  forbiddenTitles: string[]
  limit?: number
}

export interface KnowledgeRetrievalEvaluationResult {
  query: string
  passed: boolean
  matchedExpectedTitles: string[]
  missingExpectedTitles: string[]
  forbiddenTitleHits: string[]
  retrievedTitles: string[]
  result: {
    knowledgeUsed: boolean
    evidence: KnowledgeEvidence[]
    citations: KnowledgeCitation[]
  }
}

export interface LoveConversation {
  conversationId: string
  threadId: string
  agentKey: string
  title: string
  memoryNamespace: string
  memorySummary: string
}

export interface LoveConversationMessageResult {
  conversationId: string
  userMessage: ConversationMessage
  assistantMessage: ConversationMessage
  memorySummary: string
  safetyFlags: string[]
  knowledgeUsed: boolean
  citations: KnowledgeCitation[]
}

export interface LoveConversationMessagesResult {
  conversationId: string
  memorySummary: string
  messages: ConversationMessage[]
}

export interface LoveReport {
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

export interface LoveReportResult {
  conversationId: string
  report: LoveReport
  memorySummary: string
  safetyFlags: string[]
}

export interface LoveReportOptions {
  focus?: string
  style?: string
}

interface ConversationResponse {
  conversation_id: string
  thread_id: string
  agent_key: string
  title: string
  memory_namespace: string
  memory_summary?: string
}

interface MessageResponse {
  conversation_id: string
  user_message: MessageDto
  assistant_message: MessageDto
  memory_summary: string
  safety_flags: string[]
  knowledge_used?: boolean
  citations?: CitationDto[]
}

interface MessagesResponse {
  conversation_id: string
  memory_summary: string
  messages: MessageDto[]
}

interface MessageDto {
  message_id: string
  role: 'user' | 'assistant'
  content: string
  safety_flags: string[]
  citations?: CitationDto[]
}

interface CitationDto {
  chunk_id: string
  title: string
  source_uri: string
  score: number
}

interface KnowledgeChunkDto {
  chunk_id: string
  chunk_index: number
  title: string
  title_path: string
  content: string
  token_count: number
  qdrant_point_id?: string | null
  status: string
  metadata: Record<string, unknown>
}

interface KnowledgeDocumentDto {
  document_id: string
  knowledge_base_id: string
  title: string
  source_type: string
  source_uri: string
  version: string
  status: string
  metadata: Record<string, unknown>
  chunks: KnowledgeChunkDto[]
}

interface KnowledgeDocumentsResponse {
  knowledge_base_id: string
  document_count: number
  chunk_count: number
  documents: KnowledgeDocumentDto[]
}

interface KnowledgeEvidenceDto {
  chunk_id: string
  document_id: string
  knowledge_base_id: string
  title: string
  source_uri: string
  content: string
  score: number
  relationship_stage?: string | null
  primary_category?: string | null
  topic_tags: string[]
  intent_tags: string[]
  safety_level: string
}

interface KnowledgeRetrievalDebugResponse {
  query: string
  classification: Record<string, unknown>
  knowledge_used: boolean
  candidate_count: number
  selected_evidence: KnowledgeEvidenceDto[]
  citations: CitationDto[]
}

interface KnowledgeReindexResponse {
  knowledge_base_id: string
  collection_name: string
  document_count: number
  chunk_count: number
}

interface KnowledgeRetrievalEvaluationResponse {
  query: string
  passed: boolean
  matched_expected_titles: string[]
  missing_expected_titles: string[]
  forbidden_title_hits: string[]
  retrieved_titles: string[]
  result: {
    knowledge_used: boolean
    evidence: KnowledgeEvidenceDto[]
    citations: CitationDto[]
  }
}

interface LoveReportResponse {
  conversation_id: string
  report: LoveReportDto
  memory_summary: string
  safety_flags: string[]
}

interface LoveReportDto {
  report_title: string
  relationship_stage: string
  user_goal: string
  situation_summary: string
  positive_signals: string[]
  risk_signals: string[]
  emotional_needs: string[]
  next_steps: string[]
  communication_script: string
  questions_to_clarify: string[]
  safety_flags: string[]
  confidence: number
}

export async function createLoveConversation(title: string): Promise<LoveConversation> {
  const response = await apiPost<ConversationResponse>('/conversations', {
    agent_key: 'love_master_agent',
    title,
  })

  return mapConversation(response)
}

export async function getLoveConversation(conversationId: string): Promise<LoveConversation> {
  return mapConversation(await apiGet<ConversationResponse>(`/conversations/${conversationId}`))
}

export async function getLoveConversationMessages(
  conversationId: string,
): Promise<LoveConversationMessagesResult> {
  const response = await apiGet<MessagesResponse>(`/conversations/${conversationId}/messages`)

  return {
    conversationId: response.conversation_id,
    memorySummary: response.memory_summary,
    messages: response.messages.map(mapMessage),
  }
}

export async function sendLoveConversationMessage(
  conversationId: string,
  content: string,
): Promise<LoveConversationMessageResult> {
  const response = await apiPost<MessageResponse>(`/conversations/${conversationId}/messages`, {
    content,
  })

  return {
    conversationId: response.conversation_id,
    userMessage: mapMessage(response.user_message),
    assistantMessage: mapMessage(response.assistant_message),
    memorySummary: response.memory_summary,
    safetyFlags: response.safety_flags,
    knowledgeUsed: response.knowledge_used ?? false,
    citations: (response.citations ?? []).map(mapCitation),
  }
}

export async function generateLoveReport(
  conversationId: string,
  options: LoveReportOptions = {},
): Promise<LoveReportResult> {
  const response = await apiPost<LoveReportResponse>(
    `/conversations/${conversationId}/love-report`,
    options,
  )

  return {
    conversationId: response.conversation_id,
    report: mapLoveReport(response.report),
    memorySummary: response.memory_summary,
    safetyFlags: response.safety_flags,
  }
}

export async function getLoveMasterKnowledgeDocuments(): Promise<KnowledgeDocumentsResult> {
  const response = await apiGet<KnowledgeDocumentsResponse>(
    '/knowledge-bases/love-master-default/documents',
  )

  return {
    knowledgeBaseId: response.knowledge_base_id,
    documentCount: response.document_count,
    chunkCount: response.chunk_count,
    documents: response.documents.map(mapKnowledgeDocument),
  }
}

export async function getLoveMasterRetrievalDebug(
  query: string,
  limit?: number,
): Promise<KnowledgeRetrievalDebugResult> {
  const params = new URLSearchParams({ query })
  if (limit !== undefined) {
    params.set('limit', String(limit))
  }
  const response = await apiGet<KnowledgeRetrievalDebugResponse>(
    `/knowledge-bases/love-master-default/retrieval-debug?${params.toString()}`,
  )

  return {
    query: response.query,
    classification: mapClassification(response.classification),
    knowledgeUsed: response.knowledge_used,
    candidateCount: response.candidate_count,
    selectedEvidence: response.selected_evidence.map(mapKnowledgeEvidence),
    citations: (response.citations ?? []).map(mapCitation),
  }
}

export async function reindexLoveMasterKnowledgeBase(): Promise<KnowledgeReindexResult> {
  const response = await apiPost<KnowledgeReindexResponse>(
    '/knowledge-bases/love-master-default/documents/reindex',
    {},
  )

  return {
    knowledgeBaseId: response.knowledge_base_id,
    collectionName: response.collection_name,
    documentCount: response.document_count,
    chunkCount: response.chunk_count,
  }
}

export async function runLoveMasterRetrievalEvaluation(
  options: KnowledgeRetrievalEvaluationOptions,
): Promise<KnowledgeRetrievalEvaluationResult> {
  const response = await apiPost<KnowledgeRetrievalEvaluationResponse>(
    '/knowledge-bases/love-master-default/retrieval-evaluations',
    {
      query: options.query,
      expected_titles: options.expectedTitles,
      forbidden_titles: options.forbiddenTitles,
      limit: options.limit,
    },
  )

  return {
    query: response.query,
    passed: response.passed,
    matchedExpectedTitles: response.matched_expected_titles,
    missingExpectedTitles: response.missing_expected_titles,
    forbiddenTitleHits: response.forbidden_title_hits,
    retrievedTitles: response.retrieved_titles,
    result: {
      knowledgeUsed: response.result.knowledge_used,
      evidence: response.result.evidence.map(mapKnowledgeEvidence),
      citations: (response.result.citations ?? []).map(mapCitation),
    },
  }
}

function mapMessage(message: MessageDto): ConversationMessage {
  return {
    messageId: message.message_id,
    role: message.role,
    content: message.content,
    safetyFlags: message.safety_flags,
    citations: (message.citations ?? []).map(mapCitation),
  }
}

function mapCitation(citation: CitationDto): KnowledgeCitation {
  return {
    chunkId: citation.chunk_id,
    title: citation.title,
    sourceUri: citation.source_uri,
    score: citation.score,
  }
}

function mapKnowledgeDocument(document: KnowledgeDocumentDto): KnowledgeDocument {
  return {
    documentId: document.document_id,
    knowledgeBaseId: document.knowledge_base_id,
    title: document.title,
    sourceType: document.source_type,
    sourceUri: document.source_uri,
    version: document.version,
    status: document.status,
    metadata: document.metadata,
    chunks: document.chunks.map(mapKnowledgeChunk),
  }
}

function mapKnowledgeChunk(chunk: KnowledgeChunkDto): KnowledgeChunk {
  return {
    chunkId: chunk.chunk_id,
    chunkIndex: chunk.chunk_index,
    title: chunk.title,
    titlePath: chunk.title_path,
    content: chunk.content,
    tokenCount: chunk.token_count,
    qdrantPointId: chunk.qdrant_point_id ?? null,
    status: chunk.status,
    metadata: chunk.metadata,
  }
}

function mapKnowledgeEvidence(evidence: KnowledgeEvidenceDto): KnowledgeEvidence {
  return {
    chunkId: evidence.chunk_id,
    documentId: evidence.document_id,
    knowledgeBaseId: evidence.knowledge_base_id,
    title: evidence.title,
    sourceUri: evidence.source_uri,
    content: evidence.content,
    score: evidence.score,
    relationshipStage: evidence.relationship_stage ?? null,
    primaryCategory: evidence.primary_category ?? null,
    topicTags: evidence.topic_tags,
    intentTags: evidence.intent_tags,
    safetyLevel: evidence.safety_level,
  }
}

function mapClassification(classification: Record<string, unknown>): KnowledgeRetrievalDebugResult['classification'] {
  return {
    ...classification,
    relationshipStage:
      typeof classification.relationship_stage === 'string'
        ? classification.relationship_stage
        : undefined,
    primaryCategory:
      typeof classification.primary_category === 'string' ? classification.primary_category : undefined,
  }
}

function mapConversation(conversation: ConversationResponse): LoveConversation {
  return {
    conversationId: conversation.conversation_id,
    threadId: conversation.thread_id,
    agentKey: conversation.agent_key,
    title: conversation.title,
    memoryNamespace: conversation.memory_namespace,
    memorySummary: conversation.memory_summary ?? '',
  }
}

function mapLoveReport(report: LoveReportDto): LoveReport {
  return {
    reportTitle: report.report_title,
    relationshipStage: report.relationship_stage,
    userGoal: report.user_goal,
    situationSummary: report.situation_summary,
    positiveSignals: report.positive_signals,
    riskSignals: report.risk_signals,
    emotionalNeeds: report.emotional_needs,
    nextSteps: report.next_steps,
    communicationScript: report.communication_script,
    questionsToClarify: report.questions_to_clarify,
    confidence: report.confidence,
    safetyFlags: report.safety_flags,
  }
}

export function saveCurrentLoveConversationId(conversationId: string): void {
  localStorage.setItem(CURRENT_LOVE_CONVERSATION_ID_KEY, conversationId)
}

export function loadCurrentLoveConversationId(): string | null {
  return localStorage.getItem(CURRENT_LOVE_CONVERSATION_ID_KEY)
}

export function clearCurrentLoveConversationId(): void {
  localStorage.removeItem(CURRENT_LOVE_CONVERSATION_ID_KEY)
}
