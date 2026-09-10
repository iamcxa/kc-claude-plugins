import assert from 'node:assert/strict'
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {resolve} from 'node:path'
const root=process.env.RECUT_SNAPSHOT_ROOT,dir=process.env.RECUT_PROOF_DIR
if(!root || !dir)throw Error('RECUT_SNAPSHOT_ROOT and RECUT_PROOF_DIR are required')
mkdirSync(dir,{recursive:true})
for(const n of [2,3]){
 const plugin=resolve(root,`layer-${n}/kc-journey-map`)
 const {applyDiff}=await import(`${plugin}/lib/read.mjs`)
 const path=resolve(dir,`stale-layer-${n}.yaml`)
 const raw='steps:\n  - id: a\n    card: Activity\n    stories:\n      - {id: a-0, card: Shared wording}\n      - {id: a-2, card: New source wording}\n'
 writeFileSync(path,raw)
 const diff={reworded:[{id:'a-2',field:'story',step:'a',was:'Shared wording',now:'Canvas wording'}],releaseMoved:[],storiesReordered:[],duplicated:[],reordered:null,rewordConflict:[],reorderConflict:null}
 const result=applyDiff(path,diff)
 assert.deepEqual(result.applied,[])
 assert.match(result.skipped.join(),/a-2 wording changed in the file/)
 assert.equal(readFileSync(path,'utf8'),raw)
 console.log(`PASS layer ${n}: stale canvas wording is refused without modifying either story`)
}
