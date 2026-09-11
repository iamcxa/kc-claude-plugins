#!/usr/bin/env node

import { connect } from 'node:net'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const MIN_NODE = [22, 13, 0]

const checks = []
const ok = (name, detail) => checks.push({ name, ok: true, detail })
const bad = (name, detail, fix) => checks.push({ name, ok: false, detail, fix })

const [maj, min, pat] = process.versions.node.split('.').map(Number)
const newEnough = maj > MIN_NODE[0] || (maj === MIN_NODE[0] && (min > MIN_NODE[1] || (min === MIN_NODE[1] && pat >= MIN_NODE[2])))
if (newEnough) ok('node', process.version)
else
	bad(
		'node',
		`${process.version} — the canvas stores rooms in node:sqlite, which needs no flag only from v22.13.0`,
		'upgrade Node, or run the canvas on a machine with v22.13.0 or later'
	)

if (existsSync(join(ROOT, 'node_modules', 'tldraw'))) ok('dependencies', 'installed')
else bad('dependencies', 'node_modules is missing or incomplete', `npm install --prefix ${ROOT}`)

// Bind probes can miss listeners using a different IPv4/IPv6 address.
const portFree = (port) =>
	new Promise((resolve) => {
		const socket = connect({ port, host: '127.0.0.1' })
		const done = (free) => {
			socket.destroy()
			resolve(free)
		}
		socket.setTimeout(700)
		socket.once('connect', () => done(false))
		socket.once('error', () => done(true))
		socket.once('timeout', () => done(true))
	})

for (const [port, what] of [
	[5858, 'doc API'],
	[3737, 'canvas'],
]) {
	if (await portFree(port)) ok(`port ${port}`, `free (${what})`)
	else bad(`port ${port}`, `in use (${what})`, 'stop the other canvas, or free the port — several sessions cannot share one')
}

for (const { name, ok: good, detail, fix } of checks) {
	console.log(`${good ? 'ok  ' : 'FAIL'}  ${name.padEnd(14)} ${detail}`)
	if (!good) console.log(`      -> ${fix}`)
}

const failed = checks.filter((c) => !c.ok)
if (failed.length) {
	console.log(`\n${failed.length} check(s) failed. Resolve the failed prerequisites before starting the canvas.`)
	process.exit(1)
}
console.log('\nReady. npm run canvas')
