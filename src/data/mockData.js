export const pantryItems = [
  { id: 'milk', name: 'Milk', quantityRemaining: 0.4, unit: 'L', consumptionRate: 250, consumptionUnit: 'ml/day', daysRemaining: 1.5, predictedRunoutDate: '2026-09-07', confidence: .92, status: 'urgent', lastPurchaseDate: '2026-09-04', history: [{ date: 'Sep 4', quantity: '1 L' }, { date: 'Sep 1', quantity: '1 L' }, { date: 'Aug 29', quantity: '1 L' }] },
  { id: 'bread', name: 'Bread', quantityRemaining: .5, unit: 'loaf', consumptionRate: .25, consumptionUnit: 'loaf/day', daysRemaining: 1, predictedRunoutDate: '2026-09-06', confidence: .73, status: 'urgent', lastPurchaseDate: '2026-09-02', history: [{ date: 'Sep 2', quantity: '1 loaf' }, { date: 'Aug 28', quantity: '1 loaf' }, { date: 'Aug 24', quantity: '1 loaf' }] },
  { id: 'bananas', name: 'Bananas', quantityRemaining: 3, unit: 'pieces', consumptionRate: 1, consumptionUnit: 'piece/day', daysRemaining: 2, predictedRunoutDate: '2026-09-08', expiryDate: '2026-09-07', confidence: .88, status: 'restock-soon', lastPurchaseDate: '2026-09-03', history: [] },
  { id: 'eggs', name: 'Eggs', quantityRemaining: 4, unit: 'pieces', consumptionRate: 1, consumptionUnit: 'piece/day', daysRemaining: 4, predictedRunoutDate: '2026-09-10', confidence: .83, status: 'healthy', lastPurchaseDate: '2026-09-01', history: [] },
  { id: 'pasta', name: 'Pasta', quantityRemaining: 350, unit: 'g', consumptionRate: 35, consumptionUnit: 'g/day', daysRemaining: 10, predictedRunoutDate: '2026-09-16', confidence: .68, status: 'healthy', lastPurchaseDate: '2026-08-30', history: [] },
  { id: 'coffee', name: 'Coffee', quantityRemaining: 30, unit: '%', consumptionRate: 4, consumptionUnit: '%/day', daysRemaining: 18, predictedRunoutDate: '2026-09-24', confidence: .95, status: 'healthy', lastPurchaseDate: '2026-08-21', history: [] },
  { id: 'rice', name: 'Rice', quantityRemaining: 2, unit: 'kg', consumptionRate: 80, consumptionUnit: 'g/day', daysRemaining: 25, predictedRunoutDate: '2026-10-01', confidence: .86, status: 'healthy', lastPurchaseDate: '2026-08-20', history: [] },
  { id: 'oil', name: 'Cooking Oil', quantityRemaining: 60, unit: '%', consumptionRate: 2, consumptionUnit: '%/day', daysRemaining: 30, predictedRunoutDate: '2026-10-06', confidence: .59, status: 'healthy', lastPurchaseDate: '2026-08-13', history: [] },
  { id: 'tomatoes', name: 'Tomatoes', quantityRemaining: 4, unit: 'pieces', consumptionRate: .6, consumptionUnit: 'piece/day', daysRemaining: 6, predictedRunoutDate: '2026-09-12', confidence: .81, status: 'healthy', lastPurchaseDate: '2026-09-02', history: [] },
  { id: 'onions', name: 'Onions', quantityRemaining: 5, unit: 'pieces', consumptionRate: .3, consumptionUnit: 'piece/day', daysRemaining: 16, predictedRunoutDate: '2026-09-22', confidence: .9, status: 'healthy', lastPurchaseDate: '2026-08-28', history: [] },
  { id: 'garlic', name: 'Garlic', quantityRemaining: 2, unit: 'bulbs', consumptionRate: .15, consumptionUnit: 'bulb/day', daysRemaining: 14, predictedRunoutDate: '2026-09-20', confidence: .67, status: 'healthy', lastPurchaseDate: '2026-08-30', history: [] },
  { id: 'cheese', name: 'Cheese', quantityRemaining: 150, unit: 'g', consumptionRate: 20, consumptionUnit: 'g/day', daysRemaining: 8, predictedRunoutDate: '2026-09-14', confidence: .78, status: 'healthy', lastPurchaseDate: '2026-08-31', history: [] },
  { id: 'butter', name: 'Butter', quantityRemaining: 180, unit: 'g', consumptionRate: 12, consumptionUnit: 'g/day', daysRemaining: 15, predictedRunoutDate: '2026-09-21', confidence: .85, status: 'healthy', lastPurchaseDate: '2026-08-27', history: [] },
  { id: 'yogurt', name: 'Yogurt', quantityRemaining: 2, unit: 'cups', consumptionRate: .25, consumptionUnit: 'cup/day', daysRemaining: 8, predictedRunoutDate: '2026-09-14', confidence: .77, status: 'healthy', lastPurchaseDate: '2026-09-01', history: [] },
  { id: 'flour', name: 'Flour', quantityRemaining: 1, unit: 'kg', consumptionRate: 50, consumptionUnit: 'g/day', daysRemaining: 20, predictedRunoutDate: '2026-09-26', confidence: .7, status: 'healthy', lastPurchaseDate: '2026-08-20', history: [] },
]

export const purchases = [
  { id: 'p1', itemName: 'Bread', quantity: 1, unit: 'loaf', purchaseDate: '2026-09-04', price: 40, category: 'Bakery', expiryDate: '2026-09-07', notes: '' },
  { id: 'p2', itemName: 'Milk', quantity: 1, unit: 'litre', purchaseDate: '2026-09-03', price: 60, category: 'Dairy', expiryDate: '2026-09-07', notes: '' },
  { id: 'p3', itemName: 'Eggs', quantity: 12, unit: 'piece', purchaseDate: '2026-09-01', price: 75, category: 'Eggs', expiryDate: '', notes: '' },
  { id: 'p4', itemName: 'Bananas', quantity: 6, unit: 'piece', purchaseDate: '2026-09-03', price: 45, category: 'Fruits', expiryDate: '2026-09-08', notes: 'Weekend grocery order' },
  { id: 'p5', itemName: 'Pasta', quantity: 500, unit: 'g', purchaseDate: '2026-08-30', price: 95, category: 'Grains', expiryDate: '', notes: '' },
]

export const reminders = [
  { id: 'r1', type: 'restock', title: 'Restock recommended', scheduledDate: '2026-09-06', items: [{ itemName: 'Bread', reason: 'Likely to run out tomorrow' }, { itemName: 'Milk', reason: 'Likely to run out in 1–2 days' }, { itemName: 'Bananas', reason: 'Expected to run out in 2 days' }], estimatedTotal: 155, freeDeliveryThreshold: 149, status: 'pending', reasons: ['These items are expected to run out within 48 hours.', 'Ordering together avoids a separate low-value order.', 'This cart meets your free-delivery threshold.'] },
  { id: 'r2', type: 'upcoming', title: 'Plan ahead', scheduledDate: '2026-09-10', items: [{ itemName: 'Eggs', reason: 'Expected to run out in ~4 days' }], estimatedTotal: 75, freeDeliveryThreshold: 149, status: 'pending', reasons: ['We’ll wait to batch this with your next order.'] },
]

export const generatedList = { id: 'sl-123', intent: 'Dinner for 4, making pasta', freeDeliveryThreshold: 149, items: [
  { id: 'i1', name: 'Pasta', quantity: 500, unit: 'g', category: 'Grains', estimatedPrice: 70, inPantry: false },
  { id: 'i2', name: 'Tomatoes', quantity: 500, unit: 'g', category: 'Vegetables', estimatedPrice: 35, inPantry: false },
  { id: 'i3', name: 'Onion', quantity: 2, unit: 'pieces', category: 'Vegetables', estimatedPrice: 20, inPantry: false },
  { id: 'i4', name: 'Garlic', quantity: 1, unit: 'bulb', category: 'Vegetables', estimatedPrice: 15, inPantry: false },
  { id: 'i5', name: 'Cheese', quantity: 200, unit: 'g', category: 'Dairy', estimatedPrice: 95, inPantry: false },
  { id: 'i6', name: 'Olive Oil', quantity: 100, unit: 'ml', category: 'Cooking', estimatedPrice: 30, inPantry: true, pantryQuantity: '60%', duplicateWarning: true },
] }
