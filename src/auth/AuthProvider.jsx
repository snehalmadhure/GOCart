import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { supabase, isSupabaseConfigured } from '../services/supabase'
import { useMockApi } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(!useMockApi)

  useEffect(() => {
    if (useMockApi) {
      setLoading(false)
      return undefined
    }
    if (!supabase) {
      setLoading(false)
      return undefined
    }
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setLoading(false)
    })
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, nextSession) => setSession(nextSession))
    return () => subscription.subscription.unsubscribe()
  }, [])

  const value = useMemo(() => ({
    session,
    user: session?.user ?? null,
    loading,
    isMockMode: useMockApi,
    isConfigured: isSupabaseConfigured,
    signOut: () => supabase?.auth.signOut(),
  }), [session, loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
