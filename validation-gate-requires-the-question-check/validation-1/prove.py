import ast
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

root = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-detached')
state = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
base = '1c0dbb540f354300b75dba5a119d2614c8fb0c02'
out = Path('/tmp/validation-767-evidence')
out.mkdir(exist_ok=True)
scripts = root / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('test_delivery_gate', scripts / 'test_delivery_gate.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
source = (scripts / 'delivery_gate.py').read_text()
base_source = subprocess.check_output(['git', '-C', str(root), 'show', base + ':kc-dev-flow-2/scripts/delivery_gate.py'], text=True)
base_gate = type(tests.gate)('base_delivery_gate')
base_gate.__file__ = str(scripts / 'delivery_gate.py')
exec(compile(base_source, base_gate.__file__, 'exec'), base_gate.__dict__)

def function(text, name):
    return ast.dump(next(node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name == name))

assert function(source, 'question') == function(base_source, 'question')
assert function(source, 'text_problems') == function(base_source, 'text_problems')
current, prior = tests.run_check(), tests.run_variant(base_gate)
assert (current.code, current.out) == (prior.code, prior.out) == (0, current.out)
print('AC-5: question and text_problems AST unchanged; complete check output equals base', flush=True)

block = '''    # see docs/adr/0051-the-merge-ask-check-requires-the-round-count.md
    missing = summary_round_problems("\\n".join(outside_fences(gate_text)))
    problems += missing
    if missing:
        nexts.append("next: hold the ask; record the external round count in the summary.")

'''
assert source.count(block) == 1
without = source.replace(block, '')
start, end = without.index('def text_problems('), without.index('\ndef check(')
text_function = without[start:end]
assert text_function.count('    return problems, nexts') == 1
moved = without[:start] + text_function.replace('    return problems, nexts', block + '    return problems, nexts') + without[end:]
mutations = [
    ('AC-1-remove-call', source.replace('missing = summary_round_problems("\\n".join(outside_fences(gate_text)))', 'missing = []'), 'CheckRoundCountTests.test_missing_fenced_or_malformed_count_holds_without_saving_an_ask'),
    ('AC-2-require-nonzero', source.replace('r"[0-9]+(?:[.;]', 'r"[1-9][0-9]*(?:[.;]'), 'CheckRoundCountTests.test_zero_and_detail_counts_preserve_the_complete_text_output'),
    ('AC-5-move-to-text-problems', moved, 'QuestionTests.test_legacy_combined_text_still_accepts_no_round_count'),
]
mutation_results = []
with tempfile.TemporaryDirectory(prefix='mutations-', dir=root / '.context') as temp:
    temp = Path(temp)
    for path in scripts.glob('*.py'):
        shutil.copyfile(path, temp / path.name)
    for label, mutated, test in mutations:
        assert mutated != source, label
        (temp / 'delivery_gate.py').write_text(mutated)
        for cache in temp.rglob('__pycache__'):
            shutil.rmtree(cache)
        run = subprocess.run([sys.executable, '-B', str(temp / 'test_delivery_gate.py'), test], text=True, capture_output=True,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        log = run.stdout + run.stderr
        assert run.returncode == 1 and 'FAIL:' in log and 'ERROR:' not in log, (label, log)
        (out / (label + '.log')).write_text(log)
        mutation_results.append(dict(mutation=label, exit=run.returncode, target=test))
        print(f'{label}: mutation exit={run.returncode}; target assertion failed; no import errors; python -B, caches cleared', flush=True)

rows = [
    ('batch10-after-release-obligations', 1),
    ('peers-paseo-rule-matches-practice', 1),
    ('names-check-says-what-it-skipped', 1),
    ('peer-status-reaches-fresh', 1),
    ('paseo-human-surfaces-visible-and-reachable', 1),
    ('paseo-human-surfaces-visible-and-reachable', 2),
    ('model-roster-per-repo', 1),
]
replays = []
for index, (slug, number) in enumerate(rows):
    path = f'_archive/{slug}/review/validation/briefing-{number}/index.json'
    data = json.loads(subprocess.check_output(['git', '-C', str(state), 'show', '99e8bb36:' + path], text=True))
    text = data['question'] + '\n' + '\n'.join(artifact['summary'] for artifact in data['artifacts'])
    head = __import__('re').search(r'head ([0-9a-f]{40})', text)[1]

    def setup(directory):
        if index < 4:
            saved = subprocess.check_output(['git', '-C', str(state), 'show', f'99e8bb36:_archive/{slug}/review/copilot-not-run.txt'], text=True)
            target = Path(directory, 'task/review/copilot-not-run.txt')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(saved)

    kwargs = dict(task=tests.TASK, text=text, clauses=False, rounds='', head=head,
                  records={'validation-1.md': tests.record(head)}, setup=setup,
                  readme_body='extensions: [roborev, codex, copilot]\nsecond-reviewer: copilot\n')
    before = tests.run_variant(base_gate, **kwargs)
    after = tests.run_check(**kwargs)
    assert before.code == (1 if index == 4 else 0), before.out
    assert after.code == (1 if index < 5 else 0), after.out
    problems = [line for line in after.lines if line and not line.startswith(('next:', 'point:', 'class:', 'record:', 'PR head'))]
    if index < 4:
        assert problems == [tests.CheckRoundCountTests.PROBLEM], after.out
        assert after.written == {}
    else:
        assert after.out == before.out
    item = dict(task=slug, briefing=number, base_exit=before.code, candidate_exit=after.code, problems=problems)
    replays.append(item)
    print(json.dumps(item), flush=True)
(out / 'proof-results.json').write_text(json.dumps(dict(mutations=mutation_results, replays=replays), indent=2))
print('AC-3: all seven supplied texts replayed at state 99e8bb36; provider, task-history and role calls are fixture controls', flush=True)
