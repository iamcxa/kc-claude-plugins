#!/usr/bin/env python3
"""Independent aggregate-only replay. Historical source text never enters output."""
import argparse
import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import types
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--export', type=Path, required=True)
p.add_argument('--state', type=Path, required=True)
p.add_argument('--poc', type=Path, required=True)
p.add_argument('--base', type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.export / 'kc-dev-flow-2/scripts'))
import test_delivery_gate as tests
gate = tests.gate
qdir = a.state / 'gate-question-facts-are-checked-before-the-captain-reads-them/ideation-1/questions'

def historical(q, path):
    r = subprocess.run(['git', '-C', str(a.state), 'show', q['state_commit_before_ask'] + ':' + path], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def unchecked(mod, folder, text):
    return sum(not cited and not marked for _, _, cited, marked in mod.scope_claims(folder, text))

result = {'historical_state': [], 'question_replays': [], 'falsifiers': {}, 'scope': 'aggregate-only; no source sentences or private identifiers'}
gf = module(a.poc / 'kc-dev-flow-2/scripts/gate_facts.py', 'poc_gate_facts')
for filename, expected in [('case3-five-tasks', 5), ('control-five-new-tasks', 0)]:
    qpath = qdir / (filename + '.json')
    q = json.loads(qpath.read_text())
    rows = []
    for slug in q['claims']['tasks']:
        text = historical(q, slug + '.md') or historical(q, '_archive/' + slug + '.md')
        assert text is not None, 'historical task missing'
        front = gf.front(text)
        decisions = [attempt['resolution'] for record in front.get('gates', {}).get('records', []) for attempt in record.get('attempts', []) if attempt.get('resolution')]
        decisions.sort(key=lambda v: str(v.get('at')))
        rows.append(decisions[-1]['decision'] if decisions else None)
    assert len(rows) == 5 and sum(v == 'hold' for v in rows) == expected
    cli = subprocess.run([sys.executable, '-B', str(a.poc / 'kc-dev-flow-2/scripts/gate_facts.py'), 'state', '--state', str(a.state), '--question', str(qpath)], capture_output=True, text=True)
    assert cli.returncode == bool(expected)
    assert f'{expected} of 5 tasks flagged' in cli.stdout
    with contextlib.redirect_stdout(io.StringIO()):
        original = gf.STOP_DECISIONS
        gf.STOP_DECISIONS = original - {'hold'}
        mutant_exit = gf.state_check(types.SimpleNamespace(question=str(qpath), state=str(a.state), json=None))
        gf.STOP_DECISIONS = original
    assert mutant_exit == 0
    result['historical_state'].append({'offered': 5, 'held': expected, 'poc_exit': cli.returncode, 'without_hold_exit': mutant_exit})
result['falsifiers']['AC-1'] = {'poc_hold_removal_detected': True, 'dependent_candidate_result': 'ac1/result.json (separate command)'}

english = tests.variant_of('EXISTING.search(sentence)', "re.search(r'\\bexisting\\b', sentence, re.I)")
missing = tests.variant_of('and path.is_file():', 'and True:')
baseline = module(a.base / 'kc-dev-flow-2/scripts/delivery_gate.py', 'baseline_delivery_gate')
controls = [('case1-843', 1), ('case2-841', 1), ('control-839', 0), ('control-849', 1), ('control-five-new-tasks', 0), ('case3-five-tasks', 0), ('control-849-cited', 0), ('control-849-badcite', 1), ('case2-841-marked', 0)]
with tempfile.TemporaryDirectory(prefix='independent-replay-') as tmp:
    root = Path(tmp)
    for filename, expected in controls:
        q = json.loads((qdir / (filename + '.json')).read_text())
        folder = root / 'task'
        folder.mkdir(exist_ok=True)
        cards = {}
        task_name = q.get('task') or ''
        for value in gate.SAVED_FILE.findall(q['question']):
            relative = value.removeprefix(task_name + '/')
            if relative.startswith('/') or '..' in Path(relative).parts:
                continue
            body = historical(q, task_name + '/' + relative)
            if body is not None:
                # Existence and numeric content are the two product checks.
                cards[relative] = ' '.join(sorted(gate.numbers(body)))
                path = folder / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(cards[relative])
        text = q['question'].replace(task_name + '/', 'task/') if task_name else q['question']
        assert unchecked(gate, folder, text) == expected, filename
        if filename in ('case1-843', 'case2-841'):
            matched = [sentence for _, sentence, cited, marked in gate.scope_claims(folder, text) if not cited and not marked]
            assert len(matched) == 1
            wanted = '已經開好的舊任務不會被要求補標' if filename == 'case1-843' else '舊設計會被擋下'
            assert wanted in matched[0], 'marked sentence differs from the recorded false claim'
        for summary in (None, text):
            saved, before = {}, {}
            code, _ = tests.QuestionTests().ask(text, cards=cards, summary=summary, cli=True, saved=saved)
            base_code, _ = tests.QuestionTests().ask(text, cards=cards, summary=summary, module=baseline, saved=before)
            assert code == base_code == 0, filename
            assert saved['text'].count(gate.SCOPE_MARK) - text.count(gate.SCOPE_MARK) == expected
            if summary is not None:
                assert saved['summary'].count(gate.SCOPE_MARK) - text.count(gate.SCOPE_MARK) == expected
        if filename.startswith('case1-') or filename.startswith('case2-841') and not filename.endswith('marked'):
            assert unchecked(english, folder, text) == 0
            result['falsifiers']['AC-2'] = {'candidate_marks': expected, 'english_only_marks': 0}
        if filename == 'control-849-badcite':
            assert unchecked(missing, folder, text) == 0
            result['falsifiers']['AC-3'] = {'candidate_marks': 1, 'missing_file_mutant_marks': 0}
        destination = folder / 'ask.txt'
        destination.write_text(text)
        with contextlib.redirect_stdout(io.StringIO()):
            once, = gate.scope_disclosure(folder, [(destination, text)])
            twice, = gate.scope_disclosure(folder, [(destination, once)])
        assert once == twice
        result['question_replays'].append({'case': filename, 'marks': expected, 'question_and_summary_exit': code, 'baseline_exit': base_code, 'idempotent': True})
        for relative in cards:
            (folder / relative).unlink()
    items = [json.loads(line) for line in (qdir / 'corpus-fo-session-8fcbee7d.jsonl').read_text().splitlines()]
    matches = [gate.scope_claims(root, item['question']) for item in items]
    false_times = ('2026-11-11T07:48', '2026-11-11T08:52', '2026-11-11T08:55', '2026-11-11T10:23')
    false_items = [q for q in items if any(str(q.get('asked_at', '')).startswith(t) for t in false_times)]
    corpus = {'questions': len(items), 'poc_spans': sum(len(gf.sentences(q['question'])) for q in items), 'candidate_spans': sum(len(gate.sentences(line)) for q in items for _, line in gate.prose_lines(q['question'])), 'matches': sum(len(rows) for rows in matches), 'marked_questions': sum(any(not c and not m for _, _, c, m in rows) for rows in matches), 'known_false': len(false_items), 'known_false_marked': sum(unchecked(gate, root, q['question']) > 0 for q in false_items), 'english_only_false_marks': sum(unchecked(english, root, q['question']) > 0 for q in false_items)}
    assert (corpus['questions'], corpus['poc_spans'], corpus['matches'], corpus['marked_questions'], corpus['known_false'], corpus['known_false_marked'], corpus['english_only_false_marks']) == (111, 505, 11, 9, 4, 4, 0)
    result['corpus'] = corpus
    result['falsifiers']['AC-4'] = {'candidate_false_marks': 4, 'english_only_false_marks': 0}
    for filename in ['case1-843', 'case2-841', 'control-839', 'control-849', 'control-849-cited', 'control-849-badcite', 'case2-841-marked', 'corpus-fo-session-8fcbee7d']:
        path = qdir / (filename + ('.jsonl' if filename.startswith('corpus-') else '.json'))
        command = [sys.executable, '-B', str(a.poc / 'kc-dev-flow-2/scripts/gate_facts.py'), 'scope', '--question', str(path)]
        if not filename.startswith('corpus-'):
            command += ['--state', str(a.state)]
        run = subprocess.run(command, capture_output=True, text=True)
        expected = 0 if filename in ['control-839', 'control-849-cited', 'case2-841-marked'] else 1
        assert run.returncode == expected
    result['original_scope_commands'] = {'run': 8, 'expected_exit_matched': 8}
    result['record_checks'] = {}
    q1 = json.loads((qdir / 'case1-843.json').read_text())
    record1 = historical(q1, q1['task'] + '.md')
    assert record1 and 'The idle look names a backlog task with no story record' in record1
    q2 = json.loads((qdir / 'case2-841.json').read_text())
    record2 = historical(q2, q2['task'] + '/validation-2/legacy-design.json')
    assert record2 and 'stage is validation, not ideation' in record2
    result['record_checks'] = {'contradicting_primary_records_read': 2, 'confirmations': 2, 'raw_content_retained': 0}

result['check_path'] = []
for source in ['ask', 'pr_body']:
    kwargs = {'text': tests.ScopeDisclosureTests.CASES[0]} if source == 'ask' else {'facts': {'body': tests.ScopeDisclosureTests.CASES[1]}}
    checked = tests.run_check(**kwargs)
    before = tests.run_variant(baseline, **kwargs)
    assert checked.code == before.code == 0
    assert checked.text.count(gate.SCOPE_MARK) == 1 and before.text.count(gate.SCOPE_MARK) == 0
    result['check_path'].append({'source': source, 'candidate_marks': 1, 'base_marks': 0, 'exit': 0})
result['words'] = []
for text in ['', tests.ScopeDisclosureTests.CASES[0]]:
    before = tests.run_variant(baseline, text=text)
    after = tests.run_check(text=text)
    result['words'].append({'base': len(before.out.split()), 'candidate': len(after.out.split())})
print(json.dumps(result, indent=2, ensure_ascii=False))
