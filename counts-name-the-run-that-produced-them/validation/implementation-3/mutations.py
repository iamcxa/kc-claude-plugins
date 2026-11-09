"""Run the acceptance tests against deliberate defects in disposable script copies."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

worktree, output = map(Path, sys.argv[1:])
source = worktree / 'kc-dev-flow-2/scripts'
variants = [
    ('learn-join', 'learning.py', 'if action == "add" and check_counts:', 'if False:',
     ['test_learning.LearningTests.test_evidence_count_refusal_leaves_pending_token_correctable']),
    ('number-in-file', 'delivery_gate.py', 'if contents and values <= numbers("\\n".join(contents)):', 'if contents:',
     ['test_delivery_gate.CountDisclosureTests.test_question_writes_wrong_missing_and_duplicate_disclosures_without_hold']),
    ('writer', 'delivery_gate.py', 'destination.write_text(result)', 'pass',
     ['test_delivery_gate.CountDisclosureTests.test_question_writes_wrong_missing_and_duplicate_disclosures_without_hold',
      'test_delivery_gate.CountDisclosureTests.test_check_scans_pr_body_and_rewrites_ask_idempotently']),
    ('pr-body', 'delivery_gate.py', 'gate_text + "\\n" + ((facts or {}).get("body") or "")', 'gate_text',
     ['test_delivery_gate.CountDisclosureTests.test_check_scans_pr_body_and_rewrites_ask_idempotently']),
    ('poc-writer', 'delivery_gate.py', 'destination.write_text(result)', 'pass',
     ['test_poc_readme.DeriveTests.test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes'])]
results = []
for name, file, old, new, tests in variants:
    with tempfile.TemporaryDirectory(prefix='counts-mutation-', dir=worktree / '.context') as temp:
        scripts = Path(temp) / 'kc-dev-flow-2/scripts'
        shutil.copytree(source.parent, scripts.parent, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        path = scripts / file
        text = path.read_text()
        assert text.count(old) == 1, (name, old)
        path.write_text(text.replace(old, new))
        assert not list(scripts.rglob('*.pyc'))
        command = [sys.executable, '-B', '-m', 'unittest', *tests]
        done = subprocess.run(command, cwd=scripts, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True)
        (output / (name + '.log')).write_text(done.stdout + done.stderr)
        assert done.returncode == 1 and 'FAIL:' in done.stderr and 'ERROR:' not in done.stderr, (name, done.stderr)
        assert not list(scripts.rglob('*.pyc'))
        results.append(dict(mutation=name, exit=done.returncode, tests=tests, log=name + '.log'))
print(json.dumps(dict(run=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), results=results), indent=2))
