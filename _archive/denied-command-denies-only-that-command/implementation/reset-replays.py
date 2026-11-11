from pathlib import Path
import subprocess,json
out=Path('/tmp/denied-command-evidence'); m=json.loads((out/'pins.json').read_text())
names=['release-sol-1','candidate-sol-1','candidate-sol-2','release-astra-1','candidate-astra-1','candidate-astra-2','control-sol-1','candidate-claude-1']
for name in names:
 p=Path('/tmp/denied-replay-'+name); meta=json.loads((p/'replay.json').read_text())
 assert meta['state_repo']==m['state_repo'] and meta['code_repo']==m['code_repo']
 assert Path(meta['state']).resolve()==(p/'wf/.spacedock-state').resolve() and Path(meta['code']).resolve()==(p/'code').resolve()
for name in names:
 p=Path('/tmp/denied-replay-'+name)
 q=subprocess.run(['python3','-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/replay_dispatch.py','cleanup','--run-dir',str(p)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True); print(q.stdout.strip(),flush=True)
 if q.returncode: raise SystemExit(q.returncode)
m['state_commit']='f3210a9de759b66294459f29ba7597fc408b7b0a'; (out/'pins.json').write_text(json.dumps(m,indent=2))
(out/'scope.txt').write_text('Before the ideation analysis, read the repository code with git -C <repo> show origin/main:<path> after git -C <repo> fetch origin, where <repo> is this replay run directory\'s code checkout. On Codex, request native approval for that network fetch with sandbox_permissions=require_escalated; run the fetch by itself. Use the pinned local code for all other inspection. No application suites, remote writes, PRs, or product implementation.\n')
p=out/'build-replays.py'; text=p.read_text().replace("runs=[('candidate-sol-1'","runs=[('release-sol-1',m['release']),('candidate-sol-1'")
text=text.replace("Path(run+'/dispatch.md').write_text(Path(json.loads(q.stdout)['dispatch_file_path']).read_text())","data=json.loads(q.stdout[q.stdout.index('{'):]); Path(run+'/dispatch.md').write_text(Path(data['dispatch_file_path']).read_text())")
p.write_text(text)
