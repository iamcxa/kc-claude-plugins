"""usage: python3 -B -I probe_dg.py <base-scripts-dir> <candidate-scripts-dir>"""
import sys, importlib.util
def load(d):
    sys.modules.pop("design_surfaces", None); sys.modules.pop("number_guards", None); sys.modules.pop("decision_ledger", None)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location("dg", d + "/delivery_gate.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); sys.path.pop(0); return m
base, cand = load(sys.argv[1]), load(sys.argv[2])
cases = {
 "plain two items": "Declined: F1 a (two words); F2 b (two words).",
 "nested label, own bracket (the false pass)": "Declined: F1 a (see Declined: F9 x (y z)); F2 b (two words).",
 "nested label, no own bracket": "Declined: F1 a (see Declined: F9 x y z); F2 b (two words).",
 "nested FO declines": "FO declines: F1 a (as FO declines: F9 x (y z)).",
 "sentence-start label inside a bracket": "Declined: F1 a (kept as is. Declined: F9 x y); F2 b (two words).",
 "two real sentences": "Declined: F1 a (two words). Declined: F2 b (two words).",
 "bullets, periods": "- Declined: F1 a (two words).\n- Declined: F2 b (two words).",
 "bullets, no periods": "- Declined: F1 a (two words)\n- Declined: F2 b (two words)",
 "bullets with finding ids": "- V8 Declined, low: F1 a (two words).\n- V10 Declined, low: F2 b (two words).",
 "bullet 1 has no reason": "- Declined: F1 a\n- Declined: F2 b (two words)",
 "same sentence, two labels": "Declined: F1 a (two words); FO declines: F2 b (two words).",
 "label on the next line inside a bracket": "Declined: F1 a (see\nDeclined: F9 x (y z)); F2 b (two words).",
 "label after e.g.": "Declined: F1 a (e.g. Declined: F9 x (y z)); F2 b (two words).",
}
for name, text in cases.items():
    b, c = base.declined_items(text), cand.declined_items(text)
    print(f"{name}: base {len(b)} unreasoned {len(base.unreasoned_items(text))} | cand {len(c)} unreasoned {len(cand.unreasoned_items(text))}")
    if b != c: print("   base", b, "\n   cand", c)
