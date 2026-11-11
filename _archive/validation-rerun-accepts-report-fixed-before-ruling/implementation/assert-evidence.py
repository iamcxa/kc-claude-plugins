import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

repo, evidence = map(Path, sys.argv[1:3])
base = '8c714a370867eccb0d26a589c5149ad3e0c911b4'
candidate = '7d75d65ef317fc5c426eb7b0975d93a72d50acaa'
files = ['kc-dev-flow-2/scripts/dispatch_records.py', 'kc-dev-flow-2/scripts/test_dispatch_records.py',
         'docs/adr/0045-validation-reruns-require-a-later-recorded-captain-ruling.md']
def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args])
assert git('rev-parse', 'HEAD').decode().strip() == candidate
assert not git('status', '--porcelain')
assert set(git('diff', '--name-only', base, candidate).decode().splitlines()) == set(files)
hashes = {}
for file in files:
    content = git('show', candidate + ':' + file)
    assert content == (repo / file).read_bytes()
    hashes[file] = hashlib.sha256(content).hexdigest()

tests = []
for log in ['tests-green.log', 'test-real-builder.log', 'test-dispatch-stage.log', 'test-laws-check.log']:
    text = (evidence / log).read_text()
    match = re.search(r'Ran (\d+) tests? in .*\n\n(OK[^\n]*)', text)
    assert match, (log, text[-1000:])
    tests.append({'name': log, 'status': 'passed', 'message': match[0]})
red = (evidence / 'tests-red.log').read_text()
assert 'FAILED (failures=15)' in red
mutants = json.loads((evidence / 'mutations.json').read_text())
assert len(mutants) == 8 and all(row['status'] == 'passed' for row in mutants)
replay = (evidence / 'replay.log').read_text()
assert 'qnow-recorded-history candidate exit=0 <no ruling line>' in replay
assert 'qnow-recorded-history tag exit=2' in replay and 'rewritten-report;' in replay
assert re.search(r'rewrite-after-ruling candidate exit=2 .*rewritten-report-after-ruling', replay)
assert re.search(r'pre-ruling-verdict-flip candidate exit=2 .*rewritten-report-verdict-changed', replay)
assert 'qnow-recorded-history candidate exit=2' in (evidence / 'replay-mutant.log').read_text()
corpus = (evidence / 'corpus.log').read_text()
totals = re.findall(r'open-decision tasks: (\d+) changed: (\d+)', corpus)
assert sum(int(a) for a, _ in totals) == 26 and sum(int(b) for _, b in totals) == 10
changes = [ast.literal_eval(line[line.index('['):]) for line in corpus.splitlines() if '[' in line]
assert len(changes) == 10 and all(row[0] == 'rewritten-report' for row in changes)
regressions = (evidence / 'corpus-mutant.log').read_text().count("['cleared', 'needs-ruling']")
assert regressions > 0
assert 'design surfaces presentable' in (evidence / 'design-surfaces.log').read_text()
assert 'PASS: basic frontmatter' in (evidence / 'lint-skills.log').read_text()
assert 'ADR file(s) checked' in (evidence / 'adr-lint.log').read_text()
assert 'PASS: no findings' in (evidence / 'number-guards.log').read_text()
assert 'maximum 5% (package default) met' in (evidence / 'comment-ratio.log').read_text()
adr = (repo / files[2]).read_text()
assert adr.count('Amended 2026-11-11') == 1
assert '裁示前的補改都算，結論不能改（建議）' in adr
assert '決定：要不要核准「驗證報告在你裁示前被補改過，仍可再派驗證」' in adr
assert 'same ordered, non-empty list of whole-word' in adr
for reason in ['after-ruling', 'verdict-changed', 'verdict-unreadable']:
    assert 'rewritten-report-' + reason in adr
metadata = {'base': base, 'candidate': candidate, 'branch': git('branch', '--show-current').decode().strip(),
            'sha256': hashes, 'tests': tests, 'corpus': {'tasks': 26, 'changed': 10, 'other_changes': 0},
            'corpus_mutant_unintended_changes_detected': regressions,
            'product_pushed': False, 'pr_opened': False, 'roborev': 'not run', 'hosted_ci': 'not run',
            'ci_cost_per_pr': 'not measured; no CI change'}
(evidence / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
(evidence / 'tests.json').write_text(json.dumps(tests + mutants, indent=2) + '\n')
criteria = [{'name': 'AC-' + str(n), 'status': 'passed'} for n in range(1, 7)]
(evidence / 'acceptance.json').write_text(json.dumps(criteria, indent=2) + '\n')
print('PASS: exact candidate files, red/green tests, all six criteria, eight unit mutants, qnow mutant and corpus regression mutant')
