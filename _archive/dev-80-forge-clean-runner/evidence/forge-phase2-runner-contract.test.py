#!/usr/bin/env python3
"""AC-1 contract: forge Phase 2 executes every RED/GREEN run on a clean runner.

Two independent guards over each of the two Phase 2 run-execution spans. Each
failure prints the offending span or line, so the test names its reason.
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
FORGE = ROOT / "kc-plugin-forge"

SPANS = [  # label, file, start heading, end heading, in-session frame?
    ("Phase 2 sequential", FORGE / "skills/kc-plugin-forge/SKILL.md",
     r"^### Sequential mode", r"^## Phase 2\.5"),
    ("Phase 2 parallel teammate", FORGE / "reference/parallel-forge.md",
     r"^## Phase 2: Skill TDD Teammate Template", r"^## Phase 2\.5"),
]

RUNNER = re.compile(r"\brunner\b", re.I)
RUNNER_KINDS = (re.compile(r"\bcloud\b", re.I), re.compile(r"\bbare\b", re.I))
RUN_LINE = re.compile(r"\bRED\b|\bGREEN\b|\bbaseline\b|pressure scenario", re.I)
EXEC_VERB = re.compile(r"\brun\b|\bruns\b|\bdispatch|\bspawn|\bexecut", re.I)
IN_SESSION_WORKER = re.compile(r"subagent|general-purpose|teammate|Agent\(", re.I)
FRAME = re.compile(r"teammate|subagent", re.I)

failures = []
for label, path, start, end in SPANS:
    lines = path.read_text().splitlines()
    i = next(n for n, l in enumerate(lines) if re.match(start, l))
    j = next((n for n, l in enumerate(lines[i+1:], i+1) if re.match(end, l)), len(lines))
    span, body = lines[i:j], "\n".join(lines[i:j])
    where = f"{path.relative_to(ROOT)}:{i+1}-{j}"

    # G1 (positive) — the span selects a runner from {cloud, bare} for its runs.
    if not (RUNNER.search(body) and all(k.search(body) for k in RUNNER_KINDS)):
        failures.append(f"G1 {label} ({where}): span never selects a runner from "
                        f"{{cloud, bare}} for its RED/GREEN runs")

    # G2 (negative) — no run line names an in-session worker as the executor.
    for n, line in enumerate(span, i+1):
        if RUN_LINE.search(line) and EXEC_VERB.search(line) and IN_SESSION_WORKER.search(line):
            failures.append(f"G2 {label} ({path.relative_to(ROOT)}:{n}): run executed "
                            f"in-session -> {line.strip()[:100]}")

    # G3 (frame) — an in-session worker template may not carry the run itself.
    if FRAME.search(span[0]) and any(RUN_LINE.search(l) and EXEC_VERB.search(l) for l in span):
        failures.append(f"G3 {label} ({where}): in-session worker template still "
                        f"carries the RED/GREEN run instruction")

for f in failures:
    print("FAIL:", f)
print(f"{'FAILED' if failures else 'PASSED'}: {len(failures)} violation(s)")
sys.exit(1 if failures else 0)
