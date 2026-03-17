import { z } from 'zod'

// IPC message unions
export type ServerToWorker =
  | { type: 'enqueue'; run: Run }
  | { type: 'cancel'; run_id: string }
  | { type: 'shutdown' }
  | { type: 'status' }

export type WorkerToServer =
  | { type: 'heartbeat'; ts: number }
  | { type: 'run:started'; run_id: string; pid: number }
  | { type: 'run:log'; run_id: string; event: ParsedLogEvent }
  | { type: 'run:completed'; run_id: string; summary: RunSummary }
  | { type: 'run:failed'; run_id: string; error: string }
  | { type: 'state'; queue: Run[]; current?: Run }

export type IpcMessage = ServerToWorker | WorkerToServer

// Zod schemas
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
  plugins_dir: z.string(),
})
export type AppConfig = z.infer<typeof AppConfigSchema>

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

export interface RunSummary {
  phases_completed: string[]
  signals_found: number
  actions_taken: number
  errors: string[]
}

export interface ParsedLogEvent {
  type: string
  content?: string
  raw: string
}
