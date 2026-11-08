import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

p = argparse.ArgumentParser()
for name in ('repo', 'package', 'sd_plugin', 'workflow', 'task', 'out'):
    p.add_argument(name, type=Path)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
base = '139feeaee7ce037a0c6535568cd6bd103155cbae'
expected_head = 'f429f0fac40511c6480fd92e2cccd4c0e94b2454'
head = subprocess.check_output(['git', '-C', str(a.repo), 'rev-parse', 'HEAD'], text=True).strip()
assert head == expected_head, (head, expected_head)
checks = [
    ('adr-tests', ['python3', '-B', 'kc-adr/scripts/test_adr_lint.py']),
    ('doc-tests', ['python3', '-B', 'kc-dev-flow-2/scripts/test_adr_doc_checks.py']),
    ('native-dispatch', ['python3', '-B', 'kc-dev-flow-2/scripts/test_sd_dispatch.py', '--sd-plugin-root', a.sd_plugin]),
    ('copy-sync', ['bash', 'scripts/kc-adr-copy-sync.sh', 'check']),
    ('repository-lint-skills', ['python3', '-B', 'kc-dev-flow-2/scripts/lint-skills.py']),
    ('candidate-adr-full', ['python3', '-B', 'kc-dev-flow-2/scripts/adr_lint.py', 'docs/adr']),
    ('candidate-adr-since-required', ['python3', '-B', 'kc-dev-flow-2/scripts/adr_lint.py', 'docs/adr', '--since', base, '--require', '0064']),
    ('design-surfaces', ['python3', '-B', a.package / 'scripts/design_surfaces.py', 'check', a.task]),
    ('number-guards', ['python3', '-B', a.package / 'scripts/number_guards.py', 'check', '--workflow-dir', a.workflow, '--task', a.task, '--base', base]),
    ('comment-ratio', ['python3', '-B', a.package / 'scripts/comment_ratio.py', base, head, '--workflow-dir', a.workflow]),
    ('doc-impact', ['python3', '-B', a.package / 'scripts/doc_impact.py', base, head, '--json']),
    ('mutations-and-history', ['python3', '-B', Path(__file__).with_name('prove.py'), a.repo, a.out / 'proof']),
    ('diff-whitespace', ['git', '-C', a.repo, 'diff', '--check', base, head]),
    ('installed-adr-lint-required-check', ['python3', '-B', a.package / 'scripts/adr_lint.py', 'docs/adr', '--since', base]),
]
results = []
for name, command in checks:
    command = list(map(str, command))
    done = subprocess.run(command, cwd=a.repo, capture_output=True, text=True)
    log = a.out / (name + ('.json' if name == 'doc-impact' else '.log'))
    log.write_text(done.stdout + done.stderr)
    results.append({'name': name, 'status': 'passed' if done.returncode == 0 else 'failed',
                    'command': command, 'exit': done.returncode, 'file': str(log), 'message': str(log)})
    (a.out / 'tests.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{name}: exit {done.returncode}', flush=True)
    if done.returncode and name != 'installed-adr-lint-required-check':
        raise SystemExit(f'unexpected failure: {log}')
installed = a.package / 'scripts/adr_lint.py'
relative = 'kc-dev-flow-2/scripts/adr_lint.py'
base_bytes = subprocess.check_output(['git', '-C', str(a.repo), 'show', base + ':' + relative])
receipt = {'base': base, 'candidate': head, 'branch': subprocess.check_output(['git', '-C', str(a.repo), 'branch', '--show-current'], text=True).strip(),
           'package': str(a.package), 'installed_linter_matches_base': installed.read_bytes() == base_bytes,
           'installed_sha256': hashlib.sha256(installed.read_bytes()).hexdigest(),
           'candidate_sha256': hashlib.sha256((a.repo / relative).read_bytes()).hexdigest(),
           'candidate_checks_passed': all(r['status'] == 'passed' for r in results[:-1]),
           'required_installed_check_passed': results[-1]['status'] == 'passed',
           'limits': ['Product branch not pushed; no PR opened.', 'RoboRev and CI delegated to FO; not run.', 'CI cost per PR not measured.']}
(a.out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
raise SystemExit(0 if receipt['required_installed_check_passed'] else 1)
