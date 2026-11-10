import json, os, re, subprocess, sys
from pathlib import Path
out = Path('/tmp/opencode/issue815-validation')
root = out / 'candidate'
state = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
impl = state / 'issue-815-fo-record-gaps/implementation'
summary = json.loads((impl / 'suite-summary.json').read_text())
env = {k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
env.update(PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
(out / 'suite').mkdir(exist_ok=True)
results=[]
for entry in summary['tests']:
    name=entry['name']; cmd=[sys.executable,'-B',name]
    if name.endswith('/test_sd_dispatch.py'):
        cmd += ['--sd-plugin-root','/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3']
    log=out/'suite'/(name.replace('/','_')+'.log')
    with log.open('w') as f:
        r=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text(); counts=re.findall(r'Ran (\d+) tests?',text); skips=re.findall(r'skipped=(\d+)',text)
    item=dict(name=name,command=cmd,status='passed' if r.returncode==0 else 'failed',exit=r.returncode,tests=int(counts[-1]) if counts else None,skipped=int(skips[-1]) if skips else 0,log=str(log))
    results.append(item)
    (out/'suite-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(item),flush=True)
sys.exit(any(x['exit'] for x in results))
