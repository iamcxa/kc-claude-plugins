#!/usr/bin/env python3
"""What the cycle-2 carried-merge rule would have said for each Captain validation approval, had its question ended with a Merges: line.

Usage: python3 -I -B carry_sim.py <package scripts dir> <state checkout>   (the checkout is only read; it must be a git worktree)
For each of the Captain's validation approvals whose question names a head and a PR number, append `Merges: <owner/repo>#<N> at <head>` to that
approval's question in memory, treat the approval as the newest one (nothing after its time exists) and run proto_gate.next_line twice: with the
amendment rule by commit time (the design) and with the 0.26.0 date rule (an amendment dated on or after the approval's day). Prints the outcome counts.
Also counts, over the same approvals, the head the question names against the last Candidate in the task's dispatch records.
"""
import collections, re, sys
from pathlib import Path
pkg, state = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, pkg)
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.argv = ["proto_gate", pkg, str(state)]
import proto_gate as pg
import decision_ledger as dl, delivery_gate as dg

rows = [r for r in dl.ledger(state) if r["stage"] == "validation" and r["kind"] == "resolution" and r["by"] == "person:captain" and r["decision"] == "approve"]
orig = dl.question
by_time, by_date, heads = collections.Counter(), collections.Counter(), collections.Counter()
for r in rows:
    task = state / ("_archive" if r["archived"] else "") / (r["task"] + ".md")
    q = r["question"] or ""
    head, num = re.search(r"\bhead\s+`?([0-9a-f]{7,40})", q), re.search(r"#(\d+)", q)
    if not (head and num):
        by_time["question names no head or PR"] += 1
        by_date["question names no head or PR"] += 1
        continue
    pr, full = f"iamcxa/kc-claude-plugins#{num.group(1)}", (head.group(1) + "0" * 40)[:40]
    n = r["attempt"].rsplit("-", 1)[1]
    pg.dl.question = lambda st, tp, room, _l=f" Merges: {pr} at {head.group(1)}", _n=n, _s=r["task"]: orig(st, tp, room) + (_l if room.endswith(f"/{_s}/review/validation/briefing-{_n}") else "")
    try:
        by_time[pg.next_line(task, pr, full, as_of=pg.ts(r["at"]))[1] or "carried"] += 1
        by_date[pg.next_line(task, pr, full, as_of=pg.ts(r["at"]), by_date=True)[1] or "carried"] += 1
    finally:
        pg.dl.question = orig
    cands = dg.dispatched_candidates(task)[0]
    if cands:
        heads["approved head = last dispatched head" if cands[-1].startswith(head.group(1)[:8]) else "approved head differs from the last dispatched head"] += 1
print(f"{len(rows)} Captain validation approvals")
print("amendment rule by commit time (the design):", dict(by_time))
print("amendment rule by date (0.26.0 amended_after):", dict(by_date))
print("head named in the question against the last dispatched Candidate:", dict(heads))
