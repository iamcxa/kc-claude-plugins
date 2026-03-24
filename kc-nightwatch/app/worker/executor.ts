import path from 'node:path'
import os from 'node:os'
import fs from 'node:fs/promises'
import { log } from '../shared/logger.ts'
import type { Run, RunSummary, IpcMessage, RunSummaryAction } from '../shared/types.ts'
import { parseStreamJsonLine } from './log-parser.ts'
import { buildSafehouseFlags, type PolicyTarget } from './policy.ts'
import {
  RESULT_FORCE_KILL_DELAY_MS,
  KEEP_RUNS_COUNT,
} from '../shared/constants.ts'
import { collectImplicitFeedback, collectPrReviewFeedback } from './feedback-collector.ts'
import { appendFeedback, writeFeedbackTrends } from '../server/services/feedback-store.ts'
import { recordRunOutcomes } from './auto-action.ts'
import { detectDefaultBranch, createWorktree, cleanupWorktree } from './worktree-manager.ts'

// In-memory PID tracking — keyed by run_id so cancel can target a specific run
// Map<run_id, pid> — allows per-run cancel without killing concurrent runs
export const activePids = new Map<string, number>()

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
// activeRunIds: skip deletion of any run whose directory name is in this set (parallel safety)
export async function cleanupOldRuns(
  runsDir: string,
  keepCount = KEEP_RUNS_COUNT,
  activeRunIds?: Set<string>
): Promise<void> {
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
    let deleted = 0
    for (const { name } of toDelete) {
      if (activeRunIds?.has(name)) {
        log.debug({ component: 'worker', msg: `Skipping cleanup of active run: ${name}` })
        continue
      }
      await Bun.spawn(['rm', '-rf', `${runsDir}/${name}`]).exited
      log.debug({ component: 'worker', msg: `Deleted old run artifact: ${name}` })
      deleted++
    }
    if (deleted > 0) {
      log.info({ component: 'worker', msg: `Cleaned up ${deleted} old run(s), keeping ${keepCount}` })
    }
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

  // WKTREE-01: Create isolated worktree (per D-01, D-11, D-14)
  const worktreePath = path.join(target.resolved_path, '.worktrees', `nw-${run.id}`)
  let worktreeCreated = false
  try {
    const defaultBranch = await detectDefaultBranch(target.resolved_path, target.default_branch)
    await createWorktree(target.resolved_path, worktreePath, defaultBranch)
    worktreeCreated = true
    log.info({ component: 'worker', msg: `Worktree created at ${worktreePath} from origin/${defaultBranch}` })
  } catch (err) {
    // D-10: No fallback to in-place execution — fail the run
    log.error({ component: 'worker', msg: `Worktree creation failed for run ${run.id}: ${String(err)}` })
    opts.onMessage({ type: 'run:failed', run_id: run.id, error: String(err) })
    return
  }

  const safehouseFlags = buildSafehouseFlags(target, run, opts.runsDir)
  const safehouseBin = opts.safehousePath ?? 'safehouse'

  // Build the prompt: custom_prompt overrides, otherwise invoke /kc-nightwatch skill
  const dryRunFlag = run.mode === 'dry-run' ? ' --dry-run' : ''
  const selfRepairFlag = (run as unknown as Record<string, unknown>).self_repair ? ' --self-repair' : ''
  const prompt = run.custom_prompt ?? `/kc-nightwatch${dryRunFlag}${selfRepairFlag}`

  // Build --plugin-dir flags so spawned claude can find kc-nightwatch skill + extra plugins
  const pluginDirFlags: string[] = []
  // Always include kc-nightwatch itself (this plugin's root — 2 levels up from app/worker/)
  const nwPluginRoot = path.resolve(import.meta.dir, '..', '..')
  pluginDirFlags.push('--plugin-dir', nwPluginRoot)
  // Include any extra_plugin_dirs from target config
  for (const dir of target.extra_plugin_dirs ?? []) {
    const resolved = dir.startsWith('~') ? path.join(os.homedir(), dir.slice(1)) : dir
    pluginDirFlags.push('--plugin-dir', resolved)
  }

  const claudeArgs = [
    safehouseBin,
    ...safehouseFlags,
    'claude',
    '-p', prompt,
    '--verbose',
    '--output-format', 'stream-json',
    '--model', 'claude-opus-4-5',
    '--mcp-config', journalConfigPath,
    ...pluginDirFlags,
  ]

  const child = Bun.spawn(claudeArgs, {
    stdout: 'pipe',
    stderr: 'pipe',
    cwd: worktreePath,
    env: { ...process.env },
  })

  activePids.set(run.id, child.pid)
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

  // Capture stderr in background (safehouse/claude errors go here)
  const stderrChunks: string[] = []
  ;(async () => {
    for await (const chunk of child.stderr) {
      const text = new TextDecoder().decode(chunk)
      stderrChunks.push(text)
      log.warn({ component: 'worker', msg: `Run ${run.id} stderr: ${text.trim().slice(0, 200)}` })
    }
  })()

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
    activePids.delete(run.id)

    // Write run artifacts (include stderr if stdout was empty)
    if (logLines.length === 0 && stderrChunks.length > 0) {
      logLines.push(JSON.stringify({ type: 'system', subtype: 'stderr', message: stderrChunks.join('').trim() }))
    }
    await Bun.write(logFilePath, logLines.join('\n') + '\n')

    // Only write legacy phases_completed if skill didn't produce a summary.yaml
    const summaryExists = await Bun.file(summaryPath).exists()
    if (!summaryExists) {
      await Bun.write(
        summaryPath,
        `phases_completed:\n${legacyPhases.map(p => `  - ${p}`).join('\n')}\n`
      )
    }

    // Read structured summary from NW-Claude output (Phase 5.2.5 writes this)
    try {
      const summaryFile = Bun.file(summaryPath)
      if (await summaryFile.exists()) {
        const { parse } = await import('yaml')
        const summaryData = parse(await summaryFile.text()) as Record<string, unknown> | null
        if (summaryData && typeof summaryData === 'object') {
          // Populate RunSummary from structured output
          summary.targets_active = (summaryData.targets_active as number) ?? 0
          summary.targets_skipped = (summaryData.targets_skipped as number) ?? 0
          summary.total_signals = (summaryData.total_signals as number) ?? 0
          summary.total_actions = (summaryData.total_actions as number) ?? 0
          summary.errors = (summaryData.errors as number) ?? 0
          if (summaryData.per_target && typeof summaryData.per_target === 'object') {
            summary.per_target = summaryData.per_target as typeof summary.per_target
          }
        }
      }
    } catch (err) {
      log.warn({ component: 'worker', msg: `Failed to read summary.yaml for ${run.id}: ${String(err)}` })
    }

    // FEED-04: Collect implicit feedback from PR merge status
    // FEED-07: Write feedback trends to NW journal for slow learning
    // Both are fire-and-forget — errors MUST NOT block run completion
    if (!timedOut && Object.keys(summary.per_target).length > 0) {
      try {
        // Collect all actions with pr_url across all targets
        const actionsWithTargets: Array<{ action: RunSummaryAction; target: string; run_id: string }> = []
        for (const [targetName, targetSummary] of Object.entries(summary.per_target)) {
          for (const action of targetSummary.actions ?? []) {
            if (action.pr_url) {
              actionsWithTargets.push({ action, target: targetName, run_id: run.id })
            }
          }
        }
        if (actionsWithTargets.length > 0) {
          await collectImplicitFeedback(actionsWithTargets, appendFeedback)
          // EXTFEED-02: Collect PR review feedback (reviewer approve/reject/comment verdicts)
          await collectPrReviewFeedback(actionsWithTargets, appendFeedback)
        }

        // Write feedback trends to each target's NW journal
        for (const targetName of Object.keys(summary.per_target)) {
          const journalDir = await ensureNwMemoryDir(targetName)
          await writeFeedbackTrends(targetName, journalDir)
        }
      } catch (err) {
        log.warn({ component: 'worker', msg: `Post-run feedback collection error: ${String(err)}` })
      }

      // AUTO-01/02/03: Record PR and Linear outcomes from run actions into outcomes.yaml
      try {
        await recordRunOutcomes(run, summary.per_target)
      } catch (err) {
        log.warn({ component: 'worker', msg: `Auto-action outcome recording error: ${String(err)}` })
      }
    }

    if (timedOut) {
      opts.onMessage({ type: 'run:failed', run_id: run.id, error: 'timeout' })
    } else {
      opts.onMessage({ type: 'run:completed', run_id: run.id, summary })
    }

    // Rolling cleanup — keep last 50 runs, skipping currently active run directories
    await cleanupOldRuns(opts.runsDir, KEEP_RUNS_COUNT, new Set(activePids.keys()))

    // WKTREE-02/03: Cleanup worktree LAST — after all artifacts collected (per D-12)
    if (worktreeCreated) {
      try {
        await cleanupWorktree(target.resolved_path, worktreePath)
        log.info({ component: 'worker', msg: `Worktree cleaned up for run ${run.id}` })
      } catch (err) {
        // D-13: If cleanup fails (e.g., push fails), log but don't fail the run
        // Next run's createWorktree will prune stale entries
        log.warn({ component: 'worker', msg: `Worktree cleanup error for run ${run.id}: ${String(err)}` })
      }
    }
  }
}

// Kill all active PIDs — called on worker shutdown (FOUND-06)
export async function killAllActive(): Promise<void> {
  for (const [runId, pid] of activePids) {
    log.warn({ component: 'worker', msg: `Killing active process PID ${pid} (run ${runId}) on shutdown` })
    try {
      process.kill(pid, 'SIGKILL')
    } catch {
      // Already gone
    }
  }
  activePids.clear()
}
