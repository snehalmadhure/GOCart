import { reminders } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
import { toUiReminder } from './backendMappers'
let store = copy(reminders)
export const remindersApi = {
  getAll: async () => useMockApi ? (await pause(), copy(store)) : (await request('/api/v1/restock-alerts')).map(toUiReminder),
  snooze: async (id, days) => useMockApi ? (await pause(300), store = store.map(item => item.id === id ? { ...item, status: 'snoozed', snoozedDays: days } : item), null) : toUiReminder(await request(`/api/v1/restock-alerts/${id}/snooze`, { method: 'POST', body: JSON.stringify({ days }) })),
  dismiss: async (id) => useMockApi ? (await pause(300), store = store.filter(item => item.id !== id), null) : request(`/api/v1/restock-alerts/${id}/dismiss`, { method: 'POST' }),
}
