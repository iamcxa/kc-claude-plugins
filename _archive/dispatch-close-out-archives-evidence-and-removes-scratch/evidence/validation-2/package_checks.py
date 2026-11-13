import json, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
w=pathlib.Path(sys.argv[1]); e=pathlib.Path(__file__).resolve().parent; t=pathlib.Path(sys.argv[2]); s=pathlib.Path(sys.argv[3]);p=pathlib.Path(sys.argv[4])
slug='dispatch-close-out-archives-evidence-and-removes-scratch'; base='8ce0eb6050c889b21baccf50fec35231bc888d66';head='d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6'; workflow=s.parent
jobs=[('adr-lint',[sys.executable,'-B',str(p/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0079'],w),('skill-lint',[sys.executable,'-B','kc-dev-flow-2/scripts/lint-skills.py'],t/'candidate'),('design-surfaces',[sys.executable,'-B',str(p/'scripts/design_surfaces.py'),'check',str(s/(slug+'.md'))],w),('dispatch-record-check',[sys.executable,'-B',str(p/'scripts/dispatch_records.py'),str(s/slug)],w),('comment-ratio',[sys.executable,'-B',str(p/'scripts/comment_ratio.py'),base,head,'--repo',str(w),'--workflow-dir',str(workflow)],w),('doc-impact',[sys.executable,'-B',str(p/'scripts/doc_impact.py'),base,head,'--repo',str(w),'--json'],w),('number-guards',[sys.executable,'-B',str(p/'scripts/number_guards.py'),'check','--repo',str(w),'--workflow-dir',str(workflow),'--task',str(s/(slug+'.md')),'--head',head,'--base',base],w)]
def run(job):
 name,command,cwd=job
 with (e/(name+'.log')).open('w') as f:done=subprocess.run(command,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 return {'name':name,'command':command,'cwd':str(cwd),'exit':done.returncode}
with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(run,jobs))
(e/'required-checks.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
