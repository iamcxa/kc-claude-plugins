#!/usr/bin/env python3
"""Independently compare three archived tasks with raw author-date git records."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

code, state = map(Path, sys.argv[1:3])
helper = code / "kc-dev-flow-2/scripts/task_timeline.py"
slugs = ["worth-questions-asked-only-before-the-design-gate", "main-tests-pass-with-worth-check-and-story-test", "denied-command-denies-only-that-command"]
def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
def iso(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")
results = []
for slug in slugs:
    raw = subprocess.check_output(["git", "-C", str(state), "log", "--reverse", "--format=%H %aI %s", "--", slug + ".md", slug, "_archive/" + slug + ".md", "_archive/" + slug], text=True)
    markers = []
    for line in raw.splitlines():
        sha, date, subject = line.split(" ", 2)
        match = re.fullmatch(r"(?:dispatch|advance): " + re.escape(slug) + r" entering (\S+)", subject)
        if match:
            markers.append((stamp(date), match[1], sha))
        if subject.startswith("archive " + slug + " "):
            done = stamp(date)
    expected = {}
    for i, (start, stage, sha) in enumerate(markers):
        end = markers[i + 1][0] if i + 1 < len(markers) else done
        row = expected.setdefault(stage, {"start": iso(start), "end": iso(end), "elapsed_min": 0.0, "source_commits": []})
        row["end"] = iso(end)
        row["elapsed_min"] += round((end-start).total_seconds()/60, 1)
        row["source_commits"].append(sha)
    observed = json.loads(subprocess.check_output([sys.executable, "-B", str(helper), str(state), slug, "--json"], text=True))
    for stage, want in expected.items():
        want["elapsed_min"] = round(want["elapsed_min"], 1)
        row = next(r for r in observed["stages"] if r["stage"] == stage)
        got = {key: row[key] for key in ("start", "end", "elapsed_min")}
        match = got == {k: want[k] for k in got}
        results.append({"task": slug, "stage": stage, "expected_from_git": want, "observed": got, "matched": match})
        assert match, results[-1]
    assert observed["done"] == iso(done)
print(json.dumps({"archived_tasks": len(slugs), "stage_rows": len(results), "all_matched": all(r["matched"] for r in results), "comparisons": results}, indent=2))
