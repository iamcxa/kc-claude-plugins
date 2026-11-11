#!/usr/bin/env python3
"""Archived kc-dev-flow-2 tasks of one state root: implementation-record cycle counts and today's two role events.

Usage: KC_DEV_FLOW_2_SCRIPTS=<package>/scripts python3 archive_counts.py <state root>
"""
import os, pathlib, re, sys
sys.path.insert(0, os.environ["KC_DEV_FLOW_2_SCRIPTS"])
import role_triggers as rt
base = pathlib.Path(sys.argv[1]) / "_archive"; rec = []; sb = ce = n = 0
for p in sorted(base.iterdir()):
    f = p / "index.md" if p.is_dir() else p
    if f.suffix != ".md" or not f.exists(): continue
    t = f.read_text(errors="replace")
    if "variant: kc-dev-flow-2" not in t.split("\n---", 1)[0]: continue
    n += 1; name = p.name if p.is_dir() else p.stem
    lines = list(rt.outside_fences(t)); fails, repl = rt.step_back_events(lines); reports, _ = rt.events(lines)
    sb += fails >= 2 or len(repl) >= 2; ce += reports - 1 >= 4
    dd = base / name / "dispatch"
    if dd.is_dir():
        k = max([int(m.group(1)) for x in dd.iterdir() for m in [re.match(r"^implementation-(\d+)\.md$", x.name)] if m] or [0])
        if k: rec.append(k)
print("archived kc-dev-flow-2 tasks", n, "| with implementation dispatch records", len(rec), "| >=2", sum(k >= 2 for k in rec),
      "| >=3", sum(k >= 3 for k in rec), "| >=5", sum(k >= 5 for k in rec))
print("step-back events reached:", sb, "| chief-engineer at 4 repair passes (report headings):", ce)
