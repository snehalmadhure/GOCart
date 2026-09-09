import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Leaf } from 'lucide-react'
import { useAuth } from '../auth/AuthProvider'
import { supabase } from '../services/supabase'

export default function LoginPage() {
  const { session, isMockMode, isConfigured } = useAuth()
  const location = useLocation()
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const destination = location.state?.from?.pathname || '/pantry'

  if (isMockMode || session) return <Navigate to={destination} replace />

  async function submit(event) {
    event.preventDefault()
    setMessage('')
    setSubmitting(true)
    const result = mode === 'signup'
      ? await supabase.auth.signUp({ email, password })
      : await supabase.auth.signInWithPassword({ email, password })
    setSubmitting(false)
    if (result.error) {
      setMessage(result.error.message)
    } else if (mode === 'signup' && !result.data.session) {
      setMessage('Check your email to confirm your account, then sign in.')
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[#fafbf8] px-4"><section className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-7 shadow-sm sm:p-9"><div className="mb-7 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#1b2514] text-[#c6e395]"><Leaf size={21} /></span><div><h1 className="text-xl font-semibold text-[#171f11]">GOCart</h1><p className="text-sm text-slate-500">Your private pantry planner</p></div></div>{!isConfigured ? <p className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">Sign-in is not configured for this deployment yet.</p> : <><div className="mb-6 flex rounded-xl bg-slate-100 p-1 text-sm"><button type="button" onClick={() => setMode('signin')} className={`flex-1 rounded-lg py-2 ${mode === 'signin' ? 'bg-white font-medium shadow-sm' : 'text-slate-500'}`}>Sign in</button><button type="button" onClick={() => setMode('signup')} className={`flex-1 rounded-lg py-2 ${mode === 'signup' ? 'bg-white font-medium shadow-sm' : 'text-slate-500'}`}>Create account</button></div><form onSubmit={submit} className="space-y-4"><label className="block text-sm font-medium text-slate-700">Email<input required type="email" value={email} onChange={event => setEmail(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-[#49752c]" /></label><label className="block text-sm font-medium text-slate-700">Password<input required minLength="6" type="password" value={password} onChange={event => setPassword(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-[#49752c]" /></label>{message && <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">{message}</p>}<button disabled={submitting} className="w-full rounded-xl bg-[#314522] px-4 py-3 font-medium text-white disabled:opacity-60">{submitting ? 'Please wait…' : mode === 'signup' ? 'Create account' : 'Sign in'}</button></form></>}</section></main>
}
