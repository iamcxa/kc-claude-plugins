import { log } from '../../shared/logger.ts'
import { ORPHAN_SIGTERM_WAIT_MS } from '../../shared/constants.ts'

export async function cleanupOrphans(): Promise<void> {
  const proc = Bun.spawn(['pgrep', '-f', 'safehouse.*claude'], { stdout: 'pipe' })
  await proc.exited
  const output = await Bun.readableStreamToText(proc.stdout)

  const pids = output.trim().split('\n').filter(Boolean).map(Number).filter(n => !isNaN(n))
  if (pids.length === 0) return

  log.warn({ component: 'server', msg: `Found ${pids.length} orphan process(es): ${pids.join(', ')}` })
  for (const pid of pids) {
    try {
      process.kill(pid, 'SIGTERM')
      await Bun.sleep(ORPHAN_SIGTERM_WAIT_MS)
      try { process.kill(pid, 'SIGKILL') } catch { /* already gone */ }
    } catch {
      // Process already gone
    }
  }
  log.info({ component: 'server', msg: `Cleaned up ${pids.length} orphan process(es)` })
}
