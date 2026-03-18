import { html } from 'htm/preact'
import { useState } from 'preact/hooks'
import type { RunSummaryAction } from '../../shared/types.ts'
import { api } from '../lib/api.ts'

interface Props {
  action: RunSummaryAction
  target: string
  runId: string
  existingFeedback?: 'accepted' | 'rejected' | null
}

export function ActionCard({ action, target, runId, existingFeedback }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [submitted, setSubmitted] = useState<'accepted' | 'rejected' | null>(existingFeedback ?? null)

  async function handleFeedback(verdict: 'accepted' | 'rejected') {
    setSubmitted(verdict) // Optimistic disable (Pitfall 5: double-submit prevention)
    try {
      await api.submitFeedback({
        signal_id: action.signal_id,
        target,
        run_id: runId,
        verdict,
      })
    } catch {
      // Revert on failure
      setSubmitted(existingFeedback ?? null)
    }
  }

  const confidenceColor = action.assessment.confidence === 'high' ? 'var(--success)'
    : action.assessment.confidence === 'medium' ? 'var(--warn)'
    : 'var(--muted)'

  return html`
    <div style="border:1px solid var(--border);border-radius:6px;margin-bottom:8px;overflow:hidden;">
      <!-- Collapsed header (always visible) -->
      <div
        onClick=${() => setExpanded((prev: boolean) => !prev)}
        aria-expanded=${expanded}
        style="padding:8px 12px;cursor:pointer;display:flex;align-items:center;gap:8px;background:${expanded ? 'var(--panel)' : 'transparent'};"
        onMouseEnter=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = 'var(--panel)' }}
        onMouseLeave=${(e: MouseEvent) => { if (!expanded) (e.currentTarget as HTMLElement).style.background = '' }}
      >
        <span style="flex:1;font-size:14px;">${action.summary}</span>
        <span style="font-size:11px;padding:2px 6px;border-radius:4px;background:var(--btn-secondary);color:var(--muted);">${action.type}</span>
        <span style="font-size:11px;color:${confidenceColor};font-weight:600;">${action.assessment.confidence}</span>
        <span style="font-size:12px;color:var(--muted);">${expanded ? '\u25B2' : '\u25BC'}</span>
      </div>

      <!-- Expanded content -->
      ${expanded && html`
        <div style="padding:8px 12px;border-top:1px solid var(--border);">
          <!-- Strategy section -->
          ${action.assessment.reasoning && html`
            <div style="margin-bottom:8px;">
              <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:4px;">Strategy</div>
              <div style="font-size:14px;line-height:1.5;color:var(--text);">${action.assessment.reasoning}</div>
            </div>
          `}

          <!-- Indicator -->
          <div style="margin-bottom:8px;">
            <span style="font-size:12px;color:var(--muted);">Indicator: </span>
            <span style="font-size:12px;color:var(--text);">${action.indicator}</span>
            <span style="font-size:12px;color:${confidenceColor};margin-left:8px;">
              ${action.assessment.closer_to_north_star === 'yes' ? '\u2191 Closer'
                : action.assessment.closer_to_north_star === 'no' ? '\u2193 Further'
                : '\u2192 Uncertain'}
            </span>
          </div>

          <!-- PR link -->
          ${action.pr_url && html`
            <div style="margin-bottom:8px;">
              <a href=${action.pr_url} target="_blank" style="font-size:12px;">View PR</a>
            </div>
          `}

          <!-- Feedback buttons -->
          <div style="display:flex;gap:4px;justify-content:flex-end;padding-top:4px;">
            <button
              aria-label="Accept signal"
              aria-pressed=${submitted === 'accepted'}
              disabled=${submitted !== null}
              onClick=${(e: Event) => { e.stopPropagation(); void handleFeedback('accepted') }}
              style="
                padding:3px 8px;font-size:12px;border-radius:4px;
                background:${submitted === 'accepted' ? 'var(--success)' : 'var(--btn-secondary)'};
                color:${submitted === 'accepted' ? '#fff' : 'var(--muted)'};
                border:1px solid ${submitted === 'accepted' ? 'var(--success)' : 'var(--border)'};
                cursor:${submitted ? 'not-allowed' : 'pointer'};
                opacity:${submitted !== null && submitted !== 'accepted' ? '0.5' : '1'};
              "
            >+1</button>
            <button
              aria-label="Reject signal"
              aria-pressed=${submitted === 'rejected'}
              disabled=${submitted !== null}
              onClick=${(e: Event) => { e.stopPropagation(); void handleFeedback('rejected') }}
              style="
                padding:3px 8px;font-size:12px;border-radius:4px;
                background:${submitted === 'rejected' ? 'var(--error)' : 'var(--btn-secondary)'};
                color:${submitted === 'rejected' ? '#fff' : 'var(--muted)'};
                border:1px solid ${submitted === 'rejected' ? 'var(--error)' : 'var(--border)'};
                cursor:${submitted ? 'not-allowed' : 'pointer'};
                opacity:${submitted !== null && submitted !== 'rejected' ? '0.5' : '1'};
              "
            >-1</button>
          </div>
        </div>
      `}
    </div>
  `
}
