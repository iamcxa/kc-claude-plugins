"""Four observable steps, local throwaways only. Args: CODE STATE SPACEDOCK SCRATCH."""
from pathlib import Path
import json,os,subprocess,sys,tempfile
code,state,binary,scratch=map(lambda p:Path(p).resolve(),sys.argv[1:])
head='d2d5bec640f0a61d3e044877b8443cdfdc03faa7'
base='c2f035b6612f5edb42220576b3414e993531ffd6'
task=state/'state-branch-writes-carry-no-private-identifiers'
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import scratch as scratch_api
assert scratch_api.root_for(task,task,'validation-1').resolve()==scratch, 'wrong scratch root'
scratch_api.claim_root(task,task,'validation-1')
summary=[]
with tempfile.TemporaryDirectory(prefix='captain-check-',dir=scratch) as name:
    run=Path(name)
    env={**os.environ,'TMPDIR':str(run),'SPACEDOCK_BIN':str(binary),'PYTHONDONTWRITEBYTECODE':'1'}
    def command(argv):
        p=subprocess.run(list(map(str,argv)),cwd=code,env=env,capture_output=True,text=True)
        if p.returncode:
            print('FAIL: command exit '+str(p.returncode))
            print((p.stdout+p.stderr).replace(str(Path.home()),'~'))
            raise SystemExit(p.returncode)
        return p.stdout.strip()
    assert command(['git','-C',code,'rev-parse','HEAD'])==head, 'candidate changed'
    assert command(['git','-C',code,'status','--porcelain'])=='', 'candidate worktree dirty'
    print('1 PASS: exact candidate and clean product worktree',flush=True)
    command([sys.executable,'-B',task/'evidence/implementation-1/acceptance.py',code,state,binary,run/'writers'])
    print('2 PASS: real dispatch and sealed remote bytes; compatibility unchanged with one known old digest mismatch',flush=True)
    command([sys.executable,'-B',task/'evidence/implementation-1/repair-1864/acceptance.py',code,run/'hooks'])
    print('3 PASS: refused and accepted pushes, repaired diff/path cases, unguarded detection and mode isolation',flush=True)
    command([sys.executable,'-B',code/'kc-dev-flow-2/scripts/adr_lint.py','docs/adr','--since',base,'--require','0087'])
    print('4 PASS: required decision record; throwaways removed on exit',flush=True)
