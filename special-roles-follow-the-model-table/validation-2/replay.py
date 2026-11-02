import importlib.util, subprocess, json, re, tempfile, hashlib
from pathlib import Path
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-8eed70b2')
STATE=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
BASE='146727ded0d4ce8014ea0b41a45dc3409d6b269b'
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence-8eed70b2')
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True)
def module(name,source):
 ns={'__name__':name};exec(compile(source,name,'exec'),ns);return ns
old=module('base',git(WT,'show',BASE+':kc-dev-flow-2/scripts/role_triggers.py'))
source=(WT/'kc-dev-flow-2/scripts/role_triggers.py').read_text()
new=module('candidate',source)
rev=git(STATE,'rev-parse','HEAD').strip(); paths=git(STATE,'ls-tree','-r','--name-only',rev).splitlines()
rows=[];changes=[]
for path in paths:
 if not path.endswith('.md'):continue
 text=git(STATE,'show',f'{rev}:{path}')
 if not re.match(r'---\n.*?\nstatus:',text,re.S):continue
 parts=Path(path).parts
 if len(parts)>2 or len(parts)==2 and parts[0]!='_archive' and parts[1]!='index.md':continue
 slug=Path(path).stem if not path.endswith('/index.md') else parts[-2]
 a=old['check'](STATE,slug,rev);b=new['check'](STATE,slug,rev)
 rows.append({'path':path,'base':a[0],'candidate':b[0]})
 if a[0]!=b[0]:changes.append(rows[-1])
print('State',rev,'candidate role_triggers SHA256',hashlib.sha256(source.encode()).hexdigest())
print('History',len(rows),'task files;',len(changes),'changed exit results',changes)
assert not changes
actual=git(STATE,'show',rev+':_archive/peers-paseo-rule-matches-practice.md')
no_waiver=re.sub(r'^Reviewer: kc-dev-flow-2:engineering-reviewer not run 2026-11-01:.*\n','',actual,flags=re.M)
assert no_waiver!=actual
with tempfile.TemporaryDirectory(prefix='peer-policy-replay-') as d:
 repo=Path(d);subprocess.run(['git','init','-q','-b','main',d],check=True)
 env=['git','-C',d,'-c','user.name=fixture','-c','user.email=fixture@example.invalid']
 f=repo/'peers-paseo-rule-matches-practice.md';f.write_text(no_waiver)
 subprocess.run(env+['add',f.name],check=True);subprocess.run(env+['commit','-qm','Astra without waiver'],check=True)
 a=old['check'](repo,f.stem,'HEAD');b=new['check'](repo,f.stem,'HEAD')
 print('Real peer policy without waiver: base',a[0],'candidate',b[0]);assert (a[0],b[0])==(1,0)
 f.write_text(no_waiver.replace('gpt-6-astra','gpt-6.1-sol'))
 subprocess.run(env+['add',f.name],check=True);subprocess.run(env+['commit','-qm','Sol falsifier'],check=True)
 c=new['check'](repo,f.stem,'HEAD');print('AC3 Sol mutation:',c[0]);assert c[0]==1
(E/'replay-results.json').write_text(json.dumps({'state':rev,'rows':rows,'changes':changes},indent=2))
