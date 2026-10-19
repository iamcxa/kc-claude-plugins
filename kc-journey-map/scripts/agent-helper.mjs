import { readFile } from 'node:fs/promises'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { createInterface } from 'node:readline'
import { PairedInstallation, validateInstallation } from './agent-installation.mjs'
import { openProtectedStore } from './agent-protected-store.mjs'

const category=error=>/^[a-z_]{1,80}$/.test(error?.message)?error.message:'installation_unavailable'
let store
try {
 const [command,configPath,storeRoot]=process.argv.slice(2)
 if(!['begin','finish','status','reconcile','forget','mcp'].includes(command) || !configPath) throw new Error('usage_command_config_path_optional_store_root')
 const config=JSON.parse(await readFile(configPath,'utf8'))
 if(Object.keys(config).some(key=>!['endpoint','backendId','installationId','memberId','rooms','label'].includes(key))) throw new Error('config_contains_unsupported_fields')
 validateInstallation(config)
 store=await openProtectedStore(config,storeRoot||join(homedir(),'.local/share/kc-journey-map/agents'))
 const client=new PairedInstallation(config,store)
 if(command==='mcp') {
  for await(const line of createInterface({input:process.stdin})) {
   let rpc
   try { rpc=JSON.parse(line); const reply=await client.call(rpc); if(rpc.id!==undefined && reply) process.stdout.write(JSON.stringify(reply)+'\n') }
   catch(error) { if(rpc?.id!==undefined) process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:rpc.id,error:{code:-32001,message:category(error)}})+'\n') }
  }
 } else {
  const result=command==='begin'?await client.begin():command==='finish'?await client.finish():command==='reconcile'?await client.reconcile():command==='forget'?(await store.removeRevoked(),{state:'unpaired'}):await client.status()
  process.stdout.write(JSON.stringify(result)+'\n')
 }
} catch(error) { process.stderr.write(category(error)+'\n');process.exitCode=1 }
finally { await store?.close() }
