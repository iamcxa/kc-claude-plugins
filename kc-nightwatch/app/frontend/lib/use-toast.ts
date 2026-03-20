// Toast notification system — module-level callback registration (no prop drilling)

export type ToastType = 'success' | 'error'

export interface ToastItem {
  id: number
  message: string
  type: ToastType
}

// Module-level handler — registered by the Toast component on mount
let _handler: ((msg: string, type: ToastType) => void) | null = null

/**
 * Called by the Toast component in its useEffect to register the handler.
 * Only one handler is active at a time (single Toast component in the tree).
 */
export function registerToastHandler(fn: ((msg: string, type: ToastType) => void) | null): void {
  _handler = fn
}

/**
 * Show a toast notification from any module without prop drilling.
 * Falls back silently if Toast component is not mounted.
 */
export function showToast(message: string, type: ToastType = 'success'): void {
  _handler?.(message, type)
}
