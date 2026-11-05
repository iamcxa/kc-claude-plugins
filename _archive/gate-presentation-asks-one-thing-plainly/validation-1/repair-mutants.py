import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
wt,out=map(Path,sys.argv[1:])
source=wt/"kc-dev-flow-2/scripts"
cases=[
 ("withdrawn-rows-restored",'    rows = [r for r in rows if r["attempt"] not in withdrawn]\n',""),
 ("withdrawn-treated-as-pre-ask",'pending = not answered and latest_attempt not in withdrawn','pending = not answered'),
 ("missing-grant-falls-back-to-merge",'ask = ASK if pending or captain and decision_ledger.quotes_bound_question(\n        max(captain, key=lambda r: r["at"] or "")) else ASK_UNQUOTED',
  'ask = ASK_UNQUOTED if answered and captain and not decision_ledger.quotes_bound_question(\n        max(captain, key=lambda r: r["at"] or "")) else ASK')
]
results=[]
with tempfile.TemporaryDirectory(prefix="withdrawal-falsifier-") as tmp:
    scripts=Path(tmp,"kc-dev-flow-2/scripts")
    shutil.copytree(source,scripts,ignore=shutil.ignore_patterns("__pycache__"))
    path=scripts/"delivery_gate.py"
    original=path.read_text()
    for name,old,new in cases:
        assert original.count(old)==1,(name,original.count(old))
        path.write_text(original.replace(old,new))
        for cache in scripts.rglob("__pycache__"):
            shutil.rmtree(cache)
        done=subprocess.run([sys.executable,"-B","-m","unittest","discover","-s",str(scripts),"-p","test_delivery_gate.py","-k","BoundApprovalTests"],
                            capture_output=True,text=True,cwd=tmp,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        log=out/(name+".log");log.write_text(done.stdout+done.stderr)
        caught=done.returncode==1 and "FAIL:" in done.stderr and "ERROR:" not in done.stderr
        results.append({"name":name,"caught":caught,"exit":done.returncode,"log":str(log)})
        assert caught,(name,done.stdout,done.stderr)
        path.write_text(original)
(out/"mutations.json").write_text(json.dumps(results,indent=2))
print(json.dumps({"mutations":len(results),"caught":sum(r["caught"] for r in results)}))
