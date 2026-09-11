#!/usr/bin/env python3
"""Close a ship-flow cloud-wrapper sprint: message each merged task's worker to debrief, then
write `kc-ship-close-receipt/v2` once every task can be closed.

usage: close.py <sprint> --state-dir <dir> [--dry-run]
       close.py --validate <receipt.json>

Design: `docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`, section "closed".
Reads the same `<state-dir>/*.md` task entities and `<state-dir>/_ship_fence/<sprint>.json`
batch record as `uat-doc.py` (dynamically imported here rather than re-implemented, so the two
scripts never drift on what a task's `pr:` field or the fence file mean). The fence file is the
top-level map `dispatch.sh` actually writes -- `<slug> -> {workspace, session, message_sha256}`,
no `sprint`/`tasks` wrapper -- with `merged_sha` and `debrief` added by this script as further
keys of each slug's own object, and `questions`/`residuals` as batch-level siblings.

A task is *merged* iff its entity's `pr:` frontmatter is exactly `pr-merge:<N>` -- the marker the
design says the ship FO records once the Captain's merge is observed; any other `pr:` shape
(a plain `owner/repo#N`, `#N`, or none) is not yet merged. Debrief status per task comes from the
fence file's `<slug>.debrief.status`: `"pushed"` (worker committed `_debriefs/...` and
pushed -- the receipt records its path), `"failed"` (a second rejected push -- the design's rule
that the ship FO does not write the debrief on a worker's behalf and closes anyway, recording the
failure), or absent/pending (worker hasn't debriefed yet -- blocks closing unless the Captain
recorded `captain_stopped` for that task).

For each merged task without a `pushed` or `failed` debrief yet, one
`conductor message create --session <id> --message "..."` argv is printed (the message text from
the design's "closed" section) -- in `--dry-run` this is the whole effect; a live run would also
invoke it (not done here: no Conductor call is made by this script either way, matching the POC's
"the code is rewritten after" scope -- printing the exact argv is the station's contract, the
Captain or a wrapper around this script is the one that executes it).

Exit 0 printing the messages (and, outside `--dry-run`, the receipt path once written).
Exit 3 printing `not all tasks merged` when a non-`--dry-run` run finds a task that is neither
merged nor recorded `captain_stopped`. Exit 2 on a usage error, no task found for the sprint, or a
fence file that parses as JSON but is malformed (json.JSONDecodeError, KeyError, TypeError).

`--validate <receipt.json>` exits 0 when every task entry in the receipt carries a non-empty
`debrief` field (a path or a `failure: ...` string); exits 1 naming the task(s) missing it, or on
a receipt that is not valid JSON, or whose `schema` is not `kc-ship-close-receipt/v2`.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shlex
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "schemas" / "kc-ship-close-receipt.v2.schema.json"
MERGED_RE = re.compile(r"^pr-merge:(\d+)$")


def _load_uat_doc():
    spec = importlib.util.spec_from_file_location("uat_doc", HERE / "uat-doc.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


uat_doc = _load_uat_doc()


def is_merged(task):
    return bool(task.get("pr")) and MERGED_RE.match(task["pr"]) is not None


def merged_pr_number(task):
    m = MERGED_RE.match(task["pr"] or "")
    return m.group(1) if m else None


def debrief_status(record, slug):
    return (record.get(slug, {}) or {}).get("debrief", {}) or {}


def build_debrief_field(record, slug, captain_stopped):
    status = debrief_status(record, slug)
    state = status.get("status")
    if state == "pushed":
        return status.get("path") or "failure: pushed but no path recorded"
    if state == "failed":
        return f"failure: {status.get('reason', 'push rejected twice')}"
    if slug in captain_stopped:
        return "failure: captain_stopped"
    return "failure: not recorded"


def debrief_message(task, record, slug):
    pr_number = merged_pr_number(task)
    merged_sha = (record.get(slug, {}) or {}).get("merged_sha", "")
    return (
        f"Your PR #{pr_number} merged at {merged_sha}. Run `spacedock debrief` for your "
        "session, commit it path-scoped under `_debriefs/` on the state branch, and push."
    )


def print_debrief_messages(tasks, record):
    for slug in sorted(tasks):
        task = tasks[slug]
        if not is_merged(task):
            continue
        status = debrief_status(record, slug).get("status")
        if status in ("pushed", "failed"):
            continue
        session_id = (record.get(slug, {}) or {}).get("session", "")
        message = debrief_message(task, record, slug)
        argv = ["conductor", "message", "create", "--session", str(session_id), "--message", message]
        print(shlex.join(argv))


def build_receipt(sprint, tasks, record):
    captain_stopped = set(record.get("captain_stopped", []))
    per_task = {}
    for slug in sorted(tasks):
        task = tasks[slug]
        fence = record.get(slug, {}) or {}
        per_task[slug] = {
            "slug": slug,
            "workspace_id": fence.get("workspace"),
            "session_id": fence.get("session"),
            "pr": task.get("pr"),
            "merged_sha": fence.get("merged_sha"),
            "debrief": build_debrief_field(record, slug, captain_stopped),
        }
    body = {
        "schema": "kc-ship-close-receipt/v2",
        "sprint": sprint,
        "tasks": per_task,
        "e2e": record.get("e2e", {"result": "not recorded"}),
        "questions": record.get("questions", []),
        "residuals": record.get("residuals", []),
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    body["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def run_close(sprint, state_dir, dry_run):
    tasks = uat_doc.load_task_entities(state_dir, sprint)
    if not tasks:
        print(f"close: no docs/dev entities found for sprint {sprint!r} under {state_dir}", file=sys.stderr)
        return 2
    record = uat_doc.load_batch_record(state_dir, sprint)

    print_debrief_messages(tasks, record)

    if dry_run:
        return 0

    captain_stopped = set(record.get("captain_stopped", []))
    unmerged = sorted(
        slug for slug, task in tasks.items()
        if not is_merged(task) and slug not in captain_stopped
    )
    if unmerged:
        print("not all tasks merged", file=sys.stderr)
        return 3

    pending_debrief = sorted(
        slug for slug, task in tasks.items()
        if is_merged(task)
        and slug not in captain_stopped
        and debrief_status(record, slug).get("status") not in ("pushed", "failed")
    )
    if pending_debrief:
        print(
            f"close: not closing yet; debrief pending for: {', '.join(pending_debrief)}",
        )
        return 0

    receipt = build_receipt(sprint, tasks, record)
    out_dir = Path(state_dir) / "_ship_fence"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"close-receipt-{sprint}.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"close: wrote {out_path}")
    return 0


def validate_receipt(path):
    """Plain-Python name-the-field checks run first (a missing debrief names its slug rather than
    reporting a generic JSON Schema path), then `kc-ship-close-receipt.v2.schema.json` -- the
    schema is the second gate, never a replacement for the first: it catches shape drift
    (an extra property, a wrong type) the hand-rolled checks above do not look for."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"close: cannot read receipt {path}: {exc}", file=sys.stderr)
        return 1

    if data.get("schema") != "kc-ship-close-receipt/v2":
        print(f"close: {path} is not a kc-ship-close-receipt/v2 receipt", file=sys.stderr)
        return 1

    tasks = data.get("tasks") or {}
    if not tasks:
        print(f"close: {path} has no tasks", file=sys.stderr)
        return 1

    missing = sorted(slug for slug, task in tasks.items() if not task.get("debrief"))
    if missing:
        print(f"close: missing debrief field for: {', '.join(missing)}", file=sys.stderr)
        return 1

    if jsonschema is None:
        print("close: jsonschema required", file=sys.stderr)
        return 2
    try:
        with SCHEMA_PATH.open(encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as exc:
        loc = "/".join(str(p) for p in exc.absolute_path) or "(root)"
        print(f"close: {path} violates {SCHEMA_PATH.name} at {loc}: {exc.message}", file=sys.stderr)
        return 1
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--validate":
        if len(argv) != 3:
            print(__doc__, file=sys.stderr)
            return 2
        return validate_receipt(argv[2])

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("sprint")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    try:
        return run_close(args.sprint, args.state_dir, args.dry_run)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"close: malformed batch record for sprint {args.sprint}: {exc!r}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
