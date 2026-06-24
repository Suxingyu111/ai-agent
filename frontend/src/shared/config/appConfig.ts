type EnvSource = Record<string, string | boolean | undefined>

export interface AppConfig {
  appName: string
  appEnv: string
  defaultLocale: string
  api: {
    baseUrl: string
    timeoutMs: number
    sseBaseUrl: string
    wsBaseUrl: string
  }
  features: {
    enableMock: boolean
    enableAgentBuilder: boolean
    enableWorkflowBuilder: boolean
    enableMcpMarketplace: boolean
    enableDebugPanel: boolean
  }
  storage: {
    publicBaseUrl: string
  }
  observability: {
    sentryDsn: string
    otelEndpoint: string
  }
}

function readBoolean(value: string | boolean | undefined, defaultValue: boolean): boolean {
  if (typeof value === 'boolean') {
    return value
  }
  if (value === undefined || value === '') {
    return defaultValue
  }
  return value === 'true'
}

function readNumber(value: string | boolean | undefined, defaultValue: number): number {
  if (typeof value !== 'string' || value.trim() === '') {
    return defaultValue
  }
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : defaultValue
}

function readString(value: string | boolean | undefined, defaultValue: string): string {
  return typeof value === 'string' && value.trim() !== '' ? value : defaultValue
}

export function readAppConfig(env: EnvSource): AppConfig {
  const apiBaseUrl = readString(env.VITE_API_BASE_URL, 'http://127.0.0.1:8000/api/v1')

  return {
    appName: readString(env.VITE_APP_NAME, 'AI 多智能体平台'),
    appEnv: readString(env.VITE_APP_ENV, 'development'),
    defaultLocale: readString(env.VITE_DEFAULT_LOCALE, 'zh-CN'),
    api: {
      baseUrl: apiBaseUrl,
      timeoutMs: readNumber(env.VITE_API_TIMEOUT_MS, 30000),
      sseBaseUrl: readString(env.VITE_SSE_BASE_URL, apiBaseUrl),
      wsBaseUrl: readString(env.VITE_WS_BASE_URL, 'ws://127.0.0.1:8000/api/v1'),
    },
    features: {
      enableMock: readBoolean(env.VITE_ENABLE_MOCK, false),
      enableAgentBuilder: readBoolean(env.VITE_ENABLE_AGENT_BUILDER, true),
      enableWorkflowBuilder: readBoolean(env.VITE_ENABLE_WORKFLOW_BUILDER, true),
      enableMcpMarketplace: readBoolean(env.VITE_ENABLE_MCP_MARKETPLACE, true),
      enableDebugPanel: readBoolean(env.VITE_ENABLE_DEBUG_PANEL, false),
    },
    storage: {
      publicBaseUrl: readString(env.VITE_PUBLIC_STORAGE_BASE_URL, `${apiBaseUrl}/artifacts`),
    },
    observability: {
      sentryDsn: readString(env.VITE_SENTRY_DSN, ''),
      otelEndpoint: readString(env.VITE_OTEL_EXPORTER_OTLP_ENDPOINT, ''),
    },
  }
}

export const appConfig = readAppConfig(import.meta.env)
