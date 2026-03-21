import type { Target, Run, RunSummary, ScheduleConfig, ConfigValidationResult, FeedbackEntry, CalibrationData, TargetHealthData } from '../../shared/types.ts'

const BASE = ''

async function get<T>(path: string): Promise<T> {
  const res = await fetch(BASE + path)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json() as Promise<T>
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`)
  return res.json() as Promise<T>
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`PUT ${path} failed: ${res.status}`)
  return res.json() as Promise<T>
}

async function del(path: string): Promise<void> {
  await fetch(BASE + path, { method: 'DELETE' })
}

export const api = {
  getTargets(): Promise<Target[]> {
    return get<Target[]>('/api/targets')
  },

  getRuns(filter?: { status?: string; target?: string }): Promise<Run[]> {
    const params = new URLSearchParams()
    if (filter?.status) params.set('status', filter.status)
    if (filter?.target) params.set('target', filter.target)
    const qs = params.toString()
    return get<Run[]>(`/api/runs${qs ? `?${qs}` : ''}`)
  },

  getRun(id: string): Promise<Run & { summary?: RunSummary }> {
    return get<Run & { summary?: RunSummary }>(`/api/runs/${id}`)
  },

  triggerRun(body: {
    target: string
    mode: Run['mode']
    custom_prompt?: string
    self_repair?: boolean
  }): Promise<{ run_id: string }> {
    return post<{ run_id: string }>('/api/runs', body)
  },

  cancelRun(id: string): Promise<void> {
    return del(`/api/runs/${id}`)
  },

  getSchedule(): Promise<ScheduleConfig> {
    return get<ScheduleConfig>('/api/schedule')
  },

  updateSchedule(partial: Partial<ScheduleConfig>): Promise<ScheduleConfig> {
    return put<ScheduleConfig>('/api/schedule', partial)
  },

  webhook(body: { target?: string; mode?: Run['mode'] }): Promise<{ run_id: string }> {
    return post<{ run_id: string }>('/api/webhook', body)
  },

  // Chat
  sendChatMessage(target: string, message: string): Promise<{ ok: boolean }> {
    return post<{ ok: boolean }>(`/api/chat/${encodeURIComponent(target)}/message`, { message })
  },

  resetChatSession(target: string): Promise<{ ok: boolean }> {
    return post<{ ok: boolean }>(`/api/chat/${encodeURIComponent(target)}/reset`)
  },

  briefChat(target: string, summary: unknown): Promise<{ ok: boolean }> {
    return post<{ ok: boolean }>(`/api/chat/${encodeURIComponent(target)}/brief`, { summary })
  },

  // Feedback
  submitFeedback(body: {
    signal_id: string; target: string; run_id: string;
    verdict: 'accepted' | 'rejected'; reason?: string
  }): Promise<{ ok: boolean }> {
    return post<{ ok: boolean }>('/api/feedback', body)
  },

  getFeedback(runId: string): Promise<FeedbackEntry[]> {
    return get<FeedbackEntry[]>(`/api/feedback/${runId}`)
  },

  getCalibration(): Promise<CalibrationData[]> {
    return get<CalibrationData[]>('/api/feedback/calibration')
  },

  // Config
  getConfig(file: 'targets' | 'safety'): Promise<{ content: string }> {
    return get<{ content: string }>(`/api/config/${file}`)
  },

  validateConfig(file: 'targets' | 'safety', content: string): Promise<ConfigValidationResult> {
    return put<ConfigValidationResult>(`/api/config/${file}`, { content })
  },

  saveConfig(file: 'targets' | 'safety', content: string): Promise<{ ok: boolean }> {
    return put<{ ok: boolean }>(`/api/config/${file}`, { content, confirm: true })
  },

  getConfigWarnings(): Promise<{ warnings: Record<string, unknown> }> {
    return get<{ warnings: Record<string, unknown> }>('/api/config/warnings')
  },

  addTarget(name: string, target: Record<string, unknown>): Promise<{ ok: boolean }> {
    return post<{ ok: boolean }>('/api/config/targets/add', { name, target })
  },

  editTarget(name: string, target: Record<string, unknown>): Promise<{ ok: boolean }> {
    return put<{ ok: boolean }>(`/api/config/targets/${encodeURIComponent(name)}`, { target })
  },

  removeTarget(name: string): Promise<void> {
    return del(`/api/config/targets/${encodeURIComponent(name)}`)
  },

  // Health
  getHealth(target: string): Promise<TargetHealthData> {
    return get<TargetHealthData>(`/api/health/${encodeURIComponent(target)}`)
  },

  // Worker state (queue visibility)
  getWorkerState(): Promise<{ queue: Run[]; active: Run[]; schedule?: ScheduleConfig }> {
    return get<{ queue: Run[]; active: Run[]; schedule?: ScheduleConfig }>('/api/worker/state')
  },
}
