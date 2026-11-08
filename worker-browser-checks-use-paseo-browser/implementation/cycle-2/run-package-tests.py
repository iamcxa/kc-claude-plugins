import concurrent.futures,json,os,re,subprocess,sys
from pathlib import Path
repo,out,sdroot,binary=sys.argv[1:]
repo=Path(repo); out=Path(out); (out/"package-logs").mkdir(exist_ok=True)
paths=re.findall(r'run: (?:SPACEDOCK_BIN="[^"]+" )?python3 (kc-dev-flow-2/[^\s]+\.py)',(repo/".github/workflows/kc-dev-flow-2-tests.yml").read_text())
assert paths and len(paths)==len(set(paths))
env={**os.environ,"SPACEDOCK_BIN":binary,"PYTHONDONTWRITEBYTECODE":"1"}
def run(path):
    command=[sys.executable,"-B",str(repo/path)]
    if path.endswith("/test_sd_dispatch.py"):
        command+=["--sd-plugin-root",sdroot]
    log=out/"package-logs"/(path.replace("/","__")+".log")
    try:
        with log.open("w") as f:
            done=subprocess.run(command,cwd=repo,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
        code=done.returncode
    except subprocess.TimeoutExpired:
        code=124
    text=log.read_text()
    count=re.search(r"Ran (\d+) tests? in",text)
    skip=re.search(r"OK \(skipped=(\d+)\)",text)
    result={"name":path,"status":"passed" if code==0 else "failed","exit":code,"tests":int(count[1]) if count else None,"skipped":int(skip[1]) if skip else 0,"log":str(log),"command":command}
    print(json.dumps({"name":path,"exit":code}),flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(run,paths))
(out/"package-tests.json").write_text(json.dumps(results,indent=2)+"\n")
summary={"commands":len(results),"failed":sum(x["exit"]!=0 for x in results),"unittest_cases":sum(x["tests"] or 0 for x in results),"optional_skips":sum(x["skipped"] for x in results),"sd_plugin_root":sdroot,"spacedock_bin":binary}
(out/"package-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary),flush=True)
sys.exit(1 if summary["failed"] else 0)

