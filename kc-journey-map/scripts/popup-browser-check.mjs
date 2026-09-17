#!/usr/bin/env node
// Browser evidence for canvas-document-popup (issue #465), AC-1..AC-5. Uses
// agent-browser (the project's own browser-automation CLI, already used by
// sequence-smoke.mjs) so every click is a real CDP-dispatched pointer event —
// not a scripted DOM dispatch — and asserts each control's effect, not its
// presence. Builds its own fixture repo and runs its own server/Vite pair on
// free ports; touches no port this repository's own docs reserve (3737/3742,
// 5858/5959, 3799/3800+) and leaves any already-running canvas untouched.
import { execFile, execFileSync, spawn } from 'node:child_process'
import { connect } from 'node:net'
import { mkdtempSync, mkdirSync, rmSync, writeFileSync, appendFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, join } from 'node:path'
import { promisify } from 'node:util'

// Every call here is curl; a hard cap keeps a stuck server from hanging the whole script.
const execFileP = promisify(execFile)
const run = (cmd, args) => execFileP(cmd, [...args, '--max-time', '10'])
const ROOT = new URL('..', import.meta.url).pathname.replace(/\/$/, '')
// AC-5's bare host is built from the repository this package's directory lives in,
// via `git archive`, which must run one level up (a pathspec is repo-relative).
const REPO_ROOT = join(ROOT, '..')

const failures = []
function check(label, cond, detail) {
	console.log(`${cond ? 'PASS' : 'FAIL'}: ${label}${detail ? ' — ' + detail : ''}`)
	if (!cond) failures.push(label)
}

const portFree = (port) =>
	new Promise((resolve) => {
		const socket = connect({ port, host: '127.0.0.1' })
		const done = (free) => {
			socket.destroy()
			resolve(free)
		}
		socket.setTimeout(500)
		socket.once('connect', () => done(false))
		socket.once('error', () => done(true))
		socket.once('timeout', () => done(true))
	})

async function freePort(start) {
	for (let port = start; port < start + 200; port++) {
		if (await portFree(port)) return port
	}
	throw new Error(`no free port found from ${start}`)
}

function git(cwd, args) {
	return execFileSync('git', args, { cwd, encoding: 'utf8' }).trim()
}

function buildFixtureRepo(dir) {
	mkdirSync(join(dir, 'docs'), { recursive: true })
	git(dir, ['init', '-q', '-b', 'main'])
	git(dir, ['config', 'user.email', 'popup-check@example.com'])
	git(dir, ['config', 'user.name', 'popup-browser-check'])
	writeFileSync(
		join(dir, 'docs', 'demo-chapter.md'),
		[
			'# Demo chapter',
			'',
			'Intro paragraph before the sequence.',
			'',
			'## Sequence',
			'',
			'```mermaid',
			'sequenceDiagram',
			'    autonumber',
			'    participant A',
			'    participant B',
			'    A->>B: one',
			'    B->>A: two',
			'    A->>B: three',
			'    B->>A: four',
			'```',
			'',
			'<script>window.__popup_xss_fired = true</script>',
			'',
			'## Another heading',
			'',
			'More text under another heading.',
			'',
		].join('\n'),
	)
	git(dir, ['add', 'docs/demo-chapter.md'])
	git(dir, ['commit', '-q', '-m', 'add demo chapter'])
	git(dir, ['checkout', '-q', '-b', 'review'])
	appendFileSync(join(dir, 'docs', 'demo-chapter.md'), '\n## Review-only section\n\nThis section only exists on the review branch.\n')
	git(dir, ['commit', '-q', '-am', 'add review-only section'])
	git(dir, ['checkout', '-q', '-b', 'feature/foo', 'main'])
	writeFileSync(join(dir, 'docs', 'feature-doc.md'), 'feature-foo content\n')
	git(dir, ['add', 'docs/feature-doc.md'])
	git(dir, ['commit', '-q', '-m', 'feature branch doc'])
	git(dir, ['checkout', '-q', 'main'])
}

function spawnLogged(cmd, args, opts) {
	// detached so cleanup() can kill the whole process group: `npx` spawns tsx/vite
	// as a child of itself, and killing only the npx PID leaves that grandchild running.
	const child = spawn(cmd, args, { ...opts, stdio: ['ignore', 'pipe', 'pipe'], detached: true })
	let out = ''
	child.stdout.on('data', (d) => (out += d))
	child.stderr.on('data', (d) => (out += d))
	child.output = () => out
	return child
}

async function waitFor(fn, timeoutMs, label) {
	const start = Date.now()
	while (Date.now() - start < timeoutMs) {
		if (await fn()) return true
		await new Promise((r) => setTimeout(r, 200))
	}
	throw new Error(`timed out waiting for: ${label}`)
}

const SESSION = `popup-check-${process.pid}`
function browser(args, input) {
	return execFileSync('agent-browser', ['--session', SESSION, ...args], { encoding: 'utf8', input, timeout: 30000 })
}
function browserEval(js) {
	return JSON.parse(browser(['eval', '--json', '--stdin'], js)).data.result
}

async function openRoomAndLink(base, room, url) {
	browser(['open', `${base}/?room=${room}`])
	await waitFor(async () => browserEval('!!window.editor'), 15000, 'editor ready')
	browser(
		['eval', '--stdin'],
		`(function(){window.editor.run(()=>{window.editor.createShape({id:'shape:demo',type:'note',x:200,y:200,props:{url:${JSON.stringify(url)},color:'blue'}});window.editor.select('shape:demo')});return true})()`,
	)
}

function hitTestable(selector) {
	return browserEval(
		`(function(){const el=document.querySelector(${JSON.stringify(selector)});if(!el)return false;const r=el.getBoundingClientRect();const top=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return el===top||el.contains(top)})()`,
	)
}

const procs = []
const cleanupDirs = []
function cleanup() {
	for (const p of procs) {
		try {
			process.kill(-p.pid) // negative pid: the whole detached process group, not just npx
		} catch {}
	}
	try {
		browser(['close'])
	} catch {}
	for (const d of cleanupDirs) {
		try {
			rmSync(d, { recursive: true, force: true })
		} catch {}
	}
}
process.on('exit', cleanup)
process.on('SIGINT', () => process.exit(1))

async function startCanvas({ apiPort, vitePort, roomsDir, docRepos, allowedHosts }) {
	const env = {
		...process.env,
		JOURNEY_API_PORT: String(apiPort),
		JOURNEY_ROOMS_DIR: join(roomsDir, 'rooms'),
		JOURNEY_ASSETS_DIR: join(roomsDir, 'assets'),
		JOURNEY_SAVE_DIR: join(roomsDir, 'save'),
	}
	if (docRepos) env.JOURNEY_DOC_REPOS = docRepos
	const server = spawnLogged('npx', ['tsx', 'server/canvas-server.ts'], { cwd: ROOT, env })
	procs.push(server)
	await waitFor(async () => {
		try {
			await run('curl', ['-sf', `http://127.0.0.1:${apiPort}/health`])
			return true
		} catch {
			return false
		}
	}, 20000, `server on ${apiPort}`)

	const viteEnv = { ...env, JOURNEY_CANVAS_PORT: String(vitePort) }
	if (allowedHosts) viteEnv.JOURNEY_ALLOWED_HOSTS = allowedHosts
	const vite = spawnLogged('npx', ['vite', 'dev', '--host'], { cwd: ROOT, env: viteEnv })
	procs.push(vite)
	await waitFor(async () => {
		try {
			await run('curl', ['-sf', `http://127.0.0.1:${vitePort}/`])
			return true
		} catch {
			return false
		}
	}, 20000, `vite on ${vitePort}`)
	return `http://localhost:${vitePort}`
}

async function main() {
	const fixture = mkdtempSync(join(tmpdir(), 'popup-check-fixture-'))
	cleanupDirs.push(fixture)
	buildFixtureRepo(fixture)

	const runDir = mkdtempSync(join(tmpdir(), 'popup-check-run-'))
	cleanupDirs.push(runDir)

	const apiPort = await freePort(5900)
	const vitePort = await freePort(3900)
	const base = await startCanvas({
		apiPort,
		vitePort,
		roomsDir: runDir,
		docRepos: `demo-owner/demo-repo=${fixture}`,
		allowedHosts: 'sharedorigin.test',
	})

	// --- AC-1 + AC-2 + AC-3: open in place, render, close by Close and by Escape ---
	await openRoomAndLink(base, 'ac123', 'https://github.com/demo-owner/demo-repo/blob/main/docs/demo-chapter.md#sequence')
	const pagesBefore = JSON.parse(browser(['tab', 'list', '--json'])).data.tabs.length
	const before = browserEval('JSON.stringify({sel:window.editor.getSelectedShapeIds(),cam:window.editor.getCamera(),store:window.editor.store.getStoreSnapshot()})')

	browser(['click', 'a.tl-hyperlink-button'])
	await waitFor(async () => browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, 'popup opens')
	check('AC-1: popup opens with no new tab', JSON.parse(browser(['tab', 'list', '--json'])).data.tabs.length === pagesBefore)

	check('AC-3: Close button — elementFromPoint at its own centre resolves to it', hitTestable('dialog.doc-popup[open] button[aria-label="Close"]'))
	check('AC-3: Open on GitHub — elementFromPoint at its own centre resolves to it', hitTestable('dialog.doc-popup[open] a.doc-popup-source-link'))

	await waitFor(async () => {
		const svgNums = browserEval('(function(){const svg=document.querySelector(".doc-popup-mermaid svg");return svg?Array.from(svg.querySelectorAll(".sequenceNumber")).map(n=>n.textContent):null})()')
		return svgNums && svgNums.length === 4
	}, 5000, 'mermaid autonumber rendered')
	const svgNums = browserEval('Array.from(document.querySelectorAll(".doc-popup-mermaid .sequenceNumber")).map(n=>n.textContent)')
	check('AC-2: Mermaid autonumber renders 1..4', JSON.stringify(svgNums) === JSON.stringify(['1', '2', '3', '4']), JSON.stringify(svgNums))
	check('AC-2: embedded <script> in the document did not execute', browserEval("typeof window.__popup_xss_fired === 'undefined'") === true)

	browser(['click', 'dialog.doc-popup[open] button[aria-label="Close"]'])
	await waitFor(async () => !browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, 'popup closes on Close click')
	const after = browserEval('JSON.stringify({sel:window.editor.getSelectedShapeIds(),cam:window.editor.getCamera(),store:window.editor.store.getStoreSnapshot()})')
	check('AC-3: Close click removes the dialog', !browserEval('!!document.querySelector("dialog.doc-popup[open]")'))
	check('AC-3: focus restored to the originating trigger after Close click', browserEval('document.activeElement===document.querySelector("a.tl-hyperlink-button")'))
	check('AC-3: selection, camera and the diagram itself are unchanged after Close click', before === after)

	browser(['click', 'a.tl-hyperlink-button'])
	await waitFor(async () => browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, 'popup reopens for Escape check')
	browser(['press', 'Escape'])
	await waitFor(async () => !browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, 'Escape closes the dialog')
	check('AC-3: Escape closes the dialog', !browserEval('!!document.querySelector("dialog.doc-popup[open]")'))
	check('AC-3: focus restored to the originating trigger after Escape', browserEval('document.activeElement===document.querySelector("a.tl-hyperlink-button")'))

	browser(['click', 'a.tl-hyperlink-button'])
	await waitFor(async () => browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, 'popup reopens for Open-on-GitHub check')
	browser(['click', 'dialog.doc-popup[open] a.doc-popup-source-link', '--new-tab'])
	await waitFor(async () => JSON.parse(browser(['tab', 'list', '--json'])).data.tabs.length === pagesBefore + 1, 5000, 'Open on GitHub opens a new tab')
	const tabs = JSON.parse(browser(['tab', 'list', '--json'])).data.tabs
	check('AC-3/AC-4: Open on GitHub click opens a new tab targeting the source URL', tabs.some((t) => t.url.includes('demo-owner/demo-repo/blob/main/docs/demo-chapter.md')))
	browser(['tab', 'close', 't2'])
	browser(['tab', 't1'])
	check('popup unaffected by the GitHub tab (still open, same dialog)', browserEval('!!document.querySelector("dialog.doc-popup[open]")'))
	browser(['click', 'dialog.doc-popup[open] button[aria-label="Close"]'])

	// --- AC-4: loading / unavailable (bad ref, bad path, unmapped=D1) / missing-heading ---
	await openRoomAndLink(base, 'ac4-loading', 'https://github.com/demo-owner/demo-repo/blob/main/docs/demo-chapter.md#sequence')
	browser(
		['eval', '--stdin'],
		`(function(){const orig=window.fetch;window.fetch=function(input,...rest){const url=typeof input==='string'?input:input.url;if(url&&url.includes('/repo-doc')){return new Promise((resolve)=>setTimeout(()=>resolve(orig(input,...rest)),1200))}return orig(input,...rest)};return true})()`,
	)
	browser(['click', 'a.tl-hyperlink-button'])
	await new Promise((r) => setTimeout(r, 300))
	check('AC-4 loading: Loading state renders', browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent') === 'Loading…')
	check('AC-4 loading: Open on GitHub present and hit-testable during load', hitTestable('dialog.doc-popup[open] a.doc-popup-source-link'))
	await waitFor(async () => browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent') !== 'Loading…', 5000, 'loading resolves')
	check('AC-4 loading: resolves to rendered content', browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent').startsWith('Demo chapter'))

	const unavailableCase = async (room, url, expectSubstring, label) => {
		await openRoomAndLink(base, room, url)
		browser(['click', 'a.tl-hyperlink-button'])
		await waitFor(async () => {
			const text = browserEval('(function(){const d=document.querySelector("dialog.doc-popup[open] .doc-popup-body");return d?d.textContent:null})()')
			return text && text !== 'Loading…'
		}, 8000, `${label} resolves`)
		const text = browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent')
		check(`AC-4 ${label}: unavailable state with reason`, text.includes(expectSubstring), text)
		check(`AC-4 ${label}: Open on GitHub present and hit-testable`, hitTestable('dialog.doc-popup[open] a.doc-popup-source-link'))
		check(`AC-4 ${label}: Close hit-testable and click-closable (not only in the ready render)`, hitTestable('dialog.doc-popup[open] button[aria-label="Close"]'))
		browser(['click', 'dialog.doc-popup[open] button[aria-label="Close"]'])
		await waitFor(async () => !browserEval('!!document.querySelector("dialog.doc-popup[open]")'), 5000, `${label} closes`)
	}
	await unavailableCase('ac4-badref', 'https://github.com/demo-owner/demo-repo/blob/nope/docs/demo-chapter.md#sequence', 'ref not found', 'bad ref')
	await unavailableCase('ac4-badpath', 'https://github.com/demo-owner/demo-repo/blob/main/docs/nope.md', 'not found at main', 'bad path')
	// D1: no local checkout configured collapses "private" and "nonexistent" into one state — accepted per the entity, not re-tested here.
	await unavailableCase('ac4-unmapped', 'https://github.com/other-owner/other-repo/blob/main/docs/demo-chapter.md', 'no local checkout configured', 'unmapped repo (D1)')

	await openRoomAndLink(base, 'ac4-missing-heading', 'https://github.com/demo-owner/demo-repo/blob/main/docs/demo-chapter.md#no-such-heading')
	browser(['click', 'a.tl-hyperlink-button'])
	await waitFor(async () => browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body")?.textContent.includes("was not found")'), 8000, 'missing-heading banner')
	check('AC-4 missing heading: banner shown and chapter body still rendered', browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent.includes("Demo chapter")'))
	check('AC-4 missing heading: Open on GitHub present', hitTestable('dialog.doc-popup[open] a.doc-popup-source-link'))

	// --- D2: ref pinning via the review branch ---
	await openRoomAndLink(base, 'd2-review', 'https://github.com/demo-owner/demo-repo/blob/review/docs/demo-chapter.md#review-only-section')
	browser(['click', 'a.tl-hyperlink-button'])
	await waitFor(async () => browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body")?.textContent.includes("Review-only section")'), 8000, 'review branch content')
	check('D2: ref in the link (review branch) is what the popup shows, not main', browserEval('document.querySelector("dialog.doc-popup[open] .doc-popup-body").textContent.includes("Review-only section")'))

	// --- ref containing "/" (an implementation obligation, not an AC): progressive rev-parse over ref prefixes ---
	{
		const { stdout } = await run('curl', ['-sf', `http://127.0.0.1:${apiPort}/repo-doc?owner=demo-owner&repo=demo-repo&refPath=feature/foo/docs/feature-doc.md`])
		const slashRef = JSON.parse(stdout)
		check('ref containing "/" (HTTP layer, server obligation not an AC): feature/foo resolves via progressive rev-parse', slashRef.state === 'ok' && slashRef.content.includes('feature-foo content'), JSON.stringify(slashRef))
	}

	// --- shared-board-origin (AC-1's still-needed half) ---
	// This checks the shared-board origin at the HTTP layer only, via curl against
	// allowedHosts. A browser run over a non-localhost origin is achievable by
	// mapping the host at Chromium's DNS layer through agent-browser --args
	// --host-resolver-rules=MAP <host> 127.0.0.1; this script does not do that.
	try {
		const { stdout: okStatus } = await run('curl', ['-s', '-o', '/dev/null', '-w', '%{http_code}', '--resolve', `sharedorigin.test:${vitePort}:127.0.0.1`, `http://sharedorigin.test:${vitePort}/`])
		const { stdout: blockedStatus } = await run('curl', ['-s', '-o', '/dev/null', '-w', '%{http_code}', '--resolve', `notallowed.test:${vitePort}:127.0.0.1`, `http://notallowed.test:${vitePort}/`])
		check('shared-board-origin (HTTP layer only, not AC-1 proof): allowedHosts admits the configured host', okStatus === '200', `status=${okStatus}`)
		check('shared-board-origin (HTTP layer only, not AC-1 proof): allowedHosts still blocks an unlisted host', blockedStatus === '403', `status=${blockedStatus}`)
	} catch (e) {
		check('shared-board-origin HTTP-layer check ran', false, String(e))
	}
	console.log('LIMIT: shared-board-origin is checked at the HTTP layer only here; this script does not run the AC-1 browser check — see comment above.')

	// --- AC-5: export/import round trip, opened in a bare tldraw host with no viewer ---
	// Capture the export while the candidate's own Vite is still up, then stop it before
	// starting the bare pair: two Vite dev servers pointed at the same node_modules
	// (via the symlink below) thrash each other's dep-optimizer cache if both run at once.
	await openRoomAndLink(base, 'ac5-export', 'https://github.com/demo-owner/demo-repo/blob/main/docs/demo-chapter.md#sequence')
	const storeJson = browserEval('JSON.stringify(window.editor.store.getStoreSnapshot())')

	for (const p of procs.splice(0)) {
		try {
			process.kill(-p.pid)
		} catch {}
	}

	const bareDir = mkdtempSync(join(tmpdir(), 'popup-check-bare-'))
	cleanupDirs.push(bareDir)
	const pkgDir = basename(ROOT)
	// d701df3d: the last commit on main before this viewer landed.
	execFileSync('sh', ['-c', `git archive d701df3d -- ${pkgDir} | tar -x -C "${bareDir}"`], { cwd: REPO_ROOT })
	execFileSync('sh', ['-c', `mv "${bareDir}"/${pkgDir}/* "${bareDir}"/${pkgDir}/.[!.]* "${bareDir}"/ 2>/dev/null; rmdir "${bareDir}"/${pkgDir}`])
	execFileSync('ln', ['-s', join(ROOT, 'node_modules'), join(bareDir, 'node_modules')])

	const bareApiPort = await freePort(apiPort + 50)
	const bareVitePort = await freePort(vitePort + 50)
	const bareRunDir = mkdtempSync(join(tmpdir(), 'popup-check-bare-run-'))
	cleanupDirs.push(bareRunDir)
	const bareBase = await (async () => {
		// startCanvas hardcodes cwd: ROOT for the spawned processes; run it against the bare checkout instead.
		const env = {
			...process.env,
			JOURNEY_API_PORT: String(bareApiPort),
			JOURNEY_ROOMS_DIR: join(bareRunDir, 'rooms'),
			JOURNEY_ASSETS_DIR: join(bareRunDir, 'assets'),
			JOURNEY_SAVE_DIR: join(bareRunDir, 'save'),
		}
		const server = spawnLogged('npx', ['tsx', 'server/canvas-server.ts'], { cwd: bareDir, env })
		procs.push(server)
		await waitFor(async () => {
			try {
				await run('curl', ['-sf', `http://127.0.0.1:${bareApiPort}/health`])
				return true
			} catch {
				return false
			}
		}, 20000, `bare server on ${bareApiPort}`)
		const viteEnv = { ...env, JOURNEY_CANVAS_PORT: String(bareVitePort) }
		const vite = spawnLogged('npx', ['vite', 'dev', '--host'], { cwd: bareDir, env: viteEnv })
		procs.push(vite)
		await waitFor(async () => {
			try {
				await run('curl', ['-sf', `http://127.0.0.1:${bareVitePort}/`])
				return true
			} catch {
				return false
			}
		}, 20000, `bare vite on ${bareVitePort}`)
		return `http://localhost:${bareVitePort}`
	})()

	await run('curl', ['-sf', '-X', 'PUT', '-H', 'Content-Type: application/json', '--data-binary', JSON.stringify({ snapshot: JSON.parse(storeJson) }), `http://127.0.0.1:${bareApiPort}/doc?room=ac5`])

	browser(['open', `${bareBase}/?room=ac5`])
	await waitFor(async () => browserEval('!!window.editor'), 15000, 'bare host editor ready')
	const bareTabsBefore = JSON.parse(browser(['tab', 'list', '--json'])).data.tabs.length
	browser(['click', 'a.tl-hyperlink-button', '--new-tab'])
	await waitFor(async () => JSON.parse(browser(['tab', 'list', '--json'])).data.tabs.length === bareTabsBefore + 1, 5000, 'bare host opens a new tab')
	const bareTabs = JSON.parse(browser(['tab', 'list', '--json'])).data.tabs
	check('AC-5: exported/imported chapter link opens correctly in a viewer-less tldraw host', bareTabs.some((t) => t.url.includes('demo-owner/demo-repo/blob/main/docs/demo-chapter.md')))

	console.log('')
	console.log(failures.length === 0 ? `ALL CHECKS PASSED` : `${failures.length} CHECK(S) FAILED: ${failures.join('; ')}`)
	// The spawned servers' piped stdio keep the event loop alive even after cleanup()
	// kills the process groups, so exit explicitly rather than let Node hang here.
	process.exit(failures.length === 0 ? 0 : 1)
}

await main()
