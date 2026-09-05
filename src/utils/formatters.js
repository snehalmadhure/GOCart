export const money = (value = 0) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value)
export const shortDate = (value) => value ? new Intl.DateTimeFormat('en-IN', { month: 'short', day: 'numeric' }).format(new Date(`${value}T12:00:00`)) : 'Not available'
export const fullDate = (value) => value ? new Intl.DateTimeFormat('en-IN', { month: 'long', day: 'numeric', year: 'numeric' }).format(new Date(`${value}T12:00:00`)) : 'Not available'
export const quantity = (value, unit) => `${value}${unit === '%' ? '%' : ` ${unit}`}`
export const daysLabel = (days) => days <= 1 ? 'tomorrow' : days < 2 ? '1–2 days' : `~${Math.round(days)} days`
