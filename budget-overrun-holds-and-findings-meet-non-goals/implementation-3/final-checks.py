import concurrent.futures, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path
root=Path(sys.argv[1]);out=Path('/tmp/budget-worth-repair/final');out.mkdir(parents=True,exist_ok=True)
workflow=(root/'.github/workflows/kc-dev-flow-2-tests.yml').read_text()
paths=re.findall(r'run: (?:SPACEDOCK_BIN="[^\n]+?" )?python3 (kc-dev-flow-2/[^\s]+\.py)',workflow)
assert len(paths)==len(set(paths))
patch=subprocess.check_output(['git','-C',str(root),'diff','--binary','e8664a72b0f904e5dda3c391d52ab3abaca876b4'])
(out/'tested.patch').write_bytes(patch)
identity=dict(base='e8664a72b0f904e5dda3c391d52ab3abaca876b4',head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),patch_sha256=hashlib.sha256(patch).hexdigest(),spacedock=subprocess.check_output(['/Users/kent/.local/bin/spacedock','--version'],text=True).strip())
(out/'test-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
commands=[]
for path in paths:
    command=['python3','-B',str(root/path)]
    if path.endswith('test_sd_dispatch.py'):command += ['--sd-plugin-root','/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
    commands.append((path,command))
def run(item):
    path,command=item;log=out/(path.replace('/','__')+'.log');start=time.monotonic()
    with log.open('w') as stream:
        result=subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock','PYTHONDONTWRITEBYTECODE':'1'})
    return dict(name=path,status='passed' if result.returncode==0 else 'failed',exit=result.returncode,seconds=round(time.monotonic()-start,3),command=command,log=str(log))
priority=['test_dispatch_stage.py','test_laws_check.py','test_dispatch_records.py','test_delivery_gate.py','test_learning.py','test_role_triggers.py','test_pr_watch.py','test_sd_dispatch.py']
commands.sort(key=lambda item: priority.index(Path(item[0]).name) if Path(item[0]).name in priority else len(priority))
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    futures=[pool.submit(run,c) for c in commands]
    for future in concurrent.futures.as_completed(futures):
        row=future.result();rows.append(row)
        (out/'full-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(row['name'],row['exit'],flush=True)
assert patch==subprocess.check_output(['git','-C',str(root),'diff','--binary','e8664a72b0f904e5dda3c391d52ab3abaca876b4']),'product changed during checks'
sys.exit(any(r['exit'] for r in rows))
