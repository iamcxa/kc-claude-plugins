import sys,os,subprocess,json,time
from pathlib import Path
s=Path(__file__).parent
name=sys.argv[1]; cmd=sys.argv[2:]
env={**os.environ,'TMPDIR':str(s/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
start=time.time()
with (s/'logs'/f'{name}.log').open('w') as f:
 p=subprocess.run(cmd,cwd=s/'candidate',env=env,stdout=f,stderr=subprocess.STDOUT)
r={'name':name,'command':cmd,'exit':p.returncode,'seconds':round(time.time()-start,2),'log':f'logs/{name}.log'}
(s/'logs'/f'{name}.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
print((s/'logs'/f'{name}.log').read_text()[-1600:])
sys.exit(p.returncode)
