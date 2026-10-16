type Query = (sql: string, ...bindings: Array<string | number>) => Array<Record<string, unknown>>
const cursorKey = 'maintenance:session-gc'
const prefix = 'session:'
const end = 'session;'
const batchSize = 64

export function pruneExpiredSessions(query: Query, now = Date.now()) {
 let after = prefix
 const stored = query('SELECT value FROM metadata WHERE key = ?', cursorKey)[0]?.value
 try {
  const cursor = typeof stored === 'string' ? JSON.parse(stored) : null
  if (typeof cursor === 'string' && cursor.startsWith(prefix) && cursor < end) after = cursor
 } catch {}
 const rows = query('SELECT key, value FROM metadata WHERE key >= ? AND key < ? AND key > ? ORDER BY key LIMIT 64', prefix, end, after)
 const expired: string[] = []
 for (const row of rows) {
  if (typeof row.key !== 'string' || typeof row.value !== 'string') continue
  try {
   const session = JSON.parse(row.value)
   if (typeof session?.credentialId === 'string' && /^[a-zA-Z0-9_-]+$/.test(session.credentialId) &&
    typeof session.expiresAt === 'number' && Number.isFinite(session.expiresAt) && session.expiresAt <= now) expired.push(row.key)
  } catch {}
 }
 if (expired.length) query('DELETE FROM metadata WHERE key IN (' + expired.map(() => '?').join(',') + ')', ...expired)
 query('INSERT OR REPLACE INTO metadata VALUES (?, ?)', cursorKey, JSON.stringify(rows.length === batchSize ? rows[rows.length - 1].key : prefix))
}
