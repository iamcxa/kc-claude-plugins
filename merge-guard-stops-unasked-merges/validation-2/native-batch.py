from pathlib import Path
import subprocess, sys, concurrent.futures
out=Path('/tmp/merge-guard-validation-b82f20de/evidence')
cases=[(h+'-'+m,h,m) for h in ('claude','codex') for m in ('match','missing','exception','unreadable','auto','async','nomatch','api','graphql')]
cases += [('codex-rules','codex','rules'),('claude-no-wrapper','claude','no-wrapper')]
def run(case):
 r=subprocess.run([sys.executable,'-B',str(out/'native-run.py'),*case],capture_output=True,text=True)
 print(r.stdout.strip() or r.stderr.strip(),flush=True)
 return r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 results=list(pool.map(run,cases))
sys.exit(1 if any(results) else 0)
