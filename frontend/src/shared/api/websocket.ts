import { appConfig } from '@/shared/config/appConfig'

export function createWebSocket(path: string): WebSocket {
  return new WebSocket(`${appConfig.api.wsBaseUrl}${path}`)
}
