import assert from 'node:assert/strict'
import {note} from '../lib/records.mjs'

export async function checkConcurrentHumanSessions({browser,origin,routeAssets,metadata,seed,report}) {
 const contexts=[],sockets=[[],[],[]],frames=[[],[],[]]
 const wait=async fn=>{for(let i=0;i<150;i++){if(await fn())return;await new Promise(r=>setTimeout(r,100))}throw Error('concurrent native condition timed out')}
 const document=async()=>{const r=await seed('/doc?room=live');assert.equal(r.status,200);return r.json()}
 const initial=await document(),pageId=initial.snapshot.documents.find(d=>d.state.typeName==='page').state.id
 const baseline=note({id:'shape:live-base',text:'preserved live baseline',parentId:pageId,x:100,y:100})
 assert.equal((await seed('/doc?room=live','PATCH',{put:[baseline]})).status,200)
 const make=async(member,index)=>{
  const context=await browser.newContext({viewport:{width:1280,height:900}});contexts.push(context)
  await context.addCookies([{name:'journey_human',value:'return-'+member,url:origin,httpOnly:true,sameSite:'Strict'},{name:'journey_human_csrf',value:'csrf-'+member,url:origin,sameSite:'Strict'}])
  await context.route('**/*',routeAssets)
  await context.routeWebSocket(url=>url.pathname==='/connect/live',socket=>{sockets[index].push(socket.url());const remote=socket.connectToServer();socket.onMessage(message=>{frames[index].push(String(message));remote.send(message)})})
  const page=await context.newPage();await page.goto(origin+'/?room=live')
  await page.waitForFunction(()=>window.editor?.getShape('shape:live-base')&&document.querySelector('[data-testid="room-trigger"]')?.title.endsWith('Connected'))
  const native=await page.evaluate(()=>({storeId:window.editor.store.id,sessionId:window.TLDRAW_TAB_ID_v2,supplied:window.__nativeHumanSocketParams}))
  const url=new URL(sockets[index].find(value=>new URL(value).searchParams.get('storeId')===native.storeId))
  assert.ok(native.sessionId&&native.storeId);assert.equal(url.searchParams.get('sessionId'),native.sessionId)
  assert.ok(native.supplied.some(p=>p.sessionId===native.sessionId&&p.storeId===native.storeId))
  return{page,native,url:url.href}
 }
 try {
  const first=await make('owner',0),second=await make('other',1)
  assert.notEqual(first.native.sessionId,second.native.sessionId);assert.notEqual(first.native.storeId,second.native.storeId)
  const active=async()=>{const r=await seed('/health');assert.equal(r.status,200);return(await r.json()).active.find(r=>r.roomId==='live')?.sessions}
  await wait(async()=>await active()===2)
  const put=async(page,id,x)=>page.evaluate(record=>window.editor.store.put([record]),note({id,text:id,parentId:pageId,x,y:300}))
  for(let i=1;i<=3;i++){
   await put(first.page,'shape:live-first',200+i);await second.page.waitForFunction(x=>window.editor.getShape('shape:live-first')?.x===x,200+i)
   await put(second.page,'shape:live-second',400+i);await first.page.waitForFunction(x=>window.editor.getShape('shape:live-second')?.x===x,400+i)
   assert.equal(await active(),2)
  }
  await first.page.close();await put(second.page,'shape:live-second',500)
  await wait(async()=>(await document()).snapshot.documents.some(d=>d.state.id==='shape:live-second'&&d.state.x===500))
  const replacement=await make('owner',2);await wait(async()=>await active()===2)
  const key='member-room:owner:live',policy=await metadata('get',{key})
  await metadata('put',{key,value:{...policy,revoked:true}})
  const before=frames[2].length
  await put(replacement.page,'shape:live-forbidden',600);await replacement.page.getByText(/Source access paused/).first().waitFor()
  assert.equal(await replacement.page.evaluate(()=>window.editor.getInstanceState().isReadonly),true)
  assert.equal(new URL(replacement.page.url()).searchParams.get('room'),'live')
  assert.ok(!frames[2].slice(before).some(value=>value.includes('shape:live-forbidden')))
  await put(second.page,'shape:live-second',700);await wait(async()=>(await document()).snapshot.documents.some(d=>d.state.id==='shape:live-second'&&d.state.x===700))
  assert.equal(await second.page.evaluate(()=>window.editor.store.id),second.native.storeId)
  assert.equal(await second.page.getByTestId('room-trigger').getAttribute('title'),'Room: live. Connected')
  const current=await document();assert.ok(!current.snapshot.documents.some(d=>d.state.id==='shape:live-forbidden'))
  assert.deepEqual(current.snapshot.documents.find(d=>d.state.id===baseline.id).state,baseline)
  for(const item of initial.snapshot.documents)assert.ok(current.snapshot.documents.some(d=>d.state.id===item.state.id))
  await metadata('put',{key,value:policy})
  report.nativeConcurrent={first,second,replacement,sockets,roundTrips:6,simultaneousSessions:2,remainingStoreId:second.native.storeId,revokedNoFlush:true,baselinePreserved:true}
  for(const value of Object.values(report.nativeConcurrent))if(value?.page)delete value.page
 } finally {for(const context of contexts)await context.close()}
}
