import path from 'node:path'
import os from 'node:os'
import { randomUUID } from 'node:crypto'
import { log } from '../shared/logger.ts'
import type { IpcMessage, Run, ServerToWorker, ScheduleConfig } from '../shared/types.ts'
import { HEARTBEAT_INTERVAL_MS, SCHEDULER_RUNS_ALL_TARGET } from '../shared/constants.ts'
import { executeRun, killAllActive, activePids } from './executor.ts'
import type { PolicyTarget } from './policy.ts'
import { readTargets, readYamlFile } from '../server/services/yaml-store.ts'
import { startPerTargetSchedulers, stopAllSchedulers } from './scheduler.ts'
import type { Target } from '../shared/types.ts'

log.info({ component: 'worker', msg: 'Worker started' })

const send = (msg: IpcMessage) => process.send?.(msg)

// Paths
const RUNS_DIR = path.join(import.meta.dir, '../../runs')
const SAFETY_YAML_PATH = path.join(import.meta.dir, '../../../config/safety.yaml')

// Load safety config at startup — dynamic from safety.yaml (not hardcoded)
let maxRuntimeMs = 30 * 60_000  // default fallback
const safetyRaw = await readYamlFile<{ global: { max_runtime_minutes?: number } }>(SAFETY_YAML_PATH)
if (safetyRaw?.global?.max_runtime_minutes) {
  maxRuntimeMs = safetyRaw.global.max_runtime_minutes * 60_000
  log.info({ component: 'worker', msg: `max_runtime_minutes loaded from safety.yaml: ${safetyRaw.global.max_runtime_minutes}` })
}

// Load targets at startup — real target definitions from nightwatch-targets.yaml
let targetsMap: Record<string, Target> = {}
try {
  targetsMap = await readTargets()
  log.info({ component: 'worker', msg: `Loaded ${Object.keys(targetsMap).length} targets` })
} catch (err) {
  log.warn({ component: 'worker', msg: `Failed to load targets: ${String(err)}` })
}

function resolveTarget(targetName: string): PolicyTarget {
  const target = targetsMap[targetName]
  if (!target) {
    log.warn({ component: 'worker', msg: `Target '${targetName}' not found in targets.yaml — using /tmp` })
    return { name: targetName, resolved_path: '/tmp' }
  }
  let resolvedPath: string
  if (target.path) {
    // Expand tilde — policy.ts anti-pattern rule: never pass '~' paths downstream
    resolvedPath = target.path.startsWith('~')
      ? path.join(os.homedir(), target.path.slice(1))
      : target.path
  } else {
    // Fallback: ~/.claude/plugins/local/{name}/ (plugin type auto-discovery)
    resolvedPath = path.join(os.homedir(), '.claude', 'plugins', 'local', targetName)
    log.warn({ component: 'worker', msg: `Target '${targetName}' has no path — falling back to ${resolvedPath}` })
  }
  return {
    name: target.name,
    resolved_path: resolvedPath,
    extra_plugin_dirs: target.extra_plugin_dirs ?? [],
    default_branch: target.default_branch,   // WKTREE-01: pass through for worktree branch detection
  }
}

// Per-target queue isolation (PARA-01) — replaces serial queue: Run[] + activeRun: Run | null
const targetQueues: Map<string, Run[]> = new Map()   // pending runs per target
const activeRuns: Map<string, Run> = new Map()       // at most 1 active run per target

function sendState(): void {
  const active = Array.from(activeRuns.values())
  const queue = Array.from(targetQueues.values()).flat()
  send({ type: 'state', queue, active })
}

async function processTarget(targetName: string): Promise<void> {
  if (activeRuns.has(targetName)) return  // already running for this target
  const queue = targetQueues.get(targetName)
  if (!queue || queue.length === 0) return
  const run = queue.shift()!
  activeRuns.set(targetName, run)
  sendState()
  log.info({ component: 'worker', msg: `Starting run ${run.id} for target '${run.target}'` })

  const target = resolveTarget(run.target as string)
  try {
    await executeRun(run, target, {
      runsDir: RUNS_DIR,
      maxRuntimeMs,
      onMessage: (m) => send(m),
    })
  } catch (err) {
    log.error({ component: 'worker', msg: `Run ${run.id} failed: ${String(err)}` })
    send({ type: 'run:failed', run_id: run.id, error: String(err) } satisfies IpcMessage)
  } finally {
    activeRuns.delete(targetName)
    sendState()
    void processTarget(targetName)  // drain next in this target's queue
  }
}

function enqueue(run: Run): void {
  // __all__ expands to N per-target sub-runs (D-01, D-02, D-03)
  if (run.target === SCHEDULER_RUNS_ALL_TARGET) {
    const activeTargets = Object.keys(targetsMap)
    if (activeTargets.length === 0) {
      log.warn({ component: 'worker', msg: `No targets loaded — __all__ run ${run.id} has nothing to do` })
      return
    }
    log.info({ component: 'worker', msg: `Expanding __all__ run ${run.id} into ${activeTargets.length} per-target sub-runs` })
    for (const targetName of activeTargets) {
      const subRun: Run = {
        id: randomUUID(),
        target: targetName,
        mode: run.mode,
        trigger: run.trigger,
        status: 'queued',
        queued_at: new Date().toISOString(),
        log_path: '',
      }
      subRun.log_path = `runs/${subRun.id}/log.jsonl`
      enqueue(subRun) // recursive — routes through per-target logic
    }
    return
  }

  // Per-target queue depth 1: max 1 active + 1 queued (D-04)
  const isActive = activeRuns.has(run.target)
  const queuedCount = (targetQueues.get(run.target) ?? []).length
  if (isActive && queuedCount >= 1) {
    if (run.trigger === 'interval') {
      // D-06: scheduled trigger — skip silently to prevent scheduler pile-up
      log.info({ component: 'worker', msg: `Skipping scheduled run for '${run.target}' — queue full (1 active + 1 queued)` })
      return
    }
    // D-05: manual trigger — reject with clear message
    log.warn({ component: 'worker', msg: `Rejecting run ${run.id} for '${run.target}' — target already has a queued run` })
    send({ type: 'run:failed', run_id: run.id, error: `Target '${run.target}' already has a queued run` } satisfies IpcMessage)
    return
  }

  if (!targetQueues.has(run.target)) targetQueues.set(run.target, [])
  targetQueues.get(run.target)!.push(run)
  log.info({ component: 'worker', msg: `Enqueued run ${run.id} for '${run.target}' (target queue depth: ${targetQueues.get(run.target)!.length})` })
  sendState()
  void processTarget(run.target) // each target drains independently
}

// Send initial state + immediate heartbeat (so server marks us online instantly)
sendState()
send({ type: 'heartbeat', ts: Date.now() })

// Heartbeat every 30s
const heartbeatTimer = setInterval(() => {
  send({ type: 'heartbeat', ts: Date.now() })
}, HEARTBEAT_INTERVAL_MS)

// Handle IPC messages from server
process.on('message', (msg: ServerToWorker) => {
  switch (msg.type) {
    case 'shutdown':
      log.info({ component: 'worker', msg: 'Received shutdown — killing active runs and exiting' })
      clearInterval(heartbeatTimer)
      stopAllSchedulers()
      killAllActive().then(() => process.exit(0))
      break

    case 'status':
      sendState()
      break

    case 'enqueue':
      enqueue(msg.run)
      break

    case 'cancel': {
      const pid = activePids.get(msg.run_id)
      if (pid !== undefined) {
        log.info({ component: 'worker', msg: `Cancelling active run ${msg.run_id} — sending SIGTERM to PID ${pid}` })
        try { process.kill(pid, 'SIGTERM') } catch { /* already gone */ }
      } else {
        // Search all target queues for the queued run
        let found = false
        for (const [targetName, tQueue] of targetQueues) {
          const idx = tQueue.findIndex(r => r.id === msg.run_id)
          if (idx >= 0) {
            tQueue.splice(idx, 1)
            log.info({ component: 'worker', msg: `Removed queued run ${msg.run_id} from target '${targetName}' queue` })
            sendState()
            found = true
            break
          }
        }
        if (!found) {
          log.warn({ component: 'worker', msg: `Cancel: run ${msg.run_id} not found in active or any queue` })
        }
      }
      break
    }

    case 'schedule': {
      const config: ScheduleConfig = msg.config
      log.info({ component: 'worker', msg: `Received schedule IPC — enabled: ${config.enabled}, interval: ${config.interval_hours}h` })
      // Reload targets to pick up any per-target schedule changes, then restart all timers (D-10)
      void (async () => {
        try {
          targetsMap = await readTargets()
        } catch (err) {
          log.warn({ component: 'worker', msg: `Failed to reload targets for scheduler: ${String(err)}` })
        }
        startPerTargetSchedulers(config, targetsMap, enqueue)
      })()
      break
    }
  }
})
