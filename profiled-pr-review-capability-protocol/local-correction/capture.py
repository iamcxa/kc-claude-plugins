"""Capture this local batch's immutable comparison and complete denominator."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

product = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot')
state = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/docs/dev/.spacedock-state')
target = state / 'profiled-pr-review-capability-protocol/local-correction'
scratch = Path('/tmp/capability-correction.CGT81m')
base = '3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8'
head = '9bb526170156a44cff90e2a2fab9eeab081e0eb1'

def git(*args):
    return subprocess.check_output(['git', '-C', str(product), *args])

assert git('rev-parse', 'HEAD').decode().strip() == head
assert git('branch', '--show-current').decode().strip() == 'feature/kc-pr-review-capability-protocol-pilot'
target.mkdir(exist_ok=True)
numstat = git('diff', '--numstat', base)
focused = {
    'kc-pr-flow/schemas/review-capability-catalog-v1.json',
    'kc-pr-flow/schemas/review-capability-v1.schema.json',
    'kc-pr-flow/scripts/review-capability.test.py',
    'kc-pr-flow/scripts/review-capability-corpus.tsv',
    'kc-pr-flow/scripts/review-runtime.test.sh',
    'kc-pr-flow/scripts/review-ablation.test.sh',
}
rows = []
for line in numstat.decode().splitlines():
    added, deleted, path = line.split('\t')
    rows.append(dict(path=path, added=int(added), deleted=int(deleted), focused=path in focused,
                     sha256=hashlib.sha256((product / path).read_bytes()).hexdigest()))
total = sum(row['added'] + row['deleted'] for row in rows)
focus = sum(row['added'] + row['deleted'] for row in rows if row['focused'])
batch = git('diff', '--binary', head)
cumulative = git('diff', '--binary', base)
manifest = dict(base=base, product_head=head, candidate='uncommitted working tree',
                branch='feature/kc-pr-review-capability-protocol-pilot',
                total=total, files=len(rows), focused=focus, limits=[6600, 20, 1800],
                focused_excess=focus - 1800,
                batch_diff_sha256=hashlib.sha256(batch).hexdigest(),
                cumulative_diff_sha256=hashlib.sha256(cumulative).hexdigest(), rows=rows,
                changed_batch_paths=git('diff', '--name-only', head).decode().splitlines(),
                untracked=git('ls-files', '--others', '--exclude-standard').decode().splitlines(),
                unchanged_owners={path: hashlib.sha256((product / path).read_bytes()).hexdigest()
                                  for path in ('kc-pr-flow/scripts/review-runtime.sh',
                                               'kc-pr-flow/scripts/review-runtime.test.sh')})
assert manifest['untracked'] == []
(target / 'counts.json').write_text(json.dumps(manifest, indent=2) + '\n')
(target / 'cumulative-numstat.tsv').write_bytes(numstat)
(target / 'batch.patch').write_bytes(batch)
for name in ['protocol.log', 'ablation.log', 'mutations.py', 'mutations.json',
             'admission-unit-red.log', 'admission-planner-red.log', 'adjudication-unit-red.log',
             'seal-repeat-red.log', 'compare-repeat-red.log']:
    shutil.copyfile(scratch / name, target / name)
shutil.copyfile(__file__, target / 'capture.py')
print(json.dumps({key: manifest[key] for key in ('total', 'files', 'focused', 'focused_excess',
                                               'batch_diff_sha256', 'cumulative_diff_sha256')}))
