import os, shutil, subprocess, sys, json
from pathlib import Path
WT=Path(__file__).resolve().parents[2]
SOURCE=WT/'kc-dev-flow-2'
COPY=Path(__file__).parent/'mutant'
if COPY.exists(): shutil.rmtree(COPY)
shutil.copytree(SOURCE,COPY,ignore=shutil.ignore_patterns('__pycache__'))
watch=COPY/'scripts/pr_watch.py'
extension=COPY/'extensions/learn/EXTENSION.md'
original=watch.read_text(); ext=extension.read_text()
cases=[
 ('AC-1 archive exclusion', 'def archived_learning(workflow, state, ask):', 'def archived_learning(workflow, state, ask):\n    return [], []', 'test_pr_watch.py', 'TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded'),
 ('AC-1 folder omission', r'(\.md|/index\.md)', r'(\.md)', 'test_pr_watch.py', 'TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded'),
 ('AC-1 extension guard', '    if "learn" in listed:\n        line, broken = archived_learning', '    if True:\n        line, broken = archived_learning', 'test_pr_watch.py', 'TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded'),
 ('AC-2 unread-only', '"notices", "--all"', '"notices"', 'test_pr_watch.py', 'TasksTests.test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats'),
 ('AC-2 wrong workflow key', 'job_key({"workflow": key, "task_id": slug})', 'job_key({"workflow": "", "task_id": slug})', 'test_pr_watch.py', 'TasksTests.test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats'),
 ('AC-2 state repository', '"--repo", str(root),', '"--repo", str(state),', 'test_pr_watch.py', 'TasksTests.test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats'),
 ('AC-2 uncertain missing input', 'if job not in jobs:', 'if job not in jobs or "input" not in jobs[job]:', 'test_pr_watch.py', 'TasksTests.test_keyed_uncertain_notices_without_input_are_inspected_and_malformed_lists_hold'),
 ('AC-3 live-only replay', 'def archived_learning(workflow, state, ask):', 'def archived_learning(workflow, state, ask):\n    return [], []', 'test_pr_watch.py', 'TasksTests.test_frozen_archive_replay_recovers_all_eleven_and_suppresses_backfilled_jobs'),
 ('AC-4 full provider read', '"--repo", repo, "--json", "state")', '"--repo", repo, "--json", FIELDS)', 'test_pr_watch.py', 'TasksTests.test_archive_provider_reads_only_state_and_preserves_qualified_repository'),
 ('AC-4 assume unreadable list empty', 'raise ValueError("malformed learn notices")', 'notices = []', 'test_pr_watch.py', 'TasksTests.test_keyed_uncertain_notices_without_input_are_inspected_and_malformed_lists_hold'),
 ('AC-5 archive cache write', '        line, broken = archived_learning(Path(opts.args[0]).absolute(), state, ask)', '        update(opts.state, put={"archive#7": {}})\n        line, broken = archived_learning(Path(opts.args[0]).absolute(), state, ask)', 'test_pr_watch.py', 'TasksTests.test_archive_shapes_are_sorted_deduplicated_and_guarded'),
 ('AC-6 observer pointer removed', 'observer_check.py', 'observer_removed.py', 'test_observer_check.py', 'NamedWhereFoReadsTest.test_each_text_on_the_path_to_the_sentinel_names_the_check'),
 ('AC-7 longer reminder', 'next: run kc-dev-flow-2:learn for {slug}.', 'next: please run kc-dev-flow-2:learn for {slug}.', 'test_pr_watch.py', 'TasksTests.test_ineligible_learn_hold_leaves_no_job_and_next_idle_repeats_the_name'),
 ('AC-8 silently suppress ineligible', '            pr = meta.get("pr", "")', '            if slug == "old-profile":\n                continue\n            pr = meta.get("pr", "")', 'test_pr_watch.py', 'TasksTests.test_ineligible_learn_hold_leaves_no_job_and_next_idle_repeats_the_name'),
]
rows=[]
for name,old,new,test,method in cases:
 watch.write_text(original); extension.write_text(ext)
 target=extension if name.startswith('AC-6') else watch
 text=target.read_text(); assert old in text,name
 target.write_text(text.replace(old,new,1))
 for cache in COPY.rglob('__pycache__'): shutil.rmtree(cache)
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','MUTANT_WATCH':str(COPY/'archive-watch.json')}
 done=subprocess.run([sys.executable,'-B',str(COPY/'scripts'/test),method],capture_output=True,text=True,env=env)
 log=Path(__file__).parent/(name.split()[0]+'-'+str(len(rows))+'.log');log.write_text(done.stdout+done.stderr)
 detected=done.returncode==1 and ('FAIL:' in done.stderr or 'ERROR:' in done.stderr)
 rows.append({'case':name,'exit':done.returncode,'detected':detected,'log':str(log)})
 print(json.dumps(rows[-1]),flush=True)
watch.write_text(original); extension.write_text(ext)
(Path(__file__).parent/'mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(row['detected'] for row in rows),rows
