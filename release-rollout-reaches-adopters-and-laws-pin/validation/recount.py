from pathlib import Path
import ast
import json
import subprocess

root = Path('/tmp/rollout-validation-838')
out = root / 'evidence'

def section(text, start, end=None):
    value = text[text.index(start):]
    return value[:value.index(end)] if end else value

records = []
for rev in ['base', 'candidate']:
    p = root / rev
    read = lambda f: (p / f).read_text()
    adoption = read('kc-dev-flow-2/references/sd/adoption.md')
    install = 'Roll it out once per adopter' if rev == 'base' else "Install on the Captain's word"
    spans = {
        'post-merge': section(read('CLAUDE.md'), '### Post-merge', '## Commit / PR Conventions'),
        'release-skill': read('kc-plugin-forge/skills/kc-plugin-release/SKILL.md'),
        'observe-adopters': section(read('kc-dev-flow-2/skills/maintain-flow/SKILL.md'), '## Observe adopters'),
        'laws-install-paragraph': section(adoption, install, '\n\n'),
        'workflow': read('kc-dev-flow-2/references/sd/workflow.md'),
    }
    for name, text in spans.items():
        count = len(text.split())
        wc = int(subprocess.check_output(['wc', '-w'], input=text, text=True).strip())
        assert count == wc
        records.append({'revision': rev, 'section': name, 'words': count, 'independent_wc': wc})

files = ['kc-dev-flow-2/references/sd/workflow.md', 'kc-dev-flow-2/scripts/pr_watch.py',
         'kc-dev-flow-2/scripts/delivery_gate.py', 'kc-dev-flow-2/scripts/dispatch_records.py']
assert all((root/'base'/x).read_bytes() == (root/'candidate'/x).read_bytes() for x in files)
for text in [(root / rev / 'kc-dev-flow-2/scripts/test_package_version.py').read_text() for rev in ['base', 'candidate']]:
    tree = ast.parse(text)
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'PackageVersionTest')
    methods = {x.name: ast.get_source_segment(text, x) for x in cls.body if isinstance(x, ast.FunctionDef)}
    if 'base_methods' not in globals():
        base_methods = methods
    else:
        assert methods == base_methods

result = {'sections': records, 'unchanged_lifecycle_files': files, 'legacy_test_methods_unchanged': True,
          'unchanged_moment_deltas': {'startup': 0, 'idle-open-PR': 0, 'idle-merged-PR': 0, 'after-archive': 0, 'merge-ask': 0}}
(out / 'word-counts.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
