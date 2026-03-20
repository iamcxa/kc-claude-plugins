import { html } from 'htm/preact'
import { useEffect } from 'preact/hooks'
import { signal } from '@preact/signals'
import { registerToastHandler } from '../lib/use-toast.ts'
import type { ToastItem } from '../lib/use-toast.ts'

// Module-level signal — data only, no DOM manipulation at module scope
const toasts = signal<ToastItem[]>([])
let nextId = 0

function removeToast(id: number): void {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

/**
 * Toast overlay component. Mount once at the app root.
 * Registers the toast handler so showToast() works from any module.
 *
 * z-index:300 — above TriggerDialog overlay (z-index:100).
 * The "Run queued" toast fires while the dialog is still visible.
 */
export function Toast() {
  useEffect(() => {
    registerToastHandler((message, type) => {
      const toast: ToastItem = { id: nextId++, message, type }
      toasts.value = [toast, ...toasts.value].slice(0, 3)

      if (type === 'success') {
        // Auto-dismiss after 4 seconds
        setTimeout(() => removeToast(toast.id), 4000)
      }
      // Error toasts stay until manually closed
    })

    return () => {
      // Unregister on unmount to avoid stale handler
      registerToastHandler(null)
    }
  }, [])

  const items = toasts.value

  if (items.length === 0) return null

  return html`
    <div
      style="position:fixed;top:16px;right:16px;z-index:300;display:flex;flex-direction:column;gap:8px;pointer-events:none;"
      aria-live="polite"
      aria-label="Notifications"
    >
      ${items.map(t => {
        const isSuccess = t.type === 'success'
        const bgColor = isSuccess ? '#1a3a1a' : '#3a1a1a'
        const borderColor = isSuccess ? 'var(--success)' : 'var(--error)'
        const textColor = isSuccess ? 'var(--success)' : 'var(--error)'
        const icon = isSuccess ? '\u2713' : '\u2717'

        return html`
          <div
            key=${t.id}
            role="alert"
            style="pointer-events:auto;padding:12px 16px;border-radius:8px;display:flex;align-items:center;gap:8px;min-width:280px;max-width:400px;box-shadow:0 4px 12px rgba(0,0,0,0.4);font-size:14px;background:${bgColor};border:1px solid ${borderColor};color:${textColor};"
          >
            <span aria-hidden="true">${icon}</span>
            <span style="flex:1;">${t.message}</span>
            ${!isSuccess && html`
              <button
                onClick=${() => removeToast(t.id)}
                aria-label="Dismiss"
                style="cursor:pointer;background:none;border:none;color:inherit;font-size:16px;margin-left:auto;padding:0;"
              >\u2715</button>
            `}
          </div>
        `
      })}
    </div>
  `
}
