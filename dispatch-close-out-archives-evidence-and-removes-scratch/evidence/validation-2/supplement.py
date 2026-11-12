"""Reproduce the prior emitted-instruction omission and recount emitted words."""
import io,json,pathlib,sys,unittest
import test_dispatch_stage,test_pr_watch
e=pathlib.Path(sys.argv[1]); previous=pathlib.Path(sys.argv[2])
test_dispatch_stage.WRAPPER=previous/'kc-dev-flow-2/scripts/dispatch_stage.py'
log=io.StringIO()
suite=unittest.defaultTestLoader.loadTestsFromName('DispatchStageTests.test_scratch_in_record_and_real_dispatch_artifact_without_changing_input',test_dispatch_stage)
result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
(e/'privacy-previous-native.log').write_text(log.getvalue())
assert len(result.failures)==1 and not result.errors
assert 'Never archive private repository evidence, secrets or personal data' in result.failures[0][1]
(e/'privacy-previous-native.json').write_text(json.dumps({'prior_head':'223dbb6d1b5e895a45d11537b9494aa08610c8f8','native_build_exercised':True,'new_regression_assertion_fails_on_prior_omission':True},indent=2))
case=test_pr_watch.TasksTests('test_scratch_sweep_prompts_old_and_archived_roots_and_leaves_current_and_unknown');case.setUp()
try:
 case.readme('');case.task('live',worktree=False)
 case.scratch_dispatch('live','validation-1');case.scratch_dispatch('live','validation-2')
 case.scratch_root('live','validation-1');case.scratch_root('live','validation-2')
 code,lines=case.tasks({});assert code==0
 closes=[x for x in lines if 'scripts/scratch.py close ' in x];assert len(closes)==1
 (e/'idle-emitted.txt').write_text('\n'.join(lines)+'\n')
 paragraph=(e/'captain-final/replay/emitted-record.md').read_text().split('Scratch: ',1)[1].strip().split('\n',1)[1]
 words={'worker_prose_words':len(paragraph.split()),'worker_with_scratch_line_words':len(paragraph.split())+2,'worker_ceiling':66,'idle_next_line_words':len(closes[0].split()),'idle_ceiling':21,'startup_and_workflow_text_changed':False}
 assert words['worker_prose_words']<=66 and words['idle_next_line_words']<=21
 (e/'word-budget.json').write_text(json.dumps(words,indent=2))
finally:case.doCleanups()
print('Prior native omission reproduced; emitted word ceilings met')
