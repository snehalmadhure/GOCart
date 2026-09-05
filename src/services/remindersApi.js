import { reminders } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
let store = copy(reminders)
export const remindersApi = {
  getAll: async () => useMockApi ? (await pause(), copy(store)) : request('/api/reminders'),
  snooze: async (id, days) => useMockApi ? (await pause(300), store = store.map(item => item.id === id ? { ...item, status: 'snoozed', snoozedDays: days } : item), null) : request(`/api/reminders/${id}/snooze`, { method: 'POST', body: JSON.stringify({ days }) }),
  dismiss: async (id) => useMockApi ? (await pause(300), store = store.filter(item => item.id !== id), null) : request(`/api/reminders/${id}/dismiss`, { method: 'POST' }),
}
