"""Words FO reads from the decline lines text_problems prints (problems and deduplicated next: lines), base vs candidate."""
import json, sys
from pathlib import Path
R = Path(sys.argv[1]); cases = json.loads((R / "cases.json").read_text())
def load(scripts):
    for m in ("delivery_gate", "design_surfaces", "validation_security", "role_triggers", "number_guards", "decision_ledger"): sys.modules.pop(m, None)
    sys.path.insert(0, scripts); import delivery_gate; sys.path.pop(0); return delivery_gate
res = {}
for label, scripts in (("base", sys.argv[2]), ("candidate", sys.argv[3])):
    g = load(scripts)
    for f in sorted(R.glob("*.txt")):
        slug = f.name.split(".")[0]
        kw = {"task": Path(cases[slug]["folder"] + ".md")} if "task" in g.text_problems.__code__.co_varnames else {}
        problems, nexts = g.text_problems((R / f"{slug}.task.md").read_text(), f.read_text(), **kw)
        lines = [p for p in problems if "declin" in p.lower() or "receiving task" in p]
        lines += [n for n in dict.fromkeys(nexts) if "declined item" in n or "spacedock new" in n]
        res.setdefault(f.stem, {})[label] = sum(len(l.split()) for l in lines)
for k, v in res.items(): print(f"{k}: base {v['base']} words, candidate {v['candidate']} words")
