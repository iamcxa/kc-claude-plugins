import json, pathlib, shutil, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
original=root/'candidate'
mutant=root/'mutant'
shutil.copytree(original,mutant,ignore=shutil.ignore_patterns('.git','__pycache__'),dirs_exist_ok=True)
timeline='kc-dev-flow-2/scripts/task_timeline.py'
design='kc-dev-flow-2/scripts/design_surfaces.py'
lint='kc-dev-flow-2/scripts/lint-skills.py'
cases=[
('unknown-event',timeline,'if event not in EVENTS:', 'if False:', 'test_task_timeline.py','test_contract_writer_refuses_unknown_event'),
('closed',timeline,'if q["state"] != "open" and not (event == "acted" and q["state"] == "answered"):', 'if False:', 'test_task_timeline.py','test_contract_writer_refuses_every_event_after_closing_except_one_acted'),
('acted',timeline,'if event == "acted" and q["state"] != "answered":','if False:', 'test_task_timeline.py','test_contract_writer_refuses_acted_without_answer'),
('wordless',timeline,'if revision.get("options") and not revision.get("approve_means"):','if False:', 'test_task_timeline.py','test_contract_writer_refuses_wordless_answer_without_approve_means'),
('recommend',timeline,'if fields.get(field) is not None and fields[field] not in ids:','if field != "recommend" and fields.get(field) is not None and fields[field] not in ids:', 'test_task_timeline.py','test_contract_writer_refuses_recommendation_outside_options'),
('revision',timeline,'if event == "revise" and fields.get("revision") != q["revision"] + 1:','if False:', 'test_task_timeline.py','test_contract_writer_refuses_revision_not_previous_plus_one'),
('answered-listed',timeline,'if q["state"] == "open"]','if q["state"] in ("open", "answered")]', 'test_task_timeline.py','test_replayed_fourteen_questions_at_declared_synthetic_times'),
('open-omitted',timeline,'if q["state"] == "open"]','if False]', 'test_task_timeline.py','test_replayed_fourteen_questions_at_declared_synthetic_times'),
('every-line',timeline,'e.get("event") in ("ask", "reask")','e.get("event") in EVENTS', 'test_task_timeline.py','test_mixed_legacy_ask_reask_answer_counts_only_showings_in_text_and_json'),
('lookup-removed',design,'errors.extend(check_question_records(path, lines, notes))','pass', 'test_design_surfaces.py','test_missing_record_refuses_and_present_record_passes_in_split_root_worktree'),
('always-refuse',design,'if (quoted if quoted is not None else value) not in questions:', 'if True:', 'test_design_surfaces.py','test_missing_record_refuses_and_present_record_passes_in_split_root_worktree'),
('add-time',timeline,'since = when(dates[0]) if dates else None','since = when(subprocess.run(["git", "-C", str(state), "log", "--format=%aI", "--diff-filter=A", "--", str(folder(path) / "review" / attempt["stage"] / "briefing-1" / "index.json")], capture_output=True, text=True, check=True).stdout.splitlines()[0])', 'test_task_timeline.py','test_gate_wait_uses_first_naming_commit_after_archive_moves_room'),
]
results=[]
for name,file,old,new,test,method in cases:
    text=(original/file).read_text()
    assert old in text, (name,old)
    (mutant/file).write_text(text.replace(old,new,1))
    cls='TimelineTests' if test=='test_task_timeline.py' else 'QuestionRecordTests'
    cmd=[sys.executable,'-B',str(mutant/'kc-dev-flow-2/scripts'/test),cls+'.'+method]
    saved=root/f'mutation-{name}.log'
    run=subprocess.run(cmd,cwd=mutant,text=True,capture_output=True) if not saved.exists() else subprocess.CompletedProcess(cmd,1,saved.read_text(),"")
    log=run.stdout+run.stderr
    (root/f'mutation-{name}.log').write_text(log)
    caught=run.returncode==1 and (('FAIL:' in log and 'AssertionError' in log) or (name=='add-time' and 'IndexError: list index out of range' in log and 'open_rows' in log))
    results.append(dict(name=name,exit=run.returncode,caught=caught,command=cmd,log=f'mutation-{name}.log'))
    (mutant/file).write_text(text)
text=(original/lint).read_text()
lines=text.splitlines(True)
at=next(i for i,line in enumerate(lines) if '啟動字數從 39 改成 41' in line)
start=next(i for i in range(at,-1,-1) if 'dict(delta=' in lines[i])
end=next(i for i in range(at,len(lines)) if '),' in lines[i])
(mutant/lint).write_text(''.join(lines[:start]+lines[end+1:]))
run=subprocess.run([sys.executable,'-B',str(mutant/lint)],cwd=mutant,text=True,capture_output=True)
log=run.stdout+run.stderr;(root/'mutation-budget.log').write_text(log)
results.append(dict(name='budget',exit=run.returncode,caught=run.returncode==1 and 'word' in log,log='mutation-budget.log'))
(mutant/lint).write_text(text)
(root/'mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
assert all(r['caught'] for r in results)
