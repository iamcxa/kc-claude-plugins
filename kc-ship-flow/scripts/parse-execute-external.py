#!/usr/bin/env python3
"""Extract `execute.cli[].{run,expect}` pairs from `Execute external` steps.

Consumes e2e-pipeline's flow YAML step shape (`action: "Execute external"`,
`execute: {cli: [{run, expect}]}`) narrowly -- walks the parsed document for
that shape only, with no dependency on e2e-pipeline.

Prints one shell-quoted `<run>\\t<expect>` pair per line, in step order, for
kc-ship-flow/scripts/e2e-cli.sh to consume. `expect` is the empty string when a
`cli` entry omits it; e2e-cli.sh treats anything other than `exit code <N>`
as an unrecognized expect and fails the run, so this parser does not invent
a default.

Exits 2 (not a Python traceback) on: PyYAML unavailable, the file missing or
unreadable, or the file not parsing as YAML. A partial or best-effort parse
that silently produced zero steps would make a real flow indistinguishable
from a broken one -- both must fail loud.
"""
from __future__ import annotations

import shlex
import sys

try:
    import yaml
except ImportError:
    print(
        "parse-execute-external: PyYAML (`import yaml`) is required and is not "
        "installed in this environment -- install it (e.g. `dnf install "
        "python3-pyyaml` or `pip install pyyaml`) rather than falling back to a "
        "regex parser that silently mis-parses valid YAML.",
        file=sys.stderr,
    )
    sys.exit(2)


def extract(document: object) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if not isinstance(document, dict):
        return pairs
    steps = document.get("steps")
    if not isinstance(steps, list):
        return pairs
    for step in steps:
        if not isinstance(step, dict) or step.get("action") != "Execute external":
            continue
        execute = step.get("execute")
        cli = execute.get("cli") if isinstance(execute, dict) else None
        if not isinstance(cli, list):
            continue
        for entry in cli:
            if not isinstance(entry, dict) or entry.get("run") is None:
                continue
            pairs.append((str(entry["run"]), str(entry.get("expect", ""))))
    return pairs


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: parse-execute-external.py <flow.yaml>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as error:
        print(f"parse-execute-external: cannot parse {path}: {error}", file=sys.stderr)
        sys.exit(2)
    for run, expect in extract(document):
        print(f"{shlex.quote(run)}\t{shlex.quote(expect)}")


if __name__ == "__main__":
    main()
