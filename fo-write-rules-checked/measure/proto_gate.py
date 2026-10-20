#!/usr/bin/env python3
"""Prototype of the delivery_gate.py changes that remain after the cycle-3 narrowing: R2 (decline parse and findings join), R1 (follow-ups claim) and the two rule-4 lines.

Usage: python3 -I -B proto_gate.py <package scripts dir> <state checkout>
The functions below are what the implementation would add to delivery_gate.py; they import the 0.26.0 module and change none of it.
Nothing is written: the state checkout is only read. The rule-4 half (the `Merges:` line, head binding, the Captain-only read) is deferred
and lives in proto_merges.py; the effect of the two rule-4 lines on the shipped test suite is measured by proto_narrow.py.
"""
import json, re, subprocess, sys
from pathlib import Path
pkg, state = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, pkg)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decision_ledger as dl
import delivery_gate as dg

END = re.compile(r"(?<![eE]\.[gG]\.)(?<![iI]\.[eE]\.)(?<=[.)\]])\s+(?=[A-Z][^.:\n]{0,40}:)|\n\n")
FINDING = re.compile(r"^\s*[-*]\s*\*{0,2}F\d+\*{0,2}\s*[:(]?\s*\(?\s*(Deferred risk|Polish)\b", re.M)
CLAIM = re.compile(r"\b(accepted|approved|waived|ruled)\b", re.I)
WORDS = re.compile(r"「([^」]*)」")


def declined_items(text):
    out = []
    for start in dg.DECLINE_START.finditer(text):
        rest = text[start.end():]
        end = END.search(rest)
        depth, item = 0, ""
        for ch in (rest[:end.start()] if end else rest).strip().rstrip("."):
            depth = max(depth + (ch in "([") - (ch in ")]"), 0)
            if ch == ";" and depth == 0:
                out.append(item.strip()); item = ""
            else:
                item += ch
        out.append(item.strip())
    return [i for i in out if i and i.lower() not in ("none", "nothing", "n/a")]


def reasons(item):
    found, depth, start = [], 0, 0
    for i, ch in enumerate(item):
        if ch in "([":
            start = i + 1 if depth == 0 else start
            depth += 1
        elif ch in ")]" and depth:
            depth -= 1
            if depth == 0:
                found.append(item[start:i])
    return found


def unreasoned(text):
    return [i for i in declined_items(text) if not any(len(b.split()) >= 2 for b in reasons(i))]


def findings_join(task_text, gate_text):
    report = (dg.VALIDATION_SECTION.findall(task_text) or [""])[-1]
    owed, got = len(FINDING.findall(report)), len(declined_items(gate_text))
    return f"declined items ({got}) are fewer than the validation report's Deferred risk and Polish findings ({owed})" if owed and got < owed else None


def followups_claim(task):
    path = task.with_name(task.stem + "-followups.md")
    if not path.is_file():
        return None
    text = path.read_text()
    body = text.split("\n---\n", 1)[-1]
    first = next((l for l in body.splitlines() if l.strip()), "")
    title = (re.search(r"^title:\s*(.*)$", text, re.M) or [None, ""])[1]
    hit = CLAIM.search(title) or CLAIM.search(first)
    return f"{path.name} claims the Captain's acceptance (\"{hit.group(1)}\") before the gate that records it" if hit else None


ASK_SENTENCE = "Every other PR, the Release PR included, is asked one at a time."


def class_line(cls, verdict):
    return f"class: {cls}" + (" (verdict ask)" if verdict == "ask" else "")


def run_census():
    print("-- R2: the presented declined texts of the three gates written after #671 merged (2026-10-19T08:10Z), and fo-write-checks (its own gate, minutes before): 0.26.0 check vs fixed parse")
    for slug in ("captain-question-load", "chat-only-evidence-observer-blind", "special-role-calls-fire-when-needed", "fo-write-checks"):
        for f in sorted((state / "_archive" / slug / "review" / "validation").glob("briefing-*/index.json")):
            d = json.loads(f.read_text())
            text = d["question"] + "\n" + d["artifacts"][0].get("summary", "")
            print(f"   {slug[:38]:38s} items {len(dg.declined_items(text))}->{len(declined_items(text))}  unreasoned {len(dg.unreasoned_items(text))}->{len(unreasoned(text))}")
    print("-- R2: findings join on special-role (F-id bullets in the report vs the declined items of the presented text)")
    task = state / "_archive" / "special-role-calls-fire-when-needed.md"
    d = json.loads((task.parent / "special-role-calls-fire-when-needed/review/validation/briefing-1/index.json").read_text())
    sha = re.search(r"git-root://state/([0-9a-f]{40})/", d["artifacts"][0]["uri"]).group(1)
    old = subprocess.run(["git", "-C", str(state), "show", f"{sha}:special-role-calls-fire-when-needed.md"], capture_output=True).stdout.decode()
    print("  ", findings_join(old, d["question"] + "\n" + d["artifacts"][0].get("summary", "")))
    print("-- R1: follow-ups tasks beside their task, as they stand at the pin")
    for t in sorted(state.glob("*.md")) + sorted((state / "_archive").glob("*.md")):
        hit = followups_claim(t) if not t.stem.endswith("followups") else None
        if hit:
            print("  ", hit)


def run_rule4():
    print("-- R4 (narrowed): the last next: line is the shipped ASK line plus one sentence; the class line gains the saved verdict when it is ask")
    new = dg.ASK + " " + ASK_SENTENCE
    print(f"   ASK 0.26.0 ({len(dg.ASK.split())} words): {dg.ASK}")
    print(f"   ASK candidate ({len(new.split())} words): {new}")
    for cls, verdict in (("never", "ask"), ("docs-only", "merge"), ("script-with-test", "merge")):
        print(f"   class line, saved verdict {verdict}: {class_line(cls, verdict)!r} (0.26.0: {'class: ' + cls!r})")
    saved = sorted((state / "_archive").glob("*/merge/ask-*.json")) + sorted(state.glob("*/merge/ask-*.json"))
    kinds = {}
    for f in saved:
        r = json.loads(f.read_text())
        kinds[(r.get("class"), r.get("verdict"))] = kinds.get((r.get("class"), r.get("verdict")), 0) + 1
    print(f"   saved merge asks at the pin by (class, verdict): {kinds}")


if __name__ == "__main__":
    run_census()
    run_rule4()
