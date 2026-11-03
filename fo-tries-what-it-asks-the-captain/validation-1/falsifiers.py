import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
OUT = Path(__file__).resolve().parent
for cache in (WT / 'kc-dev-flow-2').rglob('__pycache__'):
    shutil.rmtree(cache)
run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'kc-dev-flow-2/scripts', '-p', 'test_delivery_gate.py', '-k', 'Captain', '-v'], cwd=WT, text=True, capture_output=True)
(OUT / 'mutation-tests.log').write_text(run.stdout + run.stderr)
assert run.returncode == 0, run.stderr
with tempfile.TemporaryDirectory() as temp:
    copied = Path(temp) / 'kc-dev-flow-2'
    shutil.copytree(WT / 'kc-dev-flow-2', copied, ignore=shutil.ignore_patterns('__pycache__'))
    path = copied / 'skills/observer/SKILL.md'
    path.write_text(path.read_text().replace('<!-- chat-only-rules -->', '<!-- chat-only-rules -->\n- presents every step in full beside its observed output'))
    spec = importlib.util.spec_from_file_location('lint', copied / 'scripts/lint-skills.py')
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)
    errors = lint.lint_tree(copied)
    expected = "chat-only rule 'presents every step in full beside its observed output' is not in references/sd/workflow.md"
    assert any(expected in error for error in errors), errors
    (OUT / 'observer-mutation.json').write_text(json.dumps({'mutation': 'Restore removed acceptance phrase in chat-only list', 'expected': expected, 'errors': errors, 'status': 'passed'}, indent=2) + '\n')
print('PASS: step and gate mutations executed from source with caches removed; restoring observer phrase is rejected')
