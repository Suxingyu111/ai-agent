<template>
  <section class="knowledge-workbench">
    <header class="knowledge-workbench__header">
      <div>
        <p class="workspace__eyebrow">AI 恋爱大师</p>
        <h1>RAG 知识库工作台</h1>
      </div>
      <RouterLink class="knowledge-workbench__link" to="/">返回对话</RouterLink>
    </header>

    <section class="knowledge-stats" aria-label="知识库状态">
      <div>
        <span>文档</span>
        <strong>{{ documentsResult?.documentCount ?? 0 }}</strong>
      </div>
      <div>
        <span>切片</span>
        <strong>{{ documentsResult?.chunkCount ?? 0 }}</strong>
      </div>
      <div>
        <span>召回</span>
        <strong>{{ retrievalDebug?.knowledgeUsed ? '已命中' : '待查询' }}</strong>
      </div>
      <button type="button" :disabled="isLoading || isReindexing" @click="handleReindex">
        {{ isReindexing ? '重建中' : '重建索引' }}
      </button>
    </section>

    <p v-if="statusMessage" class="knowledge-status">{{ statusMessage }}</p>
    <p v-if="errorMessage" class="knowledge-error">{{ errorMessage }}</p>

    <div class="knowledge-workbench__grid">
      <section class="knowledge-panel knowledge-panel--documents" aria-label="知识库文档">
        <div class="knowledge-panel__header">
          <h2>已入库资料</h2>
          <button type="button" :disabled="isLoading" @click="loadDocuments">
            {{ isLoading ? '刷新中' : '刷新' }}
          </button>
        </div>

        <p v-if="!documentsResult && isLoading" class="knowledge-empty">正在读取知识库...</p>
        <p v-else-if="documents.length === 0" class="knowledge-empty">暂无入库资料。</p>

        <div v-else class="knowledge-document-list">
          <article
            v-for="document in documents"
            :key="document.documentId"
            class="knowledge-document"
            :class="{ 'knowledge-document--active': document.documentId === selectedDocumentId }"
          >
            <button type="button" @click="selectedDocumentId = document.documentId">
              <span>{{ document.title }}</span>
              <small>{{ document.chunks.length }} 个切片</small>
            </button>
            <dl v-if="document.documentId === selectedDocumentId">
              <div>
                <dt>来源</dt>
                <dd>{{ document.sourceUri }}</dd>
              </div>
              <div>
                <dt>分类</dt>
                <dd>{{ metadataValue(document.metadata, 'primary_category') }}</dd>
              </div>
              <div>
                <dt>审核</dt>
                <dd>{{ metadataValue(document.metadata, 'review_status') }}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>

      <section class="knowledge-panel knowledge-panel--chunks" aria-label="文档切片">
        <div class="knowledge-panel__header">
          <h2>原文切片</h2>
          <span>{{ selectedDocument?.title ?? '未选择' }}</span>
        </div>

        <div v-if="selectedDocument" class="knowledge-chunk-list">
          <article v-for="chunk in selectedDocument.chunks" :key="chunk.chunkId" class="knowledge-chunk">
            <header>
              <strong>{{ chunk.titlePath || chunk.title }}</strong>
              <span>{{ chunk.tokenCount }} tokens</span>
            </header>
            <p>{{ chunk.content }}</p>
            <small>{{ chunk.qdrantPointId || '未写入向量点位' }}</small>
          </article>
        </div>
        <p v-else class="knowledge-empty">选择一份资料查看原文切片。</p>
      </section>

      <section class="knowledge-panel knowledge-panel--debug" aria-label="召回调试">
        <div class="knowledge-panel__header">
          <h2>召回调试</h2>
          <span>{{ retrievalDebug?.candidateCount ?? 0 }} 条候选</span>
        </div>

        <form class="knowledge-form" @submit.prevent="handleDebug">
          <label>
            <span>问题</span>
            <input v-model="debugQuery" type="text" :disabled="isDebugging" />
          </label>
          <label>
            <span>条数</span>
            <input v-model.number="debugLimit" type="number" min="1" max="20" :disabled="isDebugging" />
          </label>
          <button type="submit" :disabled="isDebugging || !debugQuery.trim()">
            {{ isDebugging ? '检索中' : '检索' }}
          </button>
        </form>

        <dl v-if="retrievalDebug" class="knowledge-debug-meta">
          <div>
            <dt>关系阶段</dt>
            <dd>{{ retrievalDebug.classification.relationshipStage || 'general' }}</dd>
          </div>
          <div>
            <dt>主题分类</dt>
            <dd>{{ retrievalDebug.classification.primaryCategory || 'auto' }}</dd>
          </div>
        </dl>

        <div v-if="retrievalDebug?.selectedEvidence.length" class="knowledge-evidence-list">
          <article
            v-for="evidence in retrievalDebug.selectedEvidence"
            :key="evidence.chunkId"
            class="knowledge-evidence"
          >
            <header>
              <strong>{{ evidence.title }}</strong>
              <span>{{ Math.round(evidence.score * 100) }}%</span>
            </header>
            <p>{{ evidence.content }}</p>
            <small>{{ evidence.sourceUri }}</small>
          </article>
        </div>
        <p v-else class="knowledge-empty">输入问题后查看实际召回文本。</p>
      </section>

      <section class="knowledge-panel knowledge-panel--evaluation" aria-label="检索评估">
        <div class="knowledge-panel__header">
          <h2>检索评估</h2>
          <strong :class="evaluationResult?.passed ? 'knowledge-pass' : 'knowledge-wait'">
            {{ evaluationResult ? (evaluationResult.passed ? '通过' : '未通过') : '待运行' }}
          </strong>
        </div>

        <form class="knowledge-form knowledge-form--evaluation" @submit.prevent="handleEvaluation">
          <label>
            <span>问题</span>
            <input v-model="evaluationQuery" type="text" :disabled="isEvaluating" />
          </label>
          <label>
            <span>期望标题</span>
            <input v-model="expectedTitlesText" type="text" :disabled="isEvaluating" />
          </label>
          <label>
            <span>禁召标题</span>
            <input v-model="forbiddenTitlesText" type="text" :disabled="isEvaluating" />
          </label>
          <button type="submit" :disabled="isEvaluating || !evaluationQuery.trim()">
            {{ isEvaluating ? '评估中' : '运行评估' }}
          </button>
        </form>

        <dl v-if="evaluationResult" class="knowledge-evaluation-result">
          <div>
            <dt>命中期望</dt>
            <dd>{{ evaluationResult.matchedExpectedTitles.join('、') || '无' }}</dd>
          </div>
          <div>
            <dt>缺失期望</dt>
            <dd>{{ evaluationResult.missingExpectedTitles.join('、') || '无' }}</dd>
          </div>
          <div>
            <dt>禁召命中</dt>
            <dd>{{ evaluationResult.forbiddenTitleHits.join('、') || '无' }}</dd>
          </div>
        </dl>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  getLoveMasterKnowledgeDocuments,
  getLoveMasterRetrievalDebug,
  reindexLoveMasterKnowledgeBase,
  runLoveMasterRetrievalEvaluation,
  type KnowledgeDocument,
  type KnowledgeDocumentsResult,
  type KnowledgeRetrievalDebugResult,
  type KnowledgeRetrievalEvaluationResult,
} from '@/modules/chat/api'

const documentsResult = ref<KnowledgeDocumentsResult | null>(null)
const retrievalDebug = ref<KnowledgeRetrievalDebugResult | null>(null)
const evaluationResult = ref<KnowledgeRetrievalEvaluationResult | null>(null)
const selectedDocumentId = ref('')
const debugQuery = ref('如何沟通手机隐私和回复频率？')
const evaluationQuery = ref('如何沟通手机隐私？')
const expectedTitlesText = ref('数字边界沟通原则')
const forbiddenTitlesText = ref('')
const debugLimit = ref(5)
const isLoading = ref(false)
const isReindexing = ref(false)
const isDebugging = ref(false)
const isEvaluating = ref(false)
const statusMessage = ref('')
const errorMessage = ref('')

const documents = computed(() => documentsResult.value?.documents ?? [])
const selectedDocument = computed<KnowledgeDocument | null>(() => {
  return documents.value.find((document) => document.documentId === selectedDocumentId.value) ?? null
})

onMounted(() => {
  void loadDocuments()
})

async function loadDocuments() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    documentsResult.value = await getLoveMasterKnowledgeDocuments()
    if (!selectedDocumentId.value || !selectedDocument.value) {
      selectedDocumentId.value = documents.value[0]?.documentId ?? ''
    }
    statusMessage.value = '知识库资料已刷新。'
  } catch {
    errorMessage.value = '知识库资料读取失败。'
  } finally {
    isLoading.value = false
  }
}

async function handleReindex() {
  isReindexing.value = true
  errorMessage.value = ''

  try {
    const result = await reindexLoveMasterKnowledgeBase()
    await loadDocuments()
    statusMessage.value = `索引已重建：${result.documentCount} 份文档，${result.chunkCount} 个切片。`
  } catch {
    errorMessage.value = '知识库索引重建失败。'
  } finally {
    isReindexing.value = false
  }
}

async function handleDebug() {
  isDebugging.value = true
  errorMessage.value = ''

  try {
    retrievalDebug.value = await getLoveMasterRetrievalDebug(debugQuery.value.trim(), debugLimit.value)
    statusMessage.value = '召回调试已完成。'
  } catch {
    errorMessage.value = '召回调试失败。'
  } finally {
    isDebugging.value = false
  }
}

async function handleEvaluation() {
  isEvaluating.value = true
  errorMessage.value = ''

  try {
    evaluationResult.value = await runLoveMasterRetrievalEvaluation({
      query: evaluationQuery.value.trim(),
      expectedTitles: parseTitleList(expectedTitlesText.value),
      forbiddenTitles: parseTitleList(forbiddenTitlesText.value),
      limit: debugLimit.value,
    })
    statusMessage.value = '检索评估已完成。'
  } catch {
    errorMessage.value = '检索评估失败。'
  } finally {
    isEvaluating.value = false
  }
}

function metadataValue(metadata: Record<string, unknown>, key: string): string {
  const value = metadata[key]
  if (Array.isArray(value)) {
    return value.join('、')
  }
  return typeof value === 'string' && value.length > 0 ? value : '未标注'
}

function parseTitleList(value: string): string[] {
  return value
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean)
}
</script>
