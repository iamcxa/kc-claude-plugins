import contextlib
import io
import json
from pathlib import Path
import sys

root, out = map(Path, sys.argv[1:])
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests

q = tests.QuestionTests()
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
    assert code == 0 and "gate text complete" in output and "--reference " in output, rows[-1]
    print(name + ": matching record plus original input passes the real merge question CLI")

with contextlib.ExitStack() as cleanup:
    fixture = tests.DeliveryCheckBeforeQuestionTests()
    fixture.setUp()
    cleanup.callback(fixture.doCleanups)
    fixture.message.write_text(fixture.message.read_text() + "\n`/llms.txt` `{http://www.w3.org/2000/svg}svg`\n")
    missing = fixture.run_question()
    rows.append(dict(name="missing delivery record", exit=missing.returncode, output=missing.stdout))
    assert missing.returncode == 1 and "delivery check record" in missing.stdout and "gate text complete" not in missing.stdout
    fixture.save()
    matched = fixture.run_question()
    rows.append(dict(name="matching delivery record", exit=matched.returncode, output=matched.stdout))
    assert matched.returncode == 0 and "gate text complete" in matched.stdout and "--reference " in matched.stdout
    fixture.save(2, head=tests.S2)
    mismatched = fixture.run_question()
    rows.append(dict(name="newest mismatched delivery record", exit=mismatched.returncode, output=mismatched.stdout))
    assert mismatched.returncode == 1 and "delivery check record" in mismatched.stdout
    print("missing/matching/newest-mismatched delivery record: exit 1/0/1 with URL and namespace inputs")

(out / "combined-observations.json").write_text(json.dumps(rows, indent=2) + "\n")
print("PASS: both gate changes hold together")
