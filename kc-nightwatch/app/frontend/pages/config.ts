import { html } from 'htm/preact'

export function Config() {
  return html`
    <div style="display:flex;align-items:center;justify-content:center;height:100%;flex-direction:column;gap:16px;">
      <div style="font-size:48px;">🔒</div>
      <h2 style="margin:0;font-size:18px;color:var(--text);">Config</h2>
      <p style="margin:0;color:var(--muted);text-align:center;max-width:400px;line-height:1.6;">
        Config editor coming in Phase 3. Edit targets.yaml directly for now.
      </p>
    </div>
  `
}
