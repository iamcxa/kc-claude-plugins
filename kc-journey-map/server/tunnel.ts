import { spawn, type ChildProcess } from 'node:child_process'
import { openSync, writeSync } from 'node:fs'
import { connect } from 'node:net'

// Never this API: a public doc API is an unauthenticated write path into every room.
const TARGET = process.env.JOURNEY_SHARE_URL ?? `http://127.0.0.1:${process.env.JOURNEY_SHARE_PORT ?? 3738}`
const LOG = process.env.JOURNEY_TUNNEL_LOG ?? './.tunnel.log'
const URL_PATTERN = /https:\/\/[a-z0-9-]+\.trycloudflare\.com/
const DEADLINE_MS = Number(process.env.JOURNEY_TUNNEL_TIMEOUT_MS ?? 45_000)

type StartResult = { url: string } | { error: string; status: number }

let child: ChildProcess | null = null
let url: string | null = null

export function tunnelStatus(): { running: boolean; url: string | null; target: string } {
	return { running: child !== null, url, target: TARGET }
}

function targetReachable(): Promise<boolean> {
	const { hostname, port } = new URL(TARGET)
	return new Promise((resolve) => {
		const socket = connect({ host: hostname, port: Number(port) })
		const done = (reachable: boolean) => {
			socket.destroy()
			resolve(reachable)
		}
		socket.setTimeout(1000)
		socket.once('connect', () => done(true))
		socket.once('error', () => done(false))
		socket.once('timeout', () => done(false))
	})
}

export async function startTunnel(): Promise<StartResult> {
	if (child && url) return { url }
	if (!(await targetReachable())) {
		return { error: `nothing is listening on ${TARGET} — start the share front-end first`, status: 409 }
	}

	const log = openSync(LOG, 'a')
	// Default grace period is 30s; the stop button has to take effect now, not eventually.
	const proc = spawn('cloudflared', ['tunnel', '--grace-period', '0s', '--url', TARGET], { stdio: ['ignore', 'pipe', 'pipe'] })
	child = proc
	proc.on('exit', () => {
		if (child === proc) {
			child = null
			url = null
		}
	})

	return await new Promise<StartResult>((resolve) => {
		let settled = false
		const finish = (result: StartResult) => {
			if (settled) return
			settled = true
			clearTimeout(timer)
			resolve(result)
		}
		const timer = setTimeout(() => {
			proc.kill()
			finish({ error: 'cloudflared did not report a URL in time', status: 504 })
		}, DEADLINE_MS)

		const scan = (chunk: Buffer) => {
			writeSync(log, chunk)
			const match = chunk.toString().match(URL_PATTERN)
			if (match) {
				url = match[0]
				finish({ url: match[0] })
			}
		}
		proc.stdout?.on('data', scan)
		proc.stderr?.on('data', scan)
		proc.once('error', (e) => finish({ error: `cloudflared failed to start: ${e.message}`, status: 500 }))
		proc.once('exit', (code) => finish({ error: `cloudflared exited with code ${code}`, status: 500 }))
	})
}

export function stopTunnel(): boolean {
	if (!child) return false
	const proc = child
	proc.kill()
	setTimeout(() => proc.killed || proc.kill('SIGKILL'), 3000).unref()
	child = null
	url = null
	return true
}

// A tunnel that outlives this process is a public URL nobody is watching.
for (const signal of ['exit', 'SIGINT', 'SIGTERM'] as const) {
	process.on(signal, () => {
		child?.kill()
		if (signal !== 'exit') process.exit(0)
	})
}
