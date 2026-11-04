import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(os.environ["DIAGNOSIS_CODE_ROOT"])
OUT = Path(os.environ["DIAGNOSIS_EVIDENCE_DIR"])
sys.path.insert(0, str(ROOT / "kc-dev-flow-2/scripts"))
import test_dispatch_records as tests
import role_triggers

rows = []
env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_AUTHOR_NAME": "Validation", "GIT_AUTHOR_EMAIL": "validation@example.invalid",
       "GIT_COMMITTER_NAME": "Validation", "GIT_COMMITTER_EMAIL": "validation@example.invalid",
       "PYTHONDONTWRITEBYTECODE": "1"}

def run(args, cwd=ROOT):
    done = subprocess.run(list(map(str, args)), cwd=cwd, env=env, text=True, capture_output=True)
    row = {"command": list(map(str, args)), "cwd": str(cwd), "exit": done.returncode,
           "stdout": done.stdout, "stderr": done.stderr}
    rows.append(row)
    return done

fixture = OUT / "message-fixture"
(fixture / "task/dispatch").mkdir(parents=True)
(fixture / "README.md").write_text(tests.NO_EXTENSIONS)
(fixture / "task.md").write_text("---\nprofile: pilot\n---\n## FO alignment\nSurfaces: none\n")
record = "Symptom: page freeze\nCandidate: " + tests.HEAD + "\n" + tests.COMPLETE
for name in ("implementation-2.md", "implementation-2-message-1.md", "implementation-2-message-2.md"):
    (fixture / "task/dispatch" / name).write_text(record)
script = ROOT / "kc-dev-flow-2/scripts/dispatch_records.py"
folder = run([sys.executable, "-B", script, fixture / "task"])
named = run([sys.executable, "-B", script, "--names", "--strict", fixture / "task/dispatch/implementation-2-message-2.md"])
for args in (["git", "init", "-q", "-b", "main"], ["git", "add", "."], ["git", "commit", "-qm", "continuation fixture"]):
    assert run(args, cwd=fixture).returncode == 0
roles = run([sys.executable, "-B", ROOT / "kc-dev-flow-2/scripts/role_triggers.py", fixture, "task"])
assert folder.returncode == named.returncode == 0 and roles.returncode == 1
assert "step back: 3 implementation" in folder.stderr and "step back: 3 implementation" in named.stderr and "3 implementation dispatches" in roles.stdout
assert len(role_triggers.symptom_rounds([(p.name, p.read_text()) for p in (fixture / "task/dispatch").glob("*.md")])[("implementation", "page freeze")]) == 3
(OUT / "message-records.json").write_text(json.dumps(rows, indent=2))
print("Three supported implementation records (two message continuations): dispatch reminder present; chief-engineer owed; three counted rounds.")

word_rows = []
for row in json.loads((OUT / "words.json").read_text()):
    if "base_lines" not in row:
        continue
    def count(lines):
        p = subprocess.run(["wc", "-w"], input="\n".join(lines), text=True, capture_output=True, check=True)
        return int(p.stdout)
    before, after = count(row["base_lines"]), count(row["candidate_lines"])
    assert after-before == row["added"] and after-before <= row["limit"]
    word_rows.append({"name": row["name"], "before": before, "after": after, "added": after-before, "limit": row["limit"]})
(OUT / "words-independent.json").write_text(json.dumps(word_rows, indent=2))
print("Independent wc -w recount agrees for all five emitted-output cases.")

adr = next((ROOT / "docs/adr").glob("0026-*"))
text = adr.read_text()
def amendment_present(text):
    marker = "Amended 2026-11-03 (Captain:"
    if marker not in text:
        return False
    paragraph = text.split(marker, 1)[1]
    return all(piece in paragraph for piece in ("「可以」", "diagnosis-rounds-count-toward-step-back",
        "round two", "round three", "third record", "Dispatched:", "stderr", "ADR 0027", "48", "21", "47", "74", "budget is unchanged"))
assert amendment_present(text)
assert all(part in text for part in ("Clarified 2026-11-03", "「照你建議」", "<stage>-N-message-M.md", "Both disk and committed-state readers count it"))
assert "Message continuations" not in text
old = run(["git", "-C", ROOT, "show", "713d4e6ed6381e65fa6d8305e08b282ceb56a8fb:" + str(adr.relative_to(ROOT))])
assert old.returncode == 0 and not amendment_present(old.stdout)
copy = ROOT.parent / ".validation-adr-mutant"
shutil.copytree(ROOT / "docs/adr", copy)
path = copy / adr.name
path.write_text(text.replace("**Recommended:**", "**Removed:**"))
lint = run([sys.executable, "-B", "/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py",
            copy, "--root", ROOT, "--require", "26"])
assert lint.returncode == 1 and "Recommended:" in lint.stdout
(OUT / "adr-falsifiers.json").write_text(json.dumps({"amendment_present": True, "base_without_amendment_rejected": True, "required_statement_mutant": rows[-1]}, indent=2))
print("AC-9: candidate amendment present; base without amendment rejected; required-statement deletion rejected by ADR lint.")
