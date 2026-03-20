import { useRef, useEffect } from 'preact/hooks'
import { signal } from '@preact/signals'

/**
 * Shared signal that SSE listeners increment to trigger an immediate re-fetch.
 * SSE event handlers call: refreshTrigger.value++
 * usePoll watches this signal — any increment triggers an immediate fetch outside the interval.
 */
export const refreshTrigger = signal(0)

/**
 * Reusable polling hook with SSE-driven immediate re-fetch capability.
 *
 * @param fetchFn   - The fetch function to call on each interval tick and on refreshTrigger increment
 * @param intervalMs - Polling interval in milliseconds (e.g. 5000)
 * @param shouldPoll - Boolean condition: true = start/maintain polling, false = stop polling
 *
 * Design: usePoll manages two effects:
 * 1. Interval polling — starts/stops based on shouldPoll
 * 2. refreshTrigger watch — SSE events increment this signal → immediate fetch outside interval
 *
 * fnRef pattern avoids stale closures: fetchFn is always the latest version
 * without being a useEffect dependency (which would restart the timer on every render).
 */
export function usePoll(fetchFn: () => void, intervalMs: number, shouldPoll: boolean): void {
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Always keep fnRef current — avoids stale closure without restarting interval
  const fnRef = useRef(fetchFn)
  fnRef.current = fetchFn

  // Effect 1: Interval-based polling — starts and stops based on shouldPoll
  useEffect(() => {
    if (shouldPoll && !timerRef.current) {
      timerRef.current = setInterval(() => fnRef.current(), intervalMs)
    } else if (!shouldPoll && timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [shouldPoll])

  // Effect 2: SSE-driven immediate re-fetch — triggered by refreshTrigger increments
  // Only fires when refreshTrigger.value > 0 (initial value 0 is skipped)
  useEffect(() => {
    if (refreshTrigger.value > 0) {
      fnRef.current()
    }
  }, [refreshTrigger.value])
}
