import { pantryItems } from '../data/mockData'
import { copy, pause, request, useMockApi } from './api'
import { toUiPantryItem } from './backendMappers'
export const pantryApi = {
  getAll: async () => useMockApi ? (await pause(), copy(pantryItems)) : (await request('/api/v1/pantry')).items.map(toUiPantryItem),
  getOne: async (id) => useMockApi ? (await pause(180), copy(pantryItems.find(item => item.id === id))) : (await pantryApi.getAll()).find(item => item.id === String(id)),
}
