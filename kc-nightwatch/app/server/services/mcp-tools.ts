import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { z } from 'zod'
import path from 'node:path'
import os from 'node:os'
import { readTargets, loadOrCreateAppConfig, writeAppConfig, readYamlFile } from './yaml-store.ts'
import { listRuns, getRun, appendRun } from './run-store.ts'
import { appendFeedback, getCalibrationData } from './feedback-store.ts'
import { workerStatus, sendToWorker } from '../ipc.ts'
import type { Run, FeedbackEntry } from '../../shared/types.ts'

const NW_JOURNAL_BASE = path.join(os.homedir(), '.claude/nightwatch/memory')

export function createMcpServer(): McpServer {
  const server = new McpServer({ name: 'nightwatch', version: '1.0.0' })

  // ============================================================
  // Query tools (7)
  // ============================================================

  server.registerTool('nw_get_targets', {
    description: 'List all configured nightwatch monitoring targets',
    inputSchema: {},
  }, async () => {
    const targets = await readTargets()
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(Object.values(targets)) }],
    }
  })

  server.registerTool('nw_get_latest_run', {
    description: 'Get the most recent nightwatch run, optionally filtered by target',
    inputSchema: {
      target: z.string().optional().describe('Filter by target name (optional)'),
    },
  }, async ({ target }) => {
    const runs = await listRuns(target ? { target } : undefined)
    if (!runs.length) {
      return {
        content: [{ type: 'text' as const, text: 'No runs found' }],
        isError: true,
      }
    }
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(runs[0]) }],
    }
  })

  server.registerTool('nw_get_run', {
    description: 'Get details for a specific run by ID including summary and actions',
    inputSchema: {
      run_id: z.string().describe('The run ID to fetch'),
    },
  }, async ({ run_id }) => {
    const run = await getRun(run_id)
    if (!run) {
      return {
        content: [{ type: 'text' as const, text: `Run not found: ${run_id}` }],
        isError: true,
      }
    }
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(run) }],
    }
  })

  server.registerTool('nw_get_proposals', {
    description: 'List runs that contain proposal actions, optionally filtered by target',
    inputSchema: {
      target: z.string().optional().describe('Filter by target name (optional)'),
    },
  }, async ({ target }) => {
    const runs = await listRuns()
    const filtered = target ? runs.filter(r => r.target === target) : runs
    // Return runs that have proposal-type actions (requires summary — enrich lazily)
    const withSummaries = await Promise.all(
      filtered.map(async (run) => {
        const full = await getRun(run.id)
        const hasProposals = full?.summary
          ? Object.values(full.summary.per_target).some(pt =>
              pt.actions.some(a => a.type === 'proposal')
            )
          : false
        return hasProposals ? full : null
      })
    )
    const proposals = withSummaries.filter(Boolean)
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(proposals) }],
    }
  })

  server.registerTool('nw_get_config_warnings', {
    description: 'Get the latest config warnings from the nightwatch self-repair run',
    inputSchema: {},
  }, async () => {
    const selfRepairPath = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-self-repair.yaml')
    const data = await readYamlFile(selfRepairPath)
    if (!data) {
      return {
        content: [{ type: 'text' as const, text: JSON.stringify({ warnings: {} }) }],
      }
    }
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(data) }],
    }
  })

  server.registerTool('nw_get_schedule', {
    description: 'Get the current nightwatch schedule configuration',
    inputSchema: {},
  }, async () => {
    const config = await loadOrCreateAppConfig()
    return {
      content: [{ type: 'text' as const, text: JSON.stringify(config.schedule) }],
    }
  })

  server.registerTool('nw_read_journal', {
    description: 'Read recent journal entries for a specific target',
    inputSchema: {
      target: z.string().describe('Target name to read journal entries for'),
      limit: z.number().optional().describe('Maximum number of entries to return (default: 5)'),
    },
  }, async ({ target, limit = 5 }) => {
    const journalDir = path.join(NW_JOURNAL_BASE, target, '.private-journal')
    try {
      const glob = new Bun.Glob('*.md')
      const files: string[] = []
      for await (const file of glob.scan({ cwd: journalDir, absolute: true })) {
        files.push(file)
      }
      if (!files.length) {
        return {
          content: [{ type: 'text' as const, text: `No journal entries found for target: ${target}` }],
        }
      }

      // Sort by mtime desc, take last N
      const withMtime = await Promise.all(
        files.map(async (f) => ({ f, mtime: (await Bun.file(f).stat()).mtime }))
      )
      withMtime.sort((a, b) => b.mtime - a.mtime)
      const recent = withMtime.slice(0, limit)

      const contents = await Promise.all(recent.map(({ f }) => Bun.file(f).text()))
      return {
        content: [{ type: 'text' as const, text: contents.join('\n\n---\n\n') }],
      }
    } catch {
      return {
        content: [{ type: 'text' as const, text: `No journal directory found for target: ${target}` }],
      }
    }
  })

  // ============================================================
  // Search tool (1)
  // ============================================================

  server.registerTool('nw_search_journal', {
    description: 'Search journal entries for a specific target by keyword or phrase',
    inputSchema: {
      target: z.string().describe('Target name to search journal entries for'),
      query: z.string().describe('Search query (case-insensitive)'),
    },
  }, async ({ target, query }) => {
    const journalDir = path.join(NW_JOURNAL_BASE, target, '.private-journal')
    try {
      const glob = new Bun.Glob('*.md')
      const files: string[] = []
      for await (const file of glob.scan({ cwd: journalDir, absolute: true })) {
        files.push(file)
      }
      if (!files.length) {
        return {
          content: [{ type: 'text' as const, text: `No journal entries found for target: ${target}` }],
        }
      }

      const queryLower = query.toLowerCase()
      const matches: string[] = []
      for (const f of files) {
        const content = await Bun.file(f).text()
        if (content.toLowerCase().includes(queryLower)) {
          matches.push(`--- ${path.basename(f)} ---\n${content}`)
        }
      }

      if (!matches.length) {
        return {
          content: [{ type: 'text' as const, text: `No entries matching "${query}" found for target: ${target}` }],
        }
      }
      return {
        content: [{ type: 'text' as const, text: matches.join('\n\n') }],
      }
    } catch {
      return {
        content: [{ type: 'text' as const, text: `No journal directory found for target: ${target}` }],
      }
    }
  })

  // ============================================================
  // Action tools (4)
  // ============================================================

  server.registerTool('nw_trigger_run', {
    description: 'Trigger a nightwatch run for a target. Returns run_id for tracking.',
    inputSchema: {
      target: z.string().describe('Target name or __all__ to run all targets'),
      mode: z.enum(['production', 'dry-run']).optional().describe('Run mode (default: production)'),
      custom_prompt: z.string().optional().describe('Custom prompt to inject into the run'),
    },
  }, async ({ target, mode = 'production', custom_prompt }) => {
    if (workerStatus !== 'online') {
      return {
        content: [{ type: 'text' as const, text: 'Worker is offline — cannot enqueue run' }],
        isError: true,
      }
    }

    const run_id = crypto.randomUUID()
    const run: Run = {
      id: run_id,
      target,
      mode,
      trigger: 'manual',
      status: 'queued',
      log_path: `runs/${run_id}/log.jsonl`,
      custom_prompt,
    }

    sendToWorker({ type: 'enqueue', run })
    await appendRun(run)

    return {
      content: [{ type: 'text' as const, text: JSON.stringify({ run_id, status: 'queued' }) }],
    }
  })

  server.registerTool('nw_submit_feedback', {
    description: 'Submit feedback (accepted/rejected) for a specific signal action from a run',
    inputSchema: {
      signal_id: z.string().describe('The signal ID from the run actions'),
      target: z.string().describe('Target name the signal belongs to'),
      run_id: z.string().describe('The run ID that produced the signal'),
      verdict: z.enum(['accepted', 'rejected']).describe('Feedback verdict'),
      reason: z.string().optional().describe('Optional reason for the feedback'),
    },
  }, async ({ signal_id, target, run_id, verdict, reason }) => {
    // Validate run exists
    const runData = await getRun(run_id)
    if (!runData) {
      return {
        content: [{ type: 'text' as const, text: `Run not found: ${run_id}` }],
        isError: true,
      }
    }

    // Validate signal_id exists in run's actions for this target
    const actions = runData.summary?.per_target[target]?.actions ?? []
    const signalExists = actions.some(a => a.signal_id === signal_id)
    if (!signalExists) {
      return {
        content: [{ type: 'text' as const, text: `Signal not found: ${signal_id} in run ${run_id} for target ${target}` }],
        isError: true,
      }
    }

    const entry: FeedbackEntry = {
      signal_id,
      target,
      run_id,
      verdict,
      reason,
      source: 'user',
      submitted_at: new Date().toISOString(),
    }

    await appendFeedback(entry)
    return {
      content: [{ type: 'text' as const, text: JSON.stringify({ ok: true }) }],
    }
  })

  server.registerTool('nw_update_schedule', {
    description: 'Update the nightwatch run schedule configuration',
    inputSchema: {
      enabled: z.boolean().optional().describe('Whether scheduled runs are enabled'),
      interval_hours: z.number().optional().describe('Hours between scheduled runs'),
    },
  }, async ({ enabled, interval_hours }) => {
    const config = await loadOrCreateAppConfig()

    if (enabled !== undefined) config.schedule.enabled = enabled
    if (interval_hours !== undefined) config.schedule.interval_hours = interval_hours

    await writeAppConfig(config)
    sendToWorker({ type: 'schedule', config: config.schedule })

    return {
      content: [{ type: 'text' as const, text: JSON.stringify(config.schedule) }],
    }
  })

  server.registerTool('nw_implement_proposal', {
    description: 'Implement a proposal (stub — use nw_trigger_run with custom_prompt instead)',
    inputSchema: {
      proposal_id: z.string().describe('The proposal ID to implement'),
    },
  }, async () => {
    return {
      content: [{
        type: 'text' as const,
        text: 'Proposal implementation is not yet available via MCP. Use nw_trigger_run with a custom prompt to implement proposals manually.',
      }],
    }
  })

  return server
}
