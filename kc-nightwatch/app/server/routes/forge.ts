import path from 'node:path'
import os from 'node:os'
import { Hono } from 'hono'
import { readYamlFile } from '../services/yaml-store.ts'
import type { ForgeResultData } from '../../shared/types.ts'

export const forgeRoutes = new Hono()

// D-10: Same file as /api/config/warnings but different field
// NOT imported from config.ts (not exported there — Pitfall 5)
const SELF_REPAIR_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-self-repair.yaml')
const STALE_THRESHOLD_MS = 36 * 60 * 60 * 1000  // 36 hours

forgeRoutes.get('/api/forge/results', async (c) => {
  const data = await readYamlFile<Record<string, unknown>>(SELF_REPAIR_YAML_PATH)

  if (!data) {
    return c.json({ forge_result: null, run_date: null, stale: true } satisfies ForgeResultData)
  }

  const runDate = (data.run_date as string | undefined) ?? null
  const stale = runDate
    ? (Date.now() - new Date(runDate).getTime()) > STALE_THRESHOLD_MS
    : true

  const forgeResult = (data.forge_result as ForgeResultData['forge_result'] | undefined) ?? null

  return c.json({ forge_result: forgeResult, run_date: runDate, stale } satisfies ForgeResultData)
})
