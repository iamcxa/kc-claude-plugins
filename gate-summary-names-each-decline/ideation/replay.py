"""Run the decline rules of delivery_gate.text_problems, base and candidate, on the saved replay texts."""
import importlib.util, json, sys
from pathlib import Path
R = Path(sys.argv[1]); out = {}
def load(name, scripts):
    sys.path.insert(0, scripts)
    for m in ("delivery_gate", "design_surfaces", "validation_security", "role_triggers", "number_guards", "decision_ledger"): sys.modules.pop(m, None)
    import delivery_gate; sys.path.pop(0); return delivery_gate
cases = json.loads((R / "cases.json").read_text())
for label, scripts in (("base", sys.argv[2]), ("candidate", sys.argv[3])):
    g = load(label, scripts)
    for f in sorted(R.glob("*.txt")):
        slug = f.name.split(".")[0]; text = f.read_text(); task_text = (R / f"{slug}.task.md").read_text()
        task = Path(cases[slug]["folder"] + ".md")
        kw = {"task": task} if "task" in g.text_problems.__code__.co_varnames else {}
        problems, _ = g.text_problems(task_text, text, **kw)
        decl = [x for x in problems if "declin" in x.lower() or "receiving task" in x]
        out.setdefault(f.stem, {})[label] = decl
for k, v in out.items():
    print(f"{k}: base {'HOLD' if v['base'] else 'pass'} {len(v['base'])} | candidate {'HOLD' if v['candidate'] else 'pass'} {len(v['candidate'])}")
    for x in v["candidate"]: print("    ", x[:170])
