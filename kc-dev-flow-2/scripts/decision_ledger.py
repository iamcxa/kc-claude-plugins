#!/usr/bin/env python3
"""Derive the gate decision ledger from a kc-dev-flow-2 state checkout.

Reads every task file (active and `_archive/`), never writes. One JSON line per gate
resolution or withdrawal; `--summary` prints counts per area instead.
"""
import argparse
import json
import re
import sys
from pathlib import Path

OVERRIDE = re.compile(
    r"Override:\s*recommended\s+(?P<rec>.+?);\s*Captain chose\s+(?P<chose>.+?);\s*area:\s*(?P<area>[^;.\n']+)")
SURFACES = re.compile(r"^Surfaces:\s*(.+)$", re.M)
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)
KEY = re.compile(r"^(?P<indent> *)(?:- )?(?P<key>[a-z-]+):(?: (?P<value>.*))?$")


def unquote(raw):
    raw = raw.strip()
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1].replace("''", "'")
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return json.loads(raw)
    return raw


def split_task(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    return text[4:end].split("\n"), text[end + 5:]


def scalar(lines, i, indent):
    """Value of the key on line i; YAML folds continuation lines into one space."""
    parts = [KEY.match(lines[i]).group("value") or ""]
    j = i + 1
    while j < len(lines) and lines[j].strip() and len(lines[j]) - len(lines[j].lstrip(" ")) > indent:
        parts.append(lines[j].strip())
        j += 1
    return unquote(" ".join(p for p in parts if p))


def gate_entries(fm):
    """Walk the SD-written `gates:` block; yield one dict per resolution or withdrawal."""
    stage = attempt = room = None
    entry = None
    entry_indent = conn_indent = -1
    in_gates = False
    for i, line in enumerate(fm):
        m = KEY.match(line)
        if not m:
            continue
        indent = len(m.group("indent")) + (2 if line.lstrip().startswith("- ") else 0)
        key, value = m.group("key"), m.group("value")
        if indent == 0:
            in_gates = key == "gates"
            continue
        if not in_gates:
            continue
        if entry is not None and indent <= entry_indent:
            yield entry
            entry = None
        if key == "stage":
            stage = value
        elif key == "id" and (value or "").startswith("gate-attempt:"):
            attempt, room = value, None
        elif key == "room-ref":
            room = value
        elif key in ("resolution", "withdrawal") and value is None:
            entry = {"stage": stage, "attempt": attempt, "kind": key, "room": room}
            entry_indent = indent
        elif entry is not None:
            if key == "conn":
                conn_indent = indent
            elif conn_indent >= 0 and indent > conn_indent and key in ("quote", "source"):
                entry["conn_" + key] = scalar(fm, i, indent)
            elif key in ("by", "at", "decision", "reason"):
                conn_indent = -1
                entry[key] = scalar(fm, i, indent)
    if entry is not None:
        yield entry


def question(state, task_path, room):
    if not room:
        return None
    index = (task_path.parent / room / "index.json")
    try:
        return json.loads(index.read_text())["question"]
    except (OSError, ValueError, KeyError):
        return None


def task_rows(state, path):
    fm, body = split_task(path.read_text())
    if fm is None:
        return []
    surfaces = SURFACES.search(body)
    amendments = [(int(n), d) for n, d in AMENDMENT.findall(body)]
    rows = []
    for e in gate_entries(fm):
        reason = e.get("reason") or ""
        over = OVERRIDE.search(reason)
        date = (e.get("at") or "")[:10]
        rows.append({
            "task": path.stem,
            "archived": path.parent.name == "_archive",
            "stage": e["stage"],
            "attempt": e["attempt"],
            "kind": e["kind"],
            "by": e.get("by"),
            "at": e.get("at"),
            "decision": e.get("decision") if e["kind"] == "resolution" else "withdraw",
            "reason": reason,
            "conn_quote": e.get("conn_quote"),
            "conn_source": e.get("conn_source"),
            "question": question(state, path, e.get("room")),
            "override": over.groupdict() if over else None,
            "area": over.group("area").strip() if over else (surfaces.group(1).strip() if surfaces else None),
            "amended_after": sum(1 for _, d in amendments if date and d >= date),
        })
    return rows


def ledger(state):
    paths = sorted(state.glob("*.md")) + sorted((state / "_archive").glob("*.md"))
    rows = []
    for p in paths:
        if p.name != "README.md":
            rows.extend(task_rows(state, p))
    return rows


def summary(rows):
    out = {}
    for r in rows:
        if r["kind"] != "resolution":
            continue
        s = out.setdefault(r["area"] or "unknown", {
            "rulings": 0, "captain": 0, "fo_delegated": 0, "overrides": 0, "amended_after": 0})
        s["rulings"] += 1
        s["captain"] += r["by"] == "person:captain"
        s["fo_delegated"] += r["by"] == "agent:first-officer"
        s["overrides"] += r["override"] is not None
        s["amended_after"] += r["amended_after"] > 0
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("state", type=Path, help="state checkout holding the task files")
    ap.add_argument("--summary", action="store_true", help="counts per area instead of rows")
    args = ap.parse_args(argv)
    if not args.state.is_dir():
        print(f"not a directory: {args.state}", file=sys.stderr)
        return 2
    rows = ledger(args.state)
    if args.summary:
        print(json.dumps(summary(rows), ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
