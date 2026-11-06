import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

root, state = map(Path, sys.argv[1:3])
out = Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
scripts = root / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
import test_delivery_gate as t

base_path = Path(sys.argv[3]) / 'kc-dev-flow-2/scripts/delivery_gate.py'
base = types.ModuleType('delivery_gate_baseline')
base.__file__ = str(base_path)
exec(compile(base_path.read_text(), str(base_path), 'exec'), base.__dict__)
snapshot = '846c4202b2a7e70bd08eee1d31406502f350aa0d'
paths = {
    786: '_archive/override-recorded-when-captain-departs/review/validation/briefing-1/index.json',
    787: '_archive/extension-instruction-check-sees-every-listed-extension/review/validation/briefing-1/index.json',
    788: '_archive/gate-presentation-asks-one-thing-plainly/review/validation/briefing-3/index.json',
}

def recorded(path):
    return json.loads(subprocess.check_output(['git', '-C', str(state), 'show', f'{snapshot}:{path}']))['question']

for number, path in paths.items():
    assert recorded(path) == t.QuestionTests.recorded_questions[number], number

question = t.QuestionTests.recorded_questions[786]
before, after = t.run_variant(base, text=question), t.run_check(text=question)
assert (before.code, before.out) == (after.code, after.out)
(out / 'check-parity.json').write_text(json.dumps(dict(base_exit=before.code, candidate_exit=after.code,
    base_output=before.out, candidate_output=after.out, fixture='same recorded question, synthetic valid task/gh; no network'), indent=2))

block = '''    if GRANT.search(gate_text) and not WORKTREE_REMOVAL.search(question_text):
        problems.append("the gate text names the merge with --match-head-commit but its question does not name removing its clean, pushed worktree")
        nexts.append("next: hold the gate; add 'and removing its clean, pushed worktree' to the question, then run this check again.")
'''
signature = 'def text_problems(task_text, gate_text, at_gate=False, reviewer_text=None):\n    problems, nexts = [], []\n'
mutations = [
    ('AC-1 remove the new condition', t.variant_of(block, ''), 'test_recorded_merge_questions_require_the_worktree_removal_clause'),
    ('AC-2 read the combined text', t.variant_of('not WORKTREE_REMOVAL.search(question_text)', 'not WORKTREE_REMOVAL.search(gate_text)'), 'test_removal_in_the_summary_does_not_grant_it_in_the_question'),
    ('AC-3 accept any worktree word', t.variant_of(t.gate.WORKTREE_REMOVAL.pattern, r'worktree'), 'test_removal_wording_names_clean_pushed_worktrees_in_one_sentence'),
    ('AC-4 check judges the clause', t.variant_of(signature, signature + '    if GRANT.search(gate_text) and not WORKTREE_REMOVAL.search(gate_text):\n        problems.append("missing worktree removal clause")\n'), 'test_the_merge_time_check_does_not_judge_the_hold_out_clause'),
    ('AC-5 print an extra passing line', t.variant_of('emit("gate text complete", ASK_FORM)', 'emit("extra passing line", "gate text complete", ASK_FORM)'), 'test_legacy_combined_text_still_accepts_no_round_count'),
]
results = []
for index, (name, module, method) in enumerate(mutations, 1):
    buffer = io.StringIO()
    with mock.patch.object(t, 'gate', module):
        result = unittest.TextTestRunner(stream=buffer, verbosity=2).run(unittest.TestSuite([t.QuestionTests(method)]))
    (out / f'mutation-{index}.log').write_text(buffer.getvalue())
    caught = bool(result.failures) and not result.errors
    results.append(dict(name=name, status='passed' if caught else 'failed', message=f'{len(result.failures)} assertions fail; {len(result.errors)} errors'))
    assert caught, name
(out / 'mutations.json').write_text(json.dumps(results, indent=2))

suite = unittest.TestSuite([t.QuestionTests('test_recorded_merge_questions_require_the_worktree_removal_clause')])
with mock.patch.object(t, 'gate', base), (out / 'new-test-on-base.log').open('w') as sink:
    result = unittest.TextTestRunner(stream=sink, verbosity=2).run(suite)
assert len(result.failures) == 2 and not result.errors

all_paths = subprocess.check_output(['git', '-C', str(state), 'ls-tree', '-r', '--name-only', snapshot], text=True).splitlines()
briefings = [p for p in all_paths if '/review/validation/briefing-' in p and p.endswith('/index.json')]
case = t.QuestionTests('test_legacy_combined_text_still_accepts_no_round_count')
corpus = []
for path in briefings:
    question = recorded(path)
    previous = case.ask(question, module=base)
    current = case.ask(question)
    owed = bool(t.gate.GRANT.search(question)) and not t.gate.WORKTREE_REMOVAL.search(question)
    changed = previous != current
    assert changed == owed, (path, previous, current, owed)
    corpus.append(dict(path=path, names_merge=bool(t.gate.GRANT.search(question)), changed=changed,
        base_exit=previous[0], candidate_exit=current[0], base_output=previous[1], candidate_output=current[1],
        disposition='intended missing clean, pushed worktree clause' if changed else 'unchanged'))
(out / 'corpus.json').write_text(json.dumps(dict(snapshot=snapshot, results=corpus), ensure_ascii=False, indent=2))
caches = list((root / 'kc-dev-flow-2').rglob('*.pyc')) + list((Path(sys.argv[3])).rglob('*.pyc'))
assert not caches, caches
summary = dict(mutants_caught=len(results), historical_fixtures_exact=True, base_rejects_new_cases=True,
    check_output_equal=True, validation_questions=len(corpus), merge_questions=sum(r['names_merge'] for r in corpus),
    changed=sum(r['changed'] for r in corpus), bytecode_caches=len(caches))
(out / 'proof-summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary))
