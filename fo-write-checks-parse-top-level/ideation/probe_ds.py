"""usage: python3 -B -I probe_ds.py <base-scripts-dir> <candidate-scripts-dir>"""
import sys, importlib.util
def load(d):
    for n in ("design_surfaces", "decision_ledger"): sys.modules.pop(n, None)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location("ds", d + "/design_surfaces.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); sys.path.pop(0); return m
base, cand = load(sys.argv[1]), load(sys.argv[2])
F = "```"
cases = {
 "no fence": "## Scope\n- a\n- b\n\n## Next\nx\n",
 "scope at EOF no newline": "## Scope\n- a",
 "heading is last line": "## Scope",
 "fenced Scope example first": f"## Design\n{F}\n## Scope\n- example\n{F}\n\n## Scope\n- real a\n- real b\n\n## Next\n",
 "fenced ## heading inside real Scope": f"## Scope\n- a\n{F}\n## Not a heading\n{F}\n- b\n\n## Next\nx\n",
 "fenced block inside real Scope kept": f"## Scope\n- a\n{F}\ncode line\n{F}\n- b\n## Next\n",
 "indented fence": f"## Design\n  {F}\n## Scope\n- ex\n  {F}\n## Scope\n- real\n",
 "two real Scope headings": "## Scope\n- first\n## Scope\n- second\n",
 "Scope notes heading": "## Scope notes\n- n\n",
 "unclosed fence before Scope": f"{F}\n## Scope\n- hidden\n",
}
for n, t in cases.items():
    b, c = base.scope_lines(t), cand.scope_lines(t)
    print(("same " if b == c else "DIFF ") + n, "" if b == c else f"\n   base {b}\n   cand {c}")
