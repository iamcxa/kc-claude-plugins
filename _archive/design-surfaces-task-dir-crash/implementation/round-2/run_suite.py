#!/usr/bin/env python3
"""Run the package workflow's Python checks without downloading/installing tools."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--temp', type=Path, required=True)
    parser.add_argument('--sd-plugin-root', type=Path, required=True)
    args = parser.parse_args()
    args.temp.mkdir(exist_ok=False)
    logs = args.output / 'suite-logs'
    logs.mkdir(exist_ok=True)
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': str(args.temp),
           'SPACEDOCK_BIN': '/Users/kent/.local/bin/spacedock'}
    workflow = args.source / '.github/workflows/kc-dev-flow-2-tests.yml'
    commands = []
    for line in workflow.read_text().splitlines():
        match = re.match(r'\s+run: (?:SPACEDOCK_BIN="[^"]+" )?python3 (?:-B )?(kc-dev-flow-2/\S+\.py)(.*)$', line)
        if not match:
            continue
        script, tail = match.groups()
        extra = ['--sd-plugin-root', str(args.sd_plugin_root)] if script.endswith('test_sd_dispatch.py') else shlex.split(tail)
        commands.append([sys.executable, '-B', script, *extra])
    results = []
    for argv in commands:
        path = argv[2]
        log = logs / (path.replace('/', '__') + '.txt')
        timed_out = False
        with log.open('w') as stream:
            try:
                done = subprocess.run(argv, cwd=args.source, env=env, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=180)
                code = done.returncode
            except subprocess.TimeoutExpired:
                code, timed_out = 124, True
        raw = log.read_text(errors='replace')
        totals = re.findall(r'^Ran (\d+) tests? in ', raw, re.M)
        skip = re.findall(r'^OK \(skipped=(\d+)\)', raw, re.M)
        item = {'name': path, 'status': 'passed' if code == 0 else 'failed',
                'command': argv, 'exit': code, 'timeout': timed_out,
                'test_total': int(totals[-1]) if totals else None,
                'skipped': int(skip[-1]) if skip else 0, 'output': str(log.relative_to(args.output))}
        results.append(item)
        print(json.dumps(item), flush=True)
        (args.output / 'suite-results.json').write_text(json.dumps(results, indent=2) + '\n')
    summary = {'commands': len(results), 'passed_commands': sum(x['exit'] == 0 for x in results),
               'unittest_total': sum(x['test_total'] or 0 for x in results),
               'unittest_skipped': sum(x['skipped'] for x in results),
               'commands_without_unittest_total': [x['name'] for x in results if x['test_total'] is None],
               'CI_environment_equivalent': False,
               'limit': 'Local macOS uses the loaded Spacedock 0.28.0 source with launcher 0.27.2; hosted CI pins its own source/runtime. No install/download step is run.'}
    (args.output / 'suite-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)
    return 0 if summary['commands'] and summary['commands'] == summary['passed_commands'] else 1


if __name__ == '__main__':
    sys.exit(main())
