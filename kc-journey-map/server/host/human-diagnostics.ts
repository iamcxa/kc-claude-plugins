// Exception text can contain credentials or identity data. Emit fixed diagnostic
// phrases, not arbitrary substrings, names, stacks, inputs or request metadata.
const operations = new Set(['record-denial', 'challenge-create', 'challenge-inspect', 'challenge-approve', 'challenge-consume', 'provider-start', 'provider-consume', 'disable-member', 'set-room', 'renew', 'logout', 'account-read'])
const names = new Set(['Error', 'TypeError', 'RangeError', 'SyntaxError', 'DOMException', 'HostError'])
const diagnostics = [
 'SQLITE_FULL', 'SQLITE_TOOBIG', 'SQLITE_BUSY', 'SQLITE_LOCKED', 'SQLITE_IOERR', 'SQLITE_AUTH', 'SQLITE_ERROR', 'SQLITE_CONSTRAINT',
 'database or disk is full', 'string or blob too big', 'too many SQL variables', 'database is locked', 'not authorized',
 'no such table', 'no such column', 'syntax error', 'constraint failed', 'storage limit', 'exceeded',
 'transactionSync', 'transaction', 'storage.transaction', 'metadata unavailable', 'registry unavailable',
 'host operation failed', 'human_entry_unconfigured', 'provider_unavailable',
]
export function logHumanError(boundary: 'denial-receipt' | 'registry' | 'provider-start', operation: unknown, error: unknown) {
 try {
  const name = error instanceof Error && names.has(error.name) ? error.name : 'UnknownError'
  const raw = error instanceof Error ? error.message : ''
  const message = diagnostics.filter(phrase => raw.includes(phrase)).join('; ') || '[redacted]'
  console.error(JSON.stringify({ event: 'journey-human-operation-error', boundary, operation: typeof operation === 'string' && operations.has(operation) ? operation : 'unknown', name, message }))
 } catch { /* A diagnostic sink failure must not replace the HTTP error. */ }
}
