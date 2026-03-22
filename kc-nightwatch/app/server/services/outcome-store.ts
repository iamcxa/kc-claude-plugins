import path from 'node:path'
import os from 'node:os'
import { readYamlFile, writeYamlFile } from './yaml-store.ts'
import type { OutcomeRecord } from '../../shared/types.ts'

// D-05: Store in ~/.claude/kc-plugins-config/ matching existing config file pattern
export const OUTCOMES_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-outcomes.yaml')

/**
 * Read all outcome records from outcomes.yaml.
 * Returns empty array if file does not exist or has no outcomes key.
 */
export async function readOutcomes(outcomesPath = OUTCOMES_YAML_PATH): Promise<OutcomeRecord[]> {
  const data = await readYamlFile<{ outcomes: OutcomeRecord[] }>(outcomesPath)
  return data?.outcomes ?? []
}

/**
 * Append a single outcome record to outcomes.yaml.
 * Creates the file if it does not exist.
 * New records are prepended (most recent first).
 */
export async function appendOutcome(record: OutcomeRecord, outcomesPath = OUTCOMES_YAML_PATH): Promise<void> {
  const existing = await readOutcomes(outcomesPath)
  existing.unshift(record)
  await writeYamlFile(outcomesPath, { outcomes: existing })
}

/**
 * Query outcomes with optional filters.
 * Returns records sorted by created_at descending.
 *
 * Filters:
 * - target: exact match on target name
 * - type: 'pr' | 'linear_issue'
 * - status: 'open' | 'merged' | 'closed' | 'completed' | 'cancelled'
 * - since: ISO date string (inclusive) — returns records with created_at >= since
 */
export async function queryOutcomes(
  filter: { target?: string; type?: string; status?: string; since?: string } = {},
  outcomesPath = OUTCOMES_YAML_PATH,
): Promise<OutcomeRecord[]> {
  let records = await readOutcomes(outcomesPath)

  if (filter.target) {
    records = records.filter(r => r.target === filter.target)
  }
  if (filter.type) {
    records = records.filter(r => r.type === filter.type)
  }
  if (filter.status) {
    records = records.filter(r => r.status === filter.status)
  }
  if (filter.since) {
    records = records.filter(r => r.created_at >= filter.since!)
  }

  // Sort by created_at descending (most recent first)
  records.sort((a, b) => b.created_at.localeCompare(a.created_at))

  return records
}
