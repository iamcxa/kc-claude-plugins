import ast, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
root=Path("/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-2"); code=root/'candidate'; mutant=root/'mutant'
state=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
def tuples(path):
 tree=ast.parse(path.read_text())
 return ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REPLAY_2026_11_13' for t in n.targets)))
source=json.loads((root/'fixture-reconciliation.json').read_text())
actual=tuples(code/'kc-dev-flow-2/scripts/test_task_timeline.py')
expected=[(r['replay'],r['question'],r['recorded_answer_at']) for r in source]
assert actual==expected
proof=[]
for row in source:
 raw=subprocess.check_output(['git','-C',str(state),'show',row['recorded_answer_commit']+':'+row['source_path']])
 assert row['source_record'] in raw.decode()
 date=subprocess.check_output(['git','-C',str(state),'show','-s','--format=%aI',row['recorded_answer_commit']],text=True).strip()
 assert date==row['recorded_answer_at'] and date[:10]=='2026-11-13'
 proof.append(dict(replay=row['replay'],commit=row['recorded_answer_commit'],path=row['source_path'],author_date=date,source_sha256=hashlib.sha256(raw).hexdigest(),question_sha256=hashlib.sha256(row['question'].encode()).hexdigest(),question_characters=len(row['question']),matches_candidate=True))
bad=list(actual);bad[4]=(bad[4][0],bad[4][1],'2026-11-05T17:40:56+08:00')
assert bad!=expected
truncated=list(actual);truncated[4]=(truncated[4][0],'要不要開「Pilot 流程改動',truncated[4][2])
assert truncated!=expected
(root/'source-audit.json').write_text(json.dumps(dict(count=len(proof),records=proof,wrong_day_detected=True,truncated_text_detected=True),ensure_ascii=False,indent=2))
results=[]
cases=[
 ('F1','kc-dev-flow-2/scripts/task_timeline.py','        if row["kind"] == "question":\n            row["question"] = row["asked"]\n','', ['python3','-B','kc-dev-flow-2/scripts/test_task_timeline.py','TimelineTests.test_readme_plain_open_entrance_and_mixed_gate_rows_have_question_text'],{},'KeyError'),
 ('F2','kc-dev-flow-2/scripts/test_design_surfaces.py','## Design\\n### Worth questions\\nAsked: keep question records; without: omission passes; premise: compare missing and present records.\\n\\n','', ['python3','-B','kc-dev-flow-2/scripts/test_design_surfaces.py','QuestionRecordTests'],{'SPACEDOCK_BIN':'/nonexistent/spacedock'},'FAIL:'),
 ('F3','kc-dev-flow-2/scripts/test_task_timeline.py','2026-11-13T14:42:40+08:00','2026-11-05T17:40:56+08:00',['python3','-B','kc-dev-flow-2/scripts/test_task_timeline.py','TimelineTests.test_replayed_fourteen_questions_at_declared_synthetic_times'],{},'AssertionError')]
for name,file,old,new,cmd,env,signal in cases:
 text=(code/file).read_text();assert text.count(old)==1,(name,text.count(old))
 (mutant/file).write_text(text.replace(old,new,1))
 run=subprocess.run(cmd,cwd=mutant,env={**os.environ,**env,'TMPDIR':str(root),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
 log=run.stdout+run.stderr;(root/(name+'-falsifier.log')).write_text(log)
 caught=run.returncode==1 and signal in log
 results.append(dict(name=name,exit=run.returncode,caught=caught,log=name+'-falsifier.log'))
 (mutant/file).write_text(text)
 assert caught,(name,log)
adr=next((mutant/'docs/adr').glob('0086-*'))
content=adr.read_bytes();adr.unlink()
run=subprocess.run(['python3',"/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py",'docs/adr','--require','0086'],cwd=mutant,capture_output=True,text=True)
(root/'adr-falsifier.log').write_text(run.stdout+run.stderr);adr.write_bytes(content)
assert run.returncode==1 and '0086' in run.stdout+run.stderr
results.append(dict(name='AC-7 missing 0086',exit=run.returncode,caught=True,log='adr-falsifier.log'))
(root/'repair-falsifiers.json').write_text(json.dumps(results,indent=2))
print('14 source tuples match exact public records and commit dates; wrong day and truncated text rejected')
print(json.dumps(results,indent=2))

