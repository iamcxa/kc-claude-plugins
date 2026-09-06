#!/usr/bin/env python3
"""Draft the ship-flow ship debrief from a batch's durable records, addressed to ship-flow.
usage: ship-debrief.py <batch-dir>

Reads, all required once the record has an issue or a defect naming them:
  <batch-dir>/receipt/close-receipt.json (or .DRAFT.json)   defects_returned, per-issue minutes
  <batch-dir>/README.md                                      "## Decisions made under `defaults`" bullets

Prints a kc-ship-close-receipt/v1 `ship_debrief` object (JSON) to stdout: one
disposition per defect (an undispositioned one is flagged in place of a fix
ticket or accepted residual, not silently dropped), minutes summed per
station, and each `defaults` decision marked `overturned` under one rule: a
decision is overturned only when a *later* bullet's text contains that
decision's own leading ISO-8601 timestamp together with "retract",
"overturn", or "correction" (case-insensitive). A timestamp shared by more
than one earlier bullet cannot mark any of them -- an ambiguous reference is
left unmarked, never applied to every candidate -- and a bullet's own
timestamp never marks itself. It is a draft for the First Officer to edit --
`candidate_correction` is always a placeholder the writer cannot fill in
from the record.

Exit 0 on success. Exit 2 on: bad argv; a missing close receipt; a missing
README.md; a missing per-issue minutes field (never silently defaulted to
[] or {}); or a close receipt that parses as JSON but is malformed or
missing a field this script reads (json.JSONDecodeError, KeyError,
TypeError). A README present without a `defaults` heading is a real zero
decisions and returns [], not a refusal.
"""
import importlib.util
import json
import os
import re
import sys

TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:]+Z)")
CORRECTION_WORDS_RE = re.compile(r"\b(retract(?:ed)?|overturn(?:ed)?|correction)\b", re.IGNORECASE)


def _load_uat_doc():
    """Reuse uat-doc.py's defaults-decision bullet parser (both `-` and `*`
    bullets, a wrapped continuation line joined to its bullet) rather than
    re-implementing it with the narrower bug this file used to carry."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uat-doc.py")
    spec = importlib.util.spec_from_file_location("kc_ship_flow_uat_doc", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


uat_doc = _load_uat_doc()


def find_first(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def mark_overturned(decisions):
    """Return a same-length list of booleans: decisions[i] is overturned iff
    some later decisions[j] (j > i) contains decisions[i]'s own leading
    timestamp plus a correction word, and that timestamp is not shared by
    any other decision before j (a collision leaves every candidate
    unmarked, never marks all of them)."""
    timestamps = [m.group(1) if (m := TIMESTAMP_RE.match(d)) else None for d in decisions]
    overturned = [False] * len(decisions)
    for later_idx, later in enumerate(decisions):
        if not CORRECTION_WORDS_RE.search(later):
            continue
        for earlier_idx in range(later_idx):
            earlier_ts = timestamps[earlier_idx]
            if not earlier_ts or earlier_ts not in later:
                continue
            collision = sum(1 for t in timestamps[:later_idx] if t == earlier_ts) > 1
            if not collision:
                overturned[earlier_idx] = True
    return overturned


def load_defaults_decisions_or_fail(batch_dir):
    readme = os.path.join(batch_dir, "README.md")
    if not os.path.isfile(readme):
        print(f"ship-debrief: missing {readme}", file=sys.stderr)
        sys.exit(2)
    decisions = uat_doc.load_defaults_decisions(batch_dir)
    return decisions if decisions is not None else []


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
    for issue_id, entry in close["issues"].items():
        if "minutes" not in entry:
            print(f"ship-debrief: {issue_id} missing minutes in {close_path}", file=sys.stderr)
            sys.exit(2)
        for station, minutes in entry["minutes"].items():
            minutes_per_station[station] = minutes_per_station.get(station, 0) + minutes

    decisions = load_defaults_decisions_or_fail(batch_dir)
    overturned = mark_overturned(decisions)
    defaults_decisions = [
        {"decision": decision, "overturned": flag} for decision, flag in zip(decisions, overturned)
    ]

    return {
        "defaults_decisions": defaults_decisions,
        "defects_disposition": defects_disposition,
        "minutes_per_station": minutes_per_station,
        "candidate_correction": "TBD (FO): one candidate correction to ship-flow from this batch.",
    }


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    batch_dir = argv[1]
    try:
        debrief = build(batch_dir)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"ship-debrief: malformed or incomplete batch record in {batch_dir}: {exc!r}", file=sys.stderr)
        return 2
    print(json.dumps(debrief, indent=1, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
