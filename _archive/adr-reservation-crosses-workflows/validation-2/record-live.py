from pathlib import Path
import hashlib,json,subprocess
o=Path('/tmp/adr-reservation-validation-801-r2')
repo=o/'live.git'
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'adr-reservation-crosses-workflows.md'
g=lambda *args: subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
log=(o/'live-number-check.log').read_text()
assert 'PASS: no findings' in log and 'state fetch failed' not in log
refs=[]
for line in g('for-each-ref','--format=%(refname:short) %(objectname)','refs/remotes/origin/spacedock-state/').splitlines():
 ref,sha=line.split()
 paths=g('ls-tree','-r','--name-only',sha).splitlines()
 paths=[p for p in paths if (p.endswith('.md') and '/' not in p) or (p.endswith('/index.md') and p.count('/')==1)]
 refs.append({'ref':ref,'sha':sha,'paths':paths})
own=[p for p in sorted([*state.glob('*.md'),*state.glob('*/index.md')]) if p.is_file() and p.resolve()!=task.resolve()]
result={'candidate':'ef3ed3e05534e2a997acbdfb055a880fde1f484a','base':'ba055b8a7a55a787ac989c4cef52d07dd75661ad',
 'on_disk_state':str(state),'on_disk_paths':[str(p) for p in own],'on_disk_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in own},
 'remote_refs':refs,'remote_paths_count':sum(len(r['paths']) for r in refs),'note':'Remote refs are isolated successful-fetch snapshots; own disk paths enumerated immediately after run, mutable shared state.'}
(o/'live-read-set.json').write_text(json.dumps(result,indent=2))
print('PASS live check; own paths',len(own),'remote refs',len(refs),'remote paths',result['remote_paths_count'])
