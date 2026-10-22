import assert from 'node:assert/strict'
import { startFixture,hash,root } from './native-account-fixture.mjs'
const fixture=await startFixture()
const material={verifier:'b'.repeat(64),csrf:'c'.repeat(64)}
const post=(path,body)=>fetch(fixture.origin+path,{method:'POST',headers:{Origin:fixture.origin,'Content-Type':'application/json','X-Journey-Entry':'1'},body:JSON.stringify(body)})
try{
 const start=await post('/auth/local/start',material).then(r=>r.json())
 assert.match(fixture.approve(start.requestId),/"approved": true/)
 const consumed=await post('/auth/local/consume',{...material,requestId:start.requestId})
 assert.equal(consumed.status,200)
 const token=/journey_human=([^;]+)/.exec(consumed.headers.get('set-cookie'))[1]
 assert.equal((await fixture.control({op:'owner-bind',writersStopped:true,input:{backendId:'synthetic-native',ownerMemberId:'owner',issuer:'local:synthetic-native',subject:'uid:'+process.geteuid(),sessionDigest:hash(token),initializationOperationId:'synthetic-preview-owner'}})).bound,true)
 console.log(JSON.stringify({kind:'ACTUAL LOCAL CANDIDATE; SYNTHETIC ACCOUNTS AND DATA ONLY',url:fixture.origin+'/?room=one',pid:process.pid,stop:'kill '+process.pid,approveCommand:'python3 '+root+'/scripts/owner-login.py '+fixture.dataDir+'/owner-login.sock <request-id>',scratch:fixture.scratch}))
}catch(error){await fixture.close();throw error}
let closing=false
async function close(){if(closing)return;closing=true;await fixture.close();process.exit(0)}
process.on('SIGTERM',()=>void close());process.on('SIGINT',()=>void close())
