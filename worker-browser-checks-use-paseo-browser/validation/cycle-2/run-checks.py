import concurrent.futures,json,os,re,subprocess,sys
from pathlib import Path
out=Path(sys.argv[1]); export=Path(sys.argv[2]); repo=sys.argv[3]; sr=Path(sys.argv[4]); package=Path(sys.argv[5])
task=sr/'worker-browser-checks-use-paseo-browser'
base='139feeaee7ce037a0c6535568cd6bd103155cbae'; head='fef21735308e7e807d04a93a5506de5284dde436'
gitenv=dict(os.environ,GIT_DIR=subprocess.check_output(['git','-C',repo,'rev-parse','--absolute-git-dir'],text=True).strip(),GIT_WORK_TREE=str(export),GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
normalenv=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
commands={}
for record in json.loads((task/'implementation/cycle-2/package-tests.json').read_text()):
    name=record['name']; command=[sys.executable,'-B',str(export/name)]
    if name.endswith('test_sd_dispatch.py'): command+=['--sd-plugin-root','/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
    commands[name]=(command,normalenv,'package')
commands['adr-lint']=([sys.executable,'-B',str(package/'scripts/adr_lint.py'),'docs/adr','--since',base],gitenv,'checks')
commands['number-guards']=([sys.executable,'-B',str(package/'scripts/number_guards.py'),'check','--workflow-dir',str(sr.parent),'--task',str(task)+'.md','--repo',str(export),'--base',base,'--head',head],gitenv,'checks')
commands['comment-ratio']=([sys.executable,'-B',str(package/'scripts/comment_ratio.py'),base,head,'--workflow-dir',str(sr.parent)],gitenv,'checks')
commands['design-surfaces']=([sys.executable,'-B',str(package/'scripts/design_surfaces.py'),'check',str(task)+'.md'],normalenv,'checks')
commands['doc-impact']=([sys.executable,'-B',str(package/'scripts/doc_impact.py'),base,head,'--json'],gitenv,'checks')
commands['dispatch-records']=([sys.executable,'-B',str(package/'scripts/dispatch_records.py'),str(task)],normalenv,'checks')
def run(item):
    name,(command,env,group)=item
    result=subprocess.run(command,cwd=export,env=env,capture_output=True,text=True,timeout=240)
    log=out/(name.replace('/','__')+'.log')
    text=result.stdout+result.stderr;log.write_text(text)
    tests=re.search(r'Ran (\d+) tests?',text); skips=re.search(r'skipped=(\d+)',text)
    return dict(name=name,status='passed' if result.returncode==0 else 'failed',exit=result.returncode,tests=int(tests[1]) if tests else None,skipped=int(skips[1]) if skips else 0,command=command,log=str(log),group=group)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,commands.items()))
(out/'all-checks.json').write_text(json.dumps(results,indent=2)+'\n')
for group in ['package','checks']:
    selected=[x for x in results if x['group']==group]
    (out/(group+'-results.json')).write_text(json.dumps(selected,indent=2)+'\n')
    print(json.dumps(dict(group=group,commands=len(selected),failed=[x['name'] for x in selected if x['exit']],tests=sum(x['tests'] or 0 for x in selected),skipped=sum(x['skipped'] for x in selected))))
sys.exit(any(x['exit'] for x in results))
