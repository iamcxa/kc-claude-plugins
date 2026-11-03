import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
sys.path.insert(0, str(WT / 'kc-dev-flow-2/scripts'))
import test_delivery_gate as fixtures

captured = json.loads((OUT / 'response-output-cli.json').read_text())
head = subprocess.check_output(['git', '-C', str(WT), 'rev-parse', 'HEAD'], text=True).strip()
assert captured['candidate'] == head
missing = OUT / 'unrecorded-path'
assert not missing.exists()
results = []
for summary in (False, True):
    for unrecorded_path in (False, True):
        fixture = fixtures.CaptainGateTests()
        fixture.setUp()
        try:
            fixture.head = head
            fixtures.captain_record(fixture.task, head)
            report = f"```sh\n{captured['command']}\n```\n```text\n{captured['output']}\n```\n"
            if unrecorded_path:
                report += f'Inspect {missing}\n'
            fixture.task.write_text(fixtures.TASK + '\n## Stage Report: validation\n' + report)
            body = fixture.step(captured['command'], observed=captured['output'],
                                ran=f"{captured['command']}; fresh shell, {captured['time']}")
            body += fixture.step('Open the preview', observed=None, ran='none — his preview account',
                                 only='sign in — his preview account', number=2)
            code, output = fixture.ask_gate(body=body, summary=summary)
            expected = int(unrecorded_path)
            assert code == expected, output
            args = [sys.executable, '-B', str(WT / 'kc-dev-flow-2/scripts/delivery_gate.py'),
                    'question', str(fixture.task), '--text-file', str(fixture.message)]
            if summary:
                args += ['--summary-file', str(fixture.root / 'summary.txt')]
            cli = subprocess.run(args, cwd=WT, text=True, capture_output=True,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            assert cli.returncode == expected, cli.stdout + cli.stderr
            if unrecorded_path:
                assert f'S4: missing path {missing}' in cli.stdout
            else:
                assert cli.stdout == 'gate text complete\n', cli.stdout
            results.append({'summary_file': summary, 'unrecorded_path': unrecorded_path,
                            'direct_exit': code, 'cli_exit': cli.returncode, 'output': cli.stdout})
        finally:
            fixture.doCleanups()
(OUT / 'question-output-probe.json').write_text(json.dumps({
    'candidate': head, 'scope': 'Disposable gate fixtures at this Candidate, with actual locally emitted log output in the latest validation report; no live preview visit',
    'cases': results}, indent=2) + '\n')
print('PASS: question accepts captured output from the latest report in both call forms; independent missing paths hold')
