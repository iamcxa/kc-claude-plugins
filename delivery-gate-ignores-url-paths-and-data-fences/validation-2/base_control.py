import contextlib
import io
import json
from pathlib import Path
import sys

root, out = map(Path, sys.argv[1:])
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests

q = tests.QuestionTests()
tests.gate.__file__ = str(Path(sys.argv[1]).parent / "base/kc-dev-flow-2/scripts/delivery_gate.py")
merge = tests.MERGE_ASK.format(tail=tests.HOLD_OUT_TAIL["unless he says he merges or holds"])
cases = [
    ("site paths", "`fix(relay): /llms.txt teaches agents` `/web/favicon.svg` `/pair`", {}),
    ("elided package", "`python3 .../scripts/adr_lint.py docs/adr --since a3f28ef6`", {}),
    ("namespace", "`{http://www.w3.org/2000/svg}svg`", {"task": tests.TASK + "\n## Stage Report: validation\n`{http://www.w3.org/2000/svg}svg`"}),
    ("design YAML", "Review this candidate.", {"summary": "Read design/built-review.md", "cards": {"design/built-review.md": "```yaml\ndesign_review:\n  adrs_read:\n    - docs/adr/0064-the-first-screen-leads-with-sign-in.md (Accepted)\n```\n"}}),
    ("review YAML", "Review this candidate.", {"summary": "Read review/chief-engineer-1.md", "cards": {"review/chief-engineer-1.md": "```yaml\nchief_engineer_advice:\n  outcome: continue\n```\n"}}),
]
rows = []
for name, text, kwargs in cases:
    code, output = q.ask(merge + "\n" + text, cli=True, **kwargs)
    rows.append(dict(name=name, exit=code, output=output))
    assert code == 1 and "Captain steps record fails" in output and ("S4" in output or "S5" in output), rows[-1]
    print(name + ": base fails the original input through the real merge question CLI")

(out / "base-observations.json").write_text(json.dumps(rows, indent=2)+"\n")
