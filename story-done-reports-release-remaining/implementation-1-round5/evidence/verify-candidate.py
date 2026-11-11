from pathlib import Path
import subprocess,json,hashlib
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2')
out=Path('/tmp/opencode-story-done-round5')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
head='01d23393ebe5bfd63d8bcafc01859c3b146021d2';merge='e079d0c555fde855527a82c7a497a4d07e6e4c04';producer='fd1caa475f85483cf5c4031a1e58656ff5d3eaff';original='fa485f008562f00ebf91deed19e58ea52bb4b4dc';base='e8664a72b0f904e5dda3c391d52ab3abaca876b4'
def git(*args):return subprocess.check_output(['git','-C',str(wt),*args])
def put(name,data): (out/name).write_text(json.dumps(data,indent=2)+'\n')
assert git('rev-parse','HEAD').decode().strip()==head
assert git('rev-parse','--show-toplevel').decode().strip()==str(wt)
assert git('branch','--show-current').decode().strip()=='spacedock-ensign/story-done-reports-release-remaining-dev2'
assert not git('status','--porcelain').strip()
assert git('rev-list','--parents','-n','1',head).decode().split()==[head,merge]
assert git('rev-list','--parents','-n','1',merge).decode().split()==[merge,original,producer]
path='kc-dev-flow-2/scripts/design_surfaces.py'
changed=git('diff','--name-only',merge,head).decode().splitlines();assert changed==[path]
before=git('show',merge+':'+path);after=git('show',head+':'+path)
expected=before.replace(b'from workflow_extensions import readme_extensions\n',b'',1).replace(b'def check_story_record(path, text, seed):\n',b'def check_story_record(path, text, seed):\n    from workflow_extensions import readme_extensions\n\n',1)
assert expected==after
(out/'authorized-repair.diff').write_bytes(git('diff','--binary',merge,head))
(out/'dev2-original.diff').write_bytes(git('diff','--binary',base,original,'--','kc-dev-flow-2/','docs/adr/'))
(out/'dev2-stacked.diff').write_bytes(git('diff','--binary',producer,head,'--','kc-dev-flow-2/','docs/adr/'))
assert not git('diff',producer,head,'--','kc-journey-map/')
stacked=git('diff','--name-only',producer,head).decode().splitlines()
assert stacked==git('diff','--name-only',base,original).decode().splitlines()
unchanged=[p for p in stacked if p!=path]
for p in unchanged: assert git('show',original+':'+p)==git('show',head+':'+p)
protected=['kc-dev-flow-2/scripts/test_laws_check.py','kc-dev-flow-2/scripts/test_design_surfaces.py','kc-dev-flow-2/scripts/test_pr_watch.py','kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py','kc-dev-flow-2/extensions/release-acceptance/fixtures/journey-progress-v1.json','kc-dev-flow-2/extensions/release-acceptance/contract-versions.json','kc-dev-flow-2/references/sd/workflow.md','.github/workflows/kc-dev-flow-2-tests.yml']
hashes=[]
for p in protected:
 old=git('show',merge+':'+p);new=git('show',head+':'+p);assert old==new
 hashes.append({'path':p,'sha256':hashlib.sha256(new).hexdigest(),'unchanged_from_merge':True})
put('candidate-proof.json',{'head':head,'parent':merge,'merge_parents':[original,producer],'branch':git('branch','--show-current').decode().strip(),'worktree':str(wt),'stacked_base':producer,'producer_subtree_unchanged':True,'repair_changes_only':changed,'repair_is_exact_import_relocation':True,'stacked_paths':stacked,'other_original_dev2_files_unchanged':unchanged,'protected_files':hashes,'working_tree_clean':True})
root=state/'story-done-reports-release-remaining/validation-1/evidence'
files=sorted(p for p in root.rglob('*') if p.is_file())
needles=['test_laws_check','laws_check.py','laws suite']
matches=[str(p.relative_to(root)) for p in files if any(n in p.read_text(errors='replace') for n in needles)]
put('validation-1-coverage.json',{'evidence_root':str(root),'searched_files':len(files),'search_terms':needles,'matching_files':matches,'recorded_test_results':json.loads((root/'test-results.json').read_text()),'record_sha256':hashlib.sha256((root/'test-results.json').read_bytes()).hexdigest(),'conclusion':'validation-1 passed the combined tree without reporting a laws-suite failure; its retained record contains no evidence that test_laws_check.py ran; this does not establish that it ran.'})
assert not matches,matches
put('red-green.json',{'regression_test':'ExitContractTest.test_check_exiting_1_with_no_stdout_exits_2','before_head':merge,'before_exit':int((out/'laws-before-fix.exit').read_text()),'after_head':head,'after_exit':int((out/'laws-after-fix.exit').read_text()),'story_tests':'JourneyStoryTests: seed and default checks','story_tests_exit':int((out/'story-after-fix.exit').read_text()),'test_source_unchanged':True,'falsifier':'Restoring the module-top workflow_extensions import makes the unchanged copied-script laws test crash before the expected exit 2.'})
assert int((out/'laws-before-fix.exit').read_text())==1
assert int((out/'laws-after-fix.exit').read_text())==0
assert int((out/'story-after-fix.exit').read_text())==0
print('candidate identity, one-file repair, protected bytes and validation-record scope verified')
