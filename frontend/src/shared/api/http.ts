import { appConfig } from '@/shared/config/appConfig'

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${appConfig.api.baseUrl}${path}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}
