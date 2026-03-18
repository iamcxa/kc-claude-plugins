import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { ConfigValidationResult } from '../../shared/types.ts'
import { api } from '../lib/api.ts'

type ConfigTab = 'targets' | 'safety'

export function Config() {
  const [tab, setTab] = useState<ConfigTab>('targets')
  const [content, setContent] = useState('')
  const [originalContent, setOriginalContent] = useState('')
  const [editing, setEditing] = useState(false)
  const [validating, setValidating] = useState(false)
  const [validationStep, setValidationStep] = useState(0)
  const [validationResult, setValidationResult] = useState<ConfigValidationResult | null>(null)
  const [warnings, setWarnings] = useState<Record<string, unknown>>({})
  const [saving, setSaving] = useState(false)

  // Load config content when tab changes
  useEffect(() => {
    setEditing(false)
    setValidationResult(null)
    setValidationStep(0)
    api.getConfig(tab).then(r => {
      setContent(r.content)
      setOriginalContent(r.content)
    }).catch(console.error)
  }, [tab])

  // Load warnings once
  useEffect(() => {
    api.getConfigWarnings().then(r => setWarnings(r.warnings)).catch(console.error)
  }, [])

  function handleEdit() { setEditing(true) }
  function handleDiscard() {
    setContent(originalContent)
    setEditing(false)
    setValidationResult(null)
    setValidationStep(0)
  }

  async function handleValidate() {
    setValidating(true)
    setValidationStep(1)
    // Step 1: Static parse (instant, happens server-side)
    // Step 2: Haiku semantic (server-side)
    setValidationStep(2)
    try {
      const result = await api.validateConfig(tab, content)
      setValidationResult(result)
      setValidationStep(result.valid ? 3 : 1)
    } catch (err) {
      setValidationResult({ valid: false, step: 'static', error: String(err) })
      setValidationStep(1)
    }
    setValidating(false)
  }

  async function handleConfirmSave() {
    setSaving(true)
    try {
      await api.saveConfig(tab, content)
      setOriginalContent(content)
      setEditing(false)
      setValidationResult(null)
      setValidationStep(0)
    } catch (err) {
      console.error('Save failed:', err)
    }
    setSaving(false)
  }

  // Extract warnings for current tab
  const tabWarnings: string[] = []
  if (warnings && typeof warnings === 'object') {
    // self-repair.yaml structure: { config_fixes: [...], ... }
    const fixes = (warnings as any).config_fixes
    if (Array.isArray(fixes)) {
      for (const fix of fixes) {
        if (typeof fix === 'object' && fix.message) {
          tabWarnings.push(fix.message)
        }
      }
    }
  }

  return html`
    <div style="height:100%;display:flex;flex-direction:column;overflow:hidden;padding:16px;">
      <!-- Tab strip -->
      <div role="tablist" style="display:flex;border-bottom:1px solid var(--border);margin-bottom:16px;">
        <button
          role="tab"
          aria-selected=${tab === 'targets'}
          onClick=${() => setTab('targets')}
          style="padding:8px 16px;font-size:14px;cursor:pointer;border:none;border-bottom:2px solid ${tab === 'targets' ? 'var(--accent)' : 'transparent'};background:none;color:${tab === 'targets' ? 'var(--text)' : 'var(--muted)'};font-weight:${tab === 'targets' ? '600' : '400'};"
        >Targets</button>
        <button
          role="tab"
          aria-selected=${tab === 'safety'}
          onClick=${() => setTab('safety')}
          style="padding:8px 16px;font-size:14px;cursor:pointer;border:none;border-bottom:2px solid ${tab === 'safety' ? 'var(--accent)' : 'transparent'};background:none;color:${tab === 'safety' ? 'var(--text)' : 'var(--muted)'};font-weight:${tab === 'safety' ? '600' : '400'};"
        >Safety</button>
      </div>

      <!-- Warnings -->
      ${tabWarnings.length > 0 && html`
        <div style="margin-bottom:8px;display:flex;flex-wrap:wrap;gap:4px;">
          ${tabWarnings.map((w, i) => html`
            <span key=${i} style="background:rgba(210,153,34,0.2);color:var(--warn);border:1px solid var(--warn);border-radius:4px;font-size:11px;padding:2px 6px;">Warning: ${w}</span>
          `)}
        </div>
      `}

      <!-- Toolbar -->
      <div style="display:flex;gap:8px;margin-bottom:8px;align-items:center;">
        ${!editing && html`
          <button onClick=${handleEdit}>Edit</button>
          <span style="font-size:12px;color:var(--muted);">Read only -- click Edit to make changes</span>
        `}
        ${editing && html`
          <button onClick=${handleValidate} disabled=${validating || saving}>Validate</button>
          <button onClick=${handleDiscard} disabled=${validating || saving}>Discard Changes</button>
        `}
      </div>

      <!-- YAML editor -->
      <textarea
        aria-label="${tab === 'targets' ? 'Targets' : 'Safety'} configuration"
        aria-readonly=${!editing}
        value=${content}
        onInput=${(e: Event) => setContent((e.target as HTMLTextAreaElement).value)}
        disabled=${!editing}
        style="
          font-family:var(--font-mono);font-size:14px;line-height:1.6;
          width:100%;min-height:400px;resize:vertical;
          background:var(--bg);color:var(--text);
          border:1px solid ${editing ? 'var(--accent)' : 'var(--border)'};
          border-radius:6px;padding:12px;
          opacity:${editing ? '1' : '0.7'};
          cursor:${editing ? 'text' : 'default'};
        "
      />

      <!-- Validation results -->
      ${validating && html`
        <div style="margin-top:8px;font-size:12px;color:var(--muted);">
          Step ${validationStep} of 4: ${validationStep === 1 ? 'Syntax check' : 'Checking semantics... (~$0.01)'}
        </div>
      `}

      ${validationResult && !validationResult.valid && html`
        <div style="background:rgba(248,81,73,0.1);border:1px solid var(--error);border-radius:6px;padding:8px 12px;font-size:14px;color:var(--error);margin-top:8px;">
          Syntax error: ${validationResult.error}
        </div>
      `}

      ${validationResult?.valid && validationResult.haiku_verdict && html`
        <div style="margin-top:8px;">
          <div style="font-size:12px;color:var(--muted);margin-bottom:4px;">Step 2 of 4: Semantic check</div>
          <div style="font-size:14px;color:${validationResult.haiku_verdict.startsWith('WARN') ? 'var(--warn)' : 'var(--success)'};">
            ${validationResult.haiku_verdict.startsWith('WARN') ? validationResult.haiku_verdict : 'Semantics OK'}
          </div>
        </div>
      `}

      ${validationResult?.valid && validationResult.diff && html`
        <div style="margin-top:8px;">
          <div style="font-size:12px;color:var(--muted);margin-bottom:4px;">Step 3 of 4: Changes preview</div>
          <div style="font-family:var(--font-mono);font-size:13px;line-height:1.4;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:8px;max-height:200px;overflow-y:auto;">
            ${validationResult.diff.map((d, i) => html`
              <div key=${i} style="color:${d.type === 'add' ? 'var(--success)' : d.type === 'remove' ? 'var(--error)' : 'var(--text)'};">
                ${d.type === 'add' ? '+ ' : d.type === 'remove' ? '- ' : '  '}${d.line}
              </div>
            `)}
          </div>
        </div>
      `}

      ${validationResult?.valid && validationStep >= 3 && html`
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button
            onClick=${handleConfirmSave}
            disabled=${saving}
            style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);"
          >Confirm Save</button>
          <span style="font-size:12px;color:var(--muted);align-self:center;">Step 4 of 4</span>
        </div>
      `}
    </div>
  `
}
