import { apiGet, apiPost } from '@/shared/api/http'

const CURRENT_LOVE_CONVERSATION_ID_KEY = 'ai-agent.love-master.current-conversation-id'

export interface ConversationMessage {
  messageId: string
  role: 'user' | 'assistant'
  content: string
  safetyFlags: string[]
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

function mapMessage(message: MessageDto): ConversationMessage {
  return {
    messageId: message.message_id,
    role: message.role,
    content: message.content,
    safetyFlags: message.safety_flags,
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
