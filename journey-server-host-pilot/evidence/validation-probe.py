#!/usr/bin/env python3
"""Reuse the candidate's disposable host runner, replacing only the test body.
No candidate source is edited. Outputs and generated code stay in ignored scratch.
"""
import os, pathlib, signal, subprocess, sys
wt = pathlib.Path(sys.argv[1]).resolve()
adapter = sys.argv[2]
expected = "4f678cd88eddbcc171df7e2037dd19d2fbf4065b"
assert adapter in ("node", "cloudflare-local")
assert subprocess.check_output(["git", "-C", str(wt), "rev-parse", "HEAD"], text=True).strip() == expected
root = wt / "kc-journey-map"
original = (root / "scripts/host-contract-check.mjs").read_text()
prefix = original.split("const baselineDir =")[0]
prefix = prefix.replace("from './cloudflare-local.mjs'", "from '../scripts/cloudflare-local.mjs'")
prefix = prefix.replace("from './journey-browser.mjs'", "from '../scripts/journey-browser.mjs'")
body = r"""
const { getTlsyncProtocolVersion } = await import('@tldraw/sync-core')
const delay = ms => new Promise(resolve => setTimeout(resolve, ms))
const until = async (predicate, ms = 2500) => {
 const deadline = Date.now() + ms
 while (!predicate()) { if (Date.now() >= deadline) throw new Error('observation timeout'); await delay(20) }
}
const sessionCookie = async id => {
 const response = await request('/session', { id, method: 'POST', headers: { Origin: origin } })
 assert.equal(response.status, 200)
 assert.match(response.headers.get('set-cookie'), /HttpOnly; Secure; SameSite=Strict/)
 return response.headers.get('set-cookie').split(';')[0]
}
const connected = async (cookie, snapshot) => {
 const ws = await openSocket('shared', 'a', { Authorization: '', Cookie: cookie })
 const frames = []
 ws.on('message', data => frames.push(String(data)))
 ws.on('error', () => {})
 ws.send(JSON.stringify({ type: 'connect', connectRequestId: crypto.randomUUID(), lastServerClock: -1,
  protocolVersion: getTlsyncProtocolVersion(), schema: snapshot.schema }))
 await until(() => frames.some(frame => frame.includes('"type":"connect"')))
 return { ws, frames }
}
const rejectedWrite = async (path, cookie, method = 'PATCH', body = {}) => {
 assert.equal((await request(path, { id: null, method, body, headers: { Cookie: cookie, Origin: origin } })).status, 401)
}
try {
 await start()
 let snapshot, page, cookieB
 await check('room isolation: cookie MCP/assets deny B reading or replacing A; same-ID bytes remain separate', async () => {
  for (const [room, id] of [['a', 'a'], ['b', 'b'], ['shared', 'a']]) await data('/doc?room=' + room, { id })
  snapshot = (await data('/doc?room=shared')).snapshot
  page = records(snapshot).find(record => record.typeName === 'page')
  assert.ok(page)
  for (const [room, id, value] of [['a', 'a', 'A-only'], ['b', 'b', 'B-only'], ['shared', 'a', 'first'], ['shared', 'b', 'latest']]) {
   assert.equal((await request('/uploads/collision?room=' + room, { id, method: 'PUT', body: value })).status, 200)
  }
  cookieB = await sessionCookie('b')
  const headers = { Cookie: cookieB, Origin: origin }
  assert.equal((await request('/doc?room=a', { id: null, headers })).status, 403)
  assert.equal((await request('/mcp', { id: null, method: 'POST', headers, body: {
   jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'patch_doc', arguments: { room: 'a', body: { remove: ['page:page'] } } }
  } })).status, 403)
  assert.equal((await request('/uploads/collision?room=a', { id: null, headers })).status, 403)
  assert.equal((await request('/uploads/collision?room=a', { id: null, method: 'PUT', headers, body: 'forged' })).status, 403)
  assert.equal(await (await request('/uploads/collision?room=a')).text(), '"A-only"')
  assert.equal(await (await request('/uploads/collision?room=b', { id: 'b' })).text(), '"B-only"')
  const health = await data('/health')
  assert.deepEqual(health.rooms.sort(), ['a', 'shared'])
  assert.deepEqual(health.active.map(r => r.roomId).sort(), ['a', 'shared'])
  report.telemetry = adapter === 'cloudflare-local' ? 'authorized registered rooms sampled; may wake rooms' : 'authorized resident rooms'
 })
 await check('recovery: export includes latest associated bytes; populated/invalid restore refused; fresh restore survives restart', async () => {
  const archive = await host.export('shared')
  assert.equal(archive.assets.length, 1)
  assert.equal(Buffer.from(archive.assets[0].bytes).toString(), '"latest"')
  await assert.rejects(host.restore(archive))
  const before = stableRecords((await data('/doc?room=shared')).snapshot)
  assert.equal(before, stableRecords(archive.document.snapshot))
  await host.close(); await start(join(scratch, 'restored'))
  await assert.rejects(host.restore({ ...archive, assets: [archive.assets[0], archive.assets[0]] }))
  assert.deepEqual((await data('/health')).rooms, [])
  assert.equal((await host.restore(archive)).assets, 1)
  await host.close(); await start(join(scratch, 'restored'))
  assert.equal(stableRecords((await data('/doc?room=shared')).snapshot), before)
  assert.equal(await (await request('/uploads/collision?room=shared')).text(), '"latest"')
  if (adapter === 'node') {
   report.restoreExplicitRefusals = logs.filter(line => line.includes('"controlError":"operator command failed"')).length
   assert.equal(report.restoreExplicitRefusals, 2, 'each refused restore must emit an explicit operator failure')
  }
  await host.close(); await start()
 })
 await check('revocation: a live cookie socket receives authorized edits, then loses read/write across all transports before close event', async () => {
  const { ws, frames } = await connected(cookieB, snapshot)
  const idle = await openSocket('shared', 'b', { Authorization: '', Cookie: cookieB })
  const idleFrames = []
  idle.on('message', data => idleFrames.push(String(data)))
  idle.on('error', () => {})
  await data('/doc?room=shared', { method: 'PATCH', body: { put: [{ ...page, name: 'before-revoke' }] } })
  await until(() => frames.some(frame => frame.includes('before-revoke')))
  const began = Date.now()
  let clientClosedAt, idleClosedAt
  const closed = new Promise(resolve => ws.once('close', code => { clientClosedAt = Date.now(); resolve(code) }))
  const idleClosed = new Promise(resolve => idle.once('close', code => { idleClosedAt = Date.now(); resolve(code) }))
  const result = await host.revoke('b')
  report.revocation = { operator: result, serverAcknowledgedMs: Date.now() - began, clientStateAtAck: ws.readyState, idleClientStateAtAck: idle.readyState }
  assert.equal(result.revoked, true)
  if (adapter === 'cloudflare-local') assert.equal(result.complete, true)
  const countAtAck = frames.length
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'push', clientClock: 1, diff: { [page.id]: ['put', { ...page, name: 'forged-after-revoke' }] } }), () => {})
  if (idle.readyState === WebSocket.OPEN) idle.send(JSON.stringify({ type: 'connect', connectRequestId: crypto.randomUUID(), lastServerClock: -1, protocolVersion: getTlsyncProtocolVersion(), schema: snapshot.schema }), () => {})
  await rejectedWrite('/doc?room=shared', cookieB)
  await rejectedWrite('/mcp', cookieB, 'POST', { jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'get_doc', arguments: { room: 'shared' } } })
  assert.equal((await request('/uploads/collision?room=shared', { id: null, headers: { Cookie: cookieB } })).status, 401)
  assert.equal((await openSocket('shared', 'b', { Authorization: '', Cookie: cookieB })).status, 401)
  await data('/doc?room=shared', { method: 'PATCH', body: { put: [{ ...page, name: 'after-revoke-private' }] } })
  await delay(250)
  assert.ok(!frames.slice(countAtAck).some(frame => frame.includes('after-revoke-private')))
  assert.ok(!idleFrames.some(frame => frame.includes('after-revoke-private')))
  assert.equal(records((await data('/doc?room=shared')).snapshot).find(r => r.id === page.id).name, 'after-revoke-private')
  let closeTimer
  assert.equal(await Promise.race([closed, new Promise((_, reject) => { closeTimer = setTimeout(() => reject(new Error('actual close event missing')), 35000) })]).finally(() => clearTimeout(closeTimer)), 1008)
  assert.equal(await Promise.race([idleClosed, new Promise((_, reject) => { closeTimer = setTimeout(() => reject(new Error('idle close event missing')), 35000) })]).finally(() => clearTimeout(closeTimer)), 1008)
  report.revocation.clientClosedMs = clientClosedAt - began
  report.revocation.idleClientClosedMs = idleClosedAt - began
  await host.close(); await start()
  assert.equal((await request('/doc?room=shared', { id: 'b' })).status, 401)
  assert.equal((await request('/doc?room=shared', { id: null, headers: { Cookie: cookieB } })).status, 401)
 })
 await check('expiry: parent deadline denies existing cookie HTTP/MCP/assets/socket admission and no live data reaches the expired socket', async () => {
  grants.find(g => g.credentialId === 'short').expiresAt = Date.now() + 4000
  await writeFile(grantFile, JSON.stringify(grants), { mode: 0o600 })
  await host.close(); await start(join(scratch, 'expiry'))
  snapshot = (await data('/doc?room=shared')).snapshot
  page = records(snapshot).find(record => record.typeName === 'page')
  const cookie = await sessionCookie('short')
  const { ws, frames } = await connected(cookie, snapshot)
  let closedAt
  const closed = new Promise(resolve => ws.once('close', code => { closedAt = Date.now(); resolve(code) }))
  const expiry = grants.find(g => g.credentialId === 'short').expiresAt
  await delay(Math.max(0, expiry - Date.now()) + 150)
  const frameCount = frames.length
  await rejectedWrite('/doc?room=shared', cookie)
  await rejectedWrite('/mcp', cookie, 'POST', { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'get_doc', arguments: { room: 'shared' } } })
  assert.equal((await request('/uploads/collision?room=shared', { id: null, headers: { Cookie: cookie } })).status, 401)
  assert.equal((await openSocket('shared', 'short', { Authorization: '', Cookie: cookie })).status, 401)
  await data('/doc?room=shared', { method: 'PATCH', body: { put: [{ ...page, name: 'after-expiry-private' }] } })
  await delay(250)
  assert.ok(!frames.slice(frameCount).some(frame => frame.includes('after-expiry-private')))
  let closeTimer
  assert.equal(await Promise.race([closed, new Promise((_, reject) => { closeTimer = setTimeout(() => reject(new Error('expiry close event missing')), 35000) })]).finally(() => clearTimeout(closeTimer)), 1008)
  report.expiryClientCloseAfterDeadlineMs = closedAt - expiry
 })
 report.status = 'PASS'
 console.log('LOCAL ONLY: hosted deployment, provider hibernation, billing and licensing NOT RUN')
} catch (e) {
 report.status = 'FAIL'; report.failure = e.stack; report.logs = logs.slice(-15)
 console.error(e.stack); process.exitCode = 1
} finally {
 await host?.close()
 report.evidenceDirectory = scratch
 await writeFile(join(scratch, 'validation-result.json'), JSON.stringify(report, null, 2))
 console.log('Evidence: ' + join(scratch, 'validation-result.json'))
}
"""
target = root / ".host-check" / "validation-transport-probe.mjs"
target.parent.mkdir(exist_ok=True)
target.write_text(prefix + body)
subprocess.run(["node", "--check", str(target)], check=True, cwd=root)
process = subprocess.Popen(["node", str(target), "--adapter", adapter, "--synthetic"], cwd=root, start_new_session=True)
try:
    sys.exit(process.wait(timeout=110))
except subprocess.TimeoutExpired:
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    raise SystemExit("validation timeout: owned process group stopped")
