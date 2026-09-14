import {writeFileSync} from 'node:fs';import assert from 'node:assert/strict';import {dirname} from 'node:path';import {fileURLToPath} from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));
const original=await import(`${root}/../necessity-audit/control/lib/render.mjs`),small=await import(`${root}/../three-unit/unit-3/kc-journey-map/lib/render.mjs`),broken=await import(`${root}/../necessity-audit/no-borders/lib/render.mjs`);
const {fixtureModel}=await import(`${root}/../necessity-audit/control/lib/fixture.mjs`);
const {createTLSchema}=await import(`${root}/../necessity-audit/control/node_modules/@tldraw/tlschema/dist-esm/index.mjs`);
const schema=createTLSchema();
const example=original.loadJourney(`${root}/../three-unit/unit-3/kc-journey-map/skills/kc-journey-map/references/journey.example.yaml`);
function meaningful(records){
 for(const r of records)schema.types[r.typeName].validate(r);
 return records.map(r=>({...r,index:records.filter(x=>x.typeName===r.typeName&&x.parentId===r.parentId).sort((a,b)=>a.index<b.index?-1:1).findIndex(x=>x.id===r.id)}));
}
const proof={normalization:'fractional index bytes vary randomly; schema validate and compare rank per parent instead',cases:[]};
const expected=meaningful(original.buildAllPages(fixtureModel,'same-room',original.PROJECTION_KEYS));
assert.notDeepEqual(meaningful(broken.buildAllPages(fixtureModel,'same-room',original.PROJECTION_KEYS)),expected);
proof.instrument_negative='removing story borders is detected';
for(const [name,model] of [['fixture',fixtureModel],['worked-example',example]])for(const selection of [original.PROJECTION_KEYS]){
 const a=meaningful(original.buildAllPages(model,'same-room',selection)),b=meaningful(small.buildAllPages(model,'same-room',selection));
 assert.deepEqual(b,a);proof.cases.push({name,selection,records:b.length,equal:true});
}
writeFileSync(`${root}/focused-projection-proof.json`,JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify(proof));
