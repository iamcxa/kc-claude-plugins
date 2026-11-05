import ast, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

root = Path(__file__).resolve().parent
scripts = root / 'candidate/kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
import decision_ledger as dl

def save(name, value):
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2))

def functions(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

candidate = functions(scripts / 'decision_ledger.py')
base = functions(root / 'base/kc-dev-flow-2/scripts/decision_ledger.py')
assert all(candidate[name] == value for name, value in base.items())
old = subprocess.check_output(['git', '-C', os.environ['VALIDATION_SOURCE_REPO'], 'show',
    '73db59bef6d1327e8b8c810b4f57601664aee1ef:kc-dev-flow-2/scripts/decision_ledger.py'], text=True)
old_helper = next(n for n in ast.parse(old).body if isinstance(n, ast.FunctionDef) and n.name == 'quotes_bound_question')
assert ast.dump(old_helper, include_attributes=False) == candidate['quotes_bound_question']
old_observer = subprocess.check_output(['git', '-C', os.environ['VALIDATION_SOURCE_REPO'], 'show',
    '73db59bef6d1327e8b8c810b4f57601664aee1ef:kc-dev-flow-2/skills/observer/SKILL.md'])
assert old_observer == (root / 'candidate/kc-dev-flow-2/skills/observer/SKILL.md').read_bytes()
save('integration-proof.json', {'base_functions_preserved': sorted(base), 'quote_helper_ast_preserved': True,
    'observer_skill_bytes_preserved': True, 'source': os.environ['VALIDATION_SOURCE_REPO']})

question = '「決定：進實作嗎？」 Approval also covers merging this head.'
rows = []
with tempfile.TemporaryDirectory(prefix='reason-composition-') as td:
    path = Path(td, 'reason.txt')
    for quoted in (False, True):
        for declared in (False, True):
            reason = 'Captain 「准」, answering 「' + (question if quoted else '決定：進實作嗎？') + '」'
            if declared:
                reason += '; Recommendation: followed'
            path.write_text(reason)
            done = subprocess.run([sys.executable, '-B', str(scripts / 'decision_ledger.py'), '--reason', str(path)], capture_output=True, text=True)
            match = dl.quotes_bound_question({'question': question, 'reason': reason})
            assert done.returncode == (0 if declared else 1)
            assert match is quoted
            rows.append({'quoted': quoted, 'declared': declared, 'exit': done.returncode, 'stdout': done.stdout, 'quote_match': match})
save('composition.json', rows)

cases = [
    ('reason-missing-declaration-accepted', '        problem = "missing declaration"', '        return 0'),
    ('reason-double-declaration-accepted', '        problem = "both declarations"', '        return 0'),
    ('reason-placeholder-accepted', '        problem = "placeholder recommendation"', '        return 0'),
    ('reason-followed-marker-widened', 'followed = FOLLOWED in reason', 'followed = "Recommendation" in reason'),
]
mutations = []
with tempfile.TemporaryDirectory(prefix='reason-falsifiers-') as td:
    copy = Path(td, 'scripts')
    shutil.copytree(scripts, copy, ignore=shutil.ignore_patterns('__pycache__'))
    path = copy / 'decision_ledger.py'
    original = path.read_text()
    for name, before, after in cases:
        assert original.count(before) == 1
        path.write_text(original.replace(before, after))
        done = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(copy),
            '-p', 'test_decision_ledger.py', '-k', 'ReasonTest'], capture_output=True, text=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        (root / (name + '.log')).write_text(done.stdout + done.stderr)
        caught = done.returncode == 1 and 'FAIL:' in done.stderr and 'ERROR:' not in done.stderr
        assert caught, done.stderr
        mutations.append({'name': name, 'caught': caught, 'exit': done.returncode})
        path.write_text(original)
save('reason-mutations.json', mutations)

report = Path('/tmp/ac5-observer-report.md').read_text()
(root / 'observer-report.md').write_text(report)
def check_report(text):
    paragraphs = text.split('\n\n')
    row = [p for p in paragraphs if p.startswith('violation |') and 'evidence: ideation reason' in p]
    return len(row) == 1 and 'D7' in row[0] and 'different questions' in row[0]
assert check_report(report)
bad = report.replace('violation | same rule | evidence: ideation reason', 'ok | same rule | evidence: ideation reason')
omitted = '\n\n'.join(p for p in report.split('\n\n') if 'evidence: ideation reason' not in p)
assert not check_report(bad) and not check_report(omitted)
ledger_rows = [json.loads(line) for line in (root / 'ledger-candidate.jsonl').read_text().splitlines()]
observed = []
for row in ledger_rows:
    if row['task'] == 'fo-tries-what-it-asks-the-captain' and row['kind'] == 'resolution' and row['by'] == 'person:captain':
        match = dl.quotes_bound_question(row)
        assert not match
        observed.append({**row, 'match': match})
assert {r['stage'] for r in observed} == {'backlog', 'ideation', 'validation'}
save('observer-ledger-check.json', observed)
save('observer-check.json', {'report_sha256': hashlib.sha256(report.encode()).hexdigest(),
    'source': '/tmp/ac5-observer-report.md', 'supplied_run_not_relaunched': True,
    'current_helper_and_instruction_equivalent': True, 'three_stage_rows_replayed': True,
    'ideation_violation_present': True, 'ok_mutant_caught': True, 'omitted_row_mutant_caught': True})

tests = sum([json.loads((root / (name + '.json')).read_text()) for name in
    ['delivery_gate', 'design_surfaces', 'decision_ledger', 'pr_watch']], [])
save('tests.json', tests)
save('suite-summary.json', {'discovered': len(tests), **{status: sum(r['status'] == status for r in tests)
    for status in ['passed', 'failed', 'skipped']}, 'historical_cases': 5})
print('integration, four native compositions, four reason mutants, observer controls: PASS')
