import { spawnSync } from 'node:child_process'
const args=process.argv.slice(2)
if(args.length!==3||args[0]!=='--adapter'||!['node','cloudflare-local'].includes(args[1])||args[2]!=='--synthetic')throw new Error('explicit --adapter node|cloudflare-local --synthetic required')
const r=spawnSync(process.execPath,['--import','tsx','--test','scripts/member-enrollment.test.ts'],{cwd:new URL('..',import.meta.url),env:{...process.env,JOURNEY_MEMBER_TEST_ADAPTER:args[1]},stdio:'inherit'})
process.exitCode=r.status??1
