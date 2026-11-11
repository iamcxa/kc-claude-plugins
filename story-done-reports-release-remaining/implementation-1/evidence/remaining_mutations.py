import os
from pathlib import Path
import subprocess,json,shutil
OUT=Path(os.environ.get('EVIDENCE_ROOT','/tmp/opencode-story-done'));P=Path(os.environ.get('DEV2_WT','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2'));package=os.environ.get('STAGE_PACKAGE','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1');results=[]
m=OUT/'mutants/consumer-extra-field';shutil.copytree(OUT/'integrated',m,ignore=shutil.ignore_patterns('node_modules','__pycache__'),dirs_exist_ok=True);(m/'kc-journey-map/node_modules').symlink_to(OUT/'integrated/kc-journey-map/node_modules',target_is_directory=True)
f=m/'kc-journey-map/lib/progress.mjs';s=f.read_text();old="const progress = { schema:";assert old in s;f.write_text(s.replace(old,"const progress = { unexpectedField: true, schema:",1))
p=subprocess.run(['python3','-B',str(m/'kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py'),'DueTests.test_live_producer_keeps_done_but_live_release_and_agrees_on_unbuilt'],capture_output=True,text=True);(OUT/'amendment-1-mutant.log').write_text(p.stdout+p.stderr);assert p.returncode==1 and 'self.assertEqual(doc, self.document)' in p.stderr,p.stderr
results.append({'name':'Captain amendment 1: unrecorded producer field','status':'passed','message':'unchanged whole-document assertion rejects extra field, exit 1'})
adr=OUT/'mutants/AC14-missing-adr';(adr/'docs/adr').mkdir(parents=True)
p=subprocess.run(['python3','-B',package+'/scripts/adr_lint.py',str(adr/'docs/adr'),'--root',str(adr),'--require','0076'],capture_output=True,text=True);(OUT/'AC14-missing-adr.log').write_text(p.stdout+p.stderr);assert p.returncode==1
results.append({'name':'AC14 required ADR omitted','status':'passed','message':'ADR linter rejects missing 0076, exit 1'})
allowed={'kc-dev-flow-2/extensions/journey-map/EXTENSION.md','kc-dev-flow-2/extensions/release-acceptance/fixtures/journey-progress-v1.json','kc-dev-flow-2/scripts/design_surfaces.py','kc-dev-flow-2/scripts/test_design_surfaces.py','kc-dev-flow-2/scripts/test_pr_watch.py','docs/adr/0076-a-journey-workflows-new-seed-records-its-story-or-none.md'}
actual=set(subprocess.check_output(['git','-C',str(P),'diff','--name-only','e8664a72b0f904e5dda3c391d52ab3abaca876b4','HEAD'],text=True).splitlines());assert actual==allowed,(actual,allowed)
mini=OUT/'mutants/AC9-workflow';mini.mkdir(parents=True)
wf='kc-dev-flow-2/references/sd/workflow.md';dest=mini/wf;dest.parent.mkdir(parents=True)
base=subprocess.check_output(['git','-C',str(P),'show','e8664a72b0f904e5dda3c391d52ab3abaca876b4:'+wf]);dest.write_bytes(base)
subprocess.run(['git','-C',str(mini),'init','-q'],check=True);subprocess.run(['git','-C',str(mini),'add',wf],check=True);subprocess.run(['git','-C',str(mini),'-c','user.name=Replay','-c','user.email=replay@example.invalid','commit','-qm','fixture'],check=True)
dest.write_bytes(base+b'\nChanged workflow\n');changed=set(subprocess.check_output(['git','-C',str(mini),'diff','--name-only'],text=True).splitlines());assert changed-allowed=={wf}
assert (P/wf).read_bytes()==base
results.append({'name':'AC9 workflow edit','status':'passed','message':'actual throwaway git diff adds forbidden workflow path; real bytes equal base'})
(OUT/'remaining-mutations.json').write_text(json.dumps(results,indent=2)+'\n');print('3 additional mutants rejected')
