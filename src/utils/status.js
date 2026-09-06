export const getPantryStatus = (item) => {
  if (item.status === 'unknown') return { key: 'learning', label: 'Learning', className: 'bg-slate-100 text-slate-600 ring-slate-200' }
  if (item.status === 'expired') return { key: 'expiring', label: 'Expired', className: 'bg-violet-50 text-violet-700 ring-violet-100' }
  if (item.status === 'out') return { key: 'urgent', label: 'Out of stock', className: 'bg-rose-50 text-rose-700 ring-rose-100' }
  if (item.expiryDate && (new Date(`${item.expiryDate}T12:00:00`) - new Date()) / 86400000 <= 2) return { key: 'expiring', label: 'Expiring Soon', className: 'bg-violet-50 text-violet-700 ring-violet-100' }
  if (item.daysRemaining <= 1) return { key: 'urgent', label: 'Low Stock', className: 'bg-rose-50 text-rose-700 ring-rose-100' }
  if (item.daysRemaining <= 3) return { key: 'restock', label: 'Restock Soon', className: 'bg-amber-50 text-amber-700 ring-amber-100' }
  return { key: 'healthy', label: 'Healthy', className: 'bg-emerald-50 text-emerald-700 ring-emerald-100' }
}
export const confidenceLabel = (value) => value >= .8 ? 'High' : value >= .65 ? 'Medium' : 'Low'
