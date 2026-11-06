import sys,subprocess,json
from pathlib import Path
payload=sys.stdin.read()
r=subprocess.run('python3 /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges/kc-dev-flow-2/scripts/merge_guard.py claude || exit 2',shell=True,input=payload,capture_output=True,text=True)
with Path('/tmp/merge-guard-repair-final-native/final-claude-graphql/hook.jsonl').open("a") as f:f.write(json.dumps({"payload":json.loads(payload),"stdout":r.stdout,"stderr":r.stderr,"exit":r.returncode})+"\n")
sys.stdout.write(r.stdout);sys.stderr.write(r.stderr);sys.exit(r.returncode)
