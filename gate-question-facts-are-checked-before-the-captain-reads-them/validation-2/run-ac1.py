#!/usr/bin/env python3
"""Run the pinned listing on original historical task bytes; emit aggregates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

p = argparse.ArgumentParser()
p.add_argument('--code', type=Path, required=True)
p.add_argument('--state', type=Path, required=True)
p.add_argument('--spacedock', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--scratch', type=Path, required=True)
a = p.parse_args()
HEAD = '455846c6d30d4ab650c1c4503bc591722231586d'
OWN = '8d083d3b9b2c48c10e32cee3e5ef693b374c6183'
REL = 'kc-dev-flow-2/scripts/pr_watch.py'
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'SPACEDOCK_BIN': str(a.spacedock), 'GIT_AUTHOR_NAME': 'Validation Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid', 'GIT_COMMITTER_NAME': 'Validation Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
a.output.mkdir(parents=True, exist_ok=True)
root = a.scratch
root.mkdir(parents=True)
assert not (Path('/tmp/dev2') / ('validation-fixture-' + root.parent.name)).exists()
manifest = {'scratch_roots': [str(root)], 'created_tmp_roots': [str(root)], 'remove_after_evidence_commit': True}
(a.output / 'scratch.json').write_text(json.dumps(manifest, indent=2) + '\n')

def run(argv, **kwargs):
    return subprocess.run(list(map(str, argv)), capture_output=True, text=True, env=env, **kwargs)

def git(repo, *argv):
    r = run(['git', '-C', repo, *argv])
    if r.returncode:
        (root / 'failure.txt').write_text(r.stdout + r.stderr)
        raise RuntimeError('git operation failed; diagnostic retained only in scratch')
    return r.stdout

assert git(a.code, 'rev-parse', 'HEAD').strip() == OWN
assert not git(a.code, 'status', '--porcelain').strip()
clone = root / 'candidate'
clone.mkdir()
archive = subprocess.Popen(['git', '-C', str(a.code), 'archive', HEAD], stdout=subprocess.PIPE, env=env)
subprocess.run(['tar', '-x', '-C', str(clone)], stdin=archive.stdout, check=True, env=env)
archive.stdout.close()
assert archive.wait() == 0
git(clone, 'init', '-q', '-b', 'export-fixture')
git(clone, 'remote', 'add', 'origin', 'file:///validation-fixture-' + root.parent.name)
git(clone, 'add', '--', '.')
git(clone, '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'exported public candidate fixture')
script = clone / REL
original = git(a.code, 'show', HEAD + ':' + REL)
assert script.read_text() == original
qdir = a.state / 'gate-question-facts-are-checked-before-the-captain-reads-them/ideation-1/questions'
readme = (clone / 'docs/dev2/README.md').read_text()
readme, replacements = re.subn(r'^extensions:.*$', 'extensions: []', readme, count=1, flags=re.M)
assert replacements == 1
result = {'candidate': OWN, 'listing_candidate': HEAD, 'listing_sha256': hashlib.sha256(original.encode()).hexdigest(),
          'spacedock_sha256': hashlib.sha256(a.spacedock.read_bytes()).hexdigest(),
          'scope': 'original five task files per historical question, byte-identical; no other tasks copied; no GitHub/model calls',
          'configuration': 'copied candidate workflow; extensions disabled to omit unrelated review/learning work; gate/stage configuration unchanged',
          'fixtures': {}, 'mutation': {}}

def prepare(filename):
    q = json.loads((qdir / (filename + '.json')).read_text())
    workflow = clone / 'replays' / filename / 'docs/dev2'
    state = workflow / '.spacedock-state'
    state.mkdir(parents=True)
    (workflow / 'README.md').write_text(readme)
    hashes = []
    for slug in q['claims']['tasks']:
        raw = git(a.state, 'show', q['state_commit_before_ask'] + ':' + slug + '.md')
        dest = state / (slug + '.md')
        dest.write_text(raw)
        assert dest.read_bytes() == raw.encode()
        assert not re.search(r'^(?:pr|worktree):\s*\S', raw.split('---', 2)[1], re.M)
        hashes.append(hashlib.sha256(raw.encode()).hexdigest())
    git(state, 'init', '-q', '-b', 'replay')
    git(state, 'add', '--', *[slug + '.md' for slug in q['claims']['tasks']])
    git(state, '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture snapshot')
    return q, workflow, hashes

fixtures = {name: prepare(name) for name in ('case3-five-tasks', 'control-five-new-tasks')}

def observe(name):
    q, workflow, hashes = fixtures[name]
    query = run([a.spacedock, 'status', '--workflow-dir', workflow, '--where', 'gate-readiness=not-applicable',
                 '--fields', 'slug,status', '--json', '--limit', '0'])
    assert query.returncode == 0, 'native held query failed'
    rows = json.loads(query.stdout)['entities']
    actual = run([sys.executable, '-B', script, '--state', root / (name + '-watch.json'), 'tasks', workflow], cwd=clone)
    (root / (name + '-runtime.txt')).write_text(actual.stdout + actual.stderr)
    prefix = 'fact: held by the Captain, not waiting: '
    lines = [line for line in actual.stdout.splitlines() if line.startswith(prefix)]
    named = set(re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', '\n'.join(lines)))
    hits = sum(slug in named for slug in q['claims']['tasks'])
    native_hits = sum(row['slug'] in q['claims']['tasks'] for row in rows)
    return {'state_commit': q['state_commit_before_ask'], 'offered': len(q['claims']['tasks']),
            'original_files_verified': len(hashes), 'held_query_exit': query.returncode,
            'native_held': native_hits, 'tasks_command_exit': actual.returncode, 'held_fact_lines': len(lines),
            'offered_named_held': hits, 'flag_adapter_exit': int(hits > 0),
            'runtime_error_lines': sum(line.startswith('next: report ') for line in actual.stdout.splitlines())}

for name, expected in [('case3-five-tasks', 5), ('control-five-new-tasks', 0)]:
    row = observe(name)
    result['fixtures'][name] = row
    assert row['tasks_command_exit'] == 0, 'listing command failed; inspect scratch-only runtime diagnostic'
    assert row['native_held'] == row['offered_named_held'] == expected, 'listing count differs from expected'
    assert row['held_fact_lines'] == int(expected > 0)

old = '    return rows\n\n\ndef held_quote(task):'
replacement = '''    state = Path(workflow) / front(Path(workflow) / "README.md").get("state", ".")
    return [row for row in rows if not any(
        entry.get("kind") == "resolution" and entry.get("decision") == "hold"
        for entry in gate_entries(split_task((state / (row["slug"] + ".md")).read_text())[0] or []))]


def held_quote(task):'''
assert original.count(old) == 1
mutated = original.replace(old, replacement)
script.write_text(mutated)
assert not list(clone.rglob('__pycache__')), 'bytecode cache present before mutant'
mutant = observe('case3-five-tasks')
assert mutant['tasks_command_exit'] == 0 and mutant['native_held'] == 5
assert mutant['offered_named_held'] == 0 and mutant['flag_adapter_exit'] == 0
control_mutant = observe('control-five-new-tasks')
assert control_mutant['tasks_command_exit'] == 0 and control_mutant['offered_named_held'] == 0
try:
    assert mutant['offered_named_held'] == 5, 'AC-1 requires all five held offers to be named'
    rejected = False
except AssertionError:
    rejected = True
assert rejected
result['mutation'] = {'description': 'scratch-only held_rows excludes hold-resolution rows from the real native query result; upstream binary unchanged',
                      'mutant_sha256': hashlib.sha256(mutated.encode()).hexdigest(), 'case': mutant,
                      'control': control_mutant, 'acceptance_exit': int(rejected), 'acceptance_rejected': rejected}
result['product_unchanged'] = git(a.code, 'rev-parse', 'HEAD').strip() == OWN and not git(a.code, 'status', '--porcelain').strip()
assert result['product_unchanged']
result['assertions_passed'] = True
(a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print('AC-1: 5 of 5 held offers named; control 0 of 5; hold-removal mutation rejected')
