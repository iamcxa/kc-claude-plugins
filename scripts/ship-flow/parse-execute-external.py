#!/usr/bin/env python3
"""Extract `execute.cli[].{run,expect}` pairs from `Execute external` steps.

Consumes e2e-pipeline's flow YAML step shape (`action: "Execute external"`,
`execute: {cli: [{run, expect}]}`) narrowly, with a line-oriented parser
scoped to that shape only -- no general YAML parsing and no dependency on
e2e-pipeline or a third-party YAML library.

Prints one shell-quoted `<run>\\t<expect>` pair per line, in step order, for
scripts/ship-flow/e2e-cli.sh to consume.
"""
from __future__ import annotations

import re
import shlex
import sys

STEP_RE = re.compile(r"^  - id: ")
ACTION_RE = re.compile(r'^    action:\s*"?([^"\n]+?)"?\s*$')
CLI_LIST_RE = re.compile(r"^      cli:\s*$")
RUN_RE = re.compile(r'^        - run:\s*"(.*)"\s*$')
EXPECT_RE = re.compile(r'^          expect:\s*"(.*)"\s*$')
DEDENT_RE = re.compile(r"^  \S")


def parse(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    action: str | None = None
    in_cli = False
    for line in text.splitlines():
        if STEP_RE.match(line):
            action = None
            in_cli = False
            continue
        if DEDENT_RE.match(line):
            in_cli = False
            continue
        match = ACTION_RE.match(line)
        if match:
            action = match.group(1)
            continue
        if CLI_LIST_RE.match(line):
            in_cli = action == "Execute external"
            continue
        if not in_cli:
            continue
        match = RUN_RE.match(line)
        if match:
            pairs.append((match.group(1), "exit code 0"))
            continue
        match = EXPECT_RE.match(line)
        if match and pairs:
            run, _ = pairs[-1]
            pairs[-1] = (run, match.group(1))
    return pairs


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: parse-execute-external.py <flow.yaml>")
    text = open(sys.argv[1], encoding="utf-8").read()
    for run, expect in parse(text):
        print(f"{shlex.quote(run)}\t{shlex.quote(expect)}")


if __name__ == "__main__":
    main()
