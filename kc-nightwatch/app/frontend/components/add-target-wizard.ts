import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import { api } from '../lib/api.ts'

interface Props {
  isOpen: boolean
  onClose: () => void
  onSaved: () => void
  editTarget?: { name: string; data: Record<string, unknown> } | null
}

const MONITOR_OPTIONS = ['github-issues', 'journal', 'git-churn', 'sentry', 'e2e-reports']
const RESPOND_OPTIONS = ['code-fix', 'proposal', 'e2e-flow']

export function AddTargetWizard({ isOpen, onClose, onSaved, editTarget }: Props) {
  const [step, setStep] = useState(1)
  const [name, setName] = useState('')
  const [type, setType] = useState<'plugin' | 'product'>('plugin')
  const [northStar, setNorthStar] = useState('')
  const [watchKeywords, setWatchKeywords] = useState('')
  const [monitors, setMonitors] = useState<string[]>([])
  const [respond, setRespond] = useState<Record<string, boolean>>({})
  const [targetPath, setTargetPath] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Pre-fill for edit mode
  useEffect(() => {
    if (editTarget) {
      setName(editTarget.name)
      setType((editTarget.data.type as 'plugin' | 'product') ?? 'plugin')
      setNorthStar((editTarget.data.north_star as string) ?? '')
      setWatchKeywords(Array.isArray(editTarget.data.watch) ? (editTarget.data.watch as string[]).join(', ') : '')
      setMonitors(Array.isArray(editTarget.data.monitors) ? editTarget.data.monitors as string[] : [])
      setRespond((editTarget.data.respond as Record<string, boolean>) ?? {})
      setTargetPath((editTarget.data.path as string) ?? '')
    } else {
      // Reset form
      setName(''); setType('plugin'); setNorthStar(''); setWatchKeywords('')
      setMonitors([]); setRespond({}); setTargetPath('')
    }
    setStep(1); setError('')
  }, [isOpen, editTarget])

  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen) return null

  function toggleMonitor(m: string) {
    setMonitors(prev => prev.includes(m) ? prev.filter(x => x !== m) : [...prev, m])
  }
  function toggleRespond(r: string) {
    setRespond(prev => ({ ...prev, [r]: !prev[r] }))
  }

  function buildTarget(): Record<string, unknown> {
    return {
      type,
      path: targetPath || undefined,
      north_star: northStar,
      monitors,
      watch: watchKeywords.split(',').map(s => s.trim()).filter(Boolean),
      respond: Object.fromEntries(Object.entries(respond).filter(([, v]) => v)),
      indicators: [],
    }
  }

  async function handleSave() {
    setSaving(true); setError('')
    try {
      const target = buildTarget()
      if (editTarget) {
        await api.editTarget(editTarget.name, target)
      } else {
        await api.addTarget(name, target)
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(String(err))
    }
    setSaving(false)
  }

  const isEdit = !!editTarget
  const title = isEdit ? `Edit ${editTarget!.name}` : 'Add Target'

  const dotStyle = (s: number) => `
    width:8px;height:8px;border-radius:50%;display:inline-block;
    background:${s < step ? 'var(--success)' : s === step ? 'var(--accent)' : 'var(--border)'};
  `

  return html`
    <div
      style="position:fixed;inset:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:100;"
      onClick=${onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="wizard-title"
        style="background:var(--panel);border:1px solid var(--border);border-radius:8px;max-width:520px;width:90%;padding:24px;"
        onClick=${(e: Event) => e.stopPropagation()}
      >
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <h3 id="wizard-title" style="margin:0;font-size:16px;">${title}</h3>
          <button onClick=${onClose} style="padding:3px 8px;font-size:12px;">X</button>
        </div>

        <!-- Step dots -->
        <div style="display:flex;gap:8px;margin-bottom:16px;justify-content:center;">
          ${[1,2,3,4].map(s => html`<div key=${s} style=${dotStyle(s)} />`)}
        </div>

        <!-- Step 1: Type + Name -->
        ${step === 1 && html`
          <div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Target type</div>
            <div style="display:flex;gap:0;margin-bottom:16px;">
              <button
                style="${type === 'plugin' ? 'background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);' : ''}border-radius:6px 0 0 6px;"
                onClick=${() => setType('plugin')}
              >Plugin</button>
              <button
                style="${type === 'product' ? 'background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);' : ''}border-radius:0 6px 6px 0;border-left:none;"
                onClick=${() => setType('product')}
              >Product</button>
            </div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Target name</div>
            <input
              value=${name}
              onInput=${(e: Event) => setName((e.target as HTMLInputElement).value)}
              placeholder="e.g. my-plugin"
              disabled=${isEdit}
              style="width:100%;margin-bottom:16px;"
            />
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Path (optional)</div>
            <input
              value=${targetPath}
              onInput=${(e: Event) => setTargetPath((e.target as HTMLInputElement).value)}
              placeholder="/absolute/path/to/target"
              style="width:100%;"
            />
          </div>
        `}

        <!-- Step 2: North star + goals -->
        ${step === 2 && html`
          <div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">North star</div>
            <textarea
              value=${northStar}
              onInput=${(e: Event) => setNorthStar((e.target as HTMLTextAreaElement).value)}
              placeholder="What is the ultimate goal for improving this target?"
              rows="3"
              style="width:100%;margin-bottom:16px;resize:vertical;"
            />
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Watch keywords (comma-separated)</div>
            <input
              value=${watchKeywords}
              onInput=${(e: Event) => setWatchKeywords((e.target as HTMLInputElement).value)}
              placeholder="e.g. coverage, test, performance"
              style="width:100%;"
            />
          </div>
        `}

        <!-- Step 3: Monitors + respond -->
        ${step === 3 && html`
          <div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Monitors</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
              ${MONITOR_OPTIONS.map(m => html`
                <label key=${m} style="display:flex;align-items:center;gap:4px;cursor:pointer;">
                  <input type="checkbox" checked=${monitors.includes(m)} onChange=${() => toggleMonitor(m)} />
                  ${m}
                </label>
              `)}
            </div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Respond actions</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
              ${RESPOND_OPTIONS.map(r => html`
                <label key=${r} style="display:flex;align-items:center;gap:4px;cursor:pointer;">
                  <input type="checkbox" checked=${respond[r] ?? false} onChange=${() => toggleRespond(r)} />
                  ${r}
                </label>
              `)}
            </div>
          </div>
        `}

        <!-- Step 4: Preview + save -->
        ${step === 4 && html`
          <div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:600;">Generated YAML preview</div>
            <pre style="font-family:var(--font-mono);font-size:13px;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;overflow-x:auto;max-height:300px;overflow-y:auto;">${
              JSON.stringify({ [name || 'unnamed']: buildTarget() }, null, 2)
            }</pre>
            ${error && html`
              <div style="background:rgba(248,81,73,0.1);border:1px solid var(--error);border-radius:6px;padding:8px 12px;font-size:14px;color:var(--error);margin-top:8px;">
                ${error}
              </div>
            `}
          </div>
        `}

        <!-- Navigation -->
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:16px;">
          ${step > 1 && html`
            <button onClick=${() => setStep(s => s - 1)}>Back</button>
          `}
          ${step < 4 && html`
            <button
              onClick=${() => setStep(s => s + 1)}
              disabled=${step === 1 && !name.trim() && !isEdit}
              style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);"
            >Next</button>
          `}
          ${step === 4 && html`
            <button
              onClick=${handleSave}
              disabled=${saving}
              style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);"
            >Validate & Save</button>
          `}
        </div>
      </div>
    </div>
  `
}
