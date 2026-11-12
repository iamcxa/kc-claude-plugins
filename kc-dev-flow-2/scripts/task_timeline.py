#!/usr/bin/env python3
"""Print one task's per-stage times, dispatch counts and Captain asks; record an ask outside a gate.

  task_timeline.py <state checkout> <task slug> [--json]   print the timeline
  task_timeline.py <state checkout> --all                  one summary line over every archived task
  task_timeline.py <state checkout> <task slug> ask TEXT   append one ask outside a gate, stamped now (UTC)

Times come from records written at the time: author dates of the state checkout's commits
(`dispatch|advance: <slug> entering <stage>`, the commit adding each dispatch record and each
gate room's index.json, `archive <slug>`), the `at` of each gate resolution or withdrawal, and
`<task>/asks.jsonl`. Author dates are used because `pull --rebase` rewrites committer dates.
POC for task each-task-records-stage-time-revises-and-interruptions.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decision_ledger import gate_entries, split_task  # noqa: E402
from role_triggers import STAGE_RECORD  # noqa: E402

ENTERING = re.compile(r"^(?:dispatch|advance): (?P<slug>\S+) entering (?P<stage>\S+)$")
ARCHIVE = re.compile(r"^archive (?P<slug>\S+)")
ROOM = re.compile(r"(?:^|/)review/(?P<stage>[^/]+)/briefing-(?P<n>\d+)/index\.json$")
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2}),\s*(.+)$", re.M)


def when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def mins(a, b):
    return round((b - a).total_seconds() / 60, 1) if a and b else None


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def find_task(state, slug):
    for rel in (f"{slug}/index.md", f"{slug}.md", f"_archive/{slug}/index.md", f"_archive/{slug}.md"):
        if (state / rel).is_file():
            return state / rel
    raise SystemExit(f"task_timeline: no task file for {slug} under {state}")


def folder(task):
    return task.parent if task.name == "index.md" else task.with_suffix("")


def history(state, slug):
    out = subprocess.run(
        ["git", "-C", str(state), "log", "--reverse", "--no-renames", "--name-status",
         "--format=\x1e%aI\x1f%s", "--", f"{slug}.md", slug, f"_archive/{slug}.md", f"_archive/{slug}"],
        capture_output=True, text=True, check=True).stdout
    for chunk in out.split("\x1e")[1:]:
        head, _, body = chunk.partition("\n")
        date, subject = head.split("\x1f", 1)
        added = [line.split("\t")[-1] for line in body.splitlines() if line.startswith("A\t")]
        yield when(date), subject, added


def timeline(state, slug):
    task = find_task(state, slug)
    text = task.read_text(encoding="utf-8")
    fm, body = split_task(text)
    entering, records, rooms, done = {}, {}, {}, None
    for at, subject, added in history(state, slug):
        m = ENTERING.match(subject)
        if m and m["slug"] == slug:
            entering.setdefault(m["stage"], []).append(at)
        if ARCHIVE.match(subject) and done is None:
            done = at
        for path in added:
            name = path.rsplit("/", 1)[-1]
            r = STAGE_RECORD.fullmatch(name)
            if "/dispatch/" in f"/{path}" and r and not r[3]:
                records.setdefault(r[1], {}).setdefault(int(r[2]), at)
            g = ROOM.search(path)
            if g:
                rooms.setdefault((g["stage"], int(g["n"])), at)
    closes = {}
    for e in gate_entries(fm or []):
        if e.get("at"):
            closes.setdefault(e["stage"], []).append(
                (when(e["at"]), e.get("decision") if e["kind"] == "resolution" else "withdrawn"))
    # A repeat dispatch of a stage writes a record but no `entering` commit.
    starts = {}
    for stage in set(entering) | set(records):
        first = entering.get(stage, [])[:1]
        rec = [t for _, t in sorted(records.get(stage, {}).items())]
        starts[stage] = first + rec[len(first):] if len(rec) >= len(first) else entering[stage]
    segments = sorted((t, s) for s, ts in starts.items() for t in ts)
    ends = [t for t, _ in segments[1:]] + [done]
    rows = {}
    now = datetime.now(timezone.utc)
    for (start, stage), end in zip(segments, ends):
        row = rows.setdefault(stage, {"stage": stage, "start": start, "end": end, "elapsed": 0.0})
        row["end"] = end
        row["elapsed"] += mins(start, end or now) or 0
    for (stage, _), opened in sorted(rooms.items()):
        if stage not in rows:  # a gate with no dispatch, such as backlog: the stage is its gate
            last = max((t for t, _ in closes.get(stage, [])), default=None)
            rows[stage] = {"stage": stage, "start": opened, "end": last, "elapsed": mins(opened, last or now)}
    out = []
    for stage, row in sorted(rows.items(), key=lambda kv: kv[1]["start"]):
        attempts = []
        for (st, n), opened in sorted(rooms.items()):
            if st == stage:
                close = closes.get(stage, [])[n - 1] if n <= len(closes.get(stage, [])) else (None, "open")
                attempts.append({"attempt": n, "opened": opened, "closed": close[0], "outcome": close[1]})
        wait = sum(mins(a["opened"], a["closed"] or row["end"] or now) or 0 for a in attempts)
        last = max((a["closed"] for a in attempts if a["closed"]), default=None)
        after = mins(last, row["end"]) if last and row["end"] and last < row["end"] else 0.0
        # Record numbers are FO's dispatch count; a gap means a record was never written, not no dispatch.
        n = max(len(starts.get(stage, [])), max(records.get(stage, {}), default=0))
        out.append({
            "stage": stage, "start": iso(row["start"]), "end": iso(row["end"]),
            "elapsed_min": round(row["elapsed"], 1),
            "before_gate_min": round(row["elapsed"] - wait - after, 1),
            "captain_wait_min": round(wait, 1), "after_gate_min": after,
            "dispatches": n, "repeat_dispatches": max(n - 1, 0), "dispatch_records": len(records.get(stage, {})),
            "gate_attempts": [{**a, "opened": iso(a["opened"]), "closed": iso(a["closed"])} for a in attempts],
        })
    asks_file = folder(task) / "asks.jsonl"
    asks = [json.loads(line) for line in asks_file.read_text().splitlines() if line.strip()] if asks_file.is_file() else []
    gates = [o for v in closes.values() for _, o in v]
    return {
        "task": slug, "stages": out, "done": iso(done),
        "re_asks": gates.count("withdrawn"), "revise_decisions": gates.count("revise"),
        "amendments_outside_gate": sum(1 for _, _, place in AMENDMENT.findall(body) if "gate" not in place.lower()),
        "asks_outside_gate": len(asks) if asks_file.is_file() else None,
    }


def show(t):
    print(f"task: {t['task']}")
    for r in t["stages"]:
        print(f"  {r['stage']}: {r['start']} -> {r['end'] or 'running'}  {r['elapsed_min']} min "
              f"(before gate {r['before_gate_min']}, Captain wait {r['captain_wait_min']}, after gate {r['after_gate_min']}); "
              f"dispatches {r['dispatches']}, repeats {r['repeat_dispatches']}")
        for a in r["gate_attempts"]:
            print(f"    gate attempt {a['attempt']}: opened {a['opened']}, closed {a['closed'] or '-'}, {a['outcome']}")
    print(f"  done: {t['done'] or '-'}")
    asks = t["asks_outside_gate"]
    print(f"  asks outside a gate: {'not recorded (no asks.jsonl)' if asks is None else asks}; "
          f"withdrawn gate attempts: {t['re_asks']}; revise decisions: {t['revise_decisions']}; "
          f"amendments outside a gate: {t['amendments_outside_gate']}")


def record_ask(state, slug, text, clock=None):
    path = folder(find_task(state, slug)) / "asks.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"at": iso(clock or datetime.now(timezone.utc)), "asked": text}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"recorded ask {sum(1 for _ in path.open())} in {path}")


def sweep(state):
    rows = [timeline(state, f.stem) for f in sorted((state / "_archive").glob("*.md"))]
    timed = [r for r in rows if r["stages"]]
    print(f"archived tasks: {len(rows)}; at least one stage timed: {len(timed)}; "
          f"with a repeat dispatch: {sum(any(s['repeat_dispatches'] for s in r['stages']) for r in rows)}; "
          f"with a withdrawn gate attempt: {sum(r['re_asks'] > 0 for r in rows)}; "
          f"with an amendment outside a gate: {sum(r['amendments_outside_gate'] > 0 for r in rows)}; "
          f"with asks.jsonl: {sum(r['asks_outside_gate'] is not None for r in rows)}")
    print("no stage timed: " + " ".join(r["task"] for r in rows if not r["stages"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("state", type=Path)
    ap.add_argument("task", nargs="?")
    ap.add_argument("action", nargs="?", choices=["ask"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    if a.all:
        sweep(a.state)
    elif a.action == "ask":
        if not (a.text or "").strip():
            ap.error("ask needs the question text")
        record_ask(a.state, a.task, a.text)
    elif a.task:
        t = timeline(a.state, a.task)
        print(json.dumps(t, indent=1, ensure_ascii=False)) if a.json else show(t)
    else:
        ap.error("name a task or pass --all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
