import { z } from 'zod'

// ============================================================
// Target type — reflects nightwatch-targets.yaml v2 schema
// ============================================================
export interface Target {
  name: string
  type: 'plugin' | 'product'
  monitors: string[]        // ['github-issues', 'journal', 'git-churn', ...]
  watch: string[]           // search keywords
  respond: Record<string, boolean>  // { 'code-fix': true, 'proposal': true }
  indicators: Array<{ id: string; description: string; target?: string }>
  north_star: string
  path?: string             // absolute path to target repo/dir
  auth?: string
  extra_plugin_dirs?: string[]
  extra_mcp_config?: string[]
}

// ============================================================
// ScheduleConfig — exported standalone (extracted from AppConfigSchema)
// ============================================================
export interface ScheduleConfig {
  enabled: boolean
  interval_hours?: number
  self_repair_before: boolean
}

// ============================================================
// IPC message unions
// ============================================================
export type ServerToWorker =
  | { type: 'enqueue'; run: Run }
  | { type: 'cancel'; run_id: string }
  | { type: 'shutdown' }
  | { type: 'status' }
  | { type: 'schedule'; config: ScheduleConfig }

export type WorkerToServer =
  | { type: 'heartbeat'; ts: number }
  | { type: 'run:started'; run_id: string; pid: number }
  | { type: 'run:log'; run_id: string; event: ParsedLogEvent }
  | { type: 'run:completed'; run_id: string; summary: RunSummary }
  | { type: 'run:failed'; run_id: string; error: string }
  | { type: 'state'; queue: Run[]; current?: Run; schedule?: ScheduleConfig }

export type IpcMessage = ServerToWorker | WorkerToServer

// ============================================================
// Zod schemas
// ============================================================
export const AppConfigSchema = z.object({
  host: z.string().default('127.0.0.1'),
  port: z.number().default(3200),
  auth_token: z.string().optional(),
  schedule: z.object({
    enabled: z.boolean().default(false),
    interval_hours: z.number().optional(),
    self_repair_before: z.boolean().default(true),
  }),
  max_concurrent_runs: z.literal(1),
  safehouse_path: z.string().optional(),
  plugins_dir: z.string().default(`${process.env.HOME ?? '/tmp'}/.claude/plugins/local`),
})
export type AppConfig = z.infer<typeof AppConfigSchema>

// ============================================================
// Run type
// ============================================================
export interface Run {
  id: string
  target: string | '__all__'
  mode: 'production' | 'dry-run' | 'self-repair'
  trigger: 'manual' | 'interval' | 'webhook' | 'implementation'
  status: 'queued' | 'running' | 'completed' | 'failed' | 'timeout' | 'cancelled'
  custom_prompt?: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  log_path: string
}

// ============================================================
// RunSummary — full Appendix B shape
// ============================================================
export interface RunSummaryAction {
  signal_id: string
  type: string
  summary: string
  pr_url?: string
  branch?: string
  indicator: string
  assessment: {
    closer_to_north_star: 'yes' | 'no' | 'uncertain'
    confidence: 'high' | 'medium' | 'low'
    reasoning: string
  }
}

export interface IndicatorBaseline {
  value: number
  measurement: string
  previous_value?: number
  trend: 'improving' | 'stable' | 'degrading'
}

export interface ImplementationOutcome {
  proposal_id: string
  pr_url: string
  target: string
  indicator: string
  before: number
  after: number
  delta: number
  effective: boolean
}

export interface PerTargetSummary {
  monitors: Record<string, { status: string; signals: number }>
  pipeline: {
    found: number
    after_dedup: number
    after_confidence_filter: number
    after_cooldown: number
    classified: Record<string, number>
    executed: Record<string, number>
  }
  actions: RunSummaryAction[]
  indicator_baseline: Record<string, IndicatorBaseline>
  implementation_outcomes: ImplementationOutcome[]
  pre_assessment: string
  post_assessment: string
}

export interface RunSummary {
  targets_active: number
  targets_skipped: number
  total_signals: number
  total_actions: number
  errors: number
  per_target: Record<string, PerTargetSummary>
  // Legacy compat fields (Phase 1 executor still populates these) — keep so executor.ts compiles
  phases_completed?: string[]
}

// ============================================================
// ParsedLogEvent — extended with Phase 2 fields
// ============================================================
export interface ParsedLogEvent {
  type: string
  content?: string
  raw: string
  // Phase 2 additions:
  phase?: string            // e.g. "Phase 2", "Phase 3.5"
  tool_name?: string        // extracted from tool_use blocks
  agent_name?: string       // from "Dispatching {name} agent" text
  is_phase_start?: boolean
  is_phase_complete?: boolean
}
