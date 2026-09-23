#!/usr/bin/env python3
"""Derive a POC workflow README from a five-stage one, or check that they still agree."""
import argparse
import difflib
import sys
from pathlib import Path

STATE = "    - name: ideation"
SECTION = "### `ideation`"


def derive(text):
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line == STATE:
            i += 1
            while i < len(lines) and lines[i].startswith("      "):
                i += 1
            continue
        if line == SECTION:
            i += 1
            while i < len(lines) and not lines[i].startswith(("### ", "## ")):
                i += 1
            continue
        out.append(line)
        i += 1
    result = "\n".join(out)
    if STATE in result or SECTION in result or "\n    - name: ideation\n" in result:
        raise ValueError("ideation remains after derivation")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("derive", help="print the POC README derived from a five-stage README")
    make.add_argument("five_stage")
    check = sub.add_parser("check", help="exit 1 with a diff when the POC README drifted")
    check.add_argument("poc")
    check.add_argument("five_stage")
    args = parser.parse_args(argv)
    expected = derive(Path(args.five_stage).read_text())
    if args.command == "derive":
        sys.stdout.write(expected)
        return 0
    actual = Path(args.poc).read_text()
    if actual == expected:
        print("POC README matches the five-stage README without ideation")
        return 0
    sys.stdout.writelines(difflib.unified_diff(
        expected.splitlines(True), actual.splitlines(True), "derived", args.poc))
    return 1


if __name__ == "__main__":
    sys.exit(main())
