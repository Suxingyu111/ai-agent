import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  clearCurrentLoveConversationId,
  createLoveConversation,
  generateLoveReport,
  getLoveConversation,
  getLoveConversationMessages,
  loadCurrentLoveConversationId,
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
        },
        memory_summary: '用户当前关系阶段可能是暧昧期。',
        safety_flags: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await sendLoveConversationMessage('conv_1', '我该怎么发微信？')

    expect(result.assistantMessage.content).toContain('暧昧阶段')
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
})
