"""Revert only the repaired seams in memory; exercise their real regression tests."""
import io,json,os,pathlib,subprocess,sys,types,unittest
scripts=pathlib.Path(sys.argv[1]).resolve();repo=scripts.parents[1];out=pathlib.Path(sys.argv[2]).resolve();out.mkdir()
sys.path.insert(0,str(scripts));import scratch,test_scratch,test_dispatch_stage,test_pr_watch
old_head='d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6'
legacy=types.ModuleType('legacy_scratch');legacy.__file__=str(scripts/'scratch.py')
source=subprocess.check_output(['git','-C',str(repo),'show',old_head+':kc-dev-flow-2/scripts/scratch.py'],text=True);exec(compile(source,legacy.__file__,'exec'),legacy.__dict__)
rows=[]
def check(label,testmodule,testname,apply,restore):
 log=io.StringIO();apply()
 try:
  suite=unittest.defaultTestLoader.loadTestsFromName(testname,testmodule)
  result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 finally:restore()
 (out/(label+'.log')).write_text(log.getvalue())
 assert result.testsRun>0
 rows.append({'name':label,'status':'passed' if not result.wasSuccessful() else 'failed','message':'mutation rejected' if not result.wasSuccessful() else 'mutation survived'})
original=scratch.evidence
for label,test in [('collision-partial-write','test_compression_collision_refuses_before_changes_and_retry_keeps_digests'),('gzip-validation-after-write','test_existing_gzip_is_validated_before_compressing_other_files')]:
 check(label,test_scratch,'ScratchTests.'+test,lambda:setattr(scratch,'evidence',legacy.evidence),lambda:setattr(scratch,'evidence',original))
source=subprocess.check_output(['git','-C',str(repo),'show',old_head+':kc-dev-flow-2/scripts/dispatch_stage.py'],text=True)
wrapper=out/'old-selection.py';wrapper.write_text('import sys,types\nsys.path.insert(0,'+repr(str(scripts))+')\nimport dispatch_stage as s\nm=types.ModuleType("old_dispatch");m.__file__='+repr(str(scripts/'dispatch_stage.py'))+'\nexec('+repr(source)+',m.__dict__)\ns.select_record=m.select_record\nsys.exit(s.main())\n')
original_wrapper=test_dispatch_stage.WRAPPER
for label,test in [('validation-next-root','test_next_validation_accepts_its_own_scratch_path_and_retries'),('role-next-root','test_next_role_accepts_its_own_scratch_path_and_retries')]:
 check(label,test_dispatch_stage,'DispatchStageTests.'+test,lambda:setattr(test_dispatch_stage,'WRAPPER',wrapper),lambda:setattr(test_dispatch_stage,'WRAPPER',original_wrapper))
original_watch=test_pr_watch.watch
source=(scripts/'pr_watch.py').read_text()
needle='out += [line for line in scratch_lines(workflow, state, found, {slug}) if line not in out]'
assert needle in source
for label,changed in [('merged-cleanup-lost',source.replace(needle,'pass',1)),('printed-readme-lost',source.replace('f"--readme {shlex.quote(str(workflow / \'README.md\'))}"','""',1))]:
 mutant=types.ModuleType('watch_mutant');mutant.__file__=str(scripts/'pr_watch.py');exec(compile(changed,mutant.__file__,'exec'),mutant.__dict__)
 check(label,test_pr_watch,'TasksTests.test_merged_scratch_prompt_precedes_merge_record',lambda:setattr(test_pr_watch,'watch',mutant),lambda:setattr(test_pr_watch,'watch',original_watch))
pre_io=types.ModuleType('pre_io');pre_io.__file__=str(scripts/'scratch.py')
source=subprocess.check_output(['git','-C',str(repo),'show','4be5fe99f:kc-dev-flow-2/scripts/scratch.py'],text=True)
exec(compile(source,pre_io.__file__,'exec'),pre_io.__dict__)
check('later-write-loses-digest',test_scratch,'ScratchTests.test_later_gzip_write_failure_keeps_original_digests_for_retry',lambda:setattr(scratch,'evidence',pre_io.evidence),lambda:setattr(scratch,'evidence',original))
(out/'tests.json').write_text(json.dumps(rows,indent=1));print(json.dumps(rows));sys.exit(any(r['status']!='passed' for r in rows))
