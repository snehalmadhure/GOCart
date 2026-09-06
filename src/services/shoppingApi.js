import { generatedList } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
import { toUiShoppingList } from './backendMappers'
export const shoppingApi = {
  generate: async (intent) => useMockApi ? (await pause(850), { ...copy(generatedList), intent }) : toUiShoppingList(await request('/api/v1/shopping-lists/generate', { method: 'POST', body: JSON.stringify({ intent }) })),
  confirm: async (id, items) => useMockApi ? (await pause(400), { id, items }) : ({ id, items }),
}
