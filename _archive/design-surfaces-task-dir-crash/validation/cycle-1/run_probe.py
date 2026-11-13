#!/usr/bin/env python3
"""Exercise the real checker CLI; adopter output is reduced to counts in memory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--adopter-state', type=Path, action='append', default=[])
    args = parser.parse_args()
    args.scratch.mkdir(exist_ok=False)
    args.output.mkdir(exist_ok=True, parents=True)
    archive = args.scratch / 'base.tar'
    with archive.open('wb') as stream:
        subprocess.run(['git', '-C', str(args.repository), 'archive', args.base,
                        'kc-dev-flow-2/scripts', 'kc-dev-flow-2/references',
                        'kc-dev-flow-2/skills', 'kc-dev-flow-2/extensions'],
                       stdout=stream, check=True)
    base = args.scratch / 'base'
    base.mkdir()
    with tarfile.open(archive) as stream:
        stream.extractall(base, filter='data')
    scripts = {'base': base / 'kc-dev-flow-2/scripts/design_surfaces.py',
               'probe': args.source / 'kc-dev-flow-2/scripts/design_surfaces.py'}
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}

    def run(script, cwd, name, seed):
        argv = [sys.executable, '-B', str(script), 'check',
                *(['--seed'] if seed else []), name]
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                              env=env, timeout=45)
        return {'exit': done.returncode, 'stdout': done.stdout, 'stderr': done.stderr}

    fixture = args.scratch / 'fixture'
    fixture.mkdir()
    valid = '''## Scope
Non-goals: no other checker behavior
Budget: 1 implementation and 2 validation cycles
Stop condition: same-name directory no longer crashes
## FO alignment
Surfaces: none
Visible change: none
## Design
### Worth questions
Asked: repair the recorded entrance; without: valid tasks fail; premise: bare names fail.
## Acceptance criteria
**AC-1**: the checker reads the task file.
'''
    (fixture / 'task.md').write_text(valid)
    (fixture / 'task').mkdir()
    (fixture / 'loose.md').write_text(valid)
    (fixture / 'bad.md').write_text(valid.replace('Surfaces: none', 'Surfaces: unknown'))
    (fixture / 'bad').mkdir()
    (fixture / 'exact').write_text(valid)
    (fixture / 'exact.md').write_text('invalid\n')
    (fixture / 'orphan').mkdir()
    samples = []
    for seed in (False, True):
        for name in ('task', 'task.md', 'loose', 'bad', 'bad.md', 'exact', 'orphan', 'missing.md'):
            samples.append({'argument': name, 'seed': seed,
                            **{label: run(script, fixture, name, seed)
                               for label, script in scripts.items()}})
    (args.output / 'synthetic.json').write_text(json.dumps(samples, indent=2) + '\n')

    corpora = []
    for number, root in enumerate(args.adopter_state, 1):
        tasks = sorted(p for p in root.glob('*.md') if p.name != 'README.md'
                       and (p.parent / p.stem).is_dir())
        counts = {'adopter': number, 'collision_tasks': len(tasks), 'mode_checks': 0,
                  'stable_bytes': 0, 'explicit_unchanged': 0, 'alias_matches_explicit': 0,
                  'base_alias_tracebacks': 0, 'probe_alias_tracebacks': 0,
                  'probe_passes': 0, 'probe_refusals': 0, 'unavailable': 0,
                  'historical_scope_case_files': len(list(root.rglob('followup-dispatch-records-checked.md')))}
        for task in tasks:
            for seed in (False, True):
                counts['mode_checks'] += 1
                try:
                    before = hashlib.sha256(task.read_bytes()).digest()
                    old_explicit = run(scripts['base'], root, task.name, seed)
                    old_alias = run(scripts['base'], root, task.stem, seed)
                    new_explicit = run(scripts['probe'], root, task.name, seed)
                    new_alias = run(scripts['probe'], root, task.stem, seed)
                    stable = before == hashlib.sha256(task.read_bytes()).digest()
                    counts['stable_bytes'] += stable
                    counts['explicit_unchanged'] += stable and old_explicit == new_explicit
                    counts['alias_matches_explicit'] += stable and new_explicit == new_alias
                    counts['base_alias_tracebacks'] += 'Traceback' in old_alias['stderr']
                    counts['probe_alias_tracebacks'] += 'Traceback' in new_alias['stderr']
                    counts['probe_passes'] += new_alias['exit'] == 0
                    counts['probe_refusals'] += new_alias['exit'] == 1
                except (OSError, subprocess.TimeoutExpired):
                    counts['unavailable'] += 1
        corpora.append(counts)
    (args.output / 'adopter-counts.json').write_text(json.dumps(corpora, indent=2) + '\n')
    summary = {'synthetic_commands': len(samples) * 2,
               'base_default_collision_traceback': 'IsADirectoryError' in samples[0]['base']['stderr'],
               'probe_default_collision_passes': samples[0]['probe']['exit'] == 0,
               'probe_seed_collision_passes': samples[8]['probe']['exit'] == 0,
               'base_seed_collision_refused': samples[8]['base']['exit'] == 1,
               'explicit_outputs_unchanged': all(s['base'] == s['probe'] for s in samples
                                               if s['argument'] in ('task.md', 'bad.md', 'exact')),
               'adopter_mode_checks': sum(c['mode_checks'] for c in corpora),
               'adopter_explicit_unchanged': sum(c['explicit_unchanged'] for c in corpora),
               'adopter_alias_matches': sum(c['alias_matches_explicit'] for c in corpora),
               'adopter_unavailable': sum(c['unavailable'] for c in corpora)}
    (args.output / 'probe-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if (summary['base_default_collision_traceback']
                 and summary['probe_default_collision_passes']
                 and summary['probe_seed_collision_passes']
                 and summary['explicit_outputs_unchanged']
                 and summary['adopter_unavailable'] == 0
                 and summary['adopter_mode_checks'] == summary['adopter_alias_matches']
                 == summary['adopter_explicit_unchanged']) else 1


if __name__ == '__main__':
    sys.exit(main())
