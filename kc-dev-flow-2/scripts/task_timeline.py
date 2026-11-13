#!/usr/bin/env python3
"""Print one task's per-stage times, dispatch counts and Captain asks; record an ask outside a gate.

  task_timeline.py <state checkout> <task slug> [--json]   print the timeline
  task_timeline.py <state checkout> --all                  one summary line over every archived task
  task_timeline.py <state checkout> <task slug> ask TEXT   append one ask outside a gate, stamped now (UTC)

Times come from records written at the time: author dates of the state checkout's commits
(`dispatch|advance: <slug> entering <stage>`, the commit adding each dispatch record and each
gate room's index.json, `archive <slug>`), the `at` of each gate resolution or withdrawal, and
`<task>/asks.jsonl`. Author dates are used because `pull --rebase` rewrites committer dates.
A revise is a dispatch after the first, by highest plain dispatch-record number, including gaps;
follow-up messages are excluded. An interruption is an FO question outside a scheduled gate,
recorded by `ask` when asked. Gate revise decisions, withdrawals and amendments are separate.
Missing records are reported, never a work hold. Before-gate minutes include FO idle, not just
agent work. No asks.jsonl means unknown, not zero. `ask` appends locally; FO commits the record.
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
    if fm is None:
        raise ValueError(f"{task}: missing or unclosed frontmatter")
    entering, records, rooms, done = {}, {}, {}, None
    for at, subject, added in history(state, slug):
        m = ENTERING.match(subject)
        if m and m["slug"] == slug:
            entering.setdefault(m["stage"], []).append(at)
        archived = ARCHIVE.match(subject)
        if archived and archived["slug"] == slug and done is None:
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
                (int(e["attempt"].rsplit("-", 1)[1]), when(e["at"]),
                 e.get("decision") if e["kind"] == "resolution" else "withdrawn"))
    # A repeat dispatch of a stage writes a record but no `entering` commit.
    starts = {}
    for stage in set(entering) | set(records):
        first = entering.get(stage, [])
        rec = [t for n, t in sorted(records.get(stage, {}).items()) if n > len(first)]
        starts[stage] = first + rec
    segments = sorted((t, s) for s, ts in starts.items() for t in ts)
    ends = [t for t, _ in segments[1:]] + [done]
    rows = {}
    now = datetime.now(timezone.utc)
    for (start, stage), end in zip(segments, ends):
        row = rows.setdefault(stage, {"stage": stage, "start": start, "end": end, "elapsed": 0.0})
        row["end"] = end
        row["elapsed"] += mins(start, end or now) or 0
    for (stage, _), opened in sorted(rooms.items()):
        if stage not in rows:  # A gate-only stage starts at its first room.
            stage_rooms = [t for (s, _), t in rooms.items() if s == stage]
            stage_closes = {n: t for n, t, _ in closes.get(stage, [])}
            last = max(stage_closes.values(), default=None) if all(
                n in stage_closes for (s, n) in rooms if s == stage) else None
            opened = min(stage_rooms)
            rows[stage] = {"stage": stage, "start": opened, "end": last, "elapsed": mins(opened, last or now)}
    out = []
    for stage, row in sorted(rows.items(), key=lambda kv: kv[1]["start"]):
        attempts = []
        for (st, n), opened in sorted(rooms.items()):
            if st == stage:
                close = next(((t, outcome) for number, t, outcome in closes.get(stage, []) if number == n),
                             (None, "open"))
                attempts.append({"attempt": n, "opened": opened, "closed": close[0], "outcome": close[1]})
        wait = sum(mins(a["opened"], a["closed"] or row["end"] or now) or 0 for a in attempts)
        after = 0.0
        for (start, st), end in zip(segments, ends):
            if st != stage:
                continue
            end = end or now
            last = max((a["closed"] for a in attempts if a["closed"] and start <= a["closed"] <= end), default=None)
            after += mins(last, end) or 0.0
        after = round(after, 1)
        before = round(row["elapsed"] - wait - after, 1)
        if stage not in starts:
            before, after = 0.0, round(row["elapsed"] - wait, 1)
        # see docs/adr/0080-stage-times-come-from-state-records-and-outside-gate-questions-are-recorded-when-asked.md
        n = max(len(starts.get(stage, [])), max(records.get(stage, {}), default=0))
        # see docs/adr/0085-a-budget-may-bound-ideation-rounds-and-the-timeline-prints-each-round.md
        rounds = []
        for (start, st), end in zip(segments, ends):
            if st != stage:
                continue
            closed = [a for a in attempts if a["closed"] and start <= a["closed"] <= (end or now)]
            opened = [a for a in attempts if not a["closed"] and start <= a["opened"] <= (end or now)]
            following = next((s for t, s in segments if t == end), None) if end else None
            result = (", ".join(a["outcome"] for a in closed) if closed else "gate open" if opened else "running" if end is None
                      else "redispatched" if following == stage else f"next {following}" if following else "archived")
            rounds.append({"round": len(rounds) + 1, "start": iso(start), "end": iso(end),
                           "minutes": mins(start, end or now), "result": result})
        out.append({
            "stage": stage, "start": iso(row["start"]), "end": iso(row["end"]),
            "elapsed_min": round(row["elapsed"], 1),
            "before_gate_min": before,
            "captain_wait_min": round(wait, 1), "after_gate_min": after,
            "dispatches": n, "repeat_dispatches": max(n - 1, 0), "dispatch_records": len(records.get(stage, {})),
            "gate_attempts": [{**a, "opened": iso(a["opened"]), "closed": iso(a["closed"])} for a in attempts],
            "rounds": rounds,
        })
    asks_file = folder(task) / "asks.jsonl"
    asks = [json.loads(line) for line in asks_file.read_text().splitlines() if line.strip()] if asks_file.is_file() else []
    unassigned = []
    for row in out:
        row["asks"] = []
        row["asks_outside_gate"] = 0 if asks_file.is_file() else None
    for ask in asks:
        at = when(ask["at"])
        stage = next((s for (start, s), end in zip(segments, ends)
                      if start <= at < (end or now)), None)
        if stage is None:
            stage = next((r["stage"] for r in out if when(r["start"]) <= at < (when(r["end"]) if r["end"] else now)), None)
        if stage is None:
            unassigned.append(ask)
        else:
            row = next(r for r in out if r["stage"] == stage)
            row["asks"].append(ask)
            row["asks_outside_gate"] += 1
    gates = [o for v in closes.values() for _, _, o in v]
    known = set(starts) | set(closes) | {s for s, _ in rooms}
    return {
        "task": slug, "stages": out, "done": iso(done),
        "withdrawn_gate_attempts": gates.count("withdrawn"), "gate_revise_decisions": gates.count("revise"),
        "stages_without_start": sorted(known - set(rows)), "unassigned_asks": unassigned,
        "amendments_outside_gate": sum(1 for _, _, place in AMENDMENT.findall(body) if "gate" not in place.lower()),
        "asks_outside_gate": len(asks) if asks_file.is_file() else None,
    }


def show(t):
    print(f"task: {t['task']}")
    for r in t["stages"]:
        print(f"  {r['stage']}: {r['start']} -> {r['end'] or 'running'}  {r['elapsed_min']} min "
              f"(before gate {r['before_gate_min']}, Captain wait {r['captain_wait_min']}, after gate {r['after_gate_min']}); "
              f"dispatches {r['dispatches']}, repeats {r['repeat_dispatches']}")
        for x in r["rounds"]:
            print(f"    round {x['round']}: {x['start']} -> {x['end'] or 'running'}  {x['minutes']} min; {x['result']}")
        print(f"    asks outside a gate: {r['asks_outside_gate'] if r['asks_outside_gate'] is not None else 'not recorded'}")
        for ask in r["asks"]:
            print(f"      {ask['at']}: {ask['asked']}")
        for a in r["gate_attempts"]:
            print(f"    gate attempt {a['attempt']}: opened {a['opened']}, closed {a['closed'] or '-'}, {a['outcome']}")
    print(f"  done: {t['done'] or '-'}")
    if t["stages_without_start"]:
        print("  stages without start: " + ", ".join(t["stages_without_start"]))
    for ask in t["unassigned_asks"]:
        print(f"  ask with no stage start: {ask['at']}: {ask['asked']}")
    asks = t["asks_outside_gate"]
    print(f"  asks outside a gate: {'not recorded (no asks.jsonl)' if asks is None else asks}; "
          f"withdrawn gate attempts: {t['withdrawn_gate_attempts']}; revise decisions: {t['gate_revise_decisions']}; "
          f"amendments outside a gate: {t['amendments_outside_gate']}")


# see docs/adr/0080-stage-times-come-from-state-records-and-outside-gate-questions-are-recorded-when-asked.md
def record_ask(state, slug, text, clock=None):
    path = folder(find_task(state, slug)) / "asks.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"at": iso(clock or datetime.now(timezone.utc)), "asked": text}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    with path.open(encoding="utf-8") as fh:
        print(f"recorded ask {sum(1 for _ in fh)} in {path}")


# see docs/adr/0080-stage-times-come-from-state-records-and-outside-gate-questions-are-recorded-when-asked.md
def sweep(state):
    archive = state / "_archive"
    slugs = {p.stem for p in archive.glob("*.md")} | {p.parent.name for p in archive.glob("*/index.md")}
    rows = [timeline(state, slug) for slug in sorted(slugs)]
    timed = [r for r in rows if r["stages"]]
    print(f"archived tasks: {len(rows)}; at least one stage timed: {len(timed)}; "
          f"with a repeat dispatch: {sum(any(s['repeat_dispatches'] for s in r['stages']) for r in rows)}; "
          f"with a withdrawn gate attempt: {sum(r['withdrawn_gate_attempts'] > 0 for r in rows)}; "
          f"with an amendment outside a gate: {sum(r['amendments_outside_gate'] > 0 for r in rows)}; "
          f"with asks.jsonl: {sum(r['asks_outside_gate'] is not None for r in rows)}")
    print("no stage timed: " + " ".join(r["task"] for r in rows if not r["stages"]))
    for row in rows:
        if row["stages_without_start"]:
            print(f"stages without start: {row['task']}: {', '.join(row['stages_without_start'])}")


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
