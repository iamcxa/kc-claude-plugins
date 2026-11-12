from pathlib import Path
import json,os,shlex,subprocess,time,shutil
scratch=Path('/tmp/validate-853-20261112-1752')
evidence=Path(__file__).parent
repo='/tmp/validate-853-20261112-1752/objects.git'
command=next(l[len('merge-test: '):] for l in (scratch/'cost/README.md').read_text().splitlines() if l.startswith('merge-test: '))
args=['python3','-B',str(scratch/'candidate/kc-dev-flow-2/scripts/delivery_gate.py'),'merge-run',str(scratch/'cost/task.md'),'--pr','iamcxa/kc-claude-plugins#853','--head','d79053d0836c558a9269f9cf1ba222933935b820','--trunk','8ce0eb6050c889b21baccf50fec35231bc888d66','--workflow-dir',str(scratch/'cost'),'--repo-dir',repo,'--',*shlex.split(command)]
start=time.monotonic()
with (evidence/'cost-command.log').open('w') as out:
 done=subprocess.run(args,env=dict(os.environ,TMPDIR=str(scratch/'tmp'),PYTHONDONTWRITEBYTECODE='1'),stdout=out,stderr=subprocess.STDOUT)
elapsed=time.monotonic()-start
for f in (scratch/'cost/task/merge').glob('*'):shutil.copy(f,evidence/('cost-'+f.name))
(evidence/'cost.json').write_text(json.dumps({'command':command,'exit':done.returncode,'seconds':elapsed,'runs':1,'head':'d79053d0836c558a9269f9cf1ba222933935b820','trunk':'8ce0eb6050c889b21baccf50fec35231bc888d66'},indent=2)+'\n')
print('cost command finished',done.returncode,round(elapsed,2),flush=True)
raise SystemExit(done.returncode)
