import { mkdtemp, chmod, writeFile, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { build } from 'esbuild'
import { Miniflare, Response as WorkerResponse } from 'miniflare'
import { NodeHost } from '../server/host/node'
import { digest } from '../server/host/policy'
import { handle } from '../server/host/transport'
import type { EnrollmentBinding, EnrollmentTarget } from '../server/host/member-enrollment'
export const issuer='https://team.synthetic.cloudflareaccess.com',origin='https://entry.synthetic.invalid',subject='11111111-1111-4111-8111-111111111111'
export const binding:EnrollmentBinding={accountId:'account',applicationId:'app',providerId:'otp',backendId:'synthetic',origin,issuer,audience:'audience',rooms:['one','two']}
export const target=():EnrollmentTarget=>({backendId:'synthetic',origin,issuer,audience:'audience',email:'person@synthetic.invalid',memberId:'person',label:'Synthetic person',rooms:[{roomId:'one',expiresAt:Date.now()+3600_000}]})
export function provider(changes:any={}) {
 const calls:string[]=[]
 const read=async(path:string,query?:Record<string,string>)=>{
  calls.push(path+'?'+JSON.stringify(query||{}));let result:any,result_info:any
  if(path.endsWith('/organizations'))result={auth_domain:new URL(issuer).host,...changes.organization}
  else if(path.endsWith('/apps/app'))result={id:'app',aud:'audience',domain:new URL(origin).host,...changes.app}
  else if(path.endsWith('/identity_providers/otp'))result={id:'otp',type:'onetimepin',...changes.provider}
  else if(path.endsWith('/users')){result=changes.users??[{id:'directory-id-never-subject',email:'person@synthetic.invalid'}];if(changes.pages)result=changes.pages[Number(query?.page)-1]||[];result_info={total_pages:changes.pages?.length||1,page:Number(query?.page),...changes.pageInfo}}
  else if(path.endsWith('/users/directory-id-never-subject/last_seen_identity'))result=changes.absent?null:{email:'person@synthetic.invalid',account_id:'account',user_uuid:subject,iat:Math.floor(Date.now()/1000)-60,service_token_status:false,idp:{id:'otp'},...changes.identity}
  else throw new Error('unexpected synthetic provider path '+path)
  return {success:true,result,...(result_info?{result_info}:{})}
 };return {read,calls}
}
export async function fixture(adapter:string,{enabled=true,mode='cloudflare',providerFetch}:any={}) {
 const dir=await mkdtemp(join(tmpdir(),'journey-member-'));await chmod(dir,0o700)
 const config:any={version:1,backendId:'synthetic',origin,mode,issuer,audience:'audience',members:[]}
 if(mode==='local'){config.issuer='local:synthetic';config.origin='http://127.0.0.1:3737';config.localOwnerUid=process.geteuid?.();config.localMemberId='owner';config.members=[{id:'owner',issuer:config.issuer,subject:'uid:'+config.localOwnerUid,label:'Owner',role:'operator',rooms:[]}]}
 const grants=[{credentialId:'seed',secretDigest:await digest('s'.repeat(43)),principalId:'seed',rooms:['one','two'],expiresAt:Date.now()+3600_000,revoked:false}]
 let fault:any=null,counter=0,host:any,mf:any,registry:any
 const env={JOURNEY_PRIVATE_DIR:join(dir,'private'),JOURNEY_ORIGIN:config.origin,JOURNEY_HUMAN_CONFIG:join(dir,'human.json'),JOURNEY_GRANTS_FILE:join(dir,'grants.json'),JOURNEY_AGENT_PAIRING:'true',JOURNEY_MEMBER_ENROLLMENT:String(enabled),JOURNEY_MEMBER_BINDING:JSON.stringify(binding)}
 const previous=Object.fromEntries(Object.keys(env).map(k=>[k,process.env[k]]))
 if(adapter==='node'){
  await writeFile(env.JOURNEY_HUMAN_CONFIG,JSON.stringify(config),{mode:0o600});await writeFile(env.JOURNEY_GRANTS_FILE,JSON.stringify(grants),{mode:0o600});Object.assign(process.env,env);host=new NodeHost()
  for(const [k,v]of Object.entries(previous))if(v===undefined)delete process.env[k];else process.env[k]=v
  const prepare=host.db.prepare.bind(host.db),exec=host.db.exec.bind(host.db)
  host.db.prepare=(sql:string)=>{const statement=prepare(sql);if(!sql.startsWith('INSERT OR REPLACE INTO metadata'))return statement;const run=statement.run.bind(statement);statement.run=(...args:any[])=>{counter++;if(fault?.at===counter&&!fault.after)throw new Error('synthetic-before-write');const result=run(...args);if(fault?.at===counter&&fault.after)throw new Error('synthetic-after-write');return result};return statement}
  host.db.exec=(sql:string)=>{if(sql==='COMMIT'&&fault?.commit&&!fault.after)throw new Error('synthetic-before-commit');const result=exec(sql);if(sql==='COMMIT'&&fault?.commit&&fault.after)throw new Error('synthetic-after-commit');return result}
 }else{
  const entry=new URL('../server/host/cloudflare.ts',import.meta.url).pathname
  const product=await build({entryPoints:[entry],bundle:true,write:false,format:'esm',platform:'browser',conditions:['workerd','worker','browser'],external:['cloudflare:workers'],logLevel:'silent',plugins:[{name:'synthetic-transaction-fault',setup(b){b.onLoad({filter:/host\/cloudflare\.ts$/},async()=>{const {readFile}=await import('node:fs/promises');let contents=await readFile(entry,'utf8');contents=contents.replace('export class JourneyRegistry {','export class JourneyRegistry {\n testFault:any=null;testWrites=0;');contents=contents.replace('put: (key, value) => this.put(key, value)',"put: (key,value)=>{this.testWrites++;if(this.testFault?.at===this.testWrites&&!this.testFault.after)throw new Error('synthetic-before-write');this.put(key,value);if(this.testFault?.at===this.testWrites&&this.testFault.after)throw new Error('synthetic-after-write')}");contents=contents.replace("if (op === '/member') {","if(op==='/test-fault'){this.testFault=body;this.testWrites=0;return Response.json({ok:true})}\n  if (op === '/member') {");contents=contents.replace('enrollmentOperation(this.sync(),body.operation,body.input,this.env.JOURNEY_MEMBER_BINDING?JSON.parse(this.env.JOURNEY_MEMBER_BINDING):undefined,this.env.JOURNEY_MEMBER_ENROLLMENT===\'true\')',"(()=>{const result=enrollmentOperation(this.sync(),body.operation,body.input,this.env.JOURNEY_MEMBER_BINDING?JSON.parse(this.env.JOURNEY_MEMBER_BINDING):undefined,this.env.JOURNEY_MEMBER_ENROLLMENT==='true');if(this.testFault?.commit)throw new Error('synthetic-commit-boundary');return result})()");return {contents,loader:'ts'}})}}]})
  mf=new Miniflare({script:product.outputFiles[0].text,modules:true,compatibilityDate:'2026-07-01',compatibilityFlags:['nodejs_compat'],host:'127.0.0.1',port:0,bindings:{JOURNEY_ORIGIN:origin,JOURNEY_GRANTS:JSON.stringify(grants),JOURNEY_HUMAN_CONFIG:JSON.stringify(config),JOURNEY_AGENT_PAIRING:'true',JOURNEY_MEMBER_ENROLLMENT:String(enabled),JOURNEY_MEMBER_BINDING:JSON.stringify(binding)},durableObjects:{ROOMS:{className:'JourneyRoom',useSQLite:true},REGISTRY:{className:'JourneyRegistry',useSQLite:true}},durableObjectsPersist:join(dir,'objects'),outboundService:async req=>{if(!providerFetch)throw new Error('unexpected outbound '+req.url);const r=await providerFetch(req);return new WorkerResponse(await r.arrayBuffer(),{status:r.status,headers:r.headers})}})
  await mf.ready;const ns=await mf.getDurableObjectNamespace('REGISTRY');registry=ns.get(ns.idFromName('private-pilot'))
 }
 const call=async(path:string,body:any)=>{const r=await registry.fetch('https://registry/'+path,{method:'POST',body:JSON.stringify(body)});return r.json()}
 const get=async(key:string)=>host?host.meta.get(key):call('get',{key})
 const put=async(key:string,value:any)=>host?host.meta.put(key,value):call('put',{key,value})
 const list=async(prefix:string)=>host?host.meta.list(prefix):call('list',{prefix})
 const member=async(op:string,input:any)=>host?host.memberOperation(op,input):call('member',{operation:op,input})
 for(const room of ['one','two'])await put('room:'+room,{createdAt:12345})
 await put('asset:one:sentinel',{blobKey:'one/sentinel',size:123})
 await put('security-denial:sentinel',{deniedAt:1,target:{memberId:'archived'}})
 return {dir,host,mf,config,get,put,list,member,registry,grants,security:async(op:string,input:any)=>host?host.meta.security(op,input):call('security',{operation:op,input}),human:async(op:string,input:any)=>host?host.meta.human(op,input):call('human',{operation:op,input}),agent:async(op:string,input:any)=>host?host.meta.agent(op,input):call('agent',{operation:op,input}),snapshot:async()=>JSON.stringify(await list('')),fault:async(value:any)=>{if(host){fault=value;counter=0}else await call('test-fault',value)},request:async(path:string,init:any={})=>host?handle(host,new Request(origin+path,init)):mf.dispatchFetch(origin+path,init),close:async()=>{host?.close();await mf?.dispose()}}
}
