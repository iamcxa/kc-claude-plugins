import concurrent.futures, json, subprocess, sys
from pathlib import Path
out=Path('/tmp/opencode/issue815-validation')
relay=Path('/Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state')
sha=json.loads((out/'replay/replay.json').read_text())['relay']['sha']
for rel in ['_archive/theme-switch-keeps-draft.md','_archive/theme-switch-keeps-draft/design/validation-1.yaml']:
    (out/'replay/relay'/rel).write_bytes(subprocess.check_output(['git','-C',str(relay),'show',sha+':'+rel]))
tasks=[]
for label in ['own','relay']:
    state=out/'replay'/label
    paths=[*state.glob('*.md'),*state.glob('*/index.md'),*(state/'_archive').glob('*.md'),*(state/'_archive').glob('*/index.md')]
    for path in sorted(paths):
        text=path.read_text()
        if text.startswith('---\n') and '\nstatus:' in text.split('\n---\n',1)[0]:
            tasks.extend((label,path,mode) for mode in ['check','seed'])
def compare(args):
    label,path,mode=args
    row={'corpus':label,'task':str(path.relative_to(out/'replay'/label)),'mode':mode}
    for version in ['base','candidate']:
        cmd=[sys.executable,'-B',str(out/version/'kc-dev-flow-2/scripts/design_surfaces.py'),'check']+(['--seed'] if mode=='seed' else [])+[str(path)]
        r=subprocess.run(cmd,capture_output=True,text=True)
        row[version]={'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    row['changed']=row['base']!=row['candidate']
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(compare,tasks))
(out/'corpus-results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
summary={label:{'task_count':len({r['task'] for r in rows if r['corpus']==label}),'checks':sum(r['corpus']==label for r in rows),'changed':sum(r['changed'] and r['corpus']==label for r in rows)} for label in ['own','relay']}
(out/'corpus-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
