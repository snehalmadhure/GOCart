import { pantryItems } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
export const pantryApi = {
  getAll: async () => useMockApi ? (await pause(), copy(pantryItems)) : request('/api/pantry'),
  getOne: async (id) => useMockApi ? (await pause(180), copy(pantryItems.find(item => item.id === id))) : request(`/api/pantry/${id}`),
}
