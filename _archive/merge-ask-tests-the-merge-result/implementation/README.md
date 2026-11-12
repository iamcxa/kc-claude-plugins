# Implementation evidence

Candidate: d79053d0836c558a9269f9cf1ba222933935b820
Base: 8ce0eb6050c889b21baccf50fec35231bc888d66

Run from a fresh shell, with CODE set to the candidate checkout:

    python3 -B <this-directory>/acceptance_replay.py "$CODE"
    PYTHONDONTWRITEBYTECODE=1 python3 -B <this-directory>/mutation_checks.py "$CODE"

The replay reconstructs the public historical task from its recorded state commit
and serves the saved PR facts under ../poc/pr841-facts/. It creates and removes
its control source under CODE/.context; no model or real merge ask is issued.
The red and green runtime records came from real commands on the historical merge
trees; replay does not rerun those tests. Their commands, head, trunk and trees
are in runtime-red and runtime-green. The head-only run had 224 tests, 220 passed and 4 skipped; the
actual ask's merge tree had 226 tests, 1 failure and 4 skipped. tree-equality.log checks the landed tree.

full-unit-suite.log is 24 scripts, 1345 tests run (1334 passed, 11 skipped), exit 0.
The configured README command additionally prefixes lint-skills.py, run separately
at this candidate, exit 0. Together these are the same 25 local commands as CI;
the other three CI commands were run separately against installed Spacedock
0.27.2 and plugin source revision 4d158a484ec73e184861067f8ed1e20087fdc26a.
This is local macOS evidence, not hosted Linux CI or a real post-release ask.

The mutation runner clears candidate __pycache__ directories before importing,
uses python3 -B and disables bytecode in child processes. Each AC mutation was
caught by the named behavioral test. command-match is an additional control.
initial-delivery-gate-failures.log retains the two repaired test expectations.
number-guards-wrong-state-root.log retains an invocation that mistook this task's
own remote reservation for another task; the final check uses the dispatched
split-root workflow directory and passes. No new ADR number was reserved.

scratch-cleanup.log records zero entries with a direct installed Git binary;
the macOS Git launcher itself writes xcrun_db when TMPDIR is changed. The final
cleanup removes the exact scratch root listed in cleanup.log after evidence commit.
Private repositories inspected: 0. No private repository content is archived here.
