#!/usr/bin/env python3
"""Words FO reads at the merge ask, base and candidate, counted with str.split().

Usage: words.py <workflow.md at origin/main> <observer SKILL.md at origin/main>
The candidate adds no workflow.md word; the only candidate change in what FO reads is a hold line from delivery_gate.py.
"""
import re
import sys

text = open(sys.argv[1]).read()
observer = open(sys.argv[2]).read()


def between(start, end):
    a = text.index(start)
    return text[a:text.index(end, a) + len(end)]


passages = {
    "validation Gate content": between("- **Gate content:** Show actual checks", "delivering that work as POC."),
    "Delivery authority, authority paragraph": between("Project and Captain authority constrain", "explicit choice."),
    "Delivery authority, delivery_gate sentence": between("Before the merge ask, FO runs", "shows the Captain what it printed."),
}
PASS = ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing",
        "class: docs-only", "record: task/merge/ask-1.json", "next: ask for merge with this text."]
HOLD = {
    "Sufficiency": "the gate text has no 'Sufficiency:' clause: add 'Sufficiency: <the acceptance criteria this candidate met, from its validation report>'",
    "Necessity": "the gate text has no 'Necessity:' clause: add 'Necessity: <who uses this change and what breaks without it>'",
    "next": "next: hold the ask; add the missing clause to the question or summary.",
}
base = {k: len(v.split()) for k, v in passages.items()}
base["delivery_gate.py pass output (one docs-only ask)"] = sum(len(l.split()) for l in PASS)
for k, v in base.items():
    print(f"{v:4d}  {k}")
total = sum(base.values())
hold = sum(len(v.split()) for v in HOLD.values())
print(f"{total:4d}  base total at the merge ask, pass path")
print(f"{total:4d}  candidate total at the merge ask, pass path (README and pass output unchanged)")
print(f"{total + hold:4d}  candidate on a first hold with both clauses missing (+{hold}, once per ask that lacks them)")
print(f"{len(observer.split()):4d}  observer SKILL.md words today (read by the observer, not by FO)")
