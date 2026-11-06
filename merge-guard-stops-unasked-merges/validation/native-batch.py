import subprocess,concurrent.futures
cases=[('claude-match','claude','match'),('codex-rules','codex','rules'),('codex-match','codex','match'),('claude-missing','claude','missing'),('claude-exception','claude','exception'),('claude-unreadable','claude','unreadable'),('codex-missing','codex','missing'),('codex-exception','codex','exception'),('codex-unreadable','codex','unreadable'),('claude-no-wrapper','claude','no-wrapper')]
def run(case):
 r=subprocess.run(['python3','-B','/tmp/validate-merge-guard-871c6b2-z7onrnpk/merge-guard-native-run.py',*case],capture_output=True,text=True)
 return r.stdout+r.stderr
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for output in pool.map(run,cases):print(output,flush=True)
