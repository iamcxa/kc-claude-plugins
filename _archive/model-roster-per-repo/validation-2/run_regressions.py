import concurrent.futures, json, os, pathlib, re, subprocess, time
root=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo/.validation-2')
out=pathlib.Path('/tmp/roster-validation2-a8536dc5')
paths=re.findall(r'run: python3 (kc-dev-flow-2/\S+\.py)\s*\n', (root/'.github/workflows/kc-dev-flow-2-tests.yml').read_text())
paths += ['kc-dev-flow-2/scripts/test_observer_recovery.py']
def run(path):
 env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/tmp', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
 t=time.monotonic(); p=subprocess.run(['python3','-B',path],cwd=root,env=env,capture_output=True,text=True)
 log=out/(pathlib.Path(path).stem+'.log'); log.write_text(p.stdout+p.stderr)
 r=dict(path=path,exit=p.returncode,seconds=round(time.monotonic()-t,3),log=str(log)); print(json.dumps(r),flush=True); return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,paths))
(out/'regressions.json').write_text(json.dumps(results,indent=2))
raise SystemExit(any(r['exit'] for r in results))
