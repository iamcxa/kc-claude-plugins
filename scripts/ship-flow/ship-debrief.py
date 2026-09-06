#!/usr/bin/env python3
"""Draft the ship-flow ship debrief from a batch's durable records, addressed to ship-flow.
usage: ship-debrief.py <batch-dir>

Reads, all optional except receipt/close-receipt(.DRAFT).json:
  <batch-dir>/receipt/close-receipt.json (or .DRAFT.json)   defects_returned, per-issue minutes
  <batch-dir>/README.md                                      "## Decisions made under `defaults`" bullets

Prints a kc-ship-close-receipt/v1 `ship_debrief` object (JSON) to stdout: one
disposition per defect (an undispositioned one is flagged in place of a fix
ticket or accepted residual, not silently dropped), minutes summed per
station, and each `defaults` decision marked overturned only where the
record's own "Correction" marker says so. It is a draft for the First
Officer to edit -- `candidate_correction` is always a placeholder the writer
cannot fill in from the record. Exit 0 on success, 2 on usage or a missing
close receipt.
"""
import json
import os
import re
import sys


def find_first(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def load_defaults_decisions(batch_dir):
    readme = os.path.join(batch_dir, "README.md")
    if not os.path.isfile(readme):
        return []
    with open(readme, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^## Decisions made under `defaults`.*?$", text, re.MULTILINE)
    if not m:
        return []
    rest = text[m.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    section = rest[:next_heading.start()] if next_heading else rest
    lines = [line[2:].strip() for line in section.splitlines() if line.startswith("- ")]
    return [{"decision": line, "overturned": "correction" in line.lower()} for line in lines]


def build(batch_dir):
    close_path = find_first(
        os.path.join(batch_dir, "receipt", "close-receipt.json"),
        os.path.join(batch_dir, "receipt", "close-receipt.DRAFT.json"),
    )
    if not close_path:
        print(f"ship-debrief: missing {batch_dir}/receipt/close-receipt(.DRAFT).json", file=sys.stderr)
        sys.exit(2)
    with open(close_path, encoding="utf-8") as f:
        close = json.load(f)

    defects_disposition = []
    for d in close.get("defects_returned", []):
        disposition = d.get("fix_ticket") or d.get("accepted_residual") or "undispositioned -- FO to fill in disposition"
        defects_disposition.append({"id": d["id"], "disposition": disposition})

    minutes_per_station = {}
    for entry in close["issues"].values():
        for station, minutes in entry.get("minutes", {}).items():
            minutes_per_station[station] = minutes_per_station.get(station, 0) + minutes

    return {
        "defaults_decisions": load_defaults_decisions(batch_dir),
        "defects_disposition": defects_disposition,
        "minutes_per_station": minutes_per_station,
        "candidate_correction": "TBD (FO): one candidate correction to ship-flow from this batch.",
    }


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    print(json.dumps(build(argv[1]), indent=1, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
