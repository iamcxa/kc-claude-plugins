#!/usr/bin/env python3
"""Record, check and audit journey-map footprints beside kc-dev-flow-2 tasks.

A footprint is one JSON line in `<task folder>/footprints.jsonl`: a Captain ruling that answers
one question on the journey map, with his verbatim words, date and source.

  add TASK --question Q --source gate-attempt:ID|amendment:N --words W --answer A [--story S] [--journey J] [--date D]
  check TASK                      exit 1 when a journey task lacks a valid footprint or a not-needed line
  audit WORKFLOW_DIR --since D    count archived journey tasks with no record (exit 2 without --since)
  schema journey-footprint        print the field table, its version and where the history lives

TASK is the task file (active or under `_archive/`). Standard library only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
import decision_ledger as dl  # noqa: E402

SCHEMA = "journey-footprint"
WIRE = "journey-footprint/v1"
FIELDS = (
    ("schema", "the string `journey-footprint/v1` (wire pin: major only)"),
    ("id", "`fp:<task slug>:<n>`"),
    ("kind", "`answered`, the only kind in 1.0.0"),
    ("task", "task slug"),
    ("journey", "the map's `journey:` value"),
    ("story", "a story id on that map"),
    ("question", "a question id inside that story"),
    ("words", "the Captain's words, verbatim; a substring of the source text"),
    ("date", "`YYYY-MM-DD`; equals the source's date"),
    ("source", "`gate-attempt:<id>` (the resolution `reason`) or `amendment:<n>` (its `Captain:` line)"),
    ("answer", "one line, FO's statement of the decision; becomes the map's `answer`"),
)
REQUIRED = tuple(name for name, _ in FIELDS)
VERSIONS = HERE / "contract-versions.json"
ADR_TITLE = "a-captain-ruling-reaches-the-map-as-a-versioned-footprint"
FOOTER = (
    "Current table: python3 kc-dev-flow-2/extensions/journey-map/map_footprint.py schema journey-footprint\n"
    "Every version: kc-dev-flow-2/CHANGELOG.md, written by release-please from each commit.\n"
    f"First shape and each MAJOR: an ADR in the kc-claude-plugins docs/adr/ ({ADR_TITLE}).\n"
    "Read the CHANGELOG when a line carries a schema string you have not seen or a consumer refuses a major; "
    "read the ADR before removing or renaming a field."
)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})[^\n]*\n(?:[^\n]*\n)*?Captain: ([^\n]*)", re.M)
FOOTPRINTS_LINE = re.compile(r"^Map footprints:[ \t]*(.*)$", re.M)


def table_text():
    return "| field | rule |\n|---|---|\n" + "\n".join(f"| `{n}` | {r} |" for n, r in FIELDS)


def table_hash():
    return hashlib.sha256(table_text().encode()).hexdigest()


def version_problem(name):
    if name != SCHEMA:
        return f"unknown schema {name!r}; only {SCHEMA}"
    try:
        entry = json.loads(VERSIONS.read_text())[SCHEMA]
        recorded = entry["versions"].get(entry["current"])
    except (OSError, ValueError, KeyError):
        return f"{SCHEMA}: {VERSIONS.name} is unreadable or lacks the schema"
    if recorded is None:
        return f"{SCHEMA}: current version {entry['current']} has no recorded hash in {VERSIONS.name}"
    if recorded != table_hash():
        return (f"{SCHEMA}: the field table changed but version {entry['current']} did not; "
                f"bump `current` and record the new hash {table_hash()} in {VERSIONS.name}")
    return None


def cmd_schema(args):
    problem = version_problem(args.name)
    if args.name == SCHEMA:
        print(f"{SCHEMA} {json.loads(VERSIONS.read_text())[SCHEMA]['current']}")
        print(table_text())
        print(FOOTER)
    if problem:
        print(problem, file=sys.stderr)
        return 1
    return 0


def top_level(fm):
    out = {}
    for i, line in enumerate(fm):
        m = dl.KEY.match(line)
        if m and not m.group("indent") and not line.startswith("- "):
            out[m.group("key")] = dl.scalar(fm, i, 0)
    return out


class Task:
    def __init__(self, path):
        self.path = Path(path)
        self.slug = self.path.stem
        self.folder = self.path.with_suffix("")
        self.footprints = self.folder / "footprints.jsonl"
        fm, self.body = dl.split_task(self.path.read_text())
        if fm is None:
            raise ValueError(f"{path}: no frontmatter")
        self.fields = top_level(fm)
        self.journey = self.fields.get("journey", "").strip()
        self.story = self.fields.get("journey-story", "").strip()
        self.sources = {}
        for e in dl.gate_entries(fm):
            if e["kind"] == "resolution" and e.get("attempt"):
                self.sources[e["attempt"]] = (e.get("at", "")[:10], e.get("reason") or "")
        for n, date, words in AMENDMENT.findall(self.body):
            self.sources[f"amendment:{n}"] = (date, words)

    @property
    def is_journey(self):
        return bool(self.journey and self.story)

    def lines(self):
        """Yield (line number, parsed object or None, raw) for each non-empty footprint line."""
        if not self.footprints.is_file():
            return
        for n, raw in enumerate(self.footprints.read_text().splitlines(), 1):
            if raw.strip():
                try:
                    obj = json.loads(raw)
                except ValueError:
                    obj = None
                yield n, obj, raw

    def alignment(self):
        m = re.search(r"^## FO alignment[ \t]*\n(.*?)(?=^## |\Z)", self.body, re.M | re.S)
        return m.group(1) if m else ""


def problems(obj, task):
    """Reasons one footprint line is invalid for this task; empty when valid or skipped."""
    if not isinstance(obj, dict):
        return ["not a JSON object"]
    if obj.get("schema") != WIRE:
        return [f"schema {obj.get('schema')!r} is not {WIRE}"]
    if obj.get("kind") != "answered":
        return []
    out = [f"missing or empty {f}" for f in REQUIRED if not isinstance(obj.get(f), str) or not obj[f].strip()]
    if out:
        return out
    if obj["task"] != task.slug:
        out.append(f"task {obj['task']!r} is not {task.slug!r}")
    if task.journey and obj["journey"] != task.journey:
        out.append(f"journey {obj['journey']!r} differs from the task's {task.journey!r}")
    if not re.fullmatch(rf"fp:{re.escape(task.slug)}:\d+", obj["id"]):
        out.append(f"id {obj['id']!r} is not fp:{task.slug}:<n>")
    if "\n" in obj["answer"]:
        out.append("answer is not one line")
    source = task.sources.get(obj["source"])
    if source is None:
        out.append(f"source {obj['source']!r} does not resolve in the task")
    else:
        if obj["words"] not in source[1]:
            out.append("words are not inside the source text")
        if obj["date"] != source[0]:
            out.append(f"date {obj['date']} differs from the source's {source[0]}")
    return out


def valid_lines(task):
    """Return (valid count, [(line number, reason)], skipped count)."""
    valid, bad, skipped, ids = 0, [], 0, set()
    for n, obj, _ in task.lines():
        why = problems(obj, task)
        if not why and obj.get("kind") != "answered":
            skipped += 1
        elif not why and obj["id"] in ids:
            bad.append((n, f"duplicate id {obj['id']}"))
        elif why:
            bad.append((n, "; ".join(why)))
        else:
            ids.add(obj["id"])
            valid += 1
    return valid, bad, skipped


def cmd_add(args):
    task = Task(args.task)
    story = args.story or task.story
    refuse = []
    if not task.journey:
        refuse.append("the task has no `journey`")
    elif args.journey and args.journey != task.journey:
        refuse.append(f"journey {args.journey!r} differs from the task's {task.journey!r}")
    if not story:
        refuse.append("no --story and the task has no `journey-story`")
    source = task.sources.get(args.source)
    if source is None:
        refuse.append(f"source {args.source!r} does not resolve to a resolution or amendment in the task")
    else:
        if not args.words.strip() or args.words not in source[1]:
            refuse.append("words are not inside the source text; quote the Captain verbatim")
        if (args.date or source[0]) != source[0]:
            refuse.append(f"date {args.date} differs from the source's {source[0]}")
    if not args.answer.strip() or "\n" in args.answer:
        refuse.append("answer must be one non-empty line")
    existing = [o for _, o, _ in task.lines() if isinstance(o, dict)]
    if any(o.get("story") == story and o.get("question") == args.question and o.get("source") == args.source
           for o in existing):
        refuse.append("a footprint for this story, question and source already exists")
    if refuse:
        for r in refuse:
            print(f"refused: {r}", file=sys.stderr)
        return 1
    n = 1 + max([int(o["id"].rsplit(":", 1)[-1]) for o in existing
                 if isinstance(o.get("id"), str) and o["id"].rsplit(":", 1)[-1].isdigit()] or [0])
    line = {"schema": WIRE, "id": f"fp:{task.slug}:{n}", "kind": "answered", "task": task.slug,
            "journey": task.journey, "story": story, "question": args.question, "words": args.words,
            "date": source[0], "source": args.source, "answer": args.answer}
    task.folder.mkdir(exist_ok=True)
    with task.footprints.open("a") as out:
        out.write(json.dumps(line, ensure_ascii=False) + "\n")
    print(f"added {line['id']} -> {task.footprints}")
    return 0


def record_state(task):
    """Return (ok, messages) for the task's footprint record, as `check` and `audit` read it."""
    valid, bad, skipped = valid_lines(task)
    msgs = [f"{task.footprints.name}:{n}: invalid: {why}" for n, why in bad]
    m = FOOTPRINTS_LINE.search(task.alignment())
    declared = m.group(1).strip() if m else ""
    if not m:
        msgs.append("`## FO alignment` has no `Map footprints:` line")
    elif declared.startswith("not needed:"):
        if not declared[len("not needed:"):].strip():
            msgs.append("`Map footprints: not needed:` has no reason")
    else:
        c = re.fullmatch(r"(\d+) in footprints\.jsonl", declared)
        if not c:
            msgs.append(f"`Map footprints: {declared}` is neither `<n> in footprints.jsonl` nor `not needed: <reason>`")
        elif int(c.group(1)) != valid or valid < 1:
            msgs.append(f"`Map footprints:` says {c.group(1)} but {valid} valid line(s) are in {task.footprints.name}")
    return (not msgs), msgs, len(bad), skipped


def cmd_check(args):
    task = Task(args.task)
    if not task.is_journey:
        print(f"{task.slug}: not a journey task (needs `journey` and `journey-story`); nothing to check")
        return 0
    ok, msgs, _, skipped = record_state(task)
    for msg in msgs:
        print(f"{task.slug}: {msg}", file=sys.stderr)
    print(f"{task.slug}: {'ok' if ok else 'FAIL'}" + (f" ({skipped} skipped)" if skipped else ""))
    return 0 if ok else 1


def state_dir(workflow):
    readme = workflow / "README.md"
    if readme.is_file():
        fm, _ = dl.split_task(readme.read_text())
        state = top_level(fm or []).get("state")
        if state and (workflow / state).is_dir():
            return workflow / state
    return workflow


def cmd_audit(args):
    if not args.since or not DATE.match(args.since):
        print("audit needs --since YYYY-MM-DD: the date the adopter lists the extension", file=sys.stderr)
        return 2
    archive = state_dir(Path(args.workflow_dir)) / "_archive"
    unrecorded = invalid = 0
    for path in sorted(archive.glob("*.md")):
        if path.name == "README.md":
            continue
        task = Task(path)
        dates = [d for d, _ in task.sources.values()]
        if not task.is_journey or not any(d >= args.since for d in dates):
            continue
        ok, msgs, bad, _ = record_state(task)
        invalid += bad
        if not ok and bad == 0:
            unrecorded += 1
            print(f"unrecorded: {task.slug}: {msgs[0]}")
        for msg in msgs[:bad]:
            print(f"invalid: {task.slug}: {msg}")
    print(f"unrecorded {unrecorded}")
    print(f"invalid {invalid}")
    return 1 if unrecorded or invalid else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("task")
    p.add_argument("--question", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--words", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--story")
    p.add_argument("--journey")
    p.add_argument("--date")
    p.set_defaults(fn=cmd_add)
    p = sub.add_parser("check")
    p.add_argument("task")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("audit")
    p.add_argument("workflow_dir")
    p.add_argument("--since")
    p.set_defaults(fn=cmd_audit)
    p = sub.add_parser("schema")
    p.add_argument("name")
    p.set_defaults(fn=cmd_schema)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
