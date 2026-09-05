import { purchases } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
let store = copy(purchases)
export const purchasesApi = {
  getAll: async () => useMockApi ? (await pause(), copy(store)) : request('/api/purchases'),
  create: async (payload) => useMockApi ? (await pause(350), store = [{ ...payload, id: crypto.randomUUID() }, ...store], copy(store[0])) : request('/api/purchases', { method: 'POST', body: JSON.stringify(payload) }),
  update: async (id, payload) => useMockApi ? (await pause(350), store = store.map(item => item.id === id ? { ...item, ...payload } : item), copy(store.find(item => item.id === id))) : request(`/api/purchases/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  remove: async (id) => useMockApi ? (await pause(300), store = store.filter(item => item.id !== id), null) : request(`/api/purchases/${id}`, { method: 'DELETE' }),
  importHistory: async () => useMockApi ? (await pause(600), { found: 48, ready: 45, review: 3 }) : request('/api/purchases/import', { method: 'POST' }),
}
