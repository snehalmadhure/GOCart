const dateOnly = (value) => value ? value.slice(0, 10) : ''
const numberOr = (value, fallback = 0) => value == null ? fallback : Number(value)

export const toBackendPurchase = (purchase) => ({
  item_name: purchase.itemName,
  quantity: Number(purchase.quantity),
  unit: purchase.unit,
  purchased_at: `${dateOnly(purchase.purchaseDate)}T12:00:00Z`,
  ...(purchase.expiryDate ? { expires_at: `${dateOnly(purchase.expiryDate)}T12:00:00Z` } : {}),
})

export const toUiPurchase = (purchase) => ({
  id: String(purchase.id),
  itemName: purchase.item_name,
  quantity: numberOr(purchase.quantity),
  unit: purchase.unit,
  purchaseDate: dateOnly(purchase.purchased_at),
  expiryDate: dateOnly(purchase.expires_at),
  price: null,
  category: 'Other',
  notes: '',
})

export const toUiPantryItem = (item) => ({
  id: String(item.item_id),
  name: item.item_name,
  quantityRemaining: numberOr(item.estimated_quantity),
  unit: item.unit || 'unit',
  consumptionRate: 0,
  consumptionUnit: `${item.unit || 'unit'}/day`,
  daysRemaining: item.days_left == null ? Infinity : numberOr(item.days_left),
  predictedRunoutDate: dateOnly(item.run_out_at),
  expiryDate: item.status === 'expired' ? dateOnly(item.run_out_at) : '',
  confidence: item.status === 'unknown' ? 0.2 : 0.75,
  status: item.status,
  lastPurchaseDate: dateOnly(item.last_calculated_at),
  history: [],
})

export const toUiReminder = (batch) => ({
  id: String(batch.id),
  type: batch.status === 'pending' ? 'restock' : 'upcoming',
  title: batch.status === 'pending' ? 'Restock recommended' : 'Plan ahead',
  scheduledDate: dateOnly(batch.scheduled_for),
  items: batch.items.map(item => ({ itemName: item.item_name, reason: item.reason })),
  estimatedTotal: 0,
  freeDeliveryThreshold: 199,
  status: batch.status,
  snoozedDays: batch.status === 'snoozed' ? 1 : undefined,
  reasons: ['Items were grouped from your current pantry forecast.'],
})

export const toUiShoppingList = (result) => ({
  id: crypto.randomUUID(),
  intent: result.intent,
  freeDeliveryThreshold: 199,
  items: result.items.map(item => ({
    id: crypto.randomUUID(),
    name: item.item_name,
    quantity: numberOr(item.quantity),
    unit: item.unit,
    category: 'Other',
    estimatedPrice: 0,
    checked: false,
    duplicateWarning: Boolean(item.pantry_warning),
    pantryQuantity: item.pantry_warning ? 'enough' : undefined,
  })),
})
