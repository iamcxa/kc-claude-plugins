import json
from pathlib import Path
import re
import subprocess
import sys
import proof

installed = Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0')
workflow = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2')
task = workflow / '.spacedock-state/diagnosis-rounds-count-toward-step-back.md'
commands = {
    'lint': [sys.executable, '-B', proof.PKG / 'scripts/lint-skills.py'],
    'adr-lint': [sys.executable, '-B', installed / 'scripts/adr_lint.py', 'docs/adr', '--since', proof.BASE, '--require', '26'],
    'number-guards': [sys.executable, '-B', installed / 'scripts/number_guards.py', 'check', '--repo', proof.WT,
                      '--workflow-dir', workflow, '--base', proof.BASE, '--head', 'HEAD', '--task', task],
    'comment-ratio': [sys.executable, '-B', installed / 'scripts/comment_ratio.py', proof.BASE, 'HEAD', '--workflow-dir', workflow],
    'doc-impact': [sys.executable, '-B', installed / 'scripts/doc_impact.py', proof.BASE, 'HEAD', '--repo', proof.WT, '--json'],
}
results = []
for name, args in commands.items():
    done = proof.run(*args)
    (proof.OUT / f'{name}.log').write_text(done.stdout + done.stderr)
    if name == 'doc-impact' and done.returncode == 0:
        (proof.OUT / 'doc-impact.json').write_text(done.stdout)
    results.append({'name': name, 'status': 'passed' if done.returncode == 0 else 'failed',
                    'message': f'exit {done.returncode}', 'command': list(map(str, args))})
    print(f'{name}: exit {done.returncode}', flush=True)
(proof.OUT / 'checks.json').write_text(json.dumps(results, indent=2))
if '--checks-only' in sys.argv:
    assert all(row['status'] == 'passed' for row in results), results
    sys.exit(0)
log = (proof.OUT / 'full-suite.log').read_text()
summary = re.search(r'Ran (\d+) tests in ([\d.]+)s\s+OK(?: \(skipped=(\d+)\))?', log)
assert summary, log[-5000:]
(proof.OUT / 'suite.json').write_text(json.dumps([{'name': 'Full package unittest discovery', 'status': 'passed',
    'message': f'{summary[1]} tests; {summary[3] or 0} skipped; 0 failures; {summary[2]}s'}], indent=2))
assert all(row['status'] == 'passed' for row in results), results
