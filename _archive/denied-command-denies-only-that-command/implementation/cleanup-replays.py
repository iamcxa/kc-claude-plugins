from pathlib import Path
import json,subprocess
out=Path('/tmp/denied-command-evidence'); pins=json.loads((out/'pins.json').read_text())
names=['release-sol-1','candidate-sol-1','candidate-sol-2','release-astra-1','candidate-astra-1','candidate-astra-2','control-sol-1','candidate-claude-1','candidate-steer-sol-1']
for name in names:
 p=Path('/tmp/denied-replay-'+name); saved=out/'replays'/name/'replay.json'; assert saved.is_file() and saved.read_bytes()==(p/'replay.json').read_bytes(); meta=json.loads(saved.read_text()); assert meta['state_repo']==pins['state_repo'] and meta['code_repo']==pins['code_repo']; assert Path(meta['state']).resolve()==(p/'wf/.spacedock-state').resolve() and Path(meta['code']).resolve()==(p/'code').resolve()
for name in names:
 p=subprocess.run(['python3','-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/replay_dispatch.py','cleanup','--run-dir','/tmp/denied-replay-'+name],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True); print(p.stdout.strip(),flush=True)
 if p.returncode: raise SystemExit(p.returncode)
