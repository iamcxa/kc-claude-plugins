from pathlib import Path
import shutil, subprocess, json, os
root = Path('/tmp/pr750-mutation-check')
shutil.copytree('/tmp/validate-pr750-b8a66e82/kc-dev-flow-2', root / 'kc-dev-flow-2')
p = root / 'kc-dev-flow-2/scripts/dispatch_records.py'
original = p.read_text()
live = 'LiveValidationRulingTests.'
cases = [
 ('AC-1-remove-call', ', check_validation_rulings(args[1:])', '', live+'test_fresh_followup_and_filename_one_hold_then_native_ruling_clears_without_input_edits'),
 ('AC-2-filename-ordinal', 'if task is None:\n            continue\n        root = state_git_root(path)', 'if task is None or path.name == "validation-1.md":\n            continue\n        root = state_git_root(path)', live+'test_fresh_followup_and_filename_one_hold_then_native_ruling_clears_without_input_edits'),
 ('AC-4-ignore-ancestry', 'c != report_commit and ancestor(report_commit, c)', 'True', live+'test_old_and_same_commit_rulings_do_not_clear'),
 ('AC-5-cwd-root', 'root = state_git_root(path)', 'root = state_git_root(Path.cwd() / "dummy")', live+'test_plain_copy_skips_only_new_predicate_independent_of_cwd'),
 ('AC-6-no-recovery', 'print(RECOVERY)', 'pass', live+'test_refusal_recovery_once_and_reading_cost'),
 ('AC-7-gate-only', 'for key in current & committed:', 'for key in current & committed:\n        if key[0] != "gate":\n            continue', live+'test_freeform_then_on_touch_amendment_and_partial_supported_ruling'),
 ('AC-7-relax-form', 'for line, message in amendment_form(text.split("\\n"))[1]', 'for line, message in []', 'SavedValidationRulingTests.test_pinned_event_prefixes_four_refused_two_pass_and_amendment_restorations'),
]
results=[]
for name, old, new, test in cases:
    if old not in original:
        print(name, 'MUTATION TARGET MISSING', flush=True)
        continue
    for cache in root.rglob('__pycache__'):
        shutil.rmtree(cache)
    p.write_text(original.replace(old,new,1))
    try:
        run=subprocess.run(['python3','-B',str(p.with_name('test_dispatch_records.py')),test],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        output=run.stdout+run.stderr
        Path('/tmp/'+name+'.log').write_text(output)
        row={'mutation':name,'exit':run.returncode,'assertion_failure':'AssertionError' in output,'test':test}
        results.append(row)
        print(json.dumps(row),flush=True)
    finally:
        p.write_text(original)
Path('/tmp/pr750-mutations.json').write_text(json.dumps(results,indent=2))
assert len(results)==len(cases) and all(r['exit']==1 and r['assertion_failure'] for r in results)
