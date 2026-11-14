import contextlib, io, json, os, sys, types, unittest
from pathlib import Path
from unittest import mock
exec((Path(__file__).with_name('round2_probe.py')).read_text().split("if __name__=='__main__':")[0],globals())
source=subprocess.check_output(['git','-C',os.environ['SOURCE_REPO'],'show','c2f035b6612f5edb42220576b3414e993531ffd6:kc-dev-flow-2/scripts/delivery_gate.py'],text=True)
before=types.ModuleType('baseline');before.__file__=gate.__file__;exec(compile(source,before.__file__,'exec'),before.__dict__)
rows=[]
for item in json.loads((SCR/'replays.json').read_text())['cases']:
 code=SCR/('repair-final-replay-complete-'+item['task']);workflow=code/'workflow';task=workflow/'.spacedock-state/task.md';question=code/'question.txt';out=io.StringIO();original=question.read_bytes()
 with tests.stubbed(code,head=item['head'],files=['kc-dev-flow-2/scripts/delivery_gate.py'],pr=tests.pr_json(head=item['head']),adr=[p.name for p in (WT/'docs/adr').glob('*.md')]),mock.patch.object(before,'owed_role_calls',return_value=(0,[])),contextlib.redirect_stdout(out):
  old=before.check(types.SimpleNamespace(task=str(task),pr='iamcxa/kc-claude-plugins#9',text_file=str(question),head=None,sibling_pr=[],workflow_dir=str(workflow)))
 question.write_bytes(original)
 (code/'base-question-only.log').write_text(out.getvalue());assert old==1,out.getvalue();rows.append(dict(task=item['task'],base_exit=old,probe_exit=item['check_exit'],failure='baseline requires the missing hand-written confirmation and round fields'))
(SCR/'goal-check.json').write_text(json.dumps(rows,indent=2)+'\n')
mutant=tests.variant_of('if r.get("scope") == "pr" and','if True and')
log=io.StringIO()
with mock.patch.object(tests,'gate',mutant):
 result=unittest.TextTestRunner(stream=log).run(tests.ObservedFactsTests('test_recorded_local_jobs_do_not_inflate_three_real_round_counts'))
(SCR/'mutation.log').write_text(log.getvalue());assert not result.wasSuccessful()
(SCR/'mutation.json').write_text(json.dumps({'restored_local_job_counting_detected':True,'failing_subtests':len(result.failures),'real_cases':[854,856,861]},indent=2)+'\n')
