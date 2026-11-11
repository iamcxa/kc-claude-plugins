from pathlib import Path
import importlib.util,unittest,io,shutil,subprocess,json
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2');out=Path('/tmp/opencode-story-done-round4');source=root/'kc-dev-flow-2/scripts/test_laws_check.py'
spec=importlib.util.spec_from_file_location('laws_dependency_probe',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for add in [False,True]:
 if add:
  original=m.sandbox
  def with_helper(*args,**kwargs):
   runner=original(*args,**kwargs)
   shutil.copy(m.SCRIPTS/'workflow_extensions.py',runner.parent/'workflow_extensions.py')
   return runner
  m.sandbox=with_helper
 stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromName('ExitContractTest.test_check_exiting_1_with_no_stdout_exits_2',m);result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);(out/('laws-helper-'+('present' if add else 'missing')+'.log')).write_text(stream.getvalue());rows.append({'helper_in_throwaway_fixture':add,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful()})
assert [r['passed'] for r in rows]==[False,True],rows
assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True).strip()
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()=='e079d0c555fde855527a82c7a497a4d07e6e4c04'
(out/'laws-helper-probe.json').write_text(json.dumps({'probe':'unchanged test and product bytes; only copy the existing helper into the temporary fixture','results':rows,'candidate_unchanged':True},indent=2)+'\n');print(rows)
