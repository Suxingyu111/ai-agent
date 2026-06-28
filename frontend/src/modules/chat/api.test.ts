import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  clearCurrentLoveConversationId,
  createLoveConversation,
  generateLoveReport,
  getLoveConversation,
  getLoveConversationMessages,
  getLoveMasterKnowledgeDocuments,
  getLoveMasterRetrievalDebug,
  loadCurrentLoveConversationId,
  reindexLoveMasterKnowledgeBase,
  runLoveMasterRetrievalEvaluation,
  saveCurrentLoveConversationId,
  sendLoveConversationMessage,
} from './api'
import type { ApiError } from '@/shared/api/http'

describe('chat api', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('创建 AI 恋爱大师会话', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        conversation_id: 'conv_1',
        thread_id: 'thread_1',
        agent_key: 'love_master_agent',
        title: '暧昧推进',
        memory_namespace: 'agent.love_master',
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const conversation = await createLoveConversation('暧昧推进')

    expect(conversation.conversationId).toBe('conv_1')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/conversations',
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_key: 'love_master_agent',
          title: '暧昧推进',
        }),
      },
    )
  })

  it('发送用户消息并读取助手回复', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        conversation_id: 'conv_1',
        user_message: {
          message_id: 'msg_user',
          role: 'user',
          content: '我该怎么发微信？',
          safety_flags: [],
        },
        assistant_message: {
          message_id: 'msg_assistant',
          role: 'assistant',
          content: '基于你前面提到的暧昧阶段，可以轻量邀约。',
          safety_flags: [],
          citations: [
            {
              chunk_id: 'chunk_1',
              title: '暧昧期低压力邀约原则',
              source_uri: 'local://love-master/ambiguous_invitation.md',
              score: 0.82,
            },
          ],
        },
        memory_summary: '用户当前关系阶段可能是暧昧期。',
        safety_flags: [],
        knowledge_used: true,
        citations: [
          {
            chunk_id: 'chunk_1',
            title: '暧昧期低压力邀约原则',
            source_uri: 'local://love-master/ambiguous_invitation.md',
            score: 0.82,
          },
        ],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await sendLoveConversationMessage('conv_1', '我该怎么发微信？')

    expect(result.assistantMessage.content).toContain('暧昧阶段')
    expect(result.knowledgeUsed).toBe(true)
    expect(result.assistantMessage.citations[0].title).toBe('暧昧期低压力邀约原则')
    expect(result.citations[0].sourceUri).toBe('local://love-master/ambiguous_invitation.md')
    expect(result.memorySummary).toBe('用户当前关系阶段可能是暧昧期。')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/conversations/conv_1/messages',
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: '我该怎么发微信？',
        }),
      },
    )
  })

  it('发送到不存在的会话时保留 404 状态码', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({
        detail: '会话不存在。',
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(sendLoveConversationMessage('conv_missing', '我该怎么推进？')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
    } satisfies Partial<ApiError>)
  })

  it('生成结构化恋爱报告', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        conversation_id: 'conv_1',
        report: {
          report_title: '暧昧期推进分析报告',
          relationship_stage: '暧昧期',
          user_goal: '希望推进关系，但担心显得太主动。',
          situation_summary: '用户和对方暧昧两个月。',
          positive_signals: ['关系已经持续互动两个月'],
          risk_signals: ['用户担心节奏过快'],
          emotional_needs: ['需要确定感'],
          next_steps: ['先用轻量邀约测试对方投入度'],
          communication_script: '这周有个地方我觉得你会喜欢，要不要一起去？',
          questions_to_clarify: ['你们最近一次单独互动是什么时候？'],
          memory_candidates: [],
          safety_flags: [],
          confidence: 0.78,
        },
        memory_summary: '用户当前关系阶段可能是暧昧期。',
        safety_flags: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await generateLoveReport('conv_1', {
      focus: '推进关系',
      style: '温和直接',
    })

    expect(result.report.relationshipStage).toBe('暧昧期')
    expect(result.report.nextSteps).toEqual(['先用轻量邀约测试对方投入度'])
    expect(result.report.communicationScript).toContain('要不要一起去')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/conversations/conv_1/love-report',
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          focus: '推进关系',
          style: '温和直接',
        }),
      },
    )
  })

  it('读取会话详情和历史消息用于页面刷新恢复', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          conversation_id: 'conv_1',
          thread_id: 'thread_1',
          agent_key: 'love_master_agent',
          title: '暧昧推进',
          memory_namespace: 'agent.love_master',
          memory_summary: '用户当前关系阶段可能是暧昧期。',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          conversation_id: 'conv_1',
          memory_summary: '用户当前关系阶段可能是暧昧期。',
          messages: [
            {
              message_id: 'msg_user',
              role: 'user',
              content: '我和她暧昧两个月了。',
              safety_flags: [],
            },
          ],
        }),
      })
    vi.stubGlobal('fetch', fetchMock)

    const conversation = await getLoveConversation('conv_1')
    const history = await getLoveConversationMessages('conv_1')

    expect(conversation.memorySummary).toBe('用户当前关系阶段可能是暧昧期。')
    expect(history.messages[0].content).toBe('我和她暧昧两个月了。')
    expect(history.memorySummary).toBe('用户当前关系阶段可能是暧昧期。')
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/conversations/conv_1',
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      },
    )
  })

  it('保存和清理当前恋爱会话 id', () => {
    const storage = new Map<string, string>()
    vi.stubGlobal('localStorage', {
      getItem: vi.fn((key: string) => storage.get(key) ?? null),
      setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
      removeItem: vi.fn((key: string) => storage.delete(key)),
    })

    saveCurrentLoveConversationId('conv_1')
    expect(loadCurrentLoveConversationId()).toBe('conv_1')

    clearCurrentLoveConversationId()
    expect(loadCurrentLoveConversationId()).toBeNull()
  })

  it('读取知识库文档和切片', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        knowledge_base_id: 'kb_love_master_default',
        document_count: 1,
        chunk_count: 1,
        documents: [
          {
            document_id: 'doc_1',
            knowledge_base_id: 'kb_love_master_default',
            title: '数字边界沟通原则',
            source_type: 'markdown',
            source_uri: 'local://love-master/curated/safety_boundaries/digital_boundaries.md',
            version: 'v1',
            status: 'indexed',
            metadata: { primary_category: 'safety_boundaries' },
            chunks: [
              {
                chunk_id: 'chunk_1',
                chunk_index: 1,
                title: '数字边界沟通原则',
                title_path: '数字边界沟通原则 / 核心原则',
                content: '亲密关系不等于放弃隐私。',
                token_count: 18,
                qdrant_point_id: 'point_1',
                status: 'indexed',
                metadata: { safety_level: 'normal' },
              },
            ],
          },
        ],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await getLoveMasterKnowledgeDocuments()

    expect(result.documentCount).toBe(1)
    expect(result.documents[0].chunks[0].qdrantPointId).toBe('point_1')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/knowledge-bases/love-master-default/documents',
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      },
    )
  })

  it('调试知识库召回并运行检索评估', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          query: '如何沟通手机隐私？',
          classification: {
            relationship_stage: 'general',
            primary_category: 'safety_boundaries',
          },
          knowledge_used: true,
          candidate_count: 1,
          selected_evidence: [
            {
              chunk_id: 'chunk_1',
              document_id: 'doc_1',
              knowledge_base_id: 'kb_love_master_default',
              title: '数字边界沟通原则',
              source_uri: 'local://love-master/digital_boundaries.md',
              content: '亲密关系不等于放弃隐私。',
              score: 0.91,
              relationship_stage: 'general',
              primary_category: 'safety_boundaries',
              topic_tags: ['privacy'],
              intent_tags: ['strategy'],
              safety_level: 'normal',
            },
          ],
          citations: [],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          knowledge_base_id: 'kb_love_master_default',
          collection_name: 'ai_agent_dev_love_master_v1',
          document_count: 30,
          chunk_count: 90,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          query: '如何沟通手机隐私？',
          passed: true,
          matched_expected_titles: ['数字边界沟通原则'],
          missing_expected_titles: [],
          forbidden_title_hits: [],
          retrieved_titles: ['数字边界沟通原则'],
          result: {
            knowledge_used: true,
            evidence: [],
            citations: [],
          },
        }),
      })
    vi.stubGlobal('fetch', fetchMock)

    const debug = await getLoveMasterRetrievalDebug('如何沟通手机隐私？')
    const reindex = await reindexLoveMasterKnowledgeBase()
    const evaluation = await runLoveMasterRetrievalEvaluation({
      query: '如何沟通手机隐私？',
      expectedTitles: ['数字边界沟通原则'],
      forbiddenTitles: [],
      limit: 5,
    })

    expect(debug.classification.primaryCategory).toBe('safety_boundaries')
    expect(debug.selectedEvidence[0].title).toBe('数字边界沟通原则')
    expect(reindex.chunkCount).toBe(90)
    expect(evaluation.passed).toBe(true)
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/knowledge-bases/love-master-default/retrieval-debug?query=%E5%A6%82%E4%BD%95%E6%B2%9F%E9%80%9A%E6%89%8B%E6%9C%BA%E9%9A%90%E7%A7%81%EF%BC%9F',
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      },
    )
  })
})
