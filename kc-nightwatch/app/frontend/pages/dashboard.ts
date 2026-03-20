import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import type { Target, Run } from '../../shared/types.ts'
import { Sidebar } from '../components/sidebar.ts'
import { TargetDetail } from '../components/target-detail.ts'
import { TriggerDialog } from '../components/trigger-dialog.ts'
import { ChatPanel } from '../components/chat-panel.ts'
import { AddTargetWizard } from '../components/add-target-wizard.ts'
import { api } from '../lib/api.ts'
import { showToast } from '../lib/use-toast.ts'
import { usePoll } from '../lib/use-poll.ts'

interface DashboardProps {
  healthData?: Record<string, { health: 'improving' | 'stable' | 'degrading' }>
}

export function Dashboard({ healthData }: DashboardProps = {}) {
  const [targets, setTargets] = useState<Target[]>([])
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)
  const [lastRuns, setLastRuns] = useState<Record<string, Run>>({})
  const [showDialog, setShowDialog] = useState(false)
  const [dialogTarget, setDialogTarget] = useState('')
  const [hasActiveRuns, setHasActiveRuns] = useState(false)
  const [workerQueue, setWorkerQueue] = useState<Run[]>([])
  const [showAddWizard, setShowAddWizard] = useState(false)

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

      // Check if any runs are active (drives usePoll interval)
      const active = runs.some(r => r.status === 'running' || r.status === 'queued')
      setHasActiveRuns(active)
    }).catch(console.error)

    // Fetch queue state for queue display in TargetDetail
    api.getWorkerState().then(state => {
      setWorkerQueue(state.queue)
    }).catch(console.error)
  }

  // Replace inline setInterval with usePoll hook (POLL-02)
  usePoll(loadRuns, 5_000, hasActiveRuns)

  function openDialog(targetName: string) {
    setDialogTarget(targetName)
    setShowDialog(true)
  }

  function handleTrigger(opts: { mode: Run['mode']; custom_prompt?: string; self_repair: boolean }) {
    // Request notification permission on first trigger (user gesture)
    if ('Notification' in window && Notification.permission === 'default' && !localStorage.getItem('nw-notif-denied')) {
      const result = Notification.requestPermission()
      if (result && typeof result.then === 'function') {
        result.then(perm => { if (perm === 'denied') localStorage.setItem('nw-notif-denied', '1') }).catch(() => {})
      }
    }

    const targetLabel = dialogTarget === '__all__' ? 'all targets' : dialogTarget
    api.triggerRun({ target: dialogTarget, ...opts }).then(() => {
      showToast(`Run queued for ${targetLabel}`, 'success')
      loadRuns()
    }).catch((err: Error) => {
      showToast(err.message || 'Failed to trigger run', 'error')
    })
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
        onSelect=${(name: string) => { setSelectedTarget(name) }}
        onRun=${openDialog}
        onAddTarget=${() => setShowAddWizard(true)}
      />
      <div style="flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--panel);">
        <!-- Top bar with Run All button -->
        <div style="display:flex;justify-content:flex-end;padding:8px 16px;border-bottom:1px solid var(--border);">
          <button
            style="background:var(--btn-primary);color:#fff;border-color:var(--btn-primary);font-size:13px;"
            onClick=${() => openDialog('__all__')}
            disabled=${hasActiveRuns}
          >Run All</button>
        </div>
        <${TargetDetail}
          target=${selectedTargetObj}
          lastRun=${lastRunForSelected}
          workerQueue=${workerQueue}
          onRun=${(mode: 'production' | 'dry-run') => selectedTarget && openDialog(selectedTarget)}
          onRemove=${handleRemove}
        />
      </div>
      <!-- Inline chat panel -->
      <div style="width:340px;min-width:340px;border-left:1px solid var(--border);background:var(--panel);overflow:hidden;">
        <${ChatPanel} targetName=${selectedTarget} />
      </div>
      <${TriggerDialog}
        target=${dialogTarget}
        isOpen=${showDialog}
        onClose=${() => setShowDialog(false)}
        onStart=${handleTrigger}
      />
      <${AddTargetWizard}
        isOpen=${showAddWizard}
        onClose=${() => setShowAddWizard(false)}
        onSaved=${() => { setShowAddWizard(false); api.getTargets().then(setTargets).catch(console.error); loadRuns() }}
      />
    </div>
  `
}
