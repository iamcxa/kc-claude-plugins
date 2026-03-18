import path from 'node:path'
import os from 'node:os'
import fs from 'node:fs/promises'
import { log } from '../shared/logger.ts'
import type { Run, RunSummary, IpcMessage } from '../shared/types.ts'
import { parseStreamJsonLine } from './log-parser.ts'
import { buildSafehouseFlags, type PolicyTarget } from './policy.ts'
import {
  RESULT_FORCE_KILL_DELAY_MS,
  KEEP_RUNS_COUNT,
} from '../shared/constants.ts'

// In-memory PID tracking — never use files (worker has direct handles)
export const activePids = new Set<number>()

// MEM-01: Create per-target NW journal directory on first use
// CRITICAL: Use os.homedir() + path.join, never template literal '~' (policy.ts anti-pattern rule)
export async function ensureNwMemoryDir(targetName: string): Promise<string> {
  const dir = path.join(os.homedir(), '.claude', 'nightwatch', 'memory', targetName, '.private-journal')
  await fs.mkdir(dir, { recursive: true })
  return dir
}

// MEM-02: Write per-run MCP config pointing to target-specific journal
export async function writeNwJournalConfig(runDir: string, journalDir: string): Promise<string> {
  const configPath = path.join(runDir, 'nw-journal.json')
  const config = {
    mcpServers: {
      'nw-journal': {
        type: 'stdio',
        command: 'private-journal',
        args: ['--dir', journalDir],
      },
    },
  }
  await Bun.write(configPath, JSON.stringify(config, null, 2))
  return configPath
}

// Rolling cleanup — keep last N runs (FOUND-08)
export async function cleanupOldRuns(runsDir: string, keepCount = KEEP_RUNS_COUNT): Promise<void> {
  try {
    const glob = new Bun.Glob('*')
    const entries = await Array.fromAsync(glob.scan({ cwd: runsDir, onlyFiles: false }))
    if (entries.length <= keepCount) return

    const withStats = await Promise.all(
      entries.map(async (name) => {
        const stat = await Bun.file(`${runsDir}/${name}`).stat().catch(() => ({ mtime: 0 }))
        return { name, mtime: Number(stat.mtime ?? 0) }
      })
    )
    withStats.sort((a, b) => a.mtime - b.mtime)

    const toDelete = withStats.slice(0, withStats.length - keepCount)
    for (const { name } of toDelete) {
      await Bun.spawn(['rm', '-rf', `${runsDir}/${name}`]).exited
      log.debug({ component: 'worker', msg: `Deleted old run artifact: ${name}` })
    }
    log.info({ component: 'worker', msg: `Cleaned up ${toDelete.length} old run(s), keeping ${keepCount}` })
  } catch (err) {
    log.warn({ component: 'worker', msg: `Run cleanup error: ${String(err)}` })
  }
}

// Derived from safety.yaml max_runtime_minutes (read at startup via yaml-store, passed in)
export async function executeRun(
  run: Run,
  target: PolicyTarget,
  opts: {
    runsDir: string
    safehousePath?: string
    maxRuntimeMs: number  // safety.yaml max_runtime_minutes * 60_000
    onMessage: (msg: IpcMessage) => void
  }
): Promise<void> {
  const runDir = path.join(opts.runsDir, run.id)
  await Bun.spawn(['mkdir', '-p', runDir]).exited

  const logFilePath = path.join(runDir, 'log.jsonl')
  const summaryPath = path.join(runDir, 'summary.yaml')
  const logLines: string[] = []

  // MEM-01/02/03: Create per-target NW journal dir and write per-run MCP config
  // Each target gets a distinct journal path — no cross-target sharing (MEM-03)
  const journalDir = await ensureNwMemoryDir(target.name)
  const journalConfigPath = await writeNwJournalConfig(runDir, journalDir)

  const safehouseFlags = buildSafehouseFlags(target, run, opts.runsDir)
  const safehouseBin = opts.safehousePath ?? 'safehouse'

  const claudeArgs = [
    safehouseBin,
    ...safehouseFlags,
    'claude',
    '-p',
    '--output-format', 'stream-json',
    '--model', 'claude-opus-4-5',
    '--cwd', target.resolved_path,
    '--mcp-config', journalConfigPath,
    ...(run.custom_prompt ? ['--append-system-prompt', run.custom_prompt] : []),
  ]

  const child = Bun.spawn(claudeArgs, {
    stdout: 'pipe',
    stderr: 'pipe',
    env: { ...process.env },
  })

  activePids.add(child.pid)
  opts.onMessage({ type: 'run:started', run_id: run.id, pid: child.pid })

  // Enforce max_runtime_minutes from safety.yaml (FOUND-05)
  let timedOut = false
  const runtimeTimeout = setTimeout(() => {
    timedOut = true
    log.warn({ component: 'worker', msg: `Run ${run.id} timeout after ${opts.maxRuntimeMs}ms — SIGKILL` })
    child.kill('SIGKILL')
  }, opts.maxRuntimeMs)

  let resultReceived = false
  // Phase 1 minimal summary — fields not yet populated by skill; defaults to zero/empty
  const legacyPhases: string[] = []
  const summary: RunSummary = {
    targets_active: 0,
    targets_skipped: 0,
    total_signals: 0,
    total_actions: 0,
    errors: 0,
    per_target: {},
    phases_completed: legacyPhases,
  }

  try {
    for await (const chunk of child.stdout) {
      const lines = new TextDecoder().decode(chunk).split('\n').filter(Boolean)
      for (const line of lines) {
        logLines.push(line)
        const event = parseStreamJsonLine(line)

        opts.onMessage({ type: 'run:log', run_id: run.id, event })

        // CRITICAL: Force-kill after result event — Claude CLI bug workaround (GitHub #25629)
        // claude -p --output-format stream-json hangs after emitting result because active MCP
        // connections prevent clean process.exit(). Force-kill after RESULT_FORCE_KILL_DELAY_MS.
        if (event.type === 'result' && !resultReceived) {
          resultReceived = true
          log.info({
            component: 'worker',
            msg: `Result received for ${run.id} — scheduling force-kill in ${RESULT_FORCE_KILL_DELAY_MS}ms`,
          })
          setTimeout(() => {
            if (child.exitCode === null) {
              log.info({ component: 'worker', msg: `Force-killing claude process ${child.pid} after result event` })
              child.kill('SIGKILL')
            }
          }, RESULT_FORCE_KILL_DELAY_MS)
        }

        // Track phase progress from assistant messages
        if (event.type === 'assistant' && event.content) {
          const phaseMatch = event.content.match(/Phase (\d+(?:\.\d+)?)/i)
          if (phaseMatch && !legacyPhases.includes(phaseMatch[0])) {
            legacyPhases.push(phaseMatch[0])
          }
        }
      }
    }
  } finally {
    clearTimeout(runtimeTimeout)
    activePids.delete(child.pid)

    // Write run artifacts
    await Bun.write(logFilePath, logLines.join('\n') + '\n')
    await Bun.write(
      summaryPath,
      `phases_completed:\n${legacyPhases.map(p => `  - ${p}`).join('\n')}\n`
    )

    if (timedOut) {
      opts.onMessage({ type: 'run:failed', run_id: run.id, error: 'timeout' })
    } else {
      opts.onMessage({ type: 'run:completed', run_id: run.id, summary })
    }

    // Rolling cleanup — keep last 50 runs
    await cleanupOldRuns(opts.runsDir)
  }
}

// Kill all active PIDs — called on worker shutdown (FOUND-06)
export async function killAllActive(): Promise<void> {
  for (const pid of activePids) {
    log.warn({ component: 'worker', msg: `Killing active process PID ${pid} on shutdown` })
    try {
      process.kill(pid, 'SIGKILL')
    } catch {
      // Already gone
    }
  }
  activePids.clear()
}
