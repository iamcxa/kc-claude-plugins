#!/usr/bin/env python3
"""Run the supplied evidence command on exported code, mapping its one git-show read."""
import argparse
import runpy
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

p = argparse.ArgumentParser()
p.add_argument('--export', required=True)
p.add_argument('--repo', required=True)
p.add_argument('--state', required=True)
a = p.parse_args()
original = subprocess.run

def read_git(argv, *args, **kwargs):
    if isinstance(argv, list) and argv[:4] == ['git', '-C', a.export, 'show']:
        argv = [*argv[:2], a.repo, *argv[3:]]
    return original(argv, *args, **kwargs)

runner = Path(a.state) / 'gate-question-facts-are-checked-before-the-captain-reads-them/implementation-1/run-evidence.py'
sys.argv = [str(runner), '--code', a.export, '--state', a.state]
with patch.object(subprocess, 'run', read_git):
    runpy.run_path(str(runner), run_name='__main__')
