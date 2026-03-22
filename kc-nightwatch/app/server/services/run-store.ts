import path from 'node:path'
import os from 'node:os'
import { readYamlFile, writeYamlFile } from './yaml-store.ts'
import type { Run, RunSummary } from '../../shared/types.ts'

export const RUNS_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-runs.yaml')
// Runs artifacts directory (relative to app dir — contains per-run subdirs with log.jsonl + summary.yaml)
const RUNS_ARTIFACTS_DIR = new URL('../../../runs', import.meta.url).pathname

export async function listRuns(filter?: { status?: string; target?: string }): Promise<Run[]> {
  const data = await readYamlFile<{ runs: Run[] }>(RUNS_YAML_PATH)
  let runs = data?.runs ?? []
  if (filter?.status) runs = runs.filter(r => r.status === filter.status)
  if (filter?.target) runs = runs.filter(r => r.target === filter.target)
  // Sort by started_at desc, cap at 100
  runs.sort((a, b) => (b.started_at ?? '').localeCompare(a.started_at ?? ''))
  return runs.slice(0, 100)
}

export async function getRun(id: string): Promise<(Run & { summary?: RunSummary }) | null> {
  const runs = await listRuns()
  const run = runs.find(r => r.id === id) ?? null
  if (!run) return null
  const summaryPath = path.join(RUNS_ARTIFACTS_DIR, id, 'summary.yaml')
  const summary = await readYamlFile<RunSummary>(summaryPath)
  return { ...run, summary: summary ?? undefined }
}

export async function appendRun(run: Run): Promise<void> {
  const data = await readYamlFile<{ runs: Run[] }>(RUNS_YAML_PATH)
  const runs = data?.runs ?? []
  runs.unshift(run)
  await writeYamlFile(RUNS_YAML_PATH, { runs })
}

export async function updateRunStatus(
  runId: string,
  updates: Partial<Pick<Run, 'status' | 'started_at' | 'completed_at' | 'duration_seconds'>>
): Promise<void> {
  const data = await readYamlFile<{ runs: Run[] }>(RUNS_YAML_PATH)
  const runs = data?.runs ?? []
  const run = runs.find(r => r.id === runId)
  if (run) {
    Object.assign(run, updates)
    await writeYamlFile(RUNS_YAML_PATH, { runs })
  }
}
