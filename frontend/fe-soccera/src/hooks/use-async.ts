import { useEffect, useState } from "react"

type AsyncState<T> = { data: T | null; error: Error | null; loading: boolean }

/**
 * Runs `load` whenever `key` changes and tracks its result. Responses for a
 * stale key are dropped, so fast navigation never shows the previous page's data.
 */
export function useAsync<T>(key: string | null, load: () => Promise<T>): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T> & { key: string | null }>({
    key: null,
    data: null,
    error: null,
    loading: false,
  })

  useEffect(() => {
    if (key === null) return
    let cancelled = false
    load()
      .then((data) => !cancelled && setState({ key, data, error: null, loading: false }))
      .catch((error: Error) => !cancelled && setState({ key, data: null, error, loading: false }))
    return () => {
      cancelled = true
    }
    // `load` is expected to change together with `key`.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  if (key === null) return { data: null, error: null, loading: false }
  if (state.key !== key) return { data: null, error: null, loading: true }
  return { data: state.data, error: state.error, loading: state.loading }
}
