import assert from 'node:assert/strict'
import { mkdtempSync, readdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { test } from 'node:test'
import ts from 'typescript'
import { tsImport } from 'tsx/esm/api'
import { loadConfigFromFile } from 'vite'

const root = resolve(process.env.JOURNEY_PROXY_CHECK_ROOT || new URL('..', import.meta.url).pathname)
const { clientApiProxy, shareClientMode } = await tsImport(join(root, 'server/client-api-proxy.ts'), import.meta.url)
const filesIn = dir => readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? filesIn(join(dir, entry.name)) : /\.[cm]?[jt]sx?$/.test(entry.name) ? [join(dir, entry.name)] : [])
const key = (method, path) => method + ' ' + path.split(/[?#]/)[0]
const core = ['WS /connect/', 'GET /uploads/', 'PUT /uploads/', 'GET /doc']
const human = ['GET /auth/config', 'GET /auth/entry', 'GET /auth/rooms', 'POST /auth/renew', 'POST /auth/logout']
const local = ['POST /auth/local/start', 'POST /auth/local/consume']
const provider = ['POST /auth/provider/start', 'GET /auth/login']
const pairing = ['inspect', 'approve', 'deny', 'list', 'revoke'].map(operation => 'POST /agents/' + operation)
const optional = ['GET /save', 'POST /save', 'GET /repo-doc']
const all = [...core, 'GET /health', ...human, ...local, ...provider, 'GET /auth/account', ...pairing, ...optional].sort()

function networkLint(source) {
 const visit = node => {
  if (ts.isElementAccessExpression(node) && ['window', 'self', 'globalThis', 'navigator'].includes(node.expression.getText(source))) assert.fail('computed browser network access is forbidden')
  if (ts.isIdentifier(node) || ts.isStringLiteralLike(node)) {
   const name = node.text
   if (['fetch', 'journeyFetch', 'XMLHttpRequest', 'WebSocket', 'EventSource', 'sendBeacon'].includes(name)) {
    const parent = node.parent
    const allowed = ts.isIdentifier(node) && (
     (ts.isCallExpression(parent) && parent.expression === node && ['fetch', 'journeyFetch'].includes(name)) ||
     (ts.isImportSpecifier(parent) && !parent.propertyName) || ts.isTypeQueryNode(parent) ||
     (ts.isVariableDeclaration(parent) && parent.name === node && name === 'journeyFetch')
    )
    assert.ok(allowed, 'unsupported browser network spelling: ' + node.getText(source))
   }
  }
  ts.forEachChild(node, visit)
 }
 visit(source)
}

function clientOperations(files) {
 const program = ts.createProgram(files, { allowJs: true, jsx: ts.JsxEmit.ReactJSX, moduleResolution: ts.ModuleResolutionKind.Bundler, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 })
 const checker = program.getTypeChecker(), calls = [], sources = files.map(file => program.getSourceFile(file))
 const visit = node => { if (ts.isCallExpression(node)) calls.push(node); ts.forEachChild(node, visit) }
 for (const source of sources) { networkLint(source); visit(source) }
 const declaration = node => {
  let symbol = ts.isShorthandPropertyAssignment(node.parent) ? checker.getShorthandAssignmentValueSymbol(node.parent) : checker.getSymbolAtLocation(node)
  if (symbol?.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol)
  const value = symbol?.valueDeclaration
  return value && ts.isVariableDeclaration(value) ? value.initializer : value
 }
 const values = (node, bindings = new Map(), seen = new Set()) => {
  assert.ok(node && !seen.has(node), 'unresolved browser API argument')
  const next = new Set([...seen, node])
  if (ts.isStringLiteralLike(node)) return [node.text]
  if (ts.isTemplateExpression(node) && node.head.text) return [node.head.text]
  if (ts.isParenthesizedExpression(node)) return values(node.expression, bindings, next)
  if (ts.isConditionalExpression(node)) return [...values(node.whenTrue, bindings, next), ...values(node.whenFalse, bindings, next)]
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
   const left = values(node.left, bindings, next)
   return left.every(part => part.endsWith('/')) && ts.isIdentifier(node.right) && ts.isParameter(declaration(node.right) || {}) ? left.flatMap(part => values(node.right, bindings, next).map(suffix => part + suffix)) : left
  }
  if (ts.isCallExpression(node) && node.expression.getText() === 'journeyApi') return values(node.arguments[0], bindings, next)
  if (ts.isIdentifier(node)) {
   const parameter = declaration(node)
   if (bindings.has(parameter)) return values(bindings.get(parameter), bindings, next)
   if (parameter && ts.isParameter(parameter)) {
    const fn = parameter.parent, index = fn.parameters.indexOf(parameter)
    const callers = calls.filter(call => declaration(call.expression) === fn)
    assert.ok(callers.length, 'no callers for ' + node.getText())
    return callers.flatMap(call => values(call.arguments[index], bindings, next))
   }
  }
  assert.fail('unresolved browser API argument: ' + node.getText())
 }
 const requests = []
 for (const call of calls.filter(call => ['fetch', 'journeyFetch'].includes(call.expression.getText()))) {
  if (call.getSourceFile().fileName === join(root, 'server/client/api.ts')) {
   assert.equal(call.expression.getText(), 'fetch')
   assert.equal(call.arguments[0].getText(), 'input')
   assert.equal(call.parent.parent.name?.getText(), 'journeyFetch')
   continue
  }
  let fn = call.parent
  while (fn && !ts.isFunctionLike(fn)) fn = fn.parent
  const callers = fn && calls.filter(item => declaration(item.expression) === fn)
  const contexts = callers?.length ? callers.map(item => new Map(fn.parameters.map((parameter, i) => [parameter, item.arguments[i]]))) : [new Map()]
  for (const bindings of contexts) {
   const init = call.arguments[1]
   assert.ok(!init || ts.isObjectLiteralExpression(init), 'request options must be an object literal')
   assert.ok(!init?.properties.some(ts.isSpreadAssignment), 'request option spreads need explicit contract support')
   const method = init?.properties.find(prop => prop.name?.getText() === 'method')
   const methods = method ? values(method.initializer || method.name, bindings) : ['GET']
   for (const path of values(call.arguments[0], bindings)) for (const method of methods) requests.push(key(method, path))
  }
 }
 const sdk = calls.filter(call => call.expression.getText() === 'journeyApi').flatMap(call => values(call.arguments[0]))
 assert.ok(sdk.includes('/connect/') && sdk.includes('/uploads/'), 'SDK socket and image resolver contracts')
 const requestPaths = [...requests, ...core].map(operation => operation.split(' ')[1])
 for (const path of sdk) assert.ok(requestPaths.includes(path.split(/[?#]/)[0]), 'uncontracted browser URL: ' + path)
 return [...new Set([...requests, 'WS /connect/', 'GET /uploads/'])].sort()
}

const paths = clientOperations(filesIn(join(root, 'server/client')))
const temp = mkdtempSync(join(tmpdir(), 'share-contract-'))
const origin = 'http://127.0.0.1:3737'
const envFor = mode => {
 const env = mode === 'legacy' ? {} : { JOURNEY_PRIVATE_DIR: '/synthetic/private', JOURNEY_ORIGIN: origin }
 if (['local', 'cloudflare'].includes(mode)) {
  const issuer = mode === 'local' ? 'local:test' : 'https://synthetic.cloudflareaccess.com'
  const file = join(temp, mode + '.json')
  writeFileSync(file, JSON.stringify({ version: 1, backendId: 'synthetic', origin, mode, issuer, audience: 'synthetic', localOwnerUid: process.geteuid(), localMemberId: 'owner', members: [{ id: 'owner', issuer, subject: 'uid:' + process.geteuid(), label: 'Synthetic', role: 'operator', rooms: [] }] }))
  env.JOURNEY_HUMAN_CONFIG = file
 }
 return env
}
const allows = (proxy, operation) => {
 const [method, prefix] = operation.split(' '), path = prefix.endsWith('/') ? prefix + (method === 'WS' ? 'fixture' : 'fixture.png') : prefix
 return Object.entries(proxy).some(([route, options]) => {
  if (!(route.startsWith('^') ? new RegExp(route).test(path) : path.startsWith(route))) return false
  return options.bypass({ method: method === 'WS' ? 'GET' : method, url: path + '?room=A', headers: method === 'WS' ? { upgrade: 'websocket' } : {} }) !== false
 })
}

test('browser operations have an explicit method contract, including returned provider navigation', () => {
 assert.deepEqual([...paths, 'GET /auth/login'].sort(), all)
 const server = readFileSync(join(root, 'server/host/human.ts'), 'utf8')
 assert.match(server, /loginUrl: '\/auth\/login\?state='/)
 assert.match(readFileSync(join(root, 'server/client/HumanEntry.tsx'), 'utf8'), /location.href=result.loginUrl/)
})

test('each active mode forwards exactly its required client operations and denies optional probes', () => {
 for (const mode of ['legacy', 'credentials', 'local', 'cloudflare']) for (const nativeAccount of [false, true]) for (const agents of [false, true]) for (const capabilities of [false, true]) {
  const env = { ...envFor(mode), JOURNEY_NATIVE_ACCOUNT: String(nativeAccount), JOURNEY_AGENT_PAIRING: String(agents), JOURNEY_SHARE_SAVE: String(capabilities), JOURNEY_SHARE_REPO_DOC: String(capabilities), JOURNEY_SAVE_DIR: '/synthetic/save', JOURNEY_DOC_REPOS: 'synthetic/repo=/synthetic/repo', JOURNEY_ROOM_REPOS: '{"A":["synthetic/repo"]}' }
  const verified = ['local', 'cloudflare'].includes(mode)
  const expected = [...core, ...verified ? [...human, ...mode === 'local' ? local : provider, ...nativeAccount ? ['GET /auth/account'] : [], ...agents ? pairing : []] : ['GET /health'], ...capabilities && mode !== 'legacy' ? optional : []].sort()
  const proxy = clientApiProxy('http://127.0.0.1:5858', 'share', env)
  const actual = all.filter(operation => allows(proxy, operation))
  assert.deepEqual(actual, expected, JSON.stringify({mode,nativeAccount,agents,capabilities}))
  assert.equal(Object.keys(proxy).length, new Set(expected.map(operation => operation.split(' ')[1])).size, 'unused route')
  for (const path of new Set(all.map(operation => operation.split(' ')[1]))) for (const method of ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']) {
   assert.equal(allows(proxy, method + ' ' + path), expected.includes(method + ' ' + path), method + ' ' + path)
  }
 }
})

test('explicit capabilities also require private backend authorization and configured scope', () => {
 for (const env of [{}, { JOURNEY_PRIVATE_DIR: '/synthetic' }, { JOURNEY_SAVE_DIR: '/saved', JOURNEY_DOC_REPOS: 'a/b=/repo', JOURNEY_ROOM_REPOS: '{"A":["a/b"]}' }]) {
  const proxy = clientApiProxy('http://127.0.0.1:5858', 'share', { ...env, JOURNEY_SHARE_SAVE: 'true', JOURNEY_SHARE_REPO_DOC: 'true' })
  for (const operation of optional) assert.equal(allows(proxy, operation), false)
 }
 assert.throws(() => shareClientMode({ JOURNEY_HUMAN_CONFIG: '/absent' }), /private storage/)
 assert.equal(shareClientMode({ VITE_JOURNEY_HUMAN_ENTRY: 'true', JOURNEY_NATIVE_ACCOUNT: 'true', JOURNEY_AGENT_PAIRING: 'true' }).human, undefined)
})

test('unknown routes, methods, endpoint suffixes and normalized traversal stay closed', () => {
 const proxy = clientApiProxy('http://127.0.0.1:5858', 'share', { ...envFor('local'), JOURNEY_AGENT_PAIRING: 'true' })
 for (const path of ['/grants', '/session', '/capabilities', '/mcp', '/doc/other', '/health-extra', '/auth/unknown', '/auth/config/extra', '/agents/start', '/agents/redeem', '/agents/rotate', '/agents/repair']) for (const method of ['GET', 'POST']) assert.equal(allows(proxy, method + ' ' + path), false, path)
 for (const [route, options] of Object.entries(proxy)) for (const url of ['/uploads/../save', '/uploads/%2e%2e/doc', '/connect/%2e%2e/doc', '/uploads/%2f..%2fsave', '/uploads/%ZZ']) {
  if (new RegExp(route).test(url)) assert.equal(options.bypass({ method: 'GET', url }), false, url)
 }
})

test('request spelling lint rejects window/global fetch, aliases, alternate transports and unknown methods', () => {
 for (const text of ["window.fetch('/unlisted')", "window['fetch']('/unlisted')", "globalThis.fetch('/unlisted')", "self.fetch('/unlisted')", "const f = fetch; f('/unlisted')", "const {fetch:f} = window; f('/unlisted')", "fetch.call(null, '/unlisted')", "new XMLHttpRequest()", "navigator.sendBeacon('/unlisted')", "window['fe'+'tch']('/unlisted')", "import {journeyFetch as f} from './api'; f('/unlisted')"]) {
  assert.throws(() => networkLint(ts.createSourceFile('mutation.ts', text, ts.ScriptTarget.Latest, true)), /network|spelling/)
 }
 const file = join(temp, 'mutation.ts')
 for (const text of ["fetch('/unlisted')", "fetch('/health',{method:'DELETE'})", "window.fetch('/unlisted')"]) {
  writeFileSync(file, text)
  assert.throws(() => assert.deepEqual(clientOperations([...filesIn(join(root, 'server/client')), file]), paths))
 }
})

test('real share config derives its browser entry and policy from backend configuration', async () => {
 const names = ['JOURNEY_PRIVATE_DIR', 'JOURNEY_HUMAN_CONFIG', 'JOURNEY_ORIGIN', 'JOURNEY_NATIVE_ACCOUNT', 'JOURNEY_AGENT_PAIRING', 'JOURNEY_SHARE_SAVE', 'JOURNEY_SHARE_REPO_DOC', 'VITE_JOURNEY_HUMAN_ENTRY']
 const saved = Object.fromEntries(names.map(name => [name, process.env[name]]))
 try {
  for (const mode of ['legacy', 'local', 'cloudflare']) {
   for (const name of names) delete process.env[name]
   Object.assign(process.env, envFor(mode), { VITE_JOURNEY_HUMAN_ENTRY: 'true' })
   const loaded = await loadConfigFromFile({ command: 'serve', mode: 'development' }, join(root, 'vite.share.config.mts'))
   assert.equal(loaded.config.define['import.meta.env.VITE_JOURNEY_HUMAN_ENTRY'], JSON.stringify(mode !== 'legacy' ? 'true' : 'false'))
   assert.deepEqual(Object.keys(loaded.config.server.proxy), Object.keys(clientApiProxy('unused', 'share', process.env)))
  }
 } finally {
  for (const name of names) if (saved[name] === undefined) delete process.env[name]; else process.env[name] = saved[name]
  rmSync(temp, { recursive: true, force: true })
 }
})
