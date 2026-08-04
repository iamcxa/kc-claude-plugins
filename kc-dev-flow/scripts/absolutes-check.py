#!/usr/bin/env python3
"""Require every absolute in a normative document to have been dispositioned once.

The kernel says an absolute either names the enforcement point that makes it true
or is rewritten as the bounded claim the artifact supports. That rule had no
enforcement point of its own, which is the shape it exists to catch. Four
successive read-throughs of one file each found a different subset of undefended
absolutes, so the reproducer is not inattention: absolutes enter a document
faster than anyone re-reads it, and a fifth read-through would have found a fifth
subset.

So this replaces re-reading with a registry. Every block containing an absolute
is judged once and recorded as:

  prohibition  assigns a duty to a named authority; contrary execution violates
               the duty rather than falsifying the sentence
  enforced     a factual claim, with the mechanism that makes it true named
  bounded      rewritten to what the artifact supports, so it is no longer
               absolute in force

An unregistered block fails. A registered block whose text has changed fails,
because its disposition was a judgment about text that no longer exists. A
registry entry matching nothing fails, so the registry cannot rot into a list of
approvals for sentences that were deleted.

Blocks are hashed after whitespace normalisation, so rewrapping a paragraph does
not force a re-judgement while editing its words does.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# Words whose presence makes a sentence a candidate. Deliberately broad: a false
# candidate costs one registry line, a missed one costs what this exists to stop.
ABSOLUTES = re.compile(
    r"\b(exactly|only|always|never|cannot|can't|byte-for-byte|impossible"
    r"|guarantees?|guaranteed|no other|none|every|all)\b",
    re.IGNORECASE,
)
DISPOSITIONS = ("prohibition", "enforced", "bounded")
BULLET = re.compile(r"^(?:[-*] |\d+\. )")


def blocks_of(path: Path) -> list[tuple[int, str]]:
    """Split into bullets and paragraphs, returning (first line number, text)."""
    found: list[tuple[int, str]] = []
    current: list[str] = []
    start = 0
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            if current:
                found.append((start, " ".join(current)))
                current = []
        elif BULLET.match(line):
            if current:
                found.append((start, " ".join(current)))
            current, start = [line.strip()], number
        else:
            if not current:
                start = number
            current.append(line.strip())
    if current:
        found.append((start, " ".join(current)))
    return found


def digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]


def load_registry(path: Path) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    if not path.is_file():
        return entries
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.split("#", 1)[0].strip() if line.lstrip().startswith("#") else line.rstrip()
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            raise SystemExit(f"absolutes-check: {path}:{number} is not <hash>TAB<disposition>TAB<note>")
        key, disposition, note = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if disposition not in DISPOSITIONS:
            raise SystemExit(
                f"absolutes-check: {path}:{number} disposition {disposition!r} "
                f"is not one of {', '.join(DISPOSITIONS)}"
            )
        entries[key] = (disposition, note)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("files", type=Path, nargs="+")
    parser.add_argument("--emit", action="store_true", help="print registry lines for undispositioned blocks")
    args = parser.parse_args()

    registry = load_registry(args.registry)
    seen: set[str] = set()
    missing: list[tuple[Path, int, str, str]] = []

    for path in args.files:
        if not path.is_file():
            print(f"absolutes-check:FAIL:{path} is not a readable file")
            return 1
        for number, text in blocks_of(path):
            if not ABSOLUTES.search(text):
                continue
            key = digest(text)
            if key in registry:
                seen.add(key)
            else:
                missing.append((path, number, key, text))

    stale = sorted(set(registry) - seen)
    if not missing and not stale:
        print(f"absolutes-check:PASS:{len(seen)} dispositioned")
        return 0

    if args.emit:
        for path, number, key, text in missing:
            print(f"{key}\t<disposition>\t{path.name}:{number} {text[:70]}")
        return 1

    for path, number, key, text in missing:
        print(f"absolutes-check:FAIL:{path}:{number} carries an undispositioned absolute")
        print(f"  {text[:150]}")
        print(f"  add to {args.registry}:  {key}<TAB>prohibition|enforced|bounded<TAB>why")
    for key in stale:
        print(f"absolutes-check:FAIL:{args.registry} disposition {key} matches no block; delete it")
    return 1


if __name__ == "__main__":
    sys.exit(main())
