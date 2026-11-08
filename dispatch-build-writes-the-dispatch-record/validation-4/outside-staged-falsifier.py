from pathlib import Path
import json,shutil,subprocess,os,tempfile
root=Path('/tmp/pr812-validation4.Lmnx4p/candidate')
out=Path('/tmp/pr812-validation4.Lmnx4p')
with tempfile.TemporaryDirectory(prefix='pr812-outside-index-mutant-') as d:
 target=Path(d)/'kc-dev-flow-2'
 shutil.copytree(root/'kc-dev-flow-2',target)
 p=target/'scripts/dispatch_stage.py'
 src=p.read_text()
 old='            return path, False'
 assert src.count(old)==1
 p.write_text(src.replace(old,'            git(state, "add", "-A")\n'+old))
 r=subprocess.run(['python3','-B',str(target/'scripts/test_dispatch_stage.py'),'DispatchStageTests.test_real_builder_allowed_routes_preserve_other_tasks'],env=dict(os.environ,SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
 output=r.stdout+r.stderr
 (out/'outside-staged-falsifier.log').write_text(output)
 caught=r.returncode!=0 and 'FAIL:' in output and 'outside_snapshot' in output
 (out/'outside-staged-falsifier.json').write_text(json.dumps(dict(name='retry-stages-outside-scope',status='passed' if caught else 'failed',exit=r.returncode,mutation='Stage whole state repository immediately before reusing committed record',oracle='outside index and worktree snapshots must match'),indent=2)+'\n')
 assert caught
 print('outside-scope staging mutant caught')
