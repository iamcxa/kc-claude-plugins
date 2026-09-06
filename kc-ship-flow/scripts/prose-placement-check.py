#!/usr/bin/env python3
"""Prose-placement contract for `## Ship-flow runtime` (DEV-117).

Splits `kc-ship-flow/scripts/fixtures/runtime-section.2026-09-06.md` (a
verbatim copy of the deprecated docs/ship-flow/README.md section, heading
line dropped) into segments -- blank-line paragraphs, further cut on a
sentence boundary (`.` or `:` followed by whitespace and an uppercase
letter or backtick) -- and checks each segment's hash against
`kc-ship-flow/references/placement.tsv`.

A segment is placed only when its row's destination is either the literal
string `residual` (with a non-empty reason) or an existing file path
relative to the repository root. Exits 0 only when every segment in the
fixture has exactly one row, every row's segment still exists in the
fixture, and every non-residual destination file exists on disk. The
residual list is printed to stdout for the PR body table to reproduce.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "kc-ship-flow" / "scripts" / "fixtures" / "runtime-section.2026-09-06.md"
PLACEMENT = ROOT / "kc-ship-flow" / "references" / "placement.tsv"

SENTENCE_BOUNDARY = re.compile(r"(?<=[.:])\s+(?=[A-Z`])")
WHITESPACE = re.compile(r"\s+")


def die(message: str) -> None:
    print(f"prose-placement-check: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize(text: str) -> str:
    return WHITESPACE.sub(" ", text).strip()


def segment_fixture(body: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    segments: list[str] = []
    for paragraph in paragraphs:
        normalized = normalize(paragraph)
        segments.extend(s for s in SENTENCE_BOUNDARY.split(normalized) if s)
    return segments


def seg_hash(segment: str) -> str:
    return hashlib.sha256(segment.encode("utf-8")).hexdigest()[:12]


def load_placement() -> dict[str, tuple[str, str]]:
    if not PLACEMENT.is_file():
        die(f"missing placement table: {PLACEMENT}")
    rows: dict[str, tuple[str, str]] = {}
    for lineno, raw_line in enumerate(PLACEMENT.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            die(f"placement.tsv:{lineno}: expected 3 tab-separated columns, got {len(parts)}: {raw_line!r}")
        seg, destination, note = parts
        if seg in rows:
            die(f"placement.tsv:{lineno}: duplicate segment hash {seg}")
        rows[seg] = (destination, note)
    return rows


def main() -> int:
    if not FIXTURE.is_file():
        die(f"missing fixture: {FIXTURE}")
    text = FIXTURE.read_text(encoding="utf-8")
    if not text.startswith("## Ship-flow runtime"):
        die("fixture does not start with the expected '## Ship-flow runtime' heading")
    body = text.split("\n", 1)[1]
    segments = segment_fixture(body)
    if not segments:
        die("fixture produced zero segments")

    placement = load_placement()
    fixture_hashes = {seg_hash(s) for s in segments}
    placement_hashes = set(placement)

    missing = fixture_hashes - placement_hashes
    if missing:
        for segment in segments:
            if seg_hash(segment) in missing:
                print(f"prose-placement-check: UNPLACED {seg_hash(segment)}: {segment[:80]!r}", file=sys.stderr)
        die(f"{len(missing)} fixture segment(s) have no placement.tsv row")

    stale = placement_hashes - fixture_hashes
    if stale:
        die(f"{len(stale)} placement.tsv row(s) reference a segment no longer in the fixture: {sorted(stale)}")

    residual_count = 0
    for segment in segments:
        h = seg_hash(segment)
        destination, note = placement[h]
        if destination == "residual":
            if not note.strip():
                die(f"{h}: residual row has no reason")
            residual_count += 1
            print(f"prose-placement-check: RESIDUAL {h}: {note}")
            continue
        target = ROOT / destination
        if not target.is_file():
            die(f"{h}: destination file does not exist: {destination}")
        print(f"prose-placement-check: PLACED {h} -> {destination}")

    print(
        f"prose-placement-check: PASS ({len(segments)} segments, "
        f"{len(segments) - residual_count} placed, {residual_count} residual)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
