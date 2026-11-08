import { spawn, execFileSync } from 'node:child_process'
import { connect } from 'node:net'
import { mkdtempSync, openSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
const wt = process.argv[2]
const root = join(wt, 'kc-journey-map')
const run = mkdtempSync(join(tmpdir(), 'worker-browser-canvas-'))
const room = 'worker-browser-default-check'
const portFree = port => new Promise(resolve => {
  const socket = connect({port, host:'127.0.0.1'})
  const done = free => {socket.destroy(); resolve(free)}
  socket.setTimeout(500)
  socket.once('connect', () => done(false))
  socket.once('error', () => done(true))
  socket.once('timeout', () => done(true))
})
const freePort = async start => {
  for (let port = start; port < start + 200; port++) if (await portFree(port)) return port
  throw Error('no free port')
}
const apiPort = await freePort(5900)
const vitePort = await freePort(3900)
const env = {...process.env, JOURNEY_API_PORT:String(apiPort), JOURNEY_CANVAS_PORT:String(vitePort), JOURNEY_ROOMS_DIR:join(run,'rooms'), JOURNEY_ASSETS_DIR:join(run,'assets'), JOURNEY_SAVE_DIR:join(run,'save')}
const children = []
function launch(args, name) {
  const fd = openSync(join(run,name+'.log'),'w')
  const child = spawn(process.execPath,args,{cwd:root,env,stdio:['ignore',fd,fd],detached:true})
  children.push(child)
  return child.pid
}
const apiPid = launch(['node_modules/tsx/dist/cli.mjs','server/canvas-server.ts'],'api')
const vitePid = launch(['node_modules/vite/bin/vite.js','dev','--host','127.0.0.1','--strictPort'],'vite')
const fact = {wt,root,run,room,apiPort,vitePort,apiPid,vitePid,candidate:execFileSync('git',['-C',wt,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),url:`http://127.0.0.1:${vitePort}/?room=${room}`}
writeFileSync('/tmp/worker-browser-canvas-provenance.json',JSON.stringify(fact,null,2)+'\n')
const stop = () => {for(const child of children)try{process.kill(-child.pid,'SIGTERM')}catch{}}
process.on('SIGTERM',()=>{stop();process.exit(0)})
process.on('SIGINT',()=>{stop();process.exit(0)})
process.on('exit',stop)
try {
  for (const [port,path] of [[apiPort,'/health'],[vitePort,'/']]) {
    let ready = false
    for(let n=0;n<100;n++) {
      try {const r = await fetch(`http://127.0.0.1:${port}${path}`);if(r.ok){ready=true;break}}catch{}
      await new Promise(r=>setTimeout(r,200))
    }
    if(!ready)throw Error(`server not ready on ${port}; logs in ${run}`)
  }
  execFileSync(process.execPath,['lib/journey-render.mjs',join(wt,'docs/journey/kc-dev-flow-2/journey.yaml'),room],{cwd:root,env:{...env,JOURNEY_API:`http://127.0.0.1:${apiPort}`},stdio:'inherit'})
  console.log(JSON.stringify(fact))
}catch(e){console.error(e.message);stop();process.exit(1)}
await new Promise(()=>{})
