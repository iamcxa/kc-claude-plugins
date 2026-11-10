import argparse,concurrent.futures,json,os,re,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);p.add_argument('--sd-root',type=Path,required=True);p.add_argument('--sd-bin',type=Path,required=True);a=p.parse_args()
w=a.candidate;out=a.out;out.mkdir(parents=True,exist_ok=True)
files=re.findall(r'python3 (kc-dev-flow-2/[^\s]+\.py)',(w/'.github/workflows/kc-dev-flow-2-tests.yml').read_text())
env={**os.environ,'SPACEDOCK_BIN':str(a.sd_bin),'PYTHONDONTWRITEBYTECODE':'1'}
def run(file):
 name=file.replace('/','_');cmd=[sys.executable,'-B',file]
 if file.endswith('test_sd_dispatch.py'):cmd+=['--sd-plugin-root',str(a.sd_root)]
 p=out/(name+'.log')
 try:
  with p.open('w') as f:r=subprocess.run(cmd,cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
  text=p.read_text();counts=re.findall(r'Ran (\d+) tests?',text)
  result={'name':file,'status':'passed' if r.returncode==0 else 'failed','exit':r.returncode,'tests':int(counts[-1]) if counts else None,'log':str(p)}
 except subprocess.TimeoutExpired:result={'name':file,'status':'failed','message':'900s timeout','log':str(p)}
 print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(run,files))
(out/'tests.json').write_text(json.dumps(results,indent=2)+'\n')
sys.exit(int(any(r['status']=='failed' for r in results)))
