import sys, json, io, contextlib, tempfile, importlib.util, subprocess
# usage: replay_question.py <package root: kc-dev-flow-2/scripts inside, test_delivery_gate.py present> <state checkout>
from pathlib import Path
root = sys.argv[1]; state = sys.argv[2]
sys.path.insert(0, f"{root}/kc-dev-flow-2/scripts")
import delivery_gate as gate
import test_delivery_gate as t
SNAP = {"#786 override-recorded-when-captain-departs": ("846c4202b2a7e70bd08eee1d31406502f350aa0d", "_archive/override-recorded-when-captain-departs/review/validation/briefing-1/index.json"),
        "#787 extension-instruction-check-sees-every-listed-extension": ("846c4202b2a7e70bd08eee1d31406502f350aa0d", "_archive/extension-instruction-check-sees-every-listed-extension/review/validation/briefing-1/index.json"),
        "#788 gate-presentation-asks-one-thing-plainly": ("846c4202b2a7e70bd08eee1d31406502f350aa0d", "_archive/gate-presentation-asks-one-thing-plainly/review/validation/briefing-3/index.json")}
for label, (commit, path) in SNAP.items():
    q = json.loads(subprocess.check_output(["git", "-C", state, "show", f"{commit}:{path}"]))["question"]
    code, out = t.QuestionTests("test_legacy_combined_text_still_accepts_no_round_count").ask(q)
    lines = [l for l in out.splitlines() if l != t.CLAIM_SOURCE and not l.startswith("next: before gate prepare")]
    print(f"{label}: exit {code}; " + " | ".join(lines))
