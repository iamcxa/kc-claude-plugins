#!/usr/bin/env python3
"""Prototype of the delivery_gate.py changes (R1, R2, R4), run against the real state checkout. Writes nothing.

Usage: python3 -I -B proto_gate.py <package scripts dir> <state checkout>
The functions below are what the implementation would add to delivery_gate.py; they import the 0.26.0 module and change none of it.
"""
import json, re, sys
from pathlib import Path
pkg, state = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, pkg)
import decision_ledger as dl
import delivery_gate as dg

END = re.compile(r"(?<![eE]\.[gG]\.)(?<![iI]\.[eE]\.)(?<=[.)\]])\s+(?=[A-Z][^.:\n]{0,40}:)|\n\n")
REF = re.compile(r"[\w.-]+/[\w.-]+#\d+")
FINDING = re.compile(r"^\s*[-*]\s*\*{0,2}F\d+\*{0,2}\s*[:(]?\s*\(?\s*(Deferred risk|Polish)\b", re.M)
CLAIM = re.compile(r"\b(accepted|approved|waived|ruled)\b", re.I)


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


def approved(task):
    fm, _ = dl.split_task(task.read_text())
    got = [e for e in dl.gate_entries(fm) if e["stage"] == "validation" and e["kind"] == "resolution" and e.get("decision") == "approve"]
    if not got:
        return None, None
    return got[-1], dl.question(task.parent, task, got[-1]["room"])


def next_line(task, pr):
    entry, question = approved(task)
    if entry is None:
        return "next: ask the Captain with this text; nothing is carried until he approves it."
    named = REF.findall(dg.clause(question or "", "Merges") or "")
    if pr in named:
        return (f"next: merge this head; the question he approved on {entry['at'][:10]} names {pr} in its Merges: line. "
                f"Ask instead if his reason ({entry.get('reason','')[:100]}) says he merges or holds.")
    return f"next: ask the Captain to merge; the question he approved names no merge of {pr}."


if __name__ == "__main__":
    print("-- R4: real approved question of special-role-calls-fire-when-needed (no Merges: line)")
    task = state / "_archive" / "special-role-calls-fire-when-needed.md"
    print(next_line(task, "iamcxa/kc-claude-plugins#682"))
    print("-- R4: same task, the question rewritten the way the Captain's text would read with the line (copy under a scratch dir, nothing written here)")
    import shutil, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="proto-gate-"))
    shutil.copy(task, tmp / task.name)
    room = tmp / "special-role-calls-fire-when-needed" / "review" / "validation" / "briefing-1"
    room.mkdir(parents=True)
    entry, question = approved(task)
    src = json.loads((task.parent / entry["room"] / "index.json").read_text())
    for name, line in (("Merges: iamcxa/kc-claude-plugins#682", "carried"), ("Merges: none", "none"), ("Merges: iamcxa/kc-claude-plugins#672", "other PR")):
        src["question"] = question + " " + name
        (room / "index.json").write_text(json.dumps(src))
        print(f"   {line:9s}", next_line(tmp / task.name, "iamcxa/kc-claude-plugins#682"))
    print("-- R4 control: the question as approved, text only: 'hold Release PR #672' names #672 and not as a Merges: line ->", bool(REF.findall(dg.clause(question, 'Merges') or '')))
    print("-- R2: the presented declined texts of the three gates written after #671 merged (2026-10-19T08:10Z), and fo-write-checks (its own gate, minutes before): 0.26.0 check vs fixed parse")
    for slug in ("captain-question-load", "chat-only-evidence-observer-blind", "special-role-calls-fire-when-needed", "fo-write-checks"):
        for f in sorted((state / "_archive" / slug / "review" / "validation").glob("briefing-*/index.json")):
            d = json.loads(f.read_text())
            text = d["question"] + "\n" + d["artifacts"][0].get("summary", "")
            print(f"   {slug[:38]:38s} items {len(dg.declined_items(text))}->{len(declined_items(text))}  unreasoned {len(dg.unreasoned_items(text))}->{len(unreasoned(text))}")
    print("-- R2: findings join on special-role (F-id bullets in the report vs the declined items of the presented text)")
    d = json.loads((task.parent / "special-role-calls-fire-when-needed/review/validation/briefing-1/index.json").read_text())
    sha = re.search(r"git-root://state/([0-9a-f]{40})/", d["artifacts"][0]["uri"]).group(1)
    import subprocess
    old = subprocess.run(["git", "-C", str(state), "show", f"{sha}:special-role-calls-fire-when-needed.md"], capture_output=True).stdout.decode()
    print("  ", findings_join(old, d["question"] + "\n" + d["artifacts"][0].get("summary", "")))
    print("-- R1: follow-ups tasks beside their task, as they stand at the pin")
    for t in sorted(state.glob("*.md")) + sorted((state / "_archive").glob("*.md")):
        hit = followups_claim(t) if not t.stem.endswith("followups") else None
        if hit:
            print("  ", hit)
