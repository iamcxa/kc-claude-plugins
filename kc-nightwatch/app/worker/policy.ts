import type { Run } from '../shared/types.ts'
import path from 'node:path'

// Target shape (minimal — full Target type is Phase 2)
export interface PolicyTarget {
  name: string
  resolved_path: string
  extra_plugin_dirs?: string[]
}

export function buildSafehouseFlags(target: PolicyTarget, run: Run, appRunsDir: string): string[] {
  const flags: string[] = []
  const homeDir = process.env.HOME ?? '/tmp'

  // CRITICAL: Never pass ~ paths to safehouse — it does not shell-expand tildes
  const resolve = (p: string) => p.startsWith('~')
    ? path.join(homeDir, p.slice(1))
    : p

  // Target dir — read-only for dry-run, read-write for production/self-repair
  if (run.mode === 'dry-run') {
    flags.push('--add-dirs-ro', target.resolved_path)
  } else {
    flags.push('--add-dirs', target.resolved_path)
  }

  // Plugin dirs — read-only
  const basePluginDirs = [
    path.join(homeDir, '.claude/plugins/local'),
  ]
  for (const dir of [...basePluginDirs, ...(target.extra_plugin_dirs ?? []).map(resolve)]) {
    flags.push('--add-dirs-ro', dir)
  }

  // User config dir — read + write
  flags.push('--add-dirs', path.join(homeDir, '.claude/kc-plugins-config'))

  // NW memory dir — read + write
  flags.push('--add-dirs', path.join(homeDir, `.claude/nightwatch/memory/${target.name}`))

  // Run artifacts dir — write only
  flags.push('--add-dirs', path.join(appRunsDir, run.id))

  // Assertion: no tilde paths in output
  for (const flag of flags) {
    if (flag.startsWith('~')) {
      throw new Error(`buildSafehouseFlags: tilde path not resolved: ${flag}`)
    }
  }

  return flags
}
