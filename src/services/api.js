// Local development sets VITE_API_BASE_URL. On Vercel, use the same deployed
// origin so the browser reaches the co-located FastAPI function at /api/v1.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
export const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true'

export async function request(path, options = {}) {
  const session = useMockApi ? null : (await supabase?.auth.getSession())?.data.session
  const headers = { 'Content-Type': 'application/json', ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}), ...(options.headers || {}) }
  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (response.status === 401 && !useMockApi) {
    // A session from an earlier deployment or an expired Supabase token must
    // never leave the UI on a protected page that can no longer load data.
    try {
      await supabase?.auth.signOut()
    } finally {
      window.location.assign('/login')
    }
    throw new Error('Your session has expired. Please sign in again.')
  }
  if (!response.ok) throw new Error('The service is temporarily unavailable.')
  return response.status === 204 ? null : response.json()
}

export const pause = (ms = 450) => new Promise(resolve => setTimeout(resolve, ms))
export const copy = (data) => JSON.parse(JSON.stringify(data))
import { supabase } from './supabase'
