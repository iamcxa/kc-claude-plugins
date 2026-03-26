import { html } from 'htm/preact'
import { useState } from 'preact/hooks'
import type { RunSummaryAction, OutcomeRecord, FeedbackEntry } from '../../shared/types.ts'
import { api } from '../lib/api.ts'

interface Props {
  action: RunSummaryAction
  target: string
  runId: string
  existingFeedback: FeedbackEntry[]
  outcomeStatus?: { status: OutcomeRecord['status']; url: string; type: OutcomeRecord['type'] } | null
  priorityScore?: number  // 0.0–1.0 from /api/signals/priority; undefined if not yet loaded
}

function badgeBg(status: OutcomeRecord['status']): string {
  const map: Record<string, string> = {
    open: 'rgba(88,166,255,0.15)', merged: 'rgba(63,185,80,0.15)',
    completed: 'rgba(63,185,80,0.15)', closed: 'rgba(248,81,73,0.15)',
    cancelled: 'rgba(139,148,158,0.15)',
  }
  return map[status] ?? 'transparent'
}

function badgeColor(status: OutcomeRecord['status']): string {
  const map: Record<string, string> = {
    open: 'var(--accent)', merged: 'var(--success)',
    completed: 'var(--success)', closed: 'var(--error)',
    cancelled: 'var(--muted)',
  }
  return map[status] ?? 'var(--muted)'
}

function badgeText(status: OutcomeRecord['status']): string {
  const map: Record<string, string> = {
    open: 'open', merged: 'merged', completed: 'done',
    closed: 'closed', cancelled: 'cancelled',
  }
  return map[status] ?? status
}

function sourceLabel(source: FeedbackEntry['source']): string {
  const labels: Record<string, string> = {
    user: 'manual',
    pr_status: 'PR status',
    linear_status: 'Linear',
    slack_reaction: 'Slack',
    pr_review: 'PR review',
  }
  return labels[source] ?? source
}

function verdictBg(verdict: FeedbackEntry['verdict']): string {
  if (verdict === 'accepted') return 'rgba(63,185,80,0.15)'
  if (verdict === 'rejected') return 'rgba(248,81,73,0.15)'
  return 'rgba(227,179,65,0.15)'
}

function verdictColor(verdict: FeedbackEntry['verdict']): string {
  if (verdict === 'accepted') return 'var(--success)'
  if (verdict === 'rejected') return 'var(--error)'
  return 'var(--warn)'
}

export function ActionCard({ action, target, runId, existingFeedback, outcomeStatus, priorityScore }: Props) {
  const [expanded, setExpanded] = useState(false)
  const userFeedback = existingFeedback.find(f => f.source === 'user')
  const [submitted, setSubmitted] = useState<'accepted' | 'rejected' | 'uncertain' | null>(userFeedback?.verdict ?? null)
  const autoFeedback = existingFeedback.filter(f => f.source !== 'user')

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
      setSubmitted(userFeedback?.verdict ?? null)
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
        ${priorityScore !== undefined ? html`
          <span
            title="Priority score: ${priorityScore} (${action.assessment.confidence} confidence, ${action.assessment.closer_to_north_star === 'yes' ? 'aligned' : action.assessment.closer_to_north_star === 'no' ? 'not aligned' : 'uncertain'} with north star)"
            style="font-size:11px;padding:2px 6px;border-radius:4px;font-weight:600;font-variant-numeric:tabular-nums;background:${priorityScore >= 0.67 ? 'rgba(63,185,80,0.12)' : priorityScore >= 0.34 ? 'rgba(227,179,65,0.12)' : 'rgba(139,148,158,0.12)'};color:${priorityScore >= 0.67 ? 'var(--success)' : priorityScore >= 0.34 ? 'var(--warn)' : 'var(--muted)'};"
          >${priorityScore.toFixed(2)} ${action.assessment.confidence}</span>
        ` : null}
        ${outcomeStatus ? html`
          <span style="font-size:11px;padding:2px 6px;border-radius:4px;font-weight:600;background:${badgeBg(outcomeStatus.status)};color:${badgeColor(outcomeStatus.status)};">${badgeText(outcomeStatus.status)}</span>
        ` : null}
        ${autoFeedback.length > 0 ? html`
          <span style="font-size:11px;padding:2px 6px;border-radius:4px;background:rgba(88,166,255,0.15);color:var(--accent);">${autoFeedback.length} feedback</span>
        ` : null}
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

          <!-- Reflection section (assessment verdict) -->
          <div style="margin-bottom:8px;">
            <div style="font-size:12px;color:var(--muted);font-weight:600;margin-bottom:4px;">Reflection</div>
            <div style="font-size:14px;line-height:1.5;color:var(--text);">
              ${action.assessment.closer_to_north_star === 'yes'
                ? 'This action moves closer to the north star.'
                : action.assessment.closer_to_north_star === 'no'
                ? 'This action may not align with the north star.'
                : 'Impact on the north star is uncertain.'}
              ${' '}Confidence: ${action.assessment.confidence}.
            </div>
          </div>

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

          <!-- Outcome URL -->
          ${outcomeStatus?.url ? html`
            <div style="margin-bottom:8px;">
              <a href=${outcomeStatus.url} target="_blank" rel="noopener noreferrer" style="font-size:12px;color:var(--accent);">
                ${outcomeStatus.type === 'pr' ? 'View on GitHub' : 'View on Linear'}
              </a>
            </div>
          ` : null}

          <!-- Auto-collected feedback entries -->
          ${autoFeedback.length > 0 && html`
            <div style="margin-bottom:8px;padding:6px 8px;background:var(--panel);border-radius:4px;">
              <div style="font-size:11px;color:var(--muted);font-weight:600;margin-bottom:4px;">Auto-collected Feedback</div>
              ${autoFeedback.map(f => html`
                <div key=${f.signal_id + f.source + f.submitted_at} style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                  <span style="font-size:11px;padding:1px 4px;border-radius:3px;background:${verdictBg(f.verdict)};color:${verdictColor(f.verdict)};">${f.verdict}</span>
                  <span style="font-size:11px;padding:1px 4px;border-radius:3px;background:var(--btn-secondary);color:var(--muted);">${sourceLabel(f.source)}</span>
                  ${f.reason ? html`<span style="font-size:11px;color:var(--muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${f.reason}</span>` : null}
                </div>
              `)}
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
