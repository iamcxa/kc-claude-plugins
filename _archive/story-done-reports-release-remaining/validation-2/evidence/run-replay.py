from pathlib import Path
import subprocess,json,os
out=Path('/tmp/story-release-validation-2')
for name,map in [('relay','spacedock-review.yaml'),('qnow','qnow.yaml')]:
 p=subprocess.run(['node',str(out/'base/kc-journey-map/lib/journey-progress.mjs'),str(out/'replays'/name/'docs/journey'/map),'--workflow-dir',str(out/'replays'/name/'docs/dev2')],capture_output=True,text=True,timeout=100)
 (out/(name+'-base.json')).write_text(p.stdout);(out/(name+'-base.stderr')).write_text(p.stderr)
 assert json.loads(p.stdout)['diagnostic'] is None,(p.returncode,p.stderr,p.stdout[:500])
print('both old reader snapshots collected',flush=True)
p=subprocess.run(['python3','-B',str(out/'scripts/replay_progress.py')],env={**os.environ,'EVIDENCE_ROOT':str(out),'PRODUCT_WT':str(out/'candidate'),'DEV2_WT':str(out/'candidate')})
raise SystemExit(p.returncode)
