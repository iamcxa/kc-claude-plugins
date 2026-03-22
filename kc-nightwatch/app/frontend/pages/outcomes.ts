import { html } from 'htm/preact'
import { useState, useEffect, useCallback } from 'preact/hooks'
import type { OutcomeRecord } from '../../shared/types.ts'
import { api } from '../lib/api.ts'
import { usePoll } from '../lib/use-poll.ts'
import { showToast } from '../lib/use-toast.ts'

function timeAgo(dateStr?: string): string {
  if (!dateStr) return '—'
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function statusDotColor(status: OutcomeRecord['status']): string {
  const colors: Record<string, string> = {
    open: 'var(--accent)',
    merged: 'var(--success)',
    completed: 'var(--success)',
    closed: 'var(--error)',
    cancelled: 'var(--muted)',
  }
  return colors[status] ?? 'var(--muted)'
}

function typeBadgeText(type: OutcomeRecord['type']): string {
  return type === 'pr' ? 'PR' : 'Issue'
}

export function Outcomes() {
  const [outcomes, setOutcomes] = useState<OutcomeRecord[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [targetFilter, setTargetFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [checking, setChecking] = useState(false)

  const loadOutcomes = useCallback(() => {
    api.getOutcomes().then(setOutcomes).catch(console.error)
  }, [])

  useEffect(() => {
    loadOutcomes()
  }, [])

  // Poll every 60s — outcomes change async after runs (per D-14)
  usePoll(loadOutcomes, 60_000, true)

  const filtered = outcomes.filter(o => {
    if (targetFilter && o.target !== targetFilter) return false
    if (typeFilter && o.type !== typeFilter) return false
    if (statusFilter && o.status !== statusFilter) return false
    return true
  })

  const uniqueTargets = [...new Set(outcomes.map(o => o.target))]
  const selectedOutcome = selectedId ? outcomes.find(o => o.id === selectedId) ?? null : null

  function handleCheckStatus() {
    if (!selectedOutcome) return
    setChecking(true)
    api.getOutcomeStatus(selectedOutcome.id)
      .then(res => {
        setOutcomes(prev => prev.map(o =>
          o.id === selectedOutcome.id ? { ...o, status: res.status } : o
        ))
        setChecking(false)
      })
      .catch(() => {
        showToast('Status check failed', 'error')
        setChecking(false)
      })
  }

  // Detail panel view
  if (selectedId && selectedOutcome) {
    const url = selectedOutcome.url
    const urlLabel = selectedOutcome.type === 'pr' ? 'View on GitHub' : 'View on Linear'

    return html`
      <div style="height:100%;display:flex;flex-direction:column;overflow:hidden;">
        <div style="padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;">
          <a href="#/outcomes" style="color:var(--muted);font-size:13px;" onClick=${() => setSelectedId(null)}>← Back to outcomes</a>
        </div>
        <div style="flex:1;overflow-y:auto;padding:16px;">
          <div style="background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin-bottom:12px;">
            <div style="display:flex;flex-direction:column;gap:8px;">
              <!-- Target -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Target</span>
                <span style="font-size:14px;">${selectedOutcome.target}</span>
              </div>
              <!-- Type -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Type</span>
                <span style="font-size:11px;padding:2px 6px;border-radius:4px;background:var(--btn-secondary);color:var(--muted);">
                  ${typeBadgeText(selectedOutcome.type)}
                </span>
              </div>
              <!-- Status -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Status</span>
                <span style="display:inline-flex;align-items:center;gap:6px;">
                  <span style="width:8px;height:8px;border-radius:50%;background:${statusDotColor(selectedOutcome.status)};flex-shrink:0;"></span>
                  <span style="font-size:14px;">${selectedOutcome.status}</span>
                </span>
              </div>
              <!-- Created -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Created</span>
                <span style="font-size:14px;" title=${selectedOutcome.created_at}>${timeAgo(selectedOutcome.created_at)}</span>
              </div>
              <!-- Signal ID -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Signal ID</span>
                <span style="font-size:12px;font-family:monospace;">${selectedOutcome.signal_id}</span>
              </div>
              <!-- Run ID -->
              <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;">Run ID</span>
                <span style="font-size:12px;font-family:monospace;">${selectedOutcome.run_id}</span>
              </div>
              <!-- URL -->
              <div style="display:flex;gap:12px;align-items:flex-start;">
                <span style="font-size:12px;color:var(--muted);min-width:80px;padding-top:2px;">URL</span>
                <div>
                  <a href=${url} target="_blank" rel="noopener noreferrer" style="color:var(--accent);font-size:14px;word-break:break-all;">
                    ${url}
                  </a>
                  <div style="font-size:12px;color:var(--muted);margin-top:2px;">${urlLabel}</div>
                </div>
              </div>
            </div>
          </div>
          <!-- Check status button -->
          <button
            onClick=${handleCheckStatus}
            disabled=${checking}
            style="padding:3px 8px;font-size:12px;border:1px solid var(--accent);color:var(--accent);background:transparent;cursor:pointer;border-radius:4px;"
          >
            ${checking ? 'Checking...' : 'Check status'}
          </button>
        </div>
      </div>
    `
  }

  // List view
  const hasNoOutcomes = outcomes.length === 0
  const hasNoMatch = outcomes.length > 0 && filtered.length === 0

  return html`
    <div style="height:100%;display:flex;flex-direction:column;overflow:hidden;">
      <!-- Filter bar -->
      <div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;gap:12px;flex-shrink:0;">
        <select
          value=${targetFilter}
          onChange=${(e: Event) => setTargetFilter((e.target as HTMLSelectElement).value)}
          style="padding:4px 8px;"
        >
          <option value="">All targets</option>
          ${uniqueTargets.map(t => html`<option key=${t} value=${t}>${t}</option>`)}
        </select>
        <select
          value=${typeFilter}
          onChange=${(e: Event) => setTypeFilter((e.target as HTMLSelectElement).value)}
          style="padding:4px 8px;"
        >
          <option value="">All types</option>
          <option value="pr">pr</option>
          <option value="linear_issue">linear_issue</option>
        </select>
        <select
          value=${statusFilter}
          onChange=${(e: Event) => setStatusFilter((e.target as HTMLSelectElement).value)}
          style="padding:4px 8px;"
        >
          <option value="">All statuses</option>
          <option value="open">open</option>
          <option value="merged">merged</option>
          <option value="closed">closed</option>
          <option value="completed">completed</option>
          <option value="cancelled">cancelled</option>
        </select>
      </div>
      <!-- Outcomes list -->
      <div style="flex:1;overflow-y:auto;">
        ${hasNoOutcomes && html`
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:200px;gap:8px;text-align:center;padding:16px;">
            <div style="font-size:16px;font-weight:600;">No outcomes recorded yet</div>
            <div style="font-size:13px;color:var(--muted);">Outcomes appear here after a run creates PRs or Linear issues.</div>
          </div>
        `}
        ${hasNoMatch && html`
          <div style="display:flex;align-items:center;justify-content:center;height:200px;color:var(--muted);">
            No outcomes match the current filters.
          </div>
        `}
        ${!hasNoOutcomes && !hasNoMatch && filtered.map(o => {
          const summaryText = `${typeBadgeText(o.type)} \u00b7 ${o.target}`
          const truncatedSummary = summaryText.length > 60 ? summaryText.slice(0, 60) + '...' : summaryText
          return html`
            <div
              key=${o.id}
              onClick=${() => setSelectedId(o.id)}
              style="padding:12px 16px;border-bottom:1px solid var(--border);cursor:pointer;display:flex;align-items:center;gap:8px;"
              onMouseEnter=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = 'var(--panel)' }}
              onMouseLeave=${(e: MouseEvent) => { (e.currentTarget as HTMLElement).style.background = '' }}
            >
              <span style="font-size:11px;padding:2px 6px;border-radius:4px;background:var(--btn-secondary);color:var(--muted);flex-shrink:0;">
                ${typeBadgeText(o.type)}
              </span>
              <span style="font-size:14px;font-weight:600;flex-shrink:0;">${o.target}</span>
              <span style="
                font-size:12px;
                color:var(--muted);
                flex:1;
                overflow:hidden;
                text-overflow:ellipsis;
                white-space:nowrap;
              ">${truncatedSummary}</span>
              <span style="width:8px;height:8px;border-radius:50%;background:${statusDotColor(o.status)};flex-shrink:0;"></span>
              <span style="font-size:12px;color:var(--muted);flex-shrink:0;">${timeAgo(o.created_at)}</span>
            </div>
          `
        })}
      </div>
    </div>
  `
}
