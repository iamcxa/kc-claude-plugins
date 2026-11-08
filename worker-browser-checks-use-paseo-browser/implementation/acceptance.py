#!/usr/bin/env python3
"""Task-local exact-revision acceptance; no product or git configuration writes."""
import io
import json
import hashlib
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

repo, base, head, evidence = sys.argv[1:]
evidence = Path(evidence)
sentence = "Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root."
runtime_revision = "20eb8255daf0f1267a8c0dd16daf0705a7cf82ba"
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
        "For attended pages", "logins where the Captain performs human verification",
        "follow EXTENSION.md's Human terminals and pages", "Repository instructions take precedence",
        "Unattended checks use the repository's supported adapter without a required Paseo attempt.",
        "CI browser runs are unchanged", "If tools are missing", "which tool ran each step and why",
        "not run, never clean", "close tabs you open", "most recently connected browser host",
        "Keep the tab visible in the Paseo app for screenshots and clicks.",
    ]
    errors = [term for term in needed if term not in text]
    limits = [
        ("Captain's keyboard", ["native value setter", "bubbling `input` event", "read the value back"]),
        ("React Native", ["`browser_click`", "latest `browser_snapshot`", "snapshot again first"]),
        ("15 seconds", ["park the result on `window`", "poll with short calls"]),
        ("signature canvas", ["untested", "`browser_drag`", "repository's adapter for that step"]),
    ]
    bullets = [line for line in text.splitlines() if line.startswith("- ")]
    for label, workarounds in limits:
        matches = [line for line in bullets if label in line]
        if len(matches) != 1 or any(w not in matches[0] for w in workarounds):
            errors.append(label)
    if len(text.split()) > 240:
        errors.append("over 240 words")
    for statement in re.split(r"[.\n]", text):
        if (re.search(r"\bunattended\b", statement, re.I) and
                re.search(r"\bPaseo\b", statement) and
                re.search(r"\b(must|first|before|after|required)\b", statement, re.I) and
                not re.search(r"\b(without|no|not|never)\b", statement, re.I)):
            errors.append("required unattended Paseo attempt")
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
    ]
    missing = [exact for exact, label in required if exact not in text and label not in text]
    if "agent-browser" in text:
        missing.append("all-Paseo proof incomplete; alternate adapter used")
    return missing
def codex_ok(data):
    text = activity(data)
    return (text.count("[List browser tabs] {}") == 1 and "mcp__paseo__browser_list_tabs" in text and
            "Done: Codex browser reachability measured." in text)

def report_claim_errors(text):
    errors = []
    if runtime_revision not in text or "attended" not in text.lower() or "fallback" not in text.lower():
        errors.append("historical revision and attended/fallback boundary missing")
    for statement in re.split(r"[.\n]", text):
        if (re.search(r"\b(runs?|attempt[- ]?[12])\b", statement, re.I) and
                re.search(r"\b(prov(?:e[sd]?|ed|en)|proof|test(?:ed|s)?|verified|validated|demonstrates?|establish(?:es|ed)?)\b", statement, re.I) and
                re.search(r"\bunattended\b.*\bdefault\b", statement, re.I) and
                not re.search(r"\b(not|neither|never|no|without)\b", statement, re.I)):
            errors.append("historical run claimed to test an unattended default")
    return errors

base_ext = blob(base, extpath)
candidate_ext = blob(head, extpath)
candidate_guide = blob(head, guidepath)
check("AC-6 (replaces AC-1) conditional pointer and unchanged first sentence",
      quote(candidate_ext) == quote(base_ext) + " " + sentence)
check("AC-7 (replaces AC-2) attended routing and complete limits", not guide_errors(candidate_guide))
check("Pre-amendment guide fails narrowed contract", bool(guide_errors(blob("90192bb64db4614de9a7a94cc782ee5fa44748db",guidepath))))
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
    run_existing("AC-6 existing consumer", candidate_ext, True)
    before = candidate_ext.replace(quote(candidate_ext), sentence+" "+quote(base_ext))
    run_existing("AC-6 mutation sentence first rejected", before, False)
    second = base_ext + '\nAdd to scope notes: "'+sentence+'"\n'
    run_existing("AC-6 mutation second instruction rejected", second, False)
    extension.write_text(candidate_ext)
    for name, fragment in [
        ("keyboard", "set the value through the element's native value setter, dispatch a bubbling `input` event, and read the value back."),
        ("ref", "snapshot again first."),
        ("timeout", "park the result on `window`, and poll with short calls."),
        ("signature", "use the repository's adapter for that step."),
    ]:
        check("AC-7 mutation "+name+" workaround removed rejected",
              bool(guide_errors(candidate_guide.replace(fragment,"",1))))
    check("AC-7 mutation word overflow rejected", bool(guide_errors(candidate_guide+" extra"*241)))
    unattended_mutant = candidate_guide + "\nUnattended checks must try Paseo before the repository adapter.\n"
    check("AC-7 mutation unattended first attempt rejected within word cap",
          len(unattended_mutant.split()) <= 240 and
          "required unattended Paseo attempt" in guide_errors(unattended_mutant))
    moved = base_ext+"\n"+candidate_guide
    check("AC-3 mutation limits moved to FO rejected",len(moved.split())-len(base_ext.split())>20)

claude = json.loads((evidence/"attempt-2/claude-activity.json").read_text())
codex = json.loads((evidence/"codex-activity.json").read_text())
check("AC-8 (replaces AC-4) historical attended Paseo calls", not claude_errors(claude),str(claude_errors(claude)))
check("AC-8 saved attended report and screenshots", all((evidence/"attempt-2"/p).is_file() for p in ["claude-report.md","claude-before.png","claude-after.png"]))
first_claude = json.loads((evidence/"claude-activity.json").read_text())
background_report = (evidence/"claude-report.md").read_text()
attended_report = (evidence/"attempt-2/claude-report.md").read_text()
check("AC-8 background failures and per-step fallback retained",
      all(term in background_report for term in [runtime_revision,"screenshot_no_frame","browser_timeout","agent-browser","Fallback reason"]))
check("AC-8 both reports retain their actual runtime SHA", runtime_revision in background_report and runtime_revision in attended_report)
check("AC-8 first failed tab closed", "[Close browser tab]" in activity(first_claude))
check("FO follow-up second tab intentionally retained", "[Close browser tab]" not in activity(claude) and "do not close" in (evidence/"attempt-2/claude-prompt.txt").read_text().lower())
check("Historical canvas product bytes remain unchanged", not git("diff", runtime_revision, head, "--", "kc-journey-map"))
manifest = json.loads((evidence/"cycle-2/historical-evidence-sha256.json").read_text())
check("AC-8 no historical browser evidence modified",
      all(hashlib.sha256((evidence/path).read_bytes()).hexdigest()==digest for path,digest in manifest.items()))
task_text = (evidence.parent.parent/(evidence.parent.name+".md")).read_text()
latest_report = task_text.rsplit("## Stage Report: implementation\n",1)[1].split("\n## ",1)[0]
check("AC-8 implementation report preserves historical evidence boundary", not report_claim_errors(latest_report),str(report_claim_errors(latest_report)))
bad_claim = latest_report + "\nBoth runs proved an unattended Paseo default.\n"
check("AC-8 mutation unattended-default proof claim rejected",
      "historical run claimed to test an unattended default" in report_claim_errors(bad_claim))
for bad, label in [
    ({}, "no Paseo browser call"),
    ({"structuredContent":{"content":activity(claude)+"\n[Shell] agent-browser open URL"}}, "alternate adapter without reason"),
]:
    check("AC-8 mutation "+label+" rejected", bool(claude_errors(bad)))
check("AC-5 actual Codex tool exists and called once", codex_ok(codex))
check("AC-5 mutation missing measurement rejected", not codex_ok({}))
check("AC-5 no unmeasured Codex limitation", "Codex" not in candidate_guide)
(evidence/"acceptance-results.json").write_text(json.dumps(checks,indent=2)+"\n")
failed = sum(item["status"] == "failed" for item in checks)
print(json.dumps({"base":base,"candidate":head,"checks":len(checks),"status":"failed" if failed else "passed", "failed":failed,
                  "extension_words":len(candidate_ext.split()),"guide_words":len(candidate_guide.split())},indent=2))
sys.exit(1 if failed else 0)

