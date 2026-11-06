import concurrent.futures,subprocess
cases=[('final-claude-match', 'claude', 'match'), ('final-codex-match', 'codex', 'match'), ('final-claude-host', 'claude', 'host'), ('final-codex-host', 'codex', 'host'), ('final-claude-repo', 'claude', 'repo'), ('final-codex-repo', 'codex', 'repo'), ('final-claude-api', 'claude', 'api'), ('final-codex-api', 'codex', 'api')]
def run(c):
 r=subprocess.run(["python3","-B","/tmp/merge-guard-repair-final-native-run.py",*c],capture_output=True,text=True)
 return r.stdout+r.stderr
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
 for result in p.map(run,cases):print(result,flush=True)
