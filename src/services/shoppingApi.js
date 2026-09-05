import { generatedList } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
export const shoppingApi = {
  generate: async (intent) => useMockApi ? (await pause(850), { ...copy(generatedList), intent }) : request('/api/shopping-list/generate', { method: 'POST', body: JSON.stringify({ intent }) }),
  confirm: async (id, items) => useMockApi ? (await pause(400), { id, items }) : request(`/api/shopping-list/${id}/confirm`, { method: 'POST', body: JSON.stringify({ items }) }),
}
