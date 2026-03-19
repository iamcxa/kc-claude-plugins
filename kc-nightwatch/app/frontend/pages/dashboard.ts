import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import type { Target, Run } from '../../shared/types.ts'
import { Sidebar } from '../components/sidebar.ts'
import { TargetDetail } from '../components/target-detail.ts'
import { TriggerDialog } from '../components/trigger-dialog.ts'
import { api } from '../lib/api.ts'

interface DashboardProps {
  healthData?: Record<string, { health: 'improving' | 'stable' | 'degrading' }>
}

export function Dashboard({ healthData }: DashboardProps = {}) {
  const [targets, setTargets] = useState<Target[]>([])
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)
  const [lastRuns, setLastRuns] = useState<Record<string, Run>>({})
  const [showDialog, setShowDialog] = useState(false)
  const [dialogTarget, setDialogTarget] = useState('')
  const [hasActiveRun, setHasActiveRun] = useState(false)
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    // Fetch targets
    api.getTargets().then(list => {
      setTargets(list)
    }).catch(console.error)

    // Fetch runs and build lastRuns map (most recent per target)
    loadRuns()
  }, [])

  function loadRuns() {
    api.getRuns().then(runs => {
      const map: Record<string, Run> = {}
      // Sort by started_at desc, take first per target
      const sorted = [...runs].sort((a, b) => {
        const at = a.started_at ?? ''
        const bt = b.started_at ?? ''
        return bt.localeCompare(at)
      })
      for (const run of sorted) {
        if (!map[run.target]) {
          map[run.target] = run
        }
      }
      setLastRuns(map)

      // Check if any runs are active
      const active = runs.some(r => r.status === 'running' || r.status === 'queued')
      setHasActiveRun(active)

      // Poll while active
      if (active && !pollTimerRef.current) {
        pollTimerRef.current = setInterval(() => {
          loadRuns()
        }, 5_000)
      } else if (!active && pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
        pollTimerRef.current = null
      }
    }).catch(console.error)
  }

  // Cleanup poll on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current)
    }
  }, [])

  function openDialog(targetName: string) {
    setDialogTarget(targetName)
    setShowDialog(true)
  }

  function handleTrigger(opts: { mode: Run['mode']; custom_prompt?: string; self_repair: boolean }) {
    api.triggerRun({ target: dialogTarget, ...opts }).then(() => {
      loadRuns()
    }).catch(console.error)
  }

  function handleRemove() {
    // Phase 2: no remove API, just deselect
    setSelectedTarget(null)
  }

  const selectedTargetObj = targets.find(t => t.name === selectedTarget) ?? null
  const lastRunForSelected = selectedTarget ? (lastRuns[selectedTarget] ?? null) : null

  return html`
    <div style="display:flex;height:100%;overflow:hidden;">
      <${Sidebar}
        targets=${targets}
        selectedTarget=${selectedTarget}
        lastRuns=${lastRuns}
        healthData=${healthData}
        onSelect=${setSelectedTarget}
        onRun=${openDialog}
      />
      <div style="flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--panel);">
        <!-- Top bar with Run All button -->
        <div style="display:flex;justify-content:flex-end;padding:8px 16px;border-bottom:1px solid var(--border);">
          <button
            style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);font-size:13px;"
            onClick=${() => openDialog('__all__')}
            disabled=${hasActiveRun}
          >Run All</button>
        </div>
        <${TargetDetail}
          target=${selectedTargetObj}
          lastRun=${lastRunForSelected}
          onRun=${(mode: 'production' | 'dry-run') => selectedTarget && openDialog(selectedTarget)}
          onRemove=${handleRemove}
        />
      </div>
      <${TriggerDialog}
        target=${dialogTarget}
        isOpen=${showDialog}
        onClose=${() => setShowDialog(false)}
        onStart=${handleTrigger}
        isDisabled=${hasActiveRun}
      />
    </div>
  `
}
