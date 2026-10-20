import assert from 'node:assert/strict'
import { test } from 'node:test'
import { recoveryCause, recoveryResponse } from '../server/client/access-recovery'

test('read failures preserve expiry and denial, distinguish outage, and refuse untyped protocol success', async () => {
 for (const category of ['session_expired','human_revalidation_due']) {
  await assert.rejects(recoveryResponse(Response.json({category},{status:401})),error=>recoveryCause(error).kind==='expired')
 }
 for (const category of ['room_denied','room_missing','draft_identity_changed','room_context_changed']) {
  assert.equal(recoveryCause(new Error(category)).kind,'denied')
 }
 await assert.rejects(recoveryResponse(Response.json({category:'room_denied'},{status:403})),error=>recoveryCause(error).category==='room_denied')
 await assert.rejects(recoveryResponse(Response.json({error:'host operation failed'},{status:503})),error=>recoveryCause(error).kind==='unavailable')
 await assert.rejects(recoveryResponse(new Response('<html>login</html>')),error=>recoveryCause(error).kind==='unknown')
 await assert.rejects(recoveryResponse(Response.json({category:'invented_cause'},{status:400})),error=>recoveryCause(error).kind==='unknown')
 assert.equal(recoveryCause(new TypeError('Failed to fetch')).kind,'unavailable')
 assert.equal(recoveryCause(new Error('draft_original_outcome_unknown')).kind,'unknown')
 assert.deepEqual(await recoveryResponse(Response.json({room:'one'})),{room:'one'})
})
