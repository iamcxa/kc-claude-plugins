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

root, base, out = map(lambda s: Path(s).resolve(), sys.argv[1:4])
out.mkdir(parents=True, exist_ok=True)
scripts = root / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('test_delivery_gate', scripts / 'test_delivery_gate.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
attr = '🤖 Generated with [Claude Code](https://claude.com/claude-code)'
url = 'https://claude.com/claude-code'
other = 'https://preview.example.test/owner'
fixture = t.TaskFolderCaptainTests()
fixture.setUp()
rows = []
try:
    card = fixture.folder / 'review/pr-body.md'
    card.parent.mkdir()
    cases = [
        ('attribution', attr, '', False, 0, 1, []),
        ('surrounding-spaces', ' \t' + attr + '  ', '', False, 0, 1, []),
        ('internal-spaces', attr.replace(' ', '\t  '), '', False, 0, 1, []),
        ('captain-link-unrecorded', 'Open ' + other, '', False, 1, 1, [other]),
        ('captain-link-recorded', 'Open ' + other, '', True, 0, 0, []),
        ('attribution-url-card', 'Open ' + url, '', False, 1, 1, [url]),
        ('attribution-url-message', 'No links', ' Open ' + url, False, 1, 1, [url]),
        ('attribution-plus-link', attr + ' ' + other, '', False, 1, 1, [url, other]),
        ('attribution-prefix', 'Open ' + attr, '', False, 1, 1, [url]),
        ('attribution-suffix', attr + ' please', '', False, 1, 1, [url]),
        ('other-url', attr + '\nOpen ' + other, '', False, 1, 1, [other]),
    ]
    for name, content, extra, recorded, expected, expected_base, links in cases:
        card.write_text(content + '\n')
        body = fixture.step('Review this candidate.')
        if recorded:
            body += fixture.step('Open ' + other, number=2)
        fixture.run_question(message='Review this candidate. Read review/pr-body.md' + extra, body=body)
        for route in ['steps', 'question']:
            for label, tree, want in [('base', base, expected_base), ('candidate', root, expected)]:
                cmd = [sys.executable, '-B', str(tree / 'kc-dev-flow-2/scripts/delivery_gate.py'), route]
                cmd += [str(fixture.saved if route == 'steps' else fixture.task), '--text-file', str(fixture.message)]
                if route == 'question': cmd += ['--workflow-dir', str(fixture.state)]
                run = subprocess.run(cmd, cwd=fixture.repo, text=True, capture_output=True)
                log = f'{name}-{route}-{label}.log'
                (out / log).write_text(run.stdout + run.stderr)
                assert run.returncode == want, (name, route, label, run.stdout, run.stderr)
                if label == 'candidate':
                    for link in links:
                        # question deliberately presents the first failing step only.
                        if route == 'steps' or link == links[0]: assert link in run.stdout, (name, route, run.stdout)
                    if not want: assert 'S5' not in run.stdout, run.stdout
                    if name == 'other-url': assert url not in run.stdout, run.stdout
                rows.append({'case': name, 'route': route, 'revision': label, 'exit': run.returncode, 'words': len(run.stdout.split()), 'log': log})
    for route in ['question', 'steps']:
        assert (out / f'captain-link-unrecorded-{route}-candidate.log').read_bytes() == (out / f'captain-link-unrecorded-{route}-base.log').read_bytes()
    (out / 'cli-matrix.json').write_text(json.dumps(rows, indent=2))

    # Reuse the candidate's behavioral assertions to detect overbroad exemptions.
    methods = ['test_named_card_prose_link_matches_asked_and_holds_when_unrecorded']
    mutant = t.variant_of('for item in required_commands + links(coverage_text):', 'for item in required_commands:')
    capture = io.StringIO()
    with mock.patch.object(t, 'gate', mutant):
        result = unittest.TextTestRunner(stream=capture, verbosity=2).run(unittest.TestSuite(t.CaptainStepsTests(method) for method in methods))
    (out / 'captain-link-mutation.log').write_text(capture.getvalue())
    assert result.failures and not result.errors, capture.getvalue()

    card.write_text(attr + '\n')
    fixture.run_question(message='Review this candidate. Read review/pr-body.md')
    filtering = '    text = "\\n".join("" if normalized(line) in ATTRIBUTION else line for line in text.splitlines())\n'
    removed = t.variant_of(filtering, '')
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        code = removed.main(['question', str(fixture.task), '--text-file', str(fixture.message), '--workflow-dir', str(fixture.state)])
    (out / 'question-removed-exemption.log').write_text(capture.getvalue())
    assert code == 1 and url in capture.getvalue()

    changed_output = t.variant_of('emit("gate text complete", ASK_FORM)', 'emit("gate text complete changed", ASK_FORM)')
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        code = changed_output.main(['question', str(fixture.task), '--text-file', str(fixture.message), '--workflow-dir', str(fixture.state)])
    (out / 'output-drift-mutation.log').write_text(capture.getvalue())
    assert code == 0 and len(capture.getvalue().split()) == 98
    assert len((out / 'attribution-question-candidate.log').read_text().split()) == 97

    base_module = types.ModuleType('baseline')
    base_module.__file__ = t.gate.__file__
    exec(compile((base / 'kc-dev-flow-2/scripts/delivery_gate.py').read_text(), t.gate.__file__, 'exec'), base_module.__dict__)
    capture = io.StringIO()
    with mock.patch.object(t, 'gate', base_module):
        result = unittest.TextTestRunner(stream=capture, verbosity=2).run(unittest.TestSuite(t.CaptainStepsTests(method) for method in ['test_pr_body_attribution_line_needs_no_recorded_link_step', 'test_pr_body_other_url_still_needs_a_recorded_link_step']))
    (out / 'baseline-regressions.log').write_text(capture.getvalue())
    assert result.failures and not result.errors
finally:
    fixture.doCleanups()
print('PASS: 44 real CLI runs; base/candidate paired for every case on both routes.')
print('PASS: AC-1 removed-filter question, AC-2 lost-link detection, AC-4 baseline and AC-6 output-drift falsifiers caught.')
