from pathlib import Path
import os,subprocess,json
s=Path("/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/validation-2"); wt=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pilot-ideation-runs-a-probe-before-the-design"); state=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
for n in ('tmp','evidence','candidate'): (s/n).mkdir(exist_ok=True)
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1',GIT_AUTHOR_NAME='Validation fixture',GIT_AUTHOR_EMAIL='validation@localhost',GIT_COMMITTER_NAME='Validation fixture',GIT_COMMITTER_EMAIL='validation@localhost')
for name,cmd in [('code-fixture',['git','clone','--bare','--no-hardlinks',str(wt),str(s/'code.git')]),('state-fixture',['git','clone','--no-hardlinks',str(state),str(s/'state')])]:
 with (s/'evidence'/f'{name}.log').open('w') as out: subprocess.run(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
head='45d5ebb9d24665c0904aca5412123a7224d056cc';base='88f86f2749dadb6f4ef0cf9aa089c1827096865b'
data=subprocess.check_output(['git','-C',str(wt),'archive',head])
subprocess.run(['tar','-x','-C',str(s/'candidate')],input=data,check=True)
subprocess.run(['git','--git-dir='+str(s/'code.git'),'read-tree',head],check=True)
(s/'adopter-README.md').write_bytes(subprocess.check_output(['git','-C',str(wt),'show',base+':docs/dev2/README.md']))
(s/'evidence/refs.json').write_text(json.dumps(dict(candidate=head,base=base,prior='f0e00d30ce00542b2895f13173bd41075cc8bfd4'),indent=2)+'\n')
print('Fixtures and candidate export ready.')

