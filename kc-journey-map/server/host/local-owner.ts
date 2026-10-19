import { spawn } from 'node:child_process'
import { createInterface } from 'node:readline'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { NodeHost } from './node'

export async function startLocalOwner(host: NodeHost) {
 if (host.humanConfig?.mode !== 'local') return () => {}
 const path = join(host.root, 'owner-login.sock')
 const child = spawn('python3', [fileURLToPath(new URL('../../scripts/owner-login.py', import.meta.url)), '--serve', path, String(host.humanConfig.localOwnerUid)], { stdio: ['pipe', 'pipe', 'pipe'] })
 const lines = createInterface({ input: child.stdout })
 let started = false, diagnostic = ''
 const ready = new Promise<void>((resolve, reject) => {
  child.once('error', () => reject(new Error('Python 3 owner peer channel unavailable')))
  child.once('exit', () => { host.localHumanReady = false; if (!started) reject(new Error(diagnostic.trim() || 'owner peer channel unavailable')) })
  child.stderr.on('data', data => { diagnostic = (diagnostic + data.toString()).slice(-512) })
  lines.on('line', async line => {
   try {
    const message = JSON.parse(line)
    if (message.ready === true) { started = true; host.localHumanReady = true; resolve(); return }
    const result = await host.meta.human!(message.op, { requestId: message.requestId, peerUid: message.peerUid })
    child.stdin.write(JSON.stringify(result) + '\n')
   } catch (error) {
    child.stdin.write(JSON.stringify({ error: error instanceof Error ? error.message : 'owner approval unavailable' }) + '\n')
   }
  })
 })
 await ready
 return () => { host.localHumanReady = false; child.stdin.end(); child.kill('SIGTERM') }
}
