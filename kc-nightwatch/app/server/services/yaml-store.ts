import { parse, stringify } from 'yaml'
import path from 'node:path'
import os from 'node:os'
import { log } from '../../shared/logger.ts'
import { AppConfigSchema, type AppConfig, type Target } from '../../shared/types.ts'
import {
  DEFAULT_HOST,
  DEFAULT_PORT,
} from '../../shared/constants.ts'

const APP_CONFIG_PATH = new URL('../../../nightwatch-app.yaml', import.meta.url).pathname

const DEFAULT_APP_CONFIG: AppConfig = {
  host: DEFAULT_HOST,
  port: DEFAULT_PORT,
  schedule: { enabled: false, self_repair_before: true },
  plugins_dir: `${process.env.HOME ?? '/tmp'}/.claude/plugins/local`,
}

export async function loadOrCreateAppConfig(configPath = APP_CONFIG_PATH): Promise<AppConfig> {
  if (!(await Bun.file(configPath).exists())) {
    await Bun.write(configPath, stringify(DEFAULT_APP_CONFIG))
    log.info({ component: 'server', msg: `Created default nightwatch-app.yaml at ${configPath}` })
  }
  // Re-read from disk each time (do not reuse file handle created before write)
  const raw = parse(await Bun.file(configPath).text()) as unknown
  // Zod parse throws with readable message on schema mismatch
  return AppConfigSchema.parse(raw)
}

export async function readYamlFile<T>(filePath: string): Promise<T | null> {
  try {
    const file = Bun.file(filePath)
    if (!(await file.exists())) return null
    return parse(await file.text()) as T
  } catch (err) {
    log.warn({ component: 'server', msg: `Failed to read YAML: ${filePath} — ${String(err)}` })
    return null
  }
}

export async function writeYamlFile(filePath: string, data: unknown): Promise<void> {
  await Bun.write(filePath, stringify(data as Record<string, unknown>))
}

// ============================================================
// Phase 2 extensions
// ============================================================

export const TARGETS_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-targets.yaml')

// Appendix A compat: accept both old and new field names
function normalizeTarget(name: string, raw: Record<string, unknown>): Target {
  return {
    name,
    type: (raw.type as Target['type']) ?? 'plugin',
    monitors: (raw.monitors ?? raw.sources ?? []) as string[],
    watch: (raw.watch ?? raw.keywords ?? []) as string[],
    respond: (raw.respond ?? mapOldActions(raw.actions)) as Record<string, boolean>,
    indicators: (raw.indicators ?? raw.proxy_signals ?? []) as Target['indicators'],
    north_star: (raw.north_star as string) ?? '',
    path: raw.path as string | undefined,
    auth: raw.auth as string | undefined,
    extra_plugin_dirs: (raw.extra_plugin_dirs ?? []) as string[],
    extra_mcp_config: (raw.extra_mcp_config ?? []) as string[],
  }
}

function mapOldActions(actions: unknown): Record<string, boolean> {
  if (!Array.isArray(actions)) return {}
  return Object.fromEntries((actions as string[]).map((a) => {
    const key = a === 'quick-fix' ? 'code-fix' : a
    return [key, true]
  }))
}

export async function readTargets(): Promise<Record<string, Target>> {
  const raw = await readYamlFile<{ targets: Record<string, unknown> }>(TARGETS_YAML_PATH)
  if (!raw?.targets) return {}
  return Object.fromEntries(
    Object.entries(raw.targets).map(([name, t]) => [name, normalizeTarget(name, t as Record<string, unknown>)])
  )
}

/**
 * Write targets back to TARGETS_YAML_PATH, preserving the `targets:` wrapper key.
 * Used by PUT /api/targets/:name to persist per-target schedule overrides.
 */
export async function writeTargets(targets: Record<string, Target>): Promise<void> {
  // Preserve the wrapper key structure: { targets: { name: Target } }
  await writeYamlFile(TARGETS_YAML_PATH, { targets })
}

export async function writeAppConfig(config: AppConfig, configPath = APP_CONFIG_PATH): Promise<void> {
  // Always re-create file handle (Pitfall: stale handle after write)
  await Bun.write(configPath, stringify(config as Record<string, unknown>))
}
