import { describe, expect, it } from 'vitest'

import { readAppConfig } from './appConfig'

describe('readAppConfig', () => {
  it('把 Vite 环境变量规整为前端应用配置', () => {
    const config = readAppConfig({
      VITE_APP_NAME: 'AI 多智能体平台',
      VITE_APP_ENV: 'test',
      VITE_API_BASE_URL: 'http://127.0.0.1:8000/api/v1',
      VITE_API_TIMEOUT_MS: '45000',
      VITE_SSE_BASE_URL: 'http://127.0.0.1:8000/api/v1',
      VITE_WS_BASE_URL: 'ws://127.0.0.1:8000/api/v1',
      VITE_ENABLE_AGENT_BUILDER: 'true',
      VITE_ENABLE_WORKFLOW_BUILDER: 'false',
      VITE_ENABLE_MCP_MARKETPLACE: 'true',
      VITE_ENABLE_DEBUG_PANEL: 'false',
      VITE_PUBLIC_STORAGE_BASE_URL: 'http://127.0.0.1:8000/api/v1/artifacts',
    })

    expect(config.appName).toBe('AI 多智能体平台')
    expect(config.api.timeoutMs).toBe(45000)
    expect(config.features.enableWorkflowBuilder).toBe(false)
    expect(config.features.enableDebugPanel).toBe(false)
  })
})
