import json,os,shutil,subprocess
from pathlib import Path
wt=Path('<home>/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record');scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
scripts=scratch/'repair-mutants/scripts';shutil.copytree(wt/'kc-dev-flow-2/scripts',scripts,ignore=shutil.ignore_patterns('__pycache__'))
mutations=[('F1-question-field','task_timeline.py','        if row["kind"] == "question":\n            row["question"] = row["asked"]\n','', 'test_task_timeline.py','TimelineTests.test_readme_plain_open_entrance_and_mixed_gate_rows_have_question_text',{}),('F2-fixture-worth','test_design_surfaces.py','## Design\\n### Worth questions\\nAsked: keep question records; without: omission passes; premise: compare missing and present records.\\n\\n','', 'test_design_surfaces.py','QuestionRecordTests',{'SPACEDOCK_BIN':'/nonexistent/spacedock'}),('F3-wrong-day','test_task_timeline.py','2026-11-13T14:42:40+08:00','2026-11-05T17:40:56+08:00','test_task_timeline.py','TimelineTests.test_replayed_fourteen_questions_at_declared_synthetic_times',{})]
results=[]
for name,target,old,new,test,case,extra in mutations:
 p=scripts/target;original=p.read_text();assert old in original,name;p.write_text(original.replace(old,new,1))
 command=['python3','-B',str(scripts/test),case]
 with (scratch/(name+'.log')).open('w') as log:run=subprocess.run(command,cwd=wt,env={**os.environ,'TMPDIR':str(scratch/'tmp'),**extra},stdout=log,stderr=subprocess.STDOUT)
 p.write_text(original)
 results.append(dict(name=name,exit=run.returncode,command=command,status='caught' if run.returncode else 'missed'))
 print(name,run.returncode,flush=True)
(scratch/'repair-mutations.json').write_text(json.dumps(results,indent=2));assert all(r['exit'] for r in results)
