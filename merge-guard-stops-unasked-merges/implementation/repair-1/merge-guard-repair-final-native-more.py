import concurrent.futures,subprocess
cases=[('final-claude-missing','claude','missing'),('final-claude-exception','claude','exception'),('final-claude-unreadable','claude','unreadable'),('final-codex-missing','codex','missing'),('final-codex-exception','codex','exception'),('final-codex-unreadable','codex','unreadable'),('final-claude-no-wrapper','claude','no-wrapper'),('final-codex-rules','codex','rules'),('final-claude-env','claude','env'),('final-codex-command','codex','command'),('final-claude-graphql','claude','graphql'),('final-codex-graphql','codex','graphql')]
def run(c):
 r=subprocess.run(['python3','-B','/tmp/merge-guard-repair-final-native-run.py',*c],capture_output=True,text=True)
 return r.stdout+r.stderr
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(run,cases):print(result,flush=True)
