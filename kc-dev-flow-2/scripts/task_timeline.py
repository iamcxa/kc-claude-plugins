#!/usr/bin/env python3
"""Print one task's per-stage times, repeat dispatches and out-of-gate Captain asks.

Reads only records written at the time: the state checkout's git history (author
dates of Spacedock's own commits) and the gate records in the task frontmatter.
Never writes. POC: proof of concept for task each-task-records-stage-time-revises-and-interruptions.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ENTERING = re.compile(r"^(?:dispatch|advance): (?P<slug>\S+) entering (?P<stage>\S+)$")
ARCHIVE = re.compile(r"^archive (?P<slug>\S+)")
BRIEFING = re.compile(r"(?:^|/)review/(?P<stage>[^/]+)/briefing-(?P<n>\d+)/index\.json$")
DISPATCH_RECORD = re.compile(r"(?:^|/)dispatch/(?P<stage>[a-z-]+)-(?P<n>\d+)\.md$")
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2}),\s*(.+)$", re.M)


def when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def task_paths(state, slug):
    return [f"{slug}.md", slug, f"_archive/{slug}.md", f"_archive/{slug}"]


def history(state, slug):
    # Author date survives `pull --rebase`; committer date does not.
    out = subprocess.run(
        ["git", "-C", str(state), "log", "--reverse", "--no-renames", "--name-status",
         "--format=\x1e%H\x1f%aI\x1f%s", "--", *task_paths(state, slug)],
        capture_output=True, text=True, check=True).stdout
    for chunk in out.split("\x1e")[1:]:
        head, _, body = chunk.partition("\n")
        sha, date, subject = head.split("\x1f")
        files = [line.split("\t") for line in body.splitlines() if "\t" in line]
        yield sha, when(date), subject, files


def gate_records(text):
    """Return [(stage, kind, at, decision)] from the frontmatter gate records."""
    front = text.split("\n---", 1)[0]
    rows, stage, kind = [], None, None
    for line in front.splitlines():
        stripped = line.strip()
        m = re.match(r"^stage: (\S+)$", stripped)
        if m and line.startswith("          stage:"):
            stage = m[1]
            continue
        if stripped in ("resolution:", "withdrawal:"):
            kind = stripped[:-1]
            rows.append([stage, kind, None, None])
            continue
        if kind and stripped.startswith("at:"):
            rows[-1][2] = when(stripped.split(":", 1)[1].strip().strip('"'))
        elif kind and stripped.startswith("decision:"):
            rows[-1][3] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith(("application:", "- id:")):
            kind = None
    return [tuple(r) for r in rows if r[2]]


def find_task(state, slug):
    for rel in (f"{slug}.md", f"{slug}/index.md", f"_archive/{slug}.md", f"_archive/{slug}/index.md"):
        if (state / rel).is_file():
            return state / rel
    raise SystemExit(f"task_timeline: no task file for {slug} under {state}")


def minutes(a, b):
    return None if a is None or b is None else round((b - a).total_seconds() / 60, 1)


def timeline(state, slug):
    text = find_task(state, slug).read_text(encoding="utf-8")
    stages, order, opened, records, done = {}, [], {}, {}, None
    for sha, at, subject, files in history(state, slug):
        m = ENTERING.match(subject)
        if m and m["slug"] == slug:
            st = stages.setdefault(m["stage"], {"dispatches": [], "gates": []})
            st["dispatches"].append(at)
            order.append((at, m["stage"]))
        if ARCHIVE.match(subject):
            done = done or at
        for status, *paths in files:
            for path in paths:
                b = BRIEFING.search(path)
                if b and status.startswith("A"):
                    opened.setdefault((b["stage"], int(b["n"])), at)
                d = DISPATCH_RECORD.search(path)
                if d and status.startswith("A"):
                    records.setdefault(d["stage"], {}).setdefault(int(d["n"]), at)
    gates = gate_records(text)
    for (stage, n), at in sorted(opened.items()):
        stages.setdefault(stage, {"dispatches": [], "gates": []})["gates"].append({"attempt": n, "opened": at})
    for stage, recs in records.items():
        st = stages.setdefault(stage, {"dispatches": [], "gates": []})
        if len(recs) >= len(st["dispatches"]):
            # A repeat dispatch of the same stage writes a record but no `entering` commit.
            first = st["dispatches"][:1]
            st["dispatches"] = sorted(first + [t for n, t in sorted(recs.items())][len(first):])
            order.extend((t, stage) for t in st["dispatches"][len(first):])
    by_stage = {}
    for stage, kind, at, decision in gates:
        by_stage.setdefault(stage, []).append((kind, at, decision))
    for stage, st in stages.items():
        for gate, (kind, at, decision) in zip(st["gates"], by_stage.get(stage, [])):
            gate.update(closed=at, outcome=decision or kind)
    order = sorted(set(order))
    ends = [t for t, _ in order[1:]] + [done]
    rows = {}
    for (start, stage), end in zip(order, ends):
        row = rows.setdefault(stage, {"stage": stage, "start": start, "end": end, "elapsed_min": 0.0})
        row["end"] = end
        row["elapsed_min"] = round(row["elapsed_min"] + (minutes(start, end) or 0), 1)
    for stage, row in rows.items():
        st = stages[stage]
        gates_in = st["gates"]
        wait = round(sum(minutes(g["opened"], g.get("closed")) or 0 for g in gates_in), 1)
        closed = [g["closed"] for g in gates_in if g.get("closed")]
        after = minutes(max(closed), row["end"]) if closed and row["end"] and max(closed) < row["end"] else 0.0
        row.update(
            start=row["start"].isoformat(), end=row["end"].isoformat() if row["end"] else None,
            agent_min=round(row["elapsed_min"] - wait - after, 1), captain_wait_min=wait, after_gate_min=after,
            dispatches=len(st["dispatches"]), repeat_dispatches=max(len(st["dispatches"]) - 1, 0),
            dispatch_records=len(records.get(stage, ())),
            gate_attempts=[{"attempt": g["attempt"], "opened": g["opened"].isoformat(),
                            "closed": g["closed"].isoformat() if g.get("closed") else None,
                            "outcome": g.get("outcome")} for g in gates_in])
    rows = sorted(rows.values(), key=lambda r: r["start"])
    backlog = [(k, at, d) for k, at, d in by_stage.get("backlog", [])]
    amendments = [{"n": int(n), "date": d, "place": p.strip()} for n, d, p in AMENDMENT.findall(text)]
    return {
        "task": slug,
        "backlog_gate": [{"outcome": d or k, "closed": at.isoformat()} for k, at, d in backlog],
        "stages": rows,
        "done": done.isoformat() if done else None,
        "re_asks": sum(1 for _, k, _, _ in gates if k == "withdrawal"),
        "revise_decisions": sum(1 for _, _, _, d in gates if d == "revise"),
        "out_of_gate_amendments": [a for a in amendments if "gate" not in a["place"].lower()],
        "interruptions_recorded": False,
    }


def show(t):
    print(f"task: {t['task']}")
    for r in t["stages"]:
        print(f"  {r['stage']}: {r['start']} -> {r['end']}  elapsed {r['elapsed_min']} min, "
              f"agent {r['agent_min']} min, captain wait {r['captain_wait_min']} min, after gate {r['after_gate_min']} min, "
              f"dispatches {r['dispatches']} (repeat {r['repeat_dispatches']}, records {r['dispatch_records']})")
        for g in r["gate_attempts"]:
            print(f"    gate attempt {g['attempt']}: opened {g['opened']} closed {g['closed']} {g['outcome']}")
    print(f"  done: {t['done']}")
    print(f"  re-asks (withdrawn gate attempts): {t['re_asks']}; revise decisions: {t['revise_decisions']}")
    print(f"  amendments outside a gate: {len(t['out_of_gate_amendments'])}")
    print("  interruptions: not recorded (no record of a question outside a gate exists)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("task")
    ap.add_argument("--state", required=True, type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    t = timeline(a.state, a.task)
    print(json.dumps(t, indent=1, ensure_ascii=False)) if a.json else show(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
