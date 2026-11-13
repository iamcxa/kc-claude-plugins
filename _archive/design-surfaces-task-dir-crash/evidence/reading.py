#!/usr/bin/env python3
"""Count named lifecycle passages equally; do not call these full runtime totals."""
import argparse
import json
from pathlib import Path
import re
import subprocess


def section(text, heading):
    start = text.index(heading)
    match = re.search(r'\n## ', text[start + len(heading):])
    end = start + len(heading) + match.start() if match else len(text)
    return text[start:end].strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prefix = 'kc-dev-flow-2/'
    paths = ['references/sd/workflow.md', 'references/sd/mods/kc-dev-flow-2.md',
             'skills/dev/SKILL.md', 'extensions/learn/EXTENSION.md']
    versions = []
    for base in (True, False):
        texts = {p: (subprocess.run(['git', '-C', str(args.source), 'show',
                                    args.base + ':' + prefix + p], capture_output=True,
                                   text=True, check=True).stdout if base
                     else (args.source / prefix / p).read_text()) for p in paths}
        wf, mod = texts[paths[0]], texts[paths[1]]
        passages = {
            'startup': wf + texts[paths[2]] + mod,
            'idle_open_PR': section(mod, '## Hook: idle') + section(wf, '## Delivery authority') + section(wf, '## Extensions'),
            'idle_merged_PR': section(mod, '## Hook: idle') + section(wf, '## Delivery authority') + section(wf, '## Extensions'),
            'after_archive': section(mod, '## Hook: idle') + texts[paths[3]],
            'merge_ask': section(wf, '## Captain steps') + section(wf, '## Delivery authority') + section(wf, '## Extensions'),
        }
        versions.append((texts, passages))
    old, new = versions
    report = {'method': 'len(text.split()), same named passage inventory on base and probe',
              'scope': 'Package-owned instructions only. Upstream pr-merge and ordinary dynamic outputs are unchanged but not included in these totals. Optional learn reference included in after_archive on both sides.',
              'passage_files': paths,
              'all_passage_files_byte_identical': old[0] == new[0],
              'moments': [{'name': name, 'before': len(old[1][name].split()),
                           'after': len(text.split()),
                           'delta': len(text.split()) - len(old[1][name].split())}
                          for name, text in new[1].items()]}
    samples = json.loads((args.output.parent / 'synthetic.json').read_text())
    report['design_gate_command_output'] = [
        {'seed': seed, 'before': sum(len(samples[index]['base'][k].split()) for k in ('stdout', 'stderr')),
         'after': sum(len(samples[index]['probe'][k].split()) for k in ('stdout', 'stderr'))}
        for seed, index in ((False, 0), (True, 8))]
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
