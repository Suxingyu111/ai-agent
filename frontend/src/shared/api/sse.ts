import { appConfig } from '@/shared/config/appConfig'

export function createEventStream(path: string): EventSource {
  return new EventSource(`${appConfig.api.sseBaseUrl}${path}`)
}
