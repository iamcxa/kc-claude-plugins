"""Count, over saved gate-time texts, which texts the base and candidate decline rules hold."""
import json, sys
from collections import Counter
from pathlib import Path
corpus = json.load(open(sys.argv[1]))
def load(scripts):
    for m in ("delivery_gate", "design_surfaces", "validation_security", "role_triggers", "number_guards", "decision_ledger"): sys.modules.pop(m, None)
    sys.path.insert(0, scripts); import delivery_gate; sys.path.pop(0); return delivery_gate
base, cand = load(sys.argv[2]), load(sys.argv[3])
c = Counter(); r1_clauses = 0
for row in corpus:
    t, x, task = row["task_text"], row["text"], Path(row["folder"] + ".md")
    b = bool(base.unreasoned_items(x) or base.findings_join(t, x))
    r1 = cand.unlabelled_declines(x); r2 = cand.findings_join(t, x); r3 = cand.unreceived_declines(x, task)
    r1_clauses += len(r1)
    c["texts"] += 1; c["base holds"] += b; c["R1 unlabelled"] += bool(r1); c["R2 join"] += bool(r2); c["R3 receiver"] += bool(r3)
    c["candidate holds"] += bool(cand.unreasoned_items(x) or r1 or r2 or r3)
    c[f"repo {row['repo']} newly held"] += bool((r1 or r2 or r3) and not b)
print(dict(c), "R1 clauses", r1_clauses)
