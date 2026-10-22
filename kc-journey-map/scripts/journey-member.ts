import { fstatSync, readFileSync, writeFileSync, openSync, closeSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createInterface } from 'node:readline/promises'
import { stdin, stdout } from 'node:process'
import { validateTarget, scopeText, type EnrollmentTarget, type EnrollmentBinding } from '../server/host/member-enrollment'
import { resolveMember, type ProviderRead } from './member-resolver'

export function protectedFd(fd:number,writable=false) {
 if(!Number.isSafeInteger(fd)||fd<3)throw new Error('protected_descriptor_required')
 const s=fstatSync(fd)
 if(!s.isFile() || s.uid!==process.geteuid?.() || (s.mode&0o077)!==0 || s.nlink!==1 || s.size>65536 || (writable&&s.size!==0))throw new Error('owner_only_regular_descriptor_required')
 return fd
}
export function strictJson(text:string) {
 if(Buffer.byteLength(text)>65536)throw new Error('input_too_large')
 let i=0
 const ws=()=>{while(/\s/.test(text[i]||'')&&i<text.length)i++}
 const string=()=>{const start=i++;while(i<text.length){if(text[i]==='\\'){i+=2;continue}if(text[i++]==='"')return JSON.parse(text.slice(start,i))}throw new Error('invalid_json')}
 const value=():void=>{ws();if(text[i]==='{'){i++;ws();const keys=new Set();if(text[i]!=='}')for(;;){ws();if(text[i]!=='"')throw new Error('invalid_json');const k=string();if(keys.has(k))throw new Error('duplicate_key');keys.add(k);ws();if(text[i++]!==':')throw new Error('invalid_json');value();ws();if(text[i]!==',')break;i++}if(text[i++]!=='}')throw new Error('invalid_json')}
 else if(text[i]==='['){i++;ws();if(text[i]!==']')for(;;){value();ws();if(text[i]!==',')break;i++}if(text[i++]!==']')throw new Error('invalid_json')}
 else if(text[i]==='"')string();else{const m=/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(text.slice(i));if(!m)throw new Error('invalid_json');i+=m[0].length}}
 value();ws();if(i!==text.length)throw new Error('invalid_json');return JSON.parse(text)
}
export async function runMemberCommand({op,target,binding,read,send,confirm,save,operationId=crypto.randomUUID(),candidate,signal,allowedTarget}: {
 op:'enroll'|'inspect';target:EnrollmentTarget;binding:EnrollmentBinding;read:ProviderRead;send:(op:string,input:any)=>Promise<any>;confirm:(review:string)=>Promise<string>;save:(receipt:any)=>void;operationId?:string;candidate:string;signal?:AbortSignal;allowedTarget?:EnrollmentTarget
}) {
 target=validateTarget(structuredClone(target));const original=scopeText(target)
 if(allowedTarget && scopeText(validateTarget(allowedTarget))!==original)return {result:'refused',category:'delegated_scope_denied'}
 let proof
 try {proof=await resolveMember(target.email,binding,read,Date.now(),signal)}catch(error){return {result:'refused',category:signal?.aborted?'cancelled':(error as Error).message}}
 const review=JSON.stringify({target,identity:proof.subject,account:proof.accountId,application:proof.applicationId,provider:proof.providerId,role:'member',capabilities:'existing ordinary full-record creation, editing and deletion'})
 if(op==='enroll' && await confirm(review)!=='CONFIRM '+review)return {result:'refused',category:'cancelled'}
 if(signal?.aborted)return {result:'refused',category:'cancelled'}
 if(scopeText(target)!==original)throw new Error('approval_changed')
 validateTarget(target)
 let result
 try {result=await send(op,{target,proof,operationId})}catch{result={result:'unknown',category:'response_unavailable',retry:false}}
 const receipt={operationId,candidate,observedAt:proof.observedAt,proof,target,result,readback:null}
 if(op==='enroll' && result.result==='unknown'){
  try{const readback=await send('inspect',{target,proof,operationId});receipt.readback=readback?.result==='refused'?{result:'unknown',category:readback.category}:readback}catch{receipt.readback={result:'unknown'}}
 }
 try{save(receipt)}catch{return {result:'unknown',category:'local_receipt_unavailable',retry:false}}
 return {result:result.result,category:result.category,readback:receipt.readback?.result||null}
}
async function main() {
 const args=process.argv.slice(2),op=args.shift()
 if(!['enroll','inspect'].includes(op||'') || args.length!==6 || args[0]!=='--profile'||args[2]!=='--input-fd'||args[4]!=='--receipt-fd'||!/^[a-zA-Z0-9_-]+$/.test(args[1]))throw new Error('expected enroll|inspect --profile <name> --input-fd <fd> --receipt-fd <fd>')
 const inputFd=protectedFd(Number(args[3])),receiptFd=protectedFd(Number(args[5]),true)
 const profileFd=openSync(join(process.env.JOURNEY_MEMBER_PROFILE_DIR||join(homedir(),'.config/journey/profiles'),args[1]+'.json'),'r')
 let profile:any;try{protectedFd(profileFd);profile=strictJson(readFileSync(profileFd,'utf8'))}finally{closeSync(profileFd)}
 if(profile.enabled!==true || profile.writersStopped!==true || !profile.candidate)throw new Error('explicit_enabled_stopped_profile_required')
 const target=validateTarget(strictJson(readFileSync(inputFd,'utf8'))),binding=profile.binding
 if(profile.allowedTarget && scopeText(validateTarget(profile.allowedTarget))!==scopeText(target))throw new Error('delegated_scope_denied')
 const token=readFileSync(protectedFd(profile.providerFd),'utf8').trim()
 const read:ProviderRead=async(path,query)=>{
  const url=new URL('https://api.cloudflare.com/client/v4'+path);for(const [k,v]of Object.entries(query||{}))url.searchParams.set(k,v)
  const response=await fetch(url,{headers:{Authorization:'Bearer '+token},redirect:'error',signal:AbortSignal.timeout(15_000)})
  if(!response.ok)throw new Error('provider_unavailable');return response.json()
 }
 let operatorToken:string|undefined
 let nodeReader:ReturnType<typeof createInterface>|undefined
 const pending=new Map<string,{done:(v:any)=>void;reject:(e:Error)=>void;timer:ReturnType<typeof setTimeout>}>()
 const send=async(operation:string,input:any)=>{
  if(profile.transport?.mode==='node'){
   for(const fd of [profile.transport.inputFd,profile.transport.outputFd]){const s=fstatSync(fd);if((!s.isFIFO()&&!s.isSocket())||s.uid!==process.geteuid?.()||(s.mode&0o077))throw new Error('private_control_required')}
   if(!nodeReader){nodeReader=createInterface({input:awaitStream(profile.transport.outputFd)});nodeReader.on('line',line=>{try{const r=JSON.parse(line),p=pending.get(r.control);if(p){clearTimeout(p.timer);pending.delete(r.control);p.done(r.result)}}catch{}})}
   return new Promise<any>((done,reject)=>{const timer=setTimeout(()=>{pending.delete(input.operationId);reject(new Error('control_timeout'))},15_000);pending.set(input.operationId,{done,reject,timer});writeFileSync(profile.transport.inputFd,JSON.stringify({id:input.operationId,op:'member-'+operation,writersStopped:true,input})+'\n')})
  }
  if(profile.transport?.mode!=='cloudflare-private')throw new Error('unsupported_transport')
  const url=new URL(profile.transport.url);if(url.protocol!=='https:'||url.pathname!=='/'||url.search||url.hash||url.username||url.password)throw new Error('invalid_private_endpoint')
  operatorToken ??= readFileSync(protectedFd(profile.transport.credentialFd),'utf8').trim()
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+operatorToken},body:JSON.stringify({op:'member-'+operation,writersStopped:true,input}),redirect:'error',signal:AbortSignal.timeout(15_000)})
  if(!response.ok){if(response.status>=500)throw new Error('response_unknown');return {result:'refused',category:'private_operation_denied'}}return response.json()
 }
 const signal=new AbortController();process.once('SIGINT',()=>signal.abort())
 const result=await runMemberCommand({op:op as 'enroll'|'inspect',target,binding,read,send,candidate:profile.candidate,allowedTarget:profile.allowedTarget,signal:signal.signal,confirm:async review=>{if(!stdin.isTTY||!stdout.isTTY)throw new Error('interactive_review_required');const rl=createInterface({input:stdin,output:stdout});try{return await rl.question(review+'\nType CONFIRM followed by the exact review, or cancel:\n',{signal:signal.signal})}finally{rl.close()}},save:receipt=>writeFileSync(receiptFd,JSON.stringify(receipt)+'\n')})
 nodeReader?.close()
 nodeReader?.input.destroy()
 console.log(JSON.stringify(result))
}
import { Socket } from 'node:net'
const awaitStream=(fd:number)=>new Socket({fd,readable:true,writable:false})
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)main().catch(()=>{console.error('member command refused; inspect protected state before retry if a request was sent');process.exitCode=1})
