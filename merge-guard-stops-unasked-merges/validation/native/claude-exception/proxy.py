import sys,subprocess,json
from pathlib import Path
payload=sys.stdin.read()
r=subprocess.run('python3 /tmp/validate-merge-guard-871c6b2-z7onrnpk/native/claude-exception/exception.py claude || exit 2',shell=True,input=payload,capture_output=True,text=True)
with Path('/tmp/validate-merge-guard-871c6b2-z7onrnpk/native/claude-exception/hook.jsonl').open("a") as f:f.write(json.dumps({"payload":json.loads(payload),"stdout":r.stdout,"stderr":r.stderr,"exit":r.returncode})+"\n")
sys.stdout.write(r.stdout);sys.stderr.write(r.stderr);sys.exit(r.returncode)
