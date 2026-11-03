from concurrent.futures import ThreadPoolExecutor
import json
import re
import subprocess
from pathlib import Path
import os
import proof

source = Path(os.environ.get('DIAGNOSIS_STATE_SOURCE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'))
readme = source.parent / 'README.md'
revision = proof.git(source, 'rev-parse', 'HEAD').strip()
target = proof.OUT / 'corpus-state'
if not target.exists():
    done = proof.run('git', 'clone', '--shared', '--no-checkout', source, target)
    assert done.returncode == 0, done.stderr
proof.git(target, 'checkout', '--detach', revision)
paths = proof.git(target, 'ls-tree', '-r', '--name-only', revision).splitlines()
folders = sorted({path.split('/dispatch/')[0] for path in paths if '/dispatch/' in path and path.endswith('.md')})
jobs = []
for name in folders:
    folder = target / name
    jobs.append((name, 'folder', ['--readme', readme, folder]))
    newest = {}
    for record in (folder / 'dispatch').glob('*.md'):
        match = re.fullmatch(r'(implementation|validation)-([1-9][0-9]*)(?:-message-([1-9][0-9]*))?\.md', record.name)
        if match and (int(match[2]), int(match[3] or 0)) > newest.get(match[1], ((0, 0), None))[0]:
            newest[match[1]] = ((int(match[2]), int(match[3] or 0)), record)
    for stage, (_, record) in newest.items():
        jobs.append((name, f'{stage} names', ['--names', record]))
        jobs.append((name, f'{stage} strict', ['--names', '--strict', record]))


def compare(job):
    name, mode, args = job
    before = proof.cli(proof.OLD, 'dispatch_records.py', *args)
    after = proof.cli(proof.PKG, 'dispatch_records.py', *args)
    assert before.stdout == after.stdout, (job, before.stdout, after.stdout)
    lines = [line for line in after.stderr.splitlines() if line not in before.stderr.splitlines()]
    assert all("no 'Symptom:' line" in line for line in lines), (job, lines)
    changed = before.returncode != after.returncode
    if changed:
        assert 'strict' in mode and lines and before.returncode == 0 and after.returncode == 1, (job, before, after)
    return {'task': name, 'mode': mode, 'base_exit': before.returncode, 'candidate_exit': after.returncode,
            'verdict_changed': changed, 'new_hints': lines, 'stdout': after.stdout}


with ThreadPoolExecutor(max_workers=6) as pool:
    rows = list(pool.map(compare, jobs))
report = {'source_revision': revision, 'task_folders': len(folders), 'runs': len(rows),
          'strict_holds_added': sum(row['verdict_changed'] for row in rows),
          'stdout_changes': 0, 'unexpected_changes': 0, 'rows': rows}
(proof.OUT / 'corpus.json').write_text(json.dumps(report, indent=2))
print({key: value for key, value in report.items() if key != 'rows'})
