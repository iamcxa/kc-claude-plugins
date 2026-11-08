#!/usr/bin/env python3
"""Task-local exact-revision acceptance; no product or git configuration writes."""
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

repo, base, head, evidence = sys.argv[1:]
evidence = Path(evidence)
sentence = "For a local browser check you drive yourself, first read extensions/paseo/browser.md under your Package root."
extpath = "kc-dev-flow-2/extensions/paseo/EXTENSION.md"
guidepath = "kc-dev-flow-2/extensions/paseo/browser.md"
testname = "ExtensionInstructionTests.test_every_shipped_instruction_is_read_from_its_extension_file"
checks = []
def check(name, condition, message=""):
    checks.append({"name": name, "status": "passed" if condition else "failed", "message": message})

def git(*args):
    return subprocess.check_output(["git", "-C", repo, *args])
def blob(rev, path):
    return git("show", rev + ":" + path).decode()
def quote(text):
    lines = [line for line in text.splitlines() if line.startswith("Add to scope notes:")]
    assert len(lines) == 1
    return lines[0].split('"', 1)[1][:-1]
def guide_errors(text):
    needed = [
        "use Paseo's browser tools", "unless the repository's own instructions name another tool",
        "CI browser runs are unchanged", "If the tools are missing", "which tool ran each step and why",
        "not run, never clean", "close the tabs you open",
    ]
    errors = [term for term in needed if term not in text]
    limits = [
        ("Captain's keyboard", ["native value setter", "bubbling `input` event", "read the value back"]),
        ("React Native", ["`browser_click`", "latest `browser_snapshot`", "snapshot again first"]),
        ("15 seconds", ["park the result on `window`", "poll it with short calls"]),
        ("signature canvas", ["untested", "`browser_drag`", "repository's adapter for that step"]),
    ]
    bullets = [line for line in text.splitlines() if line.startswith("- ")]
    for label, workarounds in limits:
        matches = [line for line in bullets if label in line]
        if len(matches) != 1 or any(w not in matches[0] for w in workarounds):
            errors.append(label)
    if len(text.split()) > 240:
        errors.append("over 240 words")
    return errors

def activity(data):
    return data.get("structuredContent", {}).get("content", "")
def claude_errors(data):
    text = activity(data)
    required = [
        ("browser_new_tab", "[Open browser tab]"),
        ("browser_snapshot", "[Snapshot page]"),
        ("browser_click", "[Click element]"),
        ("browser_screenshot", "[Take screenshot]"),
        ("browser_close_tab", "[Close browser tab]"),
    ]
    missing = [exact for exact, label in required if exact not in text and label not in text]
    if "agent-browser" in text:
        missing.append("all-Paseo proof incomplete; alternate adapter used")
    return missing
def codex_ok(data):
    text = activity(data)
    return (text.count("[List browser tabs] {}") == 1 and "mcp__paseo__browser_list_tabs" in text and
            "Done: Codex browser reachability measured." in text)

base_ext = blob(base, extpath)
candidate_ext = blob(head, extpath)
candidate_guide = blob(head, guidepath)
check("AC-1 appended sentence and unchanged first sentence",
      quote(candidate_ext) == quote(base_ext) + " " + sentence)
check("AC-2 instructions and four complete workarounds", not guide_errors(candidate_guide))
check("AC-3 dispatch word bound", len(candidate_ext.split()) - len(base_ext.split()) <= 20,
      str({"base": len(base_ext.split()), "candidate": len(candidate_ext.split()),
           "guide": len(candidate_guide.split())}))
for path in ["kc-dev-flow-2/references/sd/workflow.md", "kc-dev-flow-2/scripts/lint-skills.py",
             "kc-dev-flow-2/scripts/dispatch_records.py"]:
    check("AC-3 unchanged " + path, blob(base,path) == blob(head,path))
changed = git("diff", "--name-only", base, head).decode().splitlines()
check("Approved product scope", sorted(changed) == sorted([extpath,guidepath]))
base_missing = subprocess.run(["git","-C",repo,"cat-file","-e",base+":"+guidepath],capture_output=True)
check("Base does not meet goal", sentence not in base_ext and base_missing.returncode != 0)

with tempfile.TemporaryDirectory(prefix="browser-acceptance-") as tmp:
    root = Path(tmp)
    with tarfile.open(fileobj=io.BytesIO(git("archive",head,"kc-dev-flow-2"))) as archive:
        archive.extractall(root, filter="data")
    extension = root / extpath
    scripts = root / "kc-dev-flow-2/scripts"
    def run_existing(label, contents, expected):
        extension.write_text(contents)
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache)
        result = subprocess.run([sys.executable,"-B","test_dispatch_records.py",testname],
                                cwd=scripts,capture_output=True,text=True)
        (evidence/(label+".log")).write_text(result.stdout+result.stderr)
        check(label, (result.returncode == 0) == expected, "exit "+str(result.returncode))
    run_existing("AC-1 existing consumer", candidate_ext, True)
    before = candidate_ext.replace(quote(candidate_ext), sentence+" "+quote(base_ext))
    run_existing("AC-1 mutation sentence first rejected", before, False)
    second = base_ext + '\nAdd to scope notes: "'+sentence+'"\n'
    run_existing("AC-1 mutation second instruction rejected", second, False)
    extension.write_text(candidate_ext)
    for name, fragment in [
        ("keyboard", "set the value through the element's native value setter, dispatch a bubbling `input` event, and read the value back."),
        ("ref", "snapshot again first."),
        ("timeout", "park the result on `window`, and poll it with short calls."),
        ("signature", "use the repository's adapter for that step."),
    ]:
        check("AC-2 mutation "+name+" workaround removed rejected",
              bool(guide_errors(candidate_guide.replace(fragment,"",1))))
    check("AC-2 mutation word overflow rejected", bool(guide_errors(candidate_guide+" extra"*241)))
    moved = base_ext+"\n"+candidate_guide
    check("AC-3 mutation limits moved to FO rejected",len(moved.split())-len(base_ext.split())>20)

claude = json.loads((evidence/"claude-activity.json").read_text())
codex = json.loads((evidence/"codex-activity.json").read_text())
check("AC-4 actual Claude tool calls", not claude_errors(claude),str(claude_errors(claude)))
check("AC-4 worker report", (evidence/"claude-report.md").is_file())
for bad, label in [
    ({}, "no Paseo browser call"),
    ({"structuredContent":{"content":activity(claude)+"\n[Shell] agent-browser open URL"}}, "alternate adapter without reason"),
]:
    check("AC-4 mutation "+label+" rejected", bool(claude_errors(bad)))
check("AC-5 actual Codex tool exists and called once", codex_ok(codex))
check("AC-5 mutation missing measurement rejected", not codex_ok({}))
check("AC-5 no unmeasured Codex limitation", "Codex" not in candidate_guide)
(evidence/"acceptance-results.json").write_text(json.dumps(checks,indent=2)+"\n")
failed = sum(item["status"] == "failed" for item in checks)
print(json.dumps({"base":base,"candidate":head,"checks":len(checks),"status":"failed" if failed else "passed", "failed":failed,
                  "extension_words":len(candidate_ext.split()),"guide_words":len(candidate_guide.split())},indent=2))
sys.exit(1 if failed else 0)

