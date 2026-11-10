from pathlib import Path
import concurrent.futures,json,subprocess,sys
out=Path(__file__).resolve().parent
rows=json.loads((out/'corpus-inputs.json').read_text())
for row in rows:
 row['before']=row['after'];row['after']=subprocess.check_output(['git','-C',row['state'],'rev-parse','HEAD'],text=True).strip()
(out/'current-tail-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
def run(row):
 cmd=[sys.executable,'-B',str(out/'candidate/kc-dev-flow-2/scripts/laws_check.py'),row['state'],'--before',row['before'],'--after',row['after'],'--readme',row['readme']]
 p=subprocess.run(cmd,capture_output=True,text=True)
 (out/('current-tail-'+row['name']+'.log')).write_text(p.stdout+p.stderr)
 lines=[x for x in p.stdout.splitlines() if x.startswith(('L4 ','violation: L4 '))]
 result={**row,'argv':cmd,'exit':p.returncode,'L4_lines':lines}
 (out/('current-tail-'+row['name']+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 assert len(lines)==1 and '0 events judged' in lines[0],result
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,rows))
(out/'current-tail.json').write_text(json.dumps(results,indent=2)+'\n')
print('No additional L4 event in the three local-tip extensions.')
