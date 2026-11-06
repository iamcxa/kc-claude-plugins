import assert from 'node:assert/strict'
import { readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { test } from 'node:test'
import ts from 'typescript'
import { loadConfigFromFile } from 'vite'

const root = resolve(process.env.JOURNEY_PROXY_CHECK_ROOT || new URL('..', import.meta.url).pathname)
const filesIn = dir => readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? filesIn(join(dir, entry.name)) : /\.tsx?$/.test(entry.name) ? [join(dir, entry.name)] : [])

function clientPaths(files) {
 const program = ts.createProgram(files, { jsx: ts.JsxEmit.ReactJSX, moduleResolution: ts.ModuleResolutionKind.Bundler, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 })
 const checker = program.getTypeChecker(), calls = []
 const visit = node => { if (ts.isCallExpression(node)) calls.push(node); ts.forEachChild(node, visit) }
 for (const file of files) visit(program.getSourceFile(file))
 const declaration = call => {
  let symbol = checker.getSymbolAtLocation(call.expression)
  if (symbol?.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol)
  const value = symbol?.valueDeclaration
  return value && ts.isVariableDeclaration(value) ? value.initializer : value
 }
 const prefixes = (node, seen = new Set()) => {
  assert.ok(node && !seen.has(node), 'unresolved or recursive browser API argument')
  const next = new Set([...seen, node])
  if (ts.isStringLiteralLike(node)) return [node.text]
  if (ts.isTemplateExpression(node) && node.head.text) return [node.head.text]
  if (ts.isParenthesizedExpression(node)) return prefixes(node.expression, next)
  if (ts.isConditionalExpression(node)) return [...prefixes(node.whenTrue, next), ...prefixes(node.whenFalse, next)]
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
   const left = prefixes(node.left, next)
   const right = ts.isIdentifier(node.right) && checker.getSymbolAtLocation(node.right)?.valueDeclaration
   if (left.every(part => part.endsWith('/')) && right && ts.isParameter(right)) {
    return left.flatMap(part => prefixes(node.right, next).map(suffix => part + suffix))
   }
   return left
  }
  if (ts.isCallExpression(node) && node.expression.getText() === 'journeyApi') return prefixes(node.arguments[0], next)
  if (ts.isIdentifier(node)) {
   const parameter = checker.getSymbolAtLocation(node)?.valueDeclaration
   if (parameter && ts.isParameter(parameter)) {
    const fn = parameter.parent, index = fn.parameters.indexOf(parameter)
    const callers = calls.filter(call => declaration(call) === fn)
    assert.ok(callers.length, 'no callers found for ' + node.getText())
    return callers.flatMap(call => prefixes(call.arguments[index], next))
   }
  }
  assert.fail('unresolved browser API argument: ' + node.getText())
 }
 return [...new Set(calls.filter(call => ['journeyApi', 'fetch'].includes(call.expression.getText())).flatMap(call => prefixes(call.arguments[0])).map(path => {
  assert.ok(path.startsWith('/'), 'expected same-origin API path: ' + path)
  return path.split(/[?#]/)[0]
 }))].sort()
}

const paths = clientPaths(filesIn(join(root, 'server/client')))
const loaded = await loadConfigFromFile({ command: 'serve', mode: 'development' }, join(root, 'vite.share.config.mts'))
assert.ok(loaded)
const proxy = loaded.config.server.proxy
const matches = (key, path) => key.startsWith('^') ? new RegExp(key).test(path) : path.startsWith(key)

test('share entrance covers every static journeyApi/fetch path, including helper arguments', () => {
 const missing = paths.filter(path => !Object.keys(proxy).some(key => matches(key, path)))
 assert.deepEqual(missing, [], 'client API paths missing from share entrance')
})

test('each share proxy entry is used by the browser client', () => {
 const unused = Object.keys(proxy).filter(key => !paths.some(path => matches(key, path)))
 assert.deepEqual(unused, [], 'unused share API prefixes')
})

test('share entrance keeps operator routes and document writes closed', () => {
 for (const path of ['/grants', '/session', '/capabilities', '/mcp', '/doc/other', '/health-extra', '/agents/start', '/agents/redeem', '/agents/rotate', '/agents/repair']) {
  assert.equal(Object.keys(proxy).some(key => matches(key, path)), false, path)
 }
 const doc = Object.entries(proxy).find(([key]) => matches(key, '/doc?room=A'))?.[1]
 if (!doc) return
 assert.ok(typeof doc !== 'string' && doc.bypass)
 for (const method of ['POST', 'PATCH', 'PUT', 'DELETE']) assert.equal(doc.bypass({ method, url: '/doc?room=A' }, undefined, doc), false)
 assert.equal(doc.bypass({ method: 'GET', url: '/doc?room=A' }, undefined, doc), undefined)
})

test('normalized requests cannot escape a shared API prefix', () => {
 for (const [prefix, url] of [['/uploads/', '/uploads/../capabilities'], ['/uploads/', '/uploads/%2E%2E/doc?room=A'], ['/auth/', '/auth/../mcp'], ['/connect/', '/connect/%2e%2e/doc?room=A']]) {
  const options = proxy[prefix]
  if (!options) continue
  assert.ok(options.bypass, prefix)
  assert.equal(options.bypass({ method: 'PATCH', url }, undefined, options), false, url)
 }
})
