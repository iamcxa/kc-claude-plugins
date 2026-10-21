#!/usr/bin/env python3
"""Effect of the two narrowed rule-4 lines on the shipped test suite (cycle 3): which pinned assertions the implementation must update.

Usage: python3 -B proto_narrow.py <package scripts dir>      (measured 3m22s, 68 tests in four parallel copies; writes only under a temp directory it removes)
Copies the 0.26.0 scripts four times and applies to each copy none (base), the ASK sentence, the `(verdict ask)` class tag, or both,
runs `unittest test_delivery_gate` in each in parallel and prints, per copy, the failing test methods with their failure counts.
A failure is a test that pins the 0.26.0 string; the base copy must pass (68 tests), or the run prints BASE FAILED and stops.
"""
import collections, re, shutil, subprocess, sys, tempfile
from pathlib import Path
pkg = Path(sys.argv[1])
SENTENCE = ' Every other PR, the Release PR included, is asked one at a time.'
ASK_OLD, ASK_NEW = 'else ask for merge with this text."', 'else ask for merge with this text.' + SENTENCE + '"'
TAG_OLD = 'emit(*points, f"class: {cls}")'
TAG_NEW = 'emit(*points, f"class: {cls}" + (" (verdict ask)" if verdict == "ask" else ""))'


def patched(dest, ask, tag):
    shutil.copytree(pkg, dest)
    f = dest / "delivery_gate.py"
    s = f.read_text()
    for old, new, on in ((ASK_OLD, ASK_NEW, ask), (TAG_OLD, TAG_NEW, tag)):
        assert s.count(old) == 1, old
        if on:
            s = s.replace(old, new)
    f.write_text(s)


with tempfile.TemporaryDirectory() as tmp:
    jobs = {}
    for name, ask, tag in (("base", False, False), ("ask sentence only", True, False), ("class tag only", False, True), ("both", True, True)):
        d = Path(tmp) / name.replace(" ", "_")
        patched(d, ask, tag)
        jobs[name] = subprocess.Popen([sys.executable, "-B", "-m", "unittest", "test_delivery_gate"], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for name, job in jobs.items():
        out = job.communicate()[0]
        ran = re.search(r"Ran (\d+) tests", out).group(1)
        fails = collections.Counter(re.sub(r" \(.*", "", m) for m in re.findall(r"^FAIL: (\S+ \(.*)$", out, re.M))
        print(f"{name}: ran {ran}, failures {sum(fails.values())} in {len(fails)} test methods")
        for method, n in sorted(fails.items()):
            print(f"   {n:3d}  {method}")
        if name == "base" and fails:
            print("BASE FAILED"); break
