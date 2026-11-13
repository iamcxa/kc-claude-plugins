import json,os,shutil,subprocess
from pathlib import Path
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record')
scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
root=scratch/'mutants/kc-dev-flow-2'
shutil.copytree(wt/'kc-dev-flow-2/scripts', root/'scripts', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
scripts=root/'scripts'
base=(scripts/'task_timeline.py').read_text()
ds=(scripts/'design_surfaces.py').read_text()
mutations=[
 ('unknown-event','task_timeline.py','if event not in EVENTS:', 'if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_unknown_event'),
 ('closed-record','task_timeline.py','if q["state"] != "open" and not (event == "acted" and q["state"] == "answered"):', 'if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_every_event_after_closing_except_one_acted'),
 ('acted-without-answer','task_timeline.py','if event == "acted" and q["state"] != "answered":','if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_acted_without_answer'),
 ('wordless-answer','task_timeline.py','if not words:','if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_wordless_answer_without_approve_means'),
 ('recommendation','task_timeline.py','if fields.get(field) is not None and fields[field] not in ids:', 'if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_recommendation_outside_options'),
 ('revision','task_timeline.py','if event == "revise" and fields.get("revision") != q["revision"] + 1:','if False:', 'test_task_timeline.py','TimelineTests.test_contract_writer_refuses_revision_not_previous_plus_one'),
 ('answered-listed','task_timeline.py','q["state"], q["answer"] = "answered", e','q["answer"] = e', 'test_task_timeline.py','TimelineTests.test_replayed_fourteen_questions_at_declared_synthetic_times'),
 ('open-omitted','task_timeline.py','rows = [q for q in questions(state, as_of) if q["state"] == "open"]','rows = []', 'test_task_timeline.py','TimelineTests.test_replayed_fourteen_questions_at_declared_synthetic_times'),
 ('count-every-line','task_timeline.py','asks = [e for e in read_asks(asks_file) if "v" not in e or (e.get("v") == 1 and e.get("event") in ("ask", "reask"))]','asks = read_asks(asks_file)', 'test_task_timeline.py','TimelineTests.test_mixed_legacy_ask_reask_answer_counts_only_showings_in_text_and_json'),
 ('lookup-removed','design_surfaces.py','    adopted, why = question_adoption(path)','    return []\n    adopted, why = question_adoption(path)', 'test_design_surfaces.py','QuestionRecordTests.test_missing_record_refuses_and_present_record_passes_in_split_root_worktree'),
 ('always-refuse','design_surfaces.py','    adopted, why = question_adoption(path)','    return ["quoted question has no ask record: Amendment 1"]\n    adopted, why = question_adoption(path)', 'test_design_surfaces.py','QuestionRecordTests.test_missing_record_refuses_and_present_record_passes_in_split_root_worktree'),
 ('index-add-time','task_timeline.py','["git", "-C", str(state), "log", "--reverse", "--format=%aI", "-S", key]','["git", "-C", str(state), "log", "--diff-filter=A", "--format=%aI", "--", (path.parent / attempt["room"] / "index.json").relative_to(state).as_posix()]', 'test_task_timeline.py','TimelineTests.test_gate_wait_uses_first_naming_commit_after_archive_moves_room'),
]
results=[]
for name,target,old,new,test,case in mutations:
    source=base if target=='task_timeline.py' else ds
    assert old in source,name
    (scripts/target).write_text(source.replace(old,new,1))
    for cache in scripts.glob('__pycache__/*'): cache.unlink()
    command=['python3','-B',str(scripts/test),case]
    with (scratch/f'mutation-{name}.log').open('w') as log:
        run=subprocess.run(command,cwd=wt,env={**os.environ,'TMPDIR':str(scratch/'tmp')},stdout=log,stderr=subprocess.STDOUT)
    results.append(dict(name=name,status='passed' if run.returncode else 'failed',exit=run.returncode,command=command,log=f'mutation-{name}.log'))
    (scripts/target).write_text(source)
    print(name,run.returncode,flush=True)
(scratch/'mutation-results.json').write_text(json.dumps(results,indent=2))
assert all(r['exit'] for r in results), results
