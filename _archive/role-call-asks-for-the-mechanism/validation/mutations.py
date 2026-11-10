import json, pathlib, re, shutil, subprocess, sys, tempfile, time
wt=pathlib.Path(sys.argv[1]);ev=pathlib.Path(sys.argv[2]);src=wt/'kc-dev-flow-2/scripts'
code=(src/'role_triggers.py').read_text()
base=(wt.parent/'base/kc-dev-flow-2/scripts/role_triggers.py').read_text()
question_tests=['StepBackTest.test_third_failure_owes_one_mechanism_call_even_with_repairs_and_rounds','SymptomRoundsTest.test_second_advises_third_owes_and_only_committed_records_count']
reason_tests=['SymptomRoundsTest.test_both_findings_events_require_distinct_causes_in_the_decline','SymptomRoundsTest.test_recorded_outcome_answers_leave_both_findings_calls_owed']
cases=[('base-0.36.0',base,question_tests+reason_tests),
 ('old-question',code.replace('question=MECHANISM if findings','question=STEP_BACK if findings'),question_tests),
 ('any-decline-clears',code.replace('waivers = [waived for waived, _ in waivers]\n        dated =','waivers = [waived for waived, _ in waivers]\n        reasoned = list(waivers)\n        dated ='),reason_tests),
 ('one-word-cause',code.replace('all(len(item) >= 3 for item in items)','all(len(item) >= 2 for item in items)'),reason_tests[:1]),
 ('case-sensitive-causes',code.replace('" ".join(item[1:]).casefold()','" ".join(item[1:])'),reason_tests[:1]),
 ('substring-suppression',code.replace('not stepped','not any(STEP_BACK in line for line in owed)'),['SymptomRoundsTest.test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated'])]
rows=[]
for name,mutant,tests in cases:
 assert mutant != code,name
 with tempfile.TemporaryDirectory(prefix='rcm-mutation-') as tmp:
  scratch=pathlib.Path(tmp)
  shutil.copy2(src/'test_role_triggers.py',scratch/'test_role_triggers.py')
  (scratch/'role_triggers.py').write_text(mutant)
  for cache in scratch.rglob('__pycache__'): shutil.rmtree(cache)
  cmd=[sys.executable,'-B','-m','unittest','-v',*[f'test_role_triggers.{t}' for t in tests]]
  r=subprocess.run(cmd,cwd=scratch,capture_output=True,text=True,timeout=180)
  (ev/(name+'.log')).write_text(r.stdout+r.stderr)
  failed=re.findall(r'^FAIL: (.*)$',r.stderr,re.M)
  row={'name':name,'command':cmd,'exit':r.returncode,'failed_cases':failed,'caught':r.returncode==1 and bool(failed) and 'ERROR:' not in r.stderr,'cache':'fresh temporary directory, __pycache__ removed, python3 -B'}
  rows.append(row)
  print(json.dumps(row),flush=True)
(ev/'mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(x['caught'] for x in rows)
