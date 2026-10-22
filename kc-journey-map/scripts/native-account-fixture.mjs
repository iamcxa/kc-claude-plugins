import assert from 'node:assert/strict'
import { openSync,closeSync,createReadStream,createWriteStream } from 'node:fs'
import { spawn,execFileSync } from 'node:child_process'
import { mkdtemp,writeFile,mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { createServer } from 'node:net'
import { createServer as createVite } from 'vite'
import { createInterface } from 'node:readline'
export const root=new URL('..',import.meta.url).pathname.replace(/\/$/,'')
export const hash=value=>createHash('sha256').update(value).digest('hex')
const port=()=>new Promise(resolve=>{const socket=createServer();socket.listen(0,'127.0.0.1',()=>{const value=socket.address().port;socket.close(()=>resolve(value))})})
export async function startFixture(){
 const scratch=await mkdtemp(join(tmpdir(),'native-account-')),apiPort=await port(),uiPort=await port(),origin='http://127.0.0.1:'+uiPort
 const secret='s'.repeat(43),bearer='synthetic.'+secret,issuer='local:synthetic-native'
 const configFile=join(scratch,'human.json'),grantsFile=join(scratch,'grants.json'),dataDir=join(scratch,'data'),saveDir=join(scratch,'save')
 await mkdir(saveDir)
 const repo=join(scratch,'synthetic-notes');await mkdir(repo)
 execFileSync('git',['init','--initial-branch=main',repo])
 await writeFile(join(repo,'README.md'),'# Synthetic fixture\n\nOnly local synthetic document content.\n')
 execFileSync('git',['-C',repo,'add','README.md'])
 execFileSync('git',['-C',repo,'-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid','commit','-m','Synthetic local document'])

 await writeFile(grantsFile,JSON.stringify([{credentialId:'synthetic',secretDigest:hash(secret),principalId:'synthetic-seed',rooms:['one','two','denied'],expiresAt:Date.now()+3600_000,revoked:false}]),{mode:0o600})
 await writeFile(configFile,JSON.stringify({version:1,backendId:'synthetic-native',origin,mode:'local',issuer,localOwnerUid:process.geteuid(),localMemberId:'owner',members:[
  {id:'owner',issuer,subject:'uid:'+process.geteuid(),label:'Synthetic owner',role:'operator',rooms:['one','two'].map(id=>({id,expiresAt:Date.now()+3600_000}))},
  {id:'member',issuer,subject:'ordinary',label:'Synthetic member',role:'operator',rooms:[{id:'one',expiresAt:Date.now()+3600_000}]}]}),{mode:0o600})
 const logs=[],pending=new Map()
 const input=join(scratch,'operator-in'),output=join(scratch,'operator-out')
 execFileSync('mkfifo',['-m','600',input,output])
 const inputFd=openSync(input,'r+'),outputFd=openSync(output,'r+'),reader=createReadStream(output),writer=createWriteStream(input)
 const child=spawn(process.execPath,['--import','tsx','server/canvas-server.ts'],{cwd:root,stdio:[inputFd,outputFd,'pipe'],env:{...process.env,JOURNEY_PRIVATE_DIR:dataDir,JOURNEY_GRANTS_FILE:grantsFile,JOURNEY_HUMAN_CONFIG:configFile,JOURNEY_ORIGIN:origin,JOURNEY_API_PORT:String(apiPort),JOURNEY_CONTROL_STDIO:'1',JOURNEY_NATIVE_ACCOUNT:'true',JOURNEY_AGENT_PAIRING:'true',JOURNEY_SAVE_DIR:saveDir,JOURNEY_DOC_REPOS:'synthetic/notes='+repo,JOURNEY_ROOM_REPOS:JSON.stringify({one:['synthetic/notes'],two:['synthetic/notes']})}})
 createInterface({input:reader}).on('line',line=>{logs.push(line);try{const value=JSON.parse(line);if(value.control){pending.get(value.control)?.(value.result);pending.delete(value.control)}}catch{}})
 child.stderr.on('data',value=>logs.push(String(value)))
 const control=command=>new Promise((resolve,reject)=>{const id=crypto.randomUUID();pending.set(id,resolve);writer.write(JSON.stringify({id,...command})+'\n');setTimeout(()=>{if(pending.delete(id))reject(new Error('control timeout '+logs.join('\n')))},5000).unref()})
 const api=(path,options={})=>fetch('http://127.0.0.1:'+apiPort+path,{...options,headers:{Authorization:'Bearer '+bearer,...options.headers}})
 let vite
 try{
  for(let n=0;n<200;n++){try{if((await api('/health')).ok)break}catch{}if(child.exitCode!==null)throw new Error(logs.join('\n'));await new Promise(r=>setTimeout(r,50));if(n===199)throw new Error('startup timeout '+logs.join('\n'))}
  for(const room of ['one','two','denied'])assert.equal((await api('/doc?room='+room)).status,200)
  process.env.JOURNEY_API_PORT=String(apiPort);process.env.JOURNEY_HUMAN_CONFIG=configFile
  vite=await createVite({cacheDir:join(scratch,'vite-cache'),configFile:join(root,'vite.config.mts'),server:{hmr:false,host:'127.0.0.1',port:uiPort,strictPort:true}});await vite.listen()
 }catch(error){await vite?.close();child.kill('SIGTERM');throw error}
 const approve=requestId=>execFileSync('python3',[join(root,'scripts/owner-login.py'),join(dataDir,'owner-login.sock'),requestId],{input:'approve\n',encoding:'utf8'})
 const close=async()=>{await vite.close();reader.destroy();writer.destroy();closeSync(inputFd);closeSync(outputFd);if(child.exitCode===null){const exit=new Promise(r=>child.once('exit',r));child.kill('SIGTERM');await exit}}
 return {scratch,origin,apiPort,api,control,approve,close,dataDir,configFile,saveDir,logs}
}
