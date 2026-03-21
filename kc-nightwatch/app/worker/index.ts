import path from 'node:path'
import os from 'node:os'
import { log } from '../shared/logger.ts'
import type { IpcMessage, Run, ServerToWorker, ScheduleConfig } from '../shared/types.ts'
import { HEARTBEAT_INTERVAL_MS, SCHEDULER_RUNS_ALL_TARGET } from '../shared/constants.ts'
import { executeRun, killAllActive, activePids } from './executor.ts'
import type { PolicyTarget } from './policy.ts'
import { readTargets, readYamlFile } from '../server/services/yaml-store.ts'
import { startScheduler, stopScheduler } from './scheduler.ts'
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
  }
}

// Execution queue — max concurrency 1 (EXEC-09)
const queue: Run[] = []
let activeRun: Run | null = null  // Phase 8: still serial, but state emits as array (ready for Phase 9 parallel)

function sendState(): void {
  const active: Run[] = activeRun ? [activeRun] : []
  send({ type: 'state', queue: [...queue], active })
}

async function processNextRun(): Promise<void> {
  if (activeRun || queue.length === 0) return
  const run = queue.shift()!
  activeRun = run
  sendState()
  log.info({ component: 'worker', msg: `Starting run ${run.id} for target '${run.target}'` })

  // Handle __all__ target: enqueue each active target as a separate run
  if (run.target === SCHEDULER_RUNS_ALL_TARGET) {
    const activeTargets = Object.keys(targetsMap)
    if (activeTargets.length === 0) {
      log.warn({ component: 'worker', msg: `No targets loaded — __all__ run ${run.id} has nothing to do` })
    } else {
      for (const targetName of activeTargets) {
        const { randomUUID } = await import('node:crypto')
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
        queue.push(subRun)
        log.info({ component: 'worker', msg: `Enqueued sub-run ${subRun.id} for target '${targetName}' (from __all__)` })
      }
    }
    activeRun = null
    sendState()
    void processNextRun()
    return
  }

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
    activeRun = null
    sendState()
    void processNextRun()
  }
}

function enqueue(run: Run): void {
  queue.push(run)
  log.info({ component: 'worker', msg: `Enqueued run ${run.id} for '${run.target}' (queue depth: ${queue.length})` })
  sendState()
  void processNextRun()
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
      stopScheduler()
      killAllActive().then(() => process.exit(0))
      break

    case 'status':
      sendState()
      break

    case 'enqueue':
      enqueue(msg.run)
      break

    case 'cancel': {
      // Check if the run is currently active — look up specific PID by run_id (not bulk kill)
      const pid = activePids.get(msg.run_id)
      if (pid !== undefined) {
        log.info({ component: 'worker', msg: `Cancelling active run ${msg.run_id} — sending SIGTERM to PID ${pid}` })
        try { process.kill(pid, 'SIGTERM') } catch { /* already gone */ }
      } else {
        const idx = queue.findIndex(r => r.id === msg.run_id)
        if (idx >= 0) {
          queue.splice(idx, 1)
          log.info({ component: 'worker', msg: `Removed queued run ${msg.run_id}` })
          sendState()
        } else {
          log.warn({ component: 'worker', msg: `Cancel: run ${msg.run_id} not found in active or queue` })
        }
      }
      break
    }

    case 'schedule': {
      const config: ScheduleConfig = msg.config
      log.info({ component: 'worker', msg: `Received schedule IPC — enabled: ${config.enabled}, interval: ${config.interval_hours}h` })
      startScheduler(config, enqueue)
      break
    }
  }
})
