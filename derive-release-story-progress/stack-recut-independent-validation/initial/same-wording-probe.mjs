import { spawn, spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createServer } from 'node:net';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
const root = process.env.RECUT_SNAPSHOT_ROOT ?? resolve(here, '..');
const plugin = resolve(root, 'layer-2/kc-journey-map');
const { stringify, parse } = await import(`${plugin}/node_modules/yaml/dist/index.js`);
const { fixtureModel } = await import(`${plugin}/lib/fixture.mjs`);
const { renderToRoom } = await import(`${plugin}/lib/render.mjs`);
const port = await new Promise(ok => { const s=createServer(); s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>ok(p));}); });
const api=`http://127.0.0.1:${port}`;
const rooms=resolve(here,'rooms'); mkdirSync(rooms,{recursive:true});
const server=spawn(process.execPath,[`${plugin}/node_modules/tsx/dist/cli.mjs`,`${plugin}/server/canvas-server.ts`],{cwd:plugin,env:{...process.env,JOURNEY_API_PORT:String(port),JOURNEY_ROOMS_DIR:rooms},stdio:['ignore','pipe','pipe']});
let logs='';server.stdout.on('data',x=>logs+=x);server.stderr.on('data',x=>logs+=x);
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const rt=text=>({type:'doc',content:[{type:'paragraph',content:[{type:'text',text}]}]});
const evidence={tree:'9c3eb9fd9ace855df2654f3f122ed8d270cf6a3b',kind:'refusal',seam:'real server PATCH -> journey-read CLI --out -> YAML identity',cases:[]};
try {
 for(let n=0;n<100;n++){try{if((await fetch(`${api}/health`)).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 for(const duplicateWording of [true,false]){
  const name=duplicateWording?'same-wording':'distinct-wording';
  const model=structuredClone(fixtureModel);
  if(duplicateWording)model.steps[0].stories[1].card=model.steps[0].stories[0].card;
  const source=resolve(here,`${name}.yaml`),out=resolve(here,`${name}-out.yaml`);
  writeFileSync(source,stringify(model));const before=hash(source);
  const rendered=await renderToRoom({path:source,room:name,api});
  if(rendered.status!==200)throw Error(JSON.stringify(rendered));
  const doc=await fetch(`${api}/doc?room=${name}`).then(r=>r.json());
  const card=doc.snapshot.documents.map(d=>d.state).find(s=>s.meta?.journey?.kind==='story' && s.meta.journey.nodeId==='a-2');
  card.props.richText=rt('Edited second story');
  const patched=await fetch(`${api}/doc?room=${name}`,{method:'PATCH',headers:{'content-type':'application/json'},body:JSON.stringify({put:[card]})});
  if(patched.status!==200)throw Error(await patched.text());
  const cli=spawnSync(process.execPath,[`${plugin}/lib/journey-read.mjs`,source,name,'--out',out],{cwd:plugin,env:{...process.env,JOURNEY_API:api},encoding:'utf8'});
  const actual=parse(readFileSync(out,'utf8')).steps[0].stories;
  const expected=model.steps[0].stories.map(s=>({...s,card:s.id==='a-2'?'Edited second story':s.card}));
  evidence.cases.push({name,render_status:rendered.status,patch_status:patched.status,cli_exit:cli.status,cli_stdout:cli.stdout,cli_stderr:cli.stderr,expected,actual,identity_preserved:JSON.stringify(expected)===JSON.stringify(actual),source_hash_before:before,source_hash_after:hash(source),source_preserved:before===hash(source)});
 }
}finally{
 server.kill('SIGTERM');await new Promise(r=>server.once('exit',r));
 evidence.owned_server_stopped=true;writeFileSync(resolve(here,'server.log'),logs);
 writeFileSync(resolve(here,'same-wording-proof.json'),JSON.stringify(evidence,null,2)+'\n');
}
console.log(JSON.stringify(evidence,null,2));
process.exitCode=evidence.cases.every(c=>c.identity_preserved && c.source_preserved)?0:1;
