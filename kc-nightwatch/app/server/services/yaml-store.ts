import { parse, stringify } from 'yaml'
import { log } from '../../shared/logger.ts'
import { AppConfigSchema, type AppConfig } from '../../shared/types.ts'
import {
  DEFAULT_HOST,
  DEFAULT_PORT,
} from '../../shared/constants.ts'

const APP_CONFIG_PATH = new URL('../../../nightwatch-app.yaml', import.meta.url).pathname

const DEFAULT_APP_CONFIG: AppConfig = {
  host: DEFAULT_HOST,
  port: DEFAULT_PORT,
  schedule: { enabled: false, self_repair_before: true },
  max_concurrent_runs: 1,
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
