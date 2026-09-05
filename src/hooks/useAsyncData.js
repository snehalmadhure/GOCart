import { useCallback, useEffect, useState } from 'react'
export function useAsyncData(load) {
  const [data, setData] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const refresh = useCallback(async () => { setLoading(true); setError(''); try { setData(await load()) } catch { setError('Something went wrong while fetching your data.') } finally { setLoading(false) } }, [load])
  useEffect(() => { refresh() }, [refresh])
  return { data, setData, loading, error, refresh }
}
