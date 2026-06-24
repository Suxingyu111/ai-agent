/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME?: string
  readonly VITE_APP_ENV?: string
  readonly VITE_DEFAULT_LOCALE?: string
  readonly VITE_API_BASE_URL?: string
  readonly VITE_API_TIMEOUT_MS?: string
  readonly VITE_SSE_BASE_URL?: string
  readonly VITE_WS_BASE_URL?: string
  readonly VITE_ENABLE_MOCK?: string
  readonly VITE_ENABLE_AGENT_BUILDER?: string
  readonly VITE_ENABLE_WORKFLOW_BUILDER?: string
  readonly VITE_ENABLE_MCP_MARKETPLACE?: string
  readonly VITE_ENABLE_DEBUG_PANEL?: string
  readonly VITE_PUBLIC_STORAGE_BASE_URL?: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_OTEL_EXPORTER_OTLP_ENDPOINT?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
