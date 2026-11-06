import json, re, sys, glob, collections
# usage: corpus_validation_questions.py <package root with prototype applied> <state checkout>
sys.path.insert(0, sys.argv[1] + "/kc-dev-flow-2/scripts")
import delivery_gate as g
S = sys.argv[2]
c = collections.Counter(); held = []
for p in sorted(glob.glob(f"{S}/**/review/validation/briefing-*/index.json", recursive=True)):
    q = json.load(open(p)).get("question") or ""
    grant = bool(g.GRANT.search(q)); clause = bool(g.WORKTREE_REMOVAL.search(q)); loose = bool(re.search(r"worktree", q, re.I))
    c[(grant, clause, loose)] += 1
    if grant and not clause: held.append(p.split(".spacedock-state/")[1])
print(dict(c)); print(len(held), "held"); print("\n".join(held[-12:]))
