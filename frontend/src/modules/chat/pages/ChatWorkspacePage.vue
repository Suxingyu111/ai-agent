<template>
  <section class="chat-workspace">
    <aside class="chat-sidebar" aria-label="会话信息">
      <div>
        <p class="chat-sidebar__eyebrow">AI 恋爱大师</p>
        <h2>情感指导</h2>
        <p class="chat-sidebar__copy">
          当前会话会记住本轮关系背景，用来连续分析恋爱难题和沟通策略。
        </p>
      </div>
      <div class="memory-panel">
        <span>对话记忆</span>
        <p>{{ memorySummary || '发送第一条消息后，将在这里沉淀关系阶段和沟通目标。' }}</p>
      </div>
      <button
        class="report-action"
        type="button"
        :disabled="isReportGenerating || isRestoring || messages.length === 0"
        @click="handleGenerateReport"
      >
        {{ isReportGenerating ? '生成中' : '生成恋爱报告' }}
      </button>
      <button class="secondary-action" type="button" :disabled="isSending" @click="handleNewConversation">
        新会话
      </button>
    </aside>

    <div class="chat-panel">
      <div class="message-list" aria-live="polite">
        <p v-if="isRestoring" class="chat-empty">正在恢复上次会话...</p>
        <p v-else-if="messages.length === 0" class="chat-empty">
          说说你现在遇到的恋爱难题，我会把本次关系背景持续记住。
        </p>
        <article
          v-for="message in messages"
          :key="message.messageId"
          class="message-bubble"
          :class="`message-bubble--${message.role}`"
        >
          <span>{{ message.role === 'user' ? '你' : 'AI 恋爱大师' }}</span>
          <p>{{ message.content }}</p>
          <details v-if="message.citations.length > 0" class="message-citations">
            <summary>参考资料 {{ message.citations.length }} 条</summary>
            <ul>
              <li v-for="citation in message.citations" :key="citation.chunkId">
                <strong>{{ citation.title }}</strong>
                <small>{{ citation.sourceUri }}</small>
              </li>
            </ul>
          </details>
        </article>
      </div>

      <section v-if="loveReport" class="love-report" aria-label="恋爱报告">
        <div class="love-report__header">
          <div>
            <span>恋爱报告</span>
            <h3>{{ loveReport.reportTitle }}</h3>
          </div>
          <strong>{{ loveReport.relationshipStage }}</strong>
        </div>
        <p class="love-report__summary">{{ loveReport.situationSummary }}</p>
        <dl class="love-report__meta">
          <div>
            <dt>目标</dt>
            <dd>{{ loveReport.userGoal }}</dd>
          </div>
          <div>
            <dt>置信度</dt>
            <dd>{{ Math.round(loveReport.confidence * 100) }}%</dd>
          </div>
        </dl>
        <div class="love-report__grid">
          <section>
            <h4>积极信号</h4>
            <ul>
              <li v-for="item in loveReport.positiveSignals" :key="item">{{ item }}</li>
            </ul>
          </section>
          <section>
            <h4>风险信号</h4>
            <ul>
              <li v-for="item in loveReport.riskSignals" :key="item">{{ item }}</li>
            </ul>
          </section>
          <section>
            <h4>下一步</h4>
            <ul>
              <li v-for="item in loveReport.nextSteps" :key="item">{{ item }}</li>
            </ul>
          </section>
          <section>
            <h4>需要补充</h4>
            <ul>
              <li v-for="item in loveReport.questionsToClarify" :key="item">{{ item }}</li>
            </ul>
          </section>
        </div>
        <blockquote>{{ loveReport.communicationScript }}</blockquote>
      </section>

      <form class="chat-composer" @submit.prevent="handleSubmit">
        <textarea
          v-model="draft"
          :disabled="isSending"
          rows="3"
          placeholder="说说你现在遇到的恋爱难题，例如：暧昧两个月了，我该怎么推进？"
        />
        <button type="submit" :disabled="isSending || !draft.trim()">
          {{ isSending ? '分析中' : '发送' }}
        </button>
      </form>

      <p v-if="errorMessage" class="chat-error">{{ errorMessage }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import {
  clearCurrentLoveConversationId,
  createLoveConversation,
  generateLoveReport,
  getLoveConversation,
  getLoveConversationMessages,
  loadCurrentLoveConversationId,
  saveCurrentLoveConversationId,
  sendLoveConversationMessage,
  type ConversationMessage,
  type LoveConversationMessageResult,
  type LoveReport,
  type LoveConversation,
} from '@/modules/chat/api'
import { isApiError } from '@/shared/api/http'

const conversation = ref<LoveConversation | null>(null)
const messages = ref<ConversationMessage[]>([])
const memorySummary = ref('')
const loveReport = ref<LoveReport | null>(null)
const draft = ref('')
const isSending = ref(false)
const isRestoring = ref(false)
const isReportGenerating = ref(false)
const errorMessage = ref('')

onMounted(() => {
  void restoreConversation()
})

async function restoreConversation() {
  const conversationId = loadCurrentLoveConversationId()
  if (!conversationId) {
    return
  }

  isRestoring.value = true
  errorMessage.value = ''

  try {
    const [restoredConversation, history] = await Promise.all([
      getLoveConversation(conversationId),
      getLoveConversationMessages(conversationId),
    ])
    conversation.value = restoredConversation
    messages.value = history.messages
    memorySummary.value = history.memorySummary || restoredConversation.memorySummary
  } catch {
    clearCurrentLoveConversationId()
    conversation.value = null
    messages.value = []
    memorySummary.value = ''
  } finally {
    isRestoring.value = false
  }
}

async function handleSubmit() {
  const content = draft.value.trim()
  if (!content || isSending.value) {
    return
  }

  isSending.value = true
  errorMessage.value = ''

  try {
    draft.value = ''
    let result: LoveConversationMessageResult
    try {
      result = await sendMessageToCurrentConversation(content)
    } catch (error) {
      if (!isApiError(error, 404)) {
        throw error
      }
      resetConversationState()
      result = await sendMessageToCurrentConversation(content)
    }
    messages.value.push(result.userMessage, result.assistantMessage)
    memorySummary.value = result.memorySummary
    loveReport.value = null
  } catch {
    errorMessage.value = '消息发送失败，请稍后重试。'
  } finally {
    isSending.value = false
  }
}

function handleNewConversation() {
  resetConversationState()
}

async function sendMessageToCurrentConversation(content: string) {
  const currentConversation = await ensureConversation()
  return sendLoveConversationMessage(currentConversation.conversationId, content)
}

async function ensureConversation() {
  if (conversation.value) {
    return conversation.value
  }

  conversation.value = await createLoveConversation('恋爱咨询')
  saveCurrentLoveConversationId(conversation.value.conversationId)
  return conversation.value
}

function resetConversationState() {
  clearCurrentLoveConversationId()
  conversation.value = null
  messages.value = []
  memorySummary.value = ''
  loveReport.value = null
  errorMessage.value = ''
}

async function handleGenerateReport() {
  if (!conversation.value || messages.value.length === 0 || isReportGenerating.value) {
    return
  }

  isReportGenerating.value = true
  errorMessage.value = ''

  try {
    const result = await generateLoveReport(conversation.value.conversationId, {
      focus: '推进关系',
      style: '温和直接',
    })
    loveReport.value = result.report
    memorySummary.value = result.memorySummary
  } catch {
    errorMessage.value = '恋爱报告生成失败，请稍后重试。'
  } finally {
    isReportGenerating.value = false
  }
}
</script>
