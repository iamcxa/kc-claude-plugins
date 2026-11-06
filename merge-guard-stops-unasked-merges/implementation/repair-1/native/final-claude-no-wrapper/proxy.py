import sys,subprocess,json
from pathlib import Path
payload=sys.stdin.read()
r=subprocess.run('python3 /tmp/merge-guard-repair-final-native/final-claude-no-wrapper/exit1.py claude',shell=True,input=payload,capture_output=True,text=True)
with Path('/tmp/merge-guard-repair-final-native/final-claude-no-wrapper/hook.jsonl').open("a") as f:f.write(json.dumps({"payload":json.loads(payload),"stdout":r.stdout,"stderr":r.stderr,"exit":r.returncode})+"\n")
sys.stdout.write(r.stdout);sys.stderr.write(r.stderr);sys.exit(r.returncode)
