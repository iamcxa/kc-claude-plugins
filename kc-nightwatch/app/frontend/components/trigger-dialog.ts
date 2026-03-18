import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { Run } from '../../shared/types.ts'

interface TriggerOpts {
  mode: Run['mode']
  custom_prompt?: string
  self_repair: boolean
}

interface Props {
  target: string
  isOpen: boolean
  onClose: () => void
  onStart: (opts: TriggerOpts) => void
  isDisabled: boolean
}

export function TriggerDialog({ target, isOpen, onClose, onStart, isDisabled }: Props) {
  const [mode, setMode] = useState<'production' | 'dry-run'>('production')
  const [customPrompt, setCustomPrompt] = useState('')
  const [selfRepair, setSelfRepair] = useState(true)

  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const title = target === '__all__' ? 'Run all targets' : `Run ${target}`

  function handleStart() {
    onStart({ mode, custom_prompt: customPrompt || undefined, self_repair: selfRepair })
    onClose()
  }

  const modeActiveStyle = 'background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);'
  const modeInactiveStyle = 'background:var(--btn-secondary);color:var(--muted);border-color:var(--border);'

  return html`
    <div
      style="position:fixed;inset:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:100;"
      onClick=${onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        style="background:var(--panel);border:1px solid var(--border);border-radius:8px;max-width:480px;width:90%;padding:24px;"
        onClick=${(e: Event) => e.stopPropagation()}
      >
        <h3 style="margin:0 0 16px;font-size:16px;">${title}</h3>

        <!-- Mode toggle -->
        <div style="margin-bottom:16px;">
          <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Mode</div>
          <div style="display:flex;gap:0;">
            <button
              style="${mode === 'production' ? modeActiveStyle : modeInactiveStyle}border-radius:6px 0 0 6px;"
              onClick=${() => setMode('production')}
            >Production</button>
            <button
              style="${mode === 'dry-run' ? modeActiveStyle : modeInactiveStyle}border-radius:0 6px 6px 0;border-left:none;"
              onClick=${() => setMode('dry-run')}
            >Dry Run</button>
          </div>
        </div>

        <!-- Custom instructions -->
        <div style="margin-bottom:16px;">
          <label style="display:block;font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:600;" htmlFor="custom-prompt">Custom instructions (optional)</label>
          <textarea
            id="custom-prompt"
            rows="4"
            placeholder="Optional: additional instructions for this run"
            value=${customPrompt}
            onInput=${(e: Event) => setCustomPrompt((e.target as HTMLTextAreaElement).value)}
            style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:8px;font-family:inherit;resize:vertical;"
          ></textarea>
        </div>

        <!-- Self-repair toggle -->
        <div style="margin-bottom:24px;display:flex;align-items:center;gap:8px;">
          <input
            type="checkbox"
            id="self-repair"
            checked=${selfRepair}
            onChange=${(e: Event) => setSelfRepair((e.target as HTMLInputElement).checked)}
          />
          <label htmlFor="self-repair" style="cursor:pointer;">Run self-repair first</label>
        </div>

        <!-- Footer -->
        <div style="display:flex;justify-content:flex-end;gap:8px;">
          <button onClick=${onClose}>Never mind</button>
          <button
            onClick=${handleStart}
            disabled=${isDisabled}
            style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);"
          >Start Run</button>
        </div>
      </div>
    </div>
  `
}
