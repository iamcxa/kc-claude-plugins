import subprocess,concurrent.futures
cases=[('claude-match','claude','match'),('codex-deny','codex','nomatch'),('codex-rules','codex','rules'),('codex-match','codex','match'),('claude-missing','claude','missing'),('claude-exception','claude','exception'),('claude-unreadable','claude','unreadable'),('codex-missing','codex','missing'),('codex-exception','codex','exception'),('codex-unreadable','codex','unreadable'),('claude-no-wrapper','claude','no-wrapper'),('claude-api','claude','api'),('codex-api','codex','api'),('claude-graphql','claude','graphql'),('codex-graphql','codex','graphql'),('claude-env','claude','env'),('codex-command','codex','command')]
def run(case):
 r=subprocess.run(['python3','-B','/tmp/merge-guard-repair-native-run.py',*case],capture_output=True,text=True)
 return r.stdout+r.stderr
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for output in pool.map(run,cases):print(output,flush=True)
