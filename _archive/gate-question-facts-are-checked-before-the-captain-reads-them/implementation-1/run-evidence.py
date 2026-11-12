#!/usr/bin/env python3
"""Replay the supplied questions; publish aggregates, never their text."""
import argparse
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--code', type=Path, required=True)
parser.add_argument('--state', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.code / 'kc-dev-flow-2/scripts'))
import test_delivery_gate as tests
g = tests.gate
questions = args.state / 'gate-question-facts-are-checked-before-the-captain-reads-them/ideation-1/questions'
scratch = Path(tempfile.mkdtemp(prefix='impl-gate-question-facts-'))
result = {'scratch_removed': str(scratch), 'fixtures': {}, 'mutations': {}}

def flags(module, folder, text):
    return sum(not cited and not marked for _, _, cited, marked in module.scope_claims(folder, text))

def snapshot_cards(q):
    cards = {}
    for cited in g.SAVED_FILE.findall(q['question']):
        name = cited.removeprefix(q.get('task', '') + '/')
        if name.startswith('/') or '..' in Path(name).parts:
            continue
        lookup = q.get('task', '') + '/' + name
        done = subprocess.run(['git', '-C', str(args.state), 'show', q['state_commit_before_ask'] + ':' + lookup],
                              capture_output=True, text=True)
        if done.returncode == 0:
            cards[name] = done.stdout
    return cards

try:
    english = tests.variant_of('EXISTING.search(sentence)', "re.search(r'\\bexisting\\b', sentence, re.I)")
    no_exists = tests.variant_of('and path.is_file():', 'and True:')
    no_scan = tests.variant_of('rows = scope_claims(folder, text)', 'rows = []')
    false_fixture = None
    for filename, expected in [('case1-843', 1), ('case2-841', 1), ('control-839', 0), ('control-849', 1),
                               ('control-849-cited', 0), ('control-849-badcite', 1), ('case2-841-marked', 0)]:
        q = json.loads((questions / (filename + '.json')).read_text())
        text = q['question']
        cards = snapshot_cards(q)
        folder = scratch / filename
        folder.mkdir()
        for name, body in cards.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        # The runtime folder has an anonymous name; preserve slug-prefixed citation resolution.
        text = text.replace(q.get('task', '') + '/', folder.name + '/')
        actual = flags(g, folder, text)
        assert actual == expected, filename
        targets = {'case1-843': '已經開好的舊任務不會被要求補標', 'case2-841': '舊設計會被擋下'}
        if filename in targets:
            assert targets[filename] in g.scope_claims(folder, text)[0][1], filename
        dest = folder / 'ask.txt'
        dest.write_text(text)
        with contextlib.redirect_stdout(io.StringIO()):
            written, = g.scope_disclosure(folder, [(dest, text)])
            repeated, = g.scope_disclosure(folder, [(dest, written)])
        assert written == repeated
        assert written.count(g.SCOPE_MARK) - text.count(g.SCOPE_MARK) == expected
        # Exercise the real question CLI with valid, generic gate metadata.
        saved = {}
        anonymous = text.replace(folder.name + '/', 'task/')
        code, _ = tests.QuestionTests().ask(anonymous, cards=cards, cli=True, saved=saved)
        baseline, _ = tests.QuestionTests().ask(anonymous, cards=cards, module=no_scan)
        assert code == baseline, filename
        assert saved['text'].count(g.SCOPE_MARK) - anonymous.count(g.SCOPE_MARK) == expected, filename
        result['fixtures'][filename] = {'claims_needing_mark': actual, 'marks_written': expected,
                                        'question_exit': code, 'baseline_exit': baseline, 'idempotent': True}
        if filename == 'case1-843':
            false_fixture = (folder, text)
        if filename == 'control-849-badcite':
            result['mutations']['missing_file'] = {'candidate_marks': actual, 'mutant_marks': flags(no_exists, folder, text)}

    corpus_file = questions / 'corpus-fo-session-8fcbee7d.jsonl'
    items = [json.loads(line) for line in corpus_file.read_text().splitlines()]
    rows = [g.scope_claims(scratch, q['question']) for q in items]
    false_times = ('2026-11-11T07:48', '2026-11-11T08:52', '2026-11-11T08:55', '2026-11-11T10:23')
    false_items = [q for q in items if any(str(q.get('asked_at', '')).startswith(t) for t in false_times)]
    legacy = lambda text: [s.strip(' ，,') for s in re.split(r'[。；;？?]|(?:[一二三四五六七八九十]、)', re.split('Squash merge', text)[0]) if len(s.strip()) > 6]
    result['corpus'] = {'questions': len(items), 'poc_sentences': sum(len(legacy(q['question'])) for q in items),
                        'candidate_sentences': sum(len(g.sentences(line)) for q in items for _, line in g.prose_lines(q['question'])),
                        'claims': sum(map(len, rows)), 'flagged_questions': sum(any(not c and not m for _, _, c, m in rs) for rs in rows),
                        'known_false_questions': len(false_items),
                        'known_false_marked': sum(flags(g, scratch, q['question']) > 0 for q in false_items),
                        'english_mutant_known_false_marked': sum(flags(english, scratch, q['question']) > 0 for q in false_items)}
    assert result['corpus']['questions'] == 111 and result['corpus']['claims'] == 11
    assert result['corpus']['flagged_questions'] == 9
    assert len(false_items) == 4 and result['corpus']['known_false_marked'] == 4
    result['mutations']['english_only'] = {'candidate_marks': flags(g, *false_fixture), 'mutant_marks': flags(english, *false_fixture)}
    for name, values in result['mutations'].items():
        observed = io.StringIO()
        def acceptance(v=values):
            assert v['mutant_marks'] == v['candidate_marks'], 'warning lost'
        suite = unittest.TestSuite([unittest.FunctionTestCase(acceptance)])
        run = unittest.TextTestRunner(stream=observed).run(suite)
        values['acceptance_failures'] = len(run.failures)
        values['killed'] = not run.wasSuccessful()
        assert values['killed'], name
    # The same real check path includes the PR body, using read-only gh fixtures.
    with contextlib.redirect_stdout(io.StringIO()):
        checked = tests.run_check(facts={'body': tests.ScopeDisclosureTests.CASES[0]})
        base = tests.run_variant(tests.variant_of('external = scope_claims(folder, extra)', 'external = []'),
                                 facts={'body': tests.ScopeDisclosureTests.CASES[0]})
    assert checked.code == base.code == 0 and g.SCOPE_MARK in checked.text and g.SCOPE_MARK not in base.text
    result['check_pr_body'] = {'candidate_exit': checked.code, 'baseline_exit': base.code, 'marks_written': checked.text.count(g.SCOPE_MARK)}
    baseline = types.ModuleType('baseline_delivery_gate')
    baseline.__file__ = g.__file__
    source = subprocess.run(['git', '-C', str(args.code), 'show',
                             'd79053d0836c558a9269f9cf1ba222933935b820:kc-dev-flow-2/scripts/delivery_gate.py'],
                            check=True, capture_output=True, text=True).stdout
    exec(compile(source, g.__file__, 'exec'), baseline.__dict__)
    result['reading_words'] = {}
    for label, text in [('no_match', ''), ('marked_claim', tests.ScopeDisclosureTests.CASES[0])]:
        original = tests.run_variant(baseline, text=text)
        candidate = tests.run_check(text=text)
        result['reading_words'][label] = {'base': len(original.out.split()), 'candidate': len(candidate.out.split()),
                                           'delta': len(candidate.out.split()) - len(original.out.split()),
                                           'base_marks': original.text.count(g.SCOPE_MARK), 'candidate_marks': candidate.text.count(g.SCOPE_MARK)}
        assert original.code == candidate.code == 0
    assert result['reading_words']['no_match']['delta'] == 0
    assert result['reading_words']['marked_claim']['base_marks'] == 0
    assert result['reading_words']['marked_claim']['candidate_marks'] == 1
    result['not_run'] = {'AC-1': 'FO: held-and-closed candidate will not exist in this dispatch; it waits for another task merge',
                         'second_corpus': 'No authorized independent corpus; FO confirms not verified',
                         'captain_answers': 'No observed use; FO confirms not verified',
                         'plain_dialog': 'No script on that path; owned by held-and-closed listing',
                         'model_reader': 'Excluded by approved design, not rerun'}
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps(result, indent=2, ensure_ascii=False))
