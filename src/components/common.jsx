import { X, AlertCircle, LoaderCircle } from 'lucide-react'

export function Card({ className = '', children }) { return <section className={`card ${className}`}>{children}</section> }
export function Badge({ className = '', children }) { return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${className}`}>{children}</span> }
export function Modal({ open, title, children, onClose, wide = false }) {
  if (!open) return null
  return <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/35 p-3 backdrop-blur-[2px] sm:items-center" role="dialog" aria-modal="true" aria-label={title} onMouseDown={onClose}>
    <div className={`max-h-[92vh] w-full overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl sm:p-7 ${wide ? 'max-w-3xl' : 'max-w-xl'}`} onMouseDown={event => event.stopPropagation()}>
      <div className="mb-5 flex items-center justify-between gap-4"><h2 className="text-xl font-bold text-slate-900">{title}</h2><button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100" onClick={onClose} aria-label="Close dialog"><X size={20} /></button></div>{children}
    </div>
  </div>
}
export function EmptyState({ icon = '✦', title, children, action }) { return <Card className="p-10 text-center"><div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-emerald-50 text-xl">{icon}</div><h2 className="text-lg font-bold text-slate-900">{title}</h2><p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">{children}</p>{action && <div className="mt-5">{action}</div>}</Card> }
export function ErrorState({ title = "Couldn't load this page.", retry }) { return <Card className="p-9 text-center"><AlertCircle className="mx-auto mb-3 text-rose-500" size={28} /><h2 className="font-bold text-slate-900">{title}</h2><p className="mt-1 text-sm text-slate-500">Something went wrong while fetching your data.</p><button className="btn-primary mt-5" onClick={retry}>Try again</button></Card> }
export function Skeleton({ className = '' }) { return <div className={`animate-pulse rounded-xl bg-slate-100 ${className}`} /> }
export function LoadingCards({ count = 4 }) { return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{Array.from({ length: count }, (_, index) => <Card className="p-5" key={index}><Skeleton className="h-5 w-1/2" /><Skeleton className="mt-5 h-16" /><Skeleton className="mt-4 h-4 w-4/5" /></Card>)}</div> }
export function Spinner({ label = 'Loading…' }) { return <span className="inline-flex items-center gap-2"><LoaderCircle className="animate-spin" size={17} />{label}</span> }
export function Toast({ toast, onClose }) { if (!toast) return null; return <div className="fixed bottom-24 right-4 z-[60] max-w-sm rounded-2xl bg-slate-900 px-4 py-3 text-sm font-medium text-white shadow-xl sm:bottom-5" role="status"><div className="flex gap-3"><span className="text-emerald-300">✓</span><p>{toast}</p><button className="text-slate-300" onClick={onClose} aria-label="Dismiss notification"><X size={16} /></button></div></div> }
