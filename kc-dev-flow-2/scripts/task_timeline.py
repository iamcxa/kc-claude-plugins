#!/usr/bin/env python3
"""Read task times and open Captain questions; append question events.

  task_timeline.py <state checkout> <task slug> [--json]   print the timeline
  task_timeline.py <state checkout> --all                  one summary line over every archived task
  task_timeline.py <state> <task> ask TEXT --holds task --by SESSION
  task_timeline.py <state> <task> reask|revise|answer|acted|withdraw KEY [fields]
  task_timeline.py <state> --open [--gates] [--as-of UTC] [--json]

Question format: references/captain-question-records.md in this package.
--option id=text[=effect] may repeat on ask/revise; on answer it is the chosen id.
--ref takes one JSON object with kind, ref and ready; it may repeat.
--late records an unknown asking time; --as-of filters reads, never stamps writes.

Times come from records written at the time: author dates of the state checkout's commits
(`dispatch|advance: <slug> entering <stage>`, the commit adding each dispatch record and each
gate room's index.json, `archive <slug>`), the `at` of each gate resolution or withdrawal, and
`<task>/asks.jsonl`. Author dates are used because `pull --rebase` rewrites committer dates.
A revise is a dispatch after the first, by highest plain dispatch-record number, including gaps;
follow-up messages are excluded. An interruption is an FO question outside a scheduled gate,
recorded by `ask` when asked. Gate revise decisions, withdrawals and amendments are separate.
Missing timing records are reported without a work hold. Before-gate minutes include FO idle, not just
agent work. No asks.jsonl means unknown, not zero. `ask` appends locally; FO commits the record.
"""
import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decision_ledger import KEY, gate_entries, question, split_task, unquote  # noqa: E402
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
    asks = [e for e in read_asks(asks_file) if "v" not in e or (e.get("v") == 1 and e.get("event") in ("ask", "reask"))]
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
            print(f"      {ask['at']}: {ask.get('asked', 'shown again: ' + ask.get('key', ''))}")
        for a in r["gate_attempts"]:
            print(f"    gate attempt {a['attempt']}: opened {a['opened']}, closed {a['closed'] or '-'}, {a['outcome']}")
    print(f"  done: {t['done'] or '-'}")
    if t["stages_without_start"]:
        print("  stages without start: " + ", ".join(t["stages_without_start"]))
    for ask in t["unassigned_asks"]:
        print(f"  ask with no stage start: {ask['at']}: {ask.get('asked', 'shown again: ' + ask.get('key', ''))}")
    asks = t["asks_outside_gate"]
    print(f"  asks outside a gate: {'not recorded (no asks.jsonl)' if asks is None else asks}; "
          f"withdrawn gate attempts: {t['withdrawn_gate_attempts']}; revise decisions: {t['gate_revise_decisions']}; "
          f"amendments outside a gate: {t['amendments_outside_gate']}")


# see docs/adr/0086-a-captain-question-outside-a-gate-stays-open-until-answered.md
EVENTS = {"ask", "reask", "revise", "answer", "acted", "withdraw"}
CHANNELS = {"chat", "dialog", "review", "message"}
HOLDS = {"task", "acceptance", "nothing"}
REVISION_FIELDS = {"asked", "holds", "options", "recommend", "grounds", "approve_means", "tasks", "refs"}
REQUIRED = {"ask": {"asked", "asked_at", "channel", "by", "holds"},
            "reask": {"channel"}, "revise": {"revision", "reason", "asked", "holds"},
            "answer": {"revision", "words", "option", "resolution", "channel"},
            "acted": {"what"}, "withdraw": {"reason"}}


def read_asks(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []


def ask_files(state):
    return sorted(p for pattern in ("*/asks.jsonl", "_archive/*/asks.jsonl") for p in state.glob(pattern))


def fold_question(events):
    q = None
    for e in events:
        if e.get("v", 0) > 1:
            if q:
                q["state"] = "unknown"
            continue
        event = e.get("event")
        if e.get("v") != 1 or event not in EVENTS:
            continue
        if q is None:
            if event != "ask":
                continue
            q = {"kind": "question", "key": e["key"], "revision": 1, "by": e["by"],
                 "waiting_since": e["asked_at"], "recorded_at": e["at"], "interruptions": 0,
                 "state": "open", "revisions": {}, "showings": {}, "review_shown": False}
        elif q["state"] != "open":
            if event == "acted" and q["state"] == "answered":
                q["state"] = "done"
            elif q["state"] != "unknown":
                print(f"question record {e['key']}: ignored {event} after {q['state']}", file=sys.stderr)
            continue
        elif event == "ask":
            continue
        if event in ("ask", "revise"):
            q.update({k: e.get(k) for k in REVISION_FIELDS})
            q["revision"] = e.get("revision", 1)
            q["revisions"][q["revision"]] = {k: e.get(k) for k in REVISION_FIELDS}
        if event in ("ask", "reask"):
            q["interruptions"] += 1
            q["last_shown"] = {"at": e["at"], "channel": e["channel"], "briefing": e.get("briefing")}
            q["showings"][e["channel"]] = q["revision"]
            q["review_shown"] |= e["channel"] == "review"
        elif event == "answer":
            q["state"], q["answer"] = "answered", e
        elif event == "withdraw":
            q["state"] = "withdrawn"
    return q


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_revision(fields):
    if not nonempty(fields.get("asked")) or fields.get("holds") not in HOLDS:
        raise ValueError("question needs nonempty asked and holds task|acceptance|nothing")
    options = fields.get("options", [])
    if not isinstance(options, list) or any(not isinstance(o, dict) or not nonempty(o.get("id"))
            or not nonempty(o.get("text")) or ("effect" in o and not nonempty(o["effect"])) for o in options):
        raise ValueError("options need id, text and optional effect")
    ids = [o["id"] for o in options]
    if len(ids) != len(set(ids)):
        raise ValueError("option ids must be distinct")
    for field in ("recommend", "approve_means"):
        if fields.get(field) is not None and fields[field] not in ids:
            raise ValueError(f"{field} must name an option")
    tasks = fields.get("tasks", [])
    if not isinstance(tasks, list) or not all(nonempty(t) and "/" not in t for t in tasks):
        raise ValueError("tasks must be task slugs")
    if "grounds" in fields and not isinstance(fields["grounds"], str):
        raise ValueError("grounds must be text")
    refs = fields.get("refs", [])
    if not isinstance(refs, list) or any(not isinstance(r, dict) or r.get("kind") not in
            {"file", "commit", "url", "command", "record"} or not nonempty(r.get("ref"))
            or not isinstance(r.get("ready"), bool) for r in refs):
        raise ValueError("refs need kind, ref and boolean ready")
    if any(r["kind"] == "file" and (Path(r["ref"]).is_absolute() or ".." in Path(r["ref"]).parts) for r in refs):
        raise ValueError("file refs must be relative to the task folder")


def write_event(state, slug, event, fields, clock=None):
    if event not in EVENTS:
        raise ValueError(f"unknown event {event}")
    fields = dict(fields)
    path = folder(find_task(state, slug)) / "asks.jsonl"
    lines = read_asks(path)
    at = iso(clock or datetime.now(timezone.utc))
    if event == "ask":
        key = f"{path.parent.name}#{1 + sum(e.get('event') == 'ask' for e in lines)}"
        if fields.get("asked_at") == "now":
            fields["asked_at"] = at
        if fields.get("asked_at") not in (None, at):
            raise ValueError("asked_at must be the write time or null for a late record")
        if not nonempty(fields.get("by")):
            command = shlex.join(["python3", str(Path(__file__).resolve()), str(state), slug, "ask",
                                  str(fields.get("asked", "")), "--holds", str(fields.get("holds") or "task"),
                                  "--channel", str(fields.get("channel") or "chat"), "--by", "<session>"])
            raise ValueError("ask needs --by with the FO session name; run: " + command)
    else:
        key = fields.pop("key", None)
        q = fold_question([e for e in lines if e.get("key") == key])
        if not q:
            raise ValueError(f"no question {key}")
        if q["state"] != "open" and not (event == "acted" and q["state"] == "answered"):
            raise ValueError(f"{key} is {q['state']}; no {event} after closing")
        if event == "acted" and q["state"] != "answered":
            raise ValueError("acted needs an answer")
        if event == "revise" and fields.get("revision") != q["revision"] + 1:
            raise ValueError("revision must be previous + 1")
        if event == "answer":
            channel = fields.get("channel")
            shown = q["showings"].get(channel)
            fields.setdefault("revision", shown)
            if shown is None or fields["revision"] != shown:
                raise ValueError("answer revision must be the latest showing in its channel")
            revision = q["revisions"][shown]
            if any(fields.get(k) is not None and not nonempty(fields[k]) for k in ("words", "option", "resolution")):
                raise ValueError("words, option and resolution must be nonempty text or null")
            words = fields.get("words")
            option = fields.get("option")
            if not words:
                if revision.get("options") and not revision.get("approve_means"):
                    raise ValueError("wordless answer needs approve_means; ask which option")
                if option is not None and option != revision.get("approve_means"):
                    raise ValueError("wordless answer must select approve_means")
                fields["option"] = revision.get("approve_means")
            if not nonempty(words) and fields.get("option") is None:
                raise ValueError("answer needs words or option, not resolution alone")
            if fields.get("option") is not None and fields["option"] not in [o["id"] for o in revision.get("options") or []]:
                raise ValueError("answer option must belong to its answered revision")
            if channel == "review" and not nonempty(fields.get("resolution")):
                raise ValueError("Review answer needs its resolution id")
            if channel != "review" and fields.get("resolution") is not None:
                raise ValueError("resolution belongs to a Review answer")
    if missing := REQUIRED[event] - fields.keys():
        raise ValueError(f"{event} needs {', '.join(sorted(missing))}")
    if "channel" in fields and fields["channel"] not in CHANNELS:
        raise ValueError("channel must be chat|dialog|review|message")
    if event in ("ask", "revise"):
        validate_revision(fields)
    for name in {"revise": ("reason",), "acted": ("what",), "withdraw": ("reason",)}.get(event, ()):
        if not nonempty(fields.get(name)):
            raise ValueError(f"{event} needs {name}")
    entry = {**fields, "v": 1, "event": event, "key": key, "at": at}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def record_ask(state, slug, text, clock=None, **fields):
    return write_event(state, slug, "ask", {"asked": text, "asked_at": "now", "channel": "chat", **fields}, clock)


def questions(state, as_of=None):
    rows = []
    for path in ask_files(state):
        lines = [e for e in read_asks(path) if as_of is None or when(e["at"]) <= as_of]
        for key in dict.fromkeys(e["key"] for e in lines if "key" in e):
            q = fold_question([e for e in lines if e.get("key") == key])
            if q:
                rows.append({**q, "task": path.parent.name, "archived": "_archive" in path.relative_to(state).parts})
    return rows


def gate_attempts(fm):
    in_gates, attempt, depth, stage, briefing = False, None, -1, None, False
    for line in fm or []:
        m = KEY.match(line)
        if not m:
            continue
        indent = len(m["indent"]) + (2 if line.lstrip().startswith("- ") else 0)
        key, value = m["key"], m["value"]
        if attempt and (indent < depth or (key == "id" and indent == depth)):
            yield attempt
            attempt = None
        if indent == 0:
            in_gates = key == "gates"
        elif in_gates:
            if key == "stage":
                stage = unquote(value or "")
            elif key == "id" and (value or "").startswith("gate-attempt:"):
                attempt, depth = {"attempt": value, "stage": stage, "room": None, "key": None}, indent
                briefing = False
            elif attempt is not None:
                if key == "briefing":
                    briefing = True
                elif key in ("resolution", "withdrawal"):
                    attempt["closed"] = key
                    briefing = False
                elif key == "id" and briefing:
                    attempt["key"] = unquote(value or "")
                elif key == "room-ref":
                    attempt["room"] = unquote(value or "")
                elif key == "at" and "closed" in attempt:
                    attempt["closed_at"] = unquote(value or "")
    if attempt:
        yield attempt


def gate_rows(state, as_of=None):
    rows, seen = [], set()
    for pattern in ("*.md", "*/index.md", "_archive/*.md", "_archive/*/index.md"):
        for path in sorted(state.glob(pattern)):
            fm, _ = split_task(path.read_text(encoding="utf-8"))
            for attempt in gate_attempts(fm):
                key = attempt["key"]
                if not key or key in seen:
                    continue
                seen.add(key)
                if "closed" in attempt and (as_of is None or not attempt.get("closed_at") or when(attempt["closed_at"]) <= as_of):
                    continue
                run = subprocess.run(["git", "-C", str(state), "log", "--reverse", "--format=%aI", "-S", key],
                                     capture_output=True, text=True, check=True)
                dates = run.stdout.splitlines()
                since = when(dates[0]) if dates else None
                upper = min(as_of or datetime.now(timezone.utc), when(attempt["closed_at"])) if attempt.get("closed_at") else as_of or datetime.now(timezone.utc)
                if since and since > upper:
                    since = None
                if as_of and (since is None or since > as_of):
                    continue
                rows.append({"kind": "gate", "key": key, "attempt": attempt["attempt"], "stage": attempt["stage"],
                             "task": folder(path).name, "question": question(state, path, attempt["room"]),
                             "by": None, "state": "open", "waiting_since": iso(since), "recorded_at": iso(since),
                             "holds": "task", "interruptions": None})
    return rows


def open_rows(state, as_of=None, gates=False):
    now = as_of or datetime.now(timezone.utc)
    rows = [q for q in questions(state, as_of) if q["state"] == "open"]
    if gates:
        rows += gate_rows(state, as_of)
    for row in rows:
        since = row["waiting_since"] or row["recorded_at"]
        row["waiting_min"] = mins(when(since), now) if since else None
        row["waiting_bound"] = "at least" if row["kind"] == "gate" or row["waiting_since"] is None else "exact"
        row["publish_review"] = row["kind"] == "question" and row["interruptions"] >= 3 and not row["review_shown"]
        for private in ("revisions", "showings", "review_shown"):
            row.pop(private, None)
    return rows


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


def option_fields(values):
    options = []
    for value in values or []:
        parts = value.split("=", 2)
        if len(parts) < 2:
            raise ValueError("option needs id=text[=effect]")
        options.append({"id": parts[0], "text": parts[1], **({"effect": parts[2]} if len(parts) == 3 else {})})
    return options


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("state", type=Path)
    ap.add_argument("task", nargs="?")
    ap.add_argument("action", nargs="?")
    ap.add_argument("text", nargs="?", help="question for ask; key for other events")
    for flag in ("json", "all", "open", "gates", "late"):
        ap.add_argument("--" + flag, action="store_true")
    ap.add_argument("--as-of")
    ap.add_argument("--holds", choices=sorted(HOLDS))
    ap.add_argument("--channel", choices=sorted(CHANNELS), default="chat")
    for flag in ("by", "recommend", "grounds", "approve-means", "question", "reason", "words", "resolution", "what", "briefing"):
        ap.add_argument("--" + flag)
    ap.add_argument("--revision", type=int)
    ap.add_argument("--tasks", nargs="*", default=[])
    ap.add_argument("--option", action="append")
    ap.add_argument("--ref", action="append", default=[])
    a = ap.parse_args(argv)
    try:
        if a.open:
            rows = open_rows(a.state, when(a.as_of) if a.as_of else None, a.gates)
            if a.json:
                print(json.dumps(rows, indent=1, ensure_ascii=False))
            else:
                for r in rows:
                    wait = (f"{r['waiting_bound']} {r['waiting_min']} min" if r['waiting_min'] is not None else "unknown")
                    if r["waiting_since"] is None:
                        wait = "unknown; " + wait
                    print(f"{r['key']} | {r['by'] or 'gate'} | {wait} | {r['holds']} | {r['question']}"
                          + (" | publish a Review briefing" if r["publish_review"] else ""))
        elif a.all:
            sweep(a.state)
        elif a.action:
            if a.action == "ask" and not nonempty(a.by):
                original = list(argv if argv is not None else sys.argv[1:])
                if "--channel" not in original:
                    original += ["--channel", "chat"]
                corrected = shlex.join(["python3", str(Path(__file__).resolve()), *original, "--by", "<session>"])
                ap.error("ask needs --by with the FO session name; run: " + corrected)
            fields = {"key": a.text}
            if a.action in ("ask", "revise"):
                fields = {"asked": a.text if a.action == "ask" else a.question, "holds": a.holds,
                          "options": option_fields(a.option), "recommend": a.recommend,
                          "approve_means": a.approve_means, "tasks": a.tasks, "refs": [json.loads(r) for r in a.ref]}
                if a.grounds is not None:
                    fields["grounds"] = a.grounds
                fields.update({"asked_at": None if a.late else "now", "by": a.by, "channel": a.channel}
                              if a.action == "ask" else {"key": a.text, "revision": a.revision, "reason": a.reason})
            elif a.action == "answer":
                if len(a.option or []) > 1:
                    raise ValueError("answer selects at most one option")
                fields.update(words=a.words, option=(a.option or [None])[0], resolution=a.resolution, channel=a.channel)
                if a.revision is not None:
                    fields["revision"] = a.revision
            elif a.action == "reask":
                fields.update(channel=a.channel, briefing=a.briefing)
            elif a.action in ("acted", "withdraw"):
                field = "what" if a.action == "acted" else "reason"
                fields[field] = getattr(a, field)
            entry = write_event(a.state, a.task, a.action, fields)
            print(f"Recorded {a.action} {entry['key']}; commit asks.jsonl to share it.")
            command = f'python3 {Path(__file__).resolve()} {a.state} {a.task}'
            if a.action in ("ask", "revise", "reask"):
                print(f'Next showing: {command} reask {entry["key"]} --channel {a.channel}')
                print(f'Answer: {command} answer {entry["key"]} --channel {a.channel} --words "<Captain words>"')
                print(f'Withdraw: {command} withdraw {entry["key"]} --reason "<reason>"')
            elif a.action == "answer":
                print(f'Acted: {command} acted {entry["key"]} --what "<action taken>"')
        elif a.task:
            t = timeline(a.state, a.task)
            print(json.dumps(t, indent=1, ensure_ascii=False)) if a.json else show(t)
        else:
            ap.error("name a task or pass --all or --open")
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        ap.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
