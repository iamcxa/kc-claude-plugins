import { randomBytes } from 'node:crypto'
import { readFile, writeFile, rename } from 'node:fs/promises'
import { digest, validateGrants } from '../server/host/policy'
const [file, credentialId, principalId, roomList, expiry, tokenFile] = process.argv.slice(2)
if (!tokenFile) throw new Error('usage: journey-grant.ts <grants.json> <new-id> <principal> <rooms-comma> <ISO-expiry> <new-token-file>')
const old = await readFile(file, 'utf8').then(JSON.parse).catch((e: any) => { if (e.code === 'ENOENT') return []; throw e })
if (old.some((g: any) => g.credentialId === credentialId)) throw new Error('use a new credential ID for rotation')
const secret = randomBytes(32).toString('base64url')
const grant = { credentialId, principalId, rooms: roomList.split(','), expiresAt: Date.parse(expiry), revoked: false, secretDigest: await digest(secret) }
if (grant.expiresAt <= Date.now()) throw new Error('expiry must be in the future')
const grants = validateGrants([...old, grant])
await writeFile(tokenFile, credentialId + '.' + secret, { flag: 'wx', mode: 0o600 })
const temporary = file + '.' + crypto.randomUUID()
await writeFile(temporary, JSON.stringify(grants, null, 2) + '\n', { flag: 'wx', mode: 0o600 })
await rename(temporary, file)
console.log('Created grant ' + credentialId + '; credential saved in the requested token file.')
