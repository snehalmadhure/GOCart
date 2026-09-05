const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const useMockApi = import.meta.env.VITE_USE_MOCK_API !== 'false'

export async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options })
  if (!response.ok) throw new Error('The service is temporarily unavailable.')
  return response.status === 204 ? null : response.json()
}

export const pause = (ms = 450) => new Promise(resolve => setTimeout(resolve, ms))
export const copy = (data) => JSON.parse(JSON.stringify(data))
