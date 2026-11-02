import importlib.util, subprocess, json, re, tempfile, hashlib
from pathlib import Path
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87')
STATE=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
BASE='c129cb215c2630d08853eeffae0fd5a2ee7e40c6'
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence')
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True)
def module(name,source):
 ns={'__name__':name};exec(compile(source,name,'exec'),ns);return ns
old=module('base',git(WT,'show',BASE+':kc-dev-flow-2/scripts/role_triggers.py'))
source=(WT/'kc-dev-flow-2/scripts/role_triggers.py').read_text()
new=module('candidate',source)
rev='fbf834f07625a7ce05a9393bc64aaa1b6cfe83d8'; paths=git(STATE,'ls-tree','-r','--name-only',rev).splitlines()
rows=[];changes=[]
for path in paths:
 if not path.endswith('.md'):continue
 text=git(STATE,'show',f'{rev}:{path}')
 if not re.match(r'---\n.*?\nstatus:',text,re.S):continue
 parts=Path(path).parts
 if len(parts)>2 or len(parts)==2 and parts[0]!='_archive' and parts[1]!='index.md':continue
 slug=Path(path).stem if not path.endswith('/index.md') else parts[-2]
 a=old['check'](STATE,slug,rev);b=new['check'](STATE,slug,rev)
 rows.append({'path':path,'base':a[0],'candidate':b[0],'base_output':a[1],'candidate_output':b[1]})
 if a!=b:changes.append(rows[-1])
print('State',rev,'candidate role_triggers SHA256',hashlib.sha256(source.encode()).hexdigest())
print('History',len(rows),'task files;',len(changes),'changed messages; changed exits',sum(r['base']!=r['candidate'] for r in rows))
print('Changed paths:',[r['path'] for r in changes])

(E/'replay-messages.json').write_text(json.dumps({'state':rev,'rows':rows,'changes':changes},indent=2))
