#!/usr/bin/env python3
"""Count tasks whose implementation/validation dispatch records pass the cycle bound their Budget line states.

Usage: overrun_holds.py <state root>...  (a root is a checkout or `git archive` extract of a state branch)
Counts come from `<task>/dispatch/<stage>-<n>.md` names; the bound from budget_bound.parse(). Questions = one per
task at the first overrun (a Captain raise is not modelled, so this is a floor on questions for over-budget tasks).
"""
import collections, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from budget_bound import parse
for r in sys.argv[1:]:
    root = pathlib.Path(r); tot = par = held = 0; firsts = collections.Counter()
    for base in (root, root / "_archive"):
        for d in sorted(base.iterdir()) if base.exists() else []:
            dd = d / "dispatch"
            if not dd.is_dir(): continue
            tf = base / (d.name + ".md")
            if not tf.exists(): tf = d / "index.md"
            if not tf.exists(): continue
            L = tf.read_text(errors="replace").split("\n"); b = None
            for i, l in enumerate(L):
                if re.match(r"^## Budget\s*$", l): b = next((x.strip() for x in L[i+1:i+6] if x.strip()), ""); break
                m = re.match(r"^(?:- )?Budget:\s*(.*)", l)
                if m: b = m.group(1); break
            if b is None: continue
            recs = [(m.group(1), int(m.group(2))) for f in dd.iterdir()
                    for m in [re.match(r"^(implementation|validation)-(\d+)\.md$", f.name)] if m]
            if not recs: continue
            tot += 1; p = parse(b)
            if not p: continue
            par += 1
            over = [(s, n) for s, n in recs if s in p and n > p[s]]
            if over: held += 1; firsts[min(over, key=lambda x: (x[1], x[0]))] += 1
    print(f"{root}: with impl/val records and a Budget line {tot}; cycle bound read {par}; held at first overrun {held}; first hold at {dict(firsts)}")
