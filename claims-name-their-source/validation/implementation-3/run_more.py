#!/usr/bin/env python3
"""AC-7 top-up: reps 4-6 of the candidate arm for P and K, same run_one as implementation-2."""
import concurrent.futures
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('replay', Path(__file__).with_name('replay.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cells = [(s, 'candidate', 'claude', r) for s in ('P', 'K') for r in (4, 5, 6)]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(lambda a: m.run_one(*a, normal=True), cells))
