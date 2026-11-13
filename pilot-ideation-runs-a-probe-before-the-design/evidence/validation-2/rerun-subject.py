from pathlib import Path
import os,subprocess,shutil,json
s=Path(__file__).parent; rows=[]
for arm in ['positive','negative']:
 root=s/('AC-8-rerun-'+arm);root.mkdir();(root/'tmp').mkdir();(root/'evidence').mkdir()
 env=dict(os.environ,TMPDIR=str(root/'tmp'),REPLAY_ROOT=str(root),PYTHONDONTWRITEBYTECODE='1')
 with (s/'evidence'/('AC-8-'+arm+'-setup.log')).open('w') as log:
  subprocess.run(['git','clone','--no-hardlinks',str(s/'code.git'),str(root/'code')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['git','-C',str(root/'code'),'checkout','--detach','88f86f2749dadb6f4ef0cf9aa089c1827096865b'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 shutil.copytree(s/'candidate/kc-dev-flow-2',root/'package/kc-dev-flow-2')
 (root/'code/.replay').mkdir()
 shutil.copyfile(s/'live/evidence/pr_watch_probe.py',root/'code/.replay/pr_watch_probe.py')
 if arm=='negative':
  p=root/'package/kc-dev-flow-2/scripts/pr_watch.py'
  text=p.read_text();old='out.append(f"fact: {slug} has no recorded PR; its worktree is not on this machine.")'
  assert text.count(old)==1
  p.write_text(text.replace(old,'out.append(f"next: record {slug} PR; its worktree is not on this machine.")'))
 for criterion in (['AC-1','AC-2','AC-3','AC-4'] if arm=='positive' else ['AC-1']):
  cmd=['python3','-B',str(root/'code/.replay/pr_watch_probe.py'),criterion]
  name='AC-8-'+arm+'-'+criterion
  with (s/'evidence'/f'{name}.log').open('w') as log:r=subprocess.run(cmd,cwd=root/'code',env=env,stdout=log,stderr=subprocess.STDOUT)
  rows.append(dict(arm=arm,criterion=criterion,command=cmd,exit=r.returncode,expected_exit=0 if arm=='positive' else 1,output=f'{name}.log'))
  print(name,r.returncode,flush=True)
  if arm=='positive' and r.returncode:break
 shutil.copytree(root/'evidence',s/'evidence'/('AC-8-'+arm),dirs_exist_ok=True)
(s/'evidence/AC-8-independent-results.json').write_text(json.dumps(rows,indent=2)+'\n')

