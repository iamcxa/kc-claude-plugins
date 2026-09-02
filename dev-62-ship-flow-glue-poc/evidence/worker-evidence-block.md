dict ['rows', 'rowCount', 'truncated']
transcript chars 5409
## Evidence
CANDIDATE_SHA: 0144264343775f4c74f517ccea488a8ef91c44bc
BRANCH: feature/dev-50-align-the-readme-linear-brief-heading-with-what-linear
BASE_SHA: f47fd8ca34f54ada90e6292bcffcdb55a96ea44c
FILES: docs/dev/README.md, scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 .context/without-it-check.py
WITHOUT_IT_REMOVED_VARIANT: git checkout f47fd8ca34f54ada90e6292bcffcdb55a96ea44c -- docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1 ("planning description needs one Goal section")
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: docs/dev/README.md line 268 Development Brief code block now reads `## Goal` (was `## Accepted outcome`); scripts/kc-dev-flow-contract-test.py manual_issue_headings lists `## Goal` in place of `## Accepted outcome`.
AC-2: With `## Goal` dropped from the README code block, `python3 scripts/kc-dev-flow-contract-test.py` fails with `kc-dev-flow contract: manual admission Issue headings are missing or duplicated` (exit 1); with `## Goal` duplicated, same failure/exit 1; restored to the committed candidate, `kc-dev-flow contract: PASS` (exit 0).
AC-3: A body built from the README code block's first ```markdown fence, placeholders filled, passed through `kc-dev-flow/scripts/linear-admission.py`'s `section(description, "Goal")` and Non-goals parsing: GOAL='Example accepted goal text.' NON_GOALS=['Not doing X', 'Not doing Y'] (see WITHOUT_IT_COMMAND retained run, exit 0).
AC-4: README line 283, "`python3 scripts/kc-dev-flow-contract-test.py` checks this shape; the minimal-stack ablation test mutates each boundary and requires rejection for the named reason." — unchanged, already names the pinning test; left untouched per the Non-goals scope boundary.
BLOCKER: none
```
