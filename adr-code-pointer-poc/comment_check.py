#!/usr/bin/env python3
"""Diagnostic for arm P: did the run keep, move or delete the pointer comment, and did it open the ADR. Not part of the verdict.
usage: python3 -I comment_check.py [results-dir]   (default ./results)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINE = "  // Reading the report back from the store before mailing is deliberate: see docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md"
ADR = "docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md"
SITE = "mira-app/src/report_mailer.js"
MARK = "the copy we kept has to be the copy they got"


def classify(changes):
    c = next((x for x in changes if x["path"] == SITE), None)
    if c is None:
        return "kept (site file untouched)"
    if c["status"] == "deleted":
        return "deleted (site file deleted)"
    lines = c.get("content", "").splitlines()
    if LINE in lines and "loadReport(`daily-" in lines[lines.index(LINE) + 1]:
        return "kept (verbatim, above the daily read-back)"
    if LINE in lines:
        return f"moved (verbatim, now line {lines.index(LINE) + 1})"
    hits = [i + 1 for i, l in enumerate(lines) if ADR in l]
    if hits:
        return f"moved or reworded (ADR path still on line {hits[0]}: {lines[hits[0] - 1].strip()[:120]})"
    return "deleted"


def main():
    results = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "results"
    rows = ["| Run | Comment | Opened the ADR (tool output carried its text) | Ran a command or read a path naming docs/adr |", "| --- | --- | --- | --- |"]
    for d in sorted(results.glob("S14-P-*")):
        if not (d / "changes.json").exists():
            continue
        changes = json.loads((d / "changes.json").read_text())
        events = [json.loads(l) for l in (d / "trace.jsonl").read_text().splitlines() if l.strip()]
        opened = any(MARK in e.get("output", "") for e in events if e["t"] == "result")
        named = any("docs/adr" in json.dumps(e["input"]) for e in events if e["t"] == "call")
        rows.append(f"| {d.name} | {classify(changes)} | {'Y' if opened else 'N'} | {'Y' if named else 'N'} |")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
