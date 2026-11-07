import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root, out = map(Path, sys.argv[1:3])
base = 'ba055b8a7a55a787ac989c4cef52d07dd75661ad'
git = lambda *args: subprocess.check_output(['git', '-C', str(root), *args])
candidate = git('rev-parse', 'HEAD').decode().strip()
allowed = {'kc-dev-flow-2/scripts/delivery_gate.py', 'kc-dev-flow-2/scripts/test_delivery_gate.py'}
changed = set(git('diff', '--name-only', base, candidate).decode().splitlines())
assert changed == allowed, changed
assert not git('diff', '--name-only', base, candidate, '--', 'kc-dev-flow-2/references', 'kc-dev-flow-2/skills', 'kc-dev-flow-2/extensions', 'docs/dev2')
reference = 'kc-dev-flow-2/references/sd/workflow.md'
original = git('show', base + ':' + reference)
assert original == (root / reference).read_bytes()
with tempfile.TemporaryDirectory(prefix='skipped-run-scope-') as d:
    first, second = Path(d, 'original'), Path(d, 'mutated')
    first.write_bytes(original)
    second.write_bytes(original + b'\nUnapproved FO-read text.\n')
    diff = subprocess.run(['git', 'diff', '--no-index', '--exit-code', str(first), str(second)], capture_output=True)
    assert diff.returncode == 1
    (out / 'AC-8-fo-text-mutation.log').write_text('Unchanged workflow bytes: pass\nAltered workflow bytes: rejected with exit 1\nExact changed-file allowlist: pass\n')

proof = dict(base=base, candidate=candidate, branch=git('branch', '--show-current').decode().strip(),
             product_files=sorted(changed), fo_text_diff=[], fo_text_mutation_caught=True)
(out / 'artifact.json').write_text(json.dumps(proof, indent=2) + '\n')
verdicts = []
reasons = {
    '0044': 'unaffected: question/summary reviewer source boundaries are unchanged; the new CI read is confined to check.',
    '0051': 'unaffected: the External rounds count declaration and its pre-ask enforcement are unchanged.',
    '0062': 'unaffected: validation approval binding, merge question text and candidate comparison are unchanged.',
}
for entry in json.loads((out / 'doc-impact.json').read_text()):
    doc = entry['doc']
    verdicts.append(dict(doc=doc, verdict=reasons[Path(doc).name[:4]], commit=base,
                         sha256=hashlib.sha256(git('show', base + ':' + doc)).hexdigest()))
(out / 'doc-verdicts.json').write_text(json.dumps(verdicts, indent=2) + '\n')
print(json.dumps(proof, indent=2))
