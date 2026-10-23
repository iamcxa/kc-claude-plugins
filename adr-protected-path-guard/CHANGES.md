# Changes to the harness copy (task `adr-protected-path-guard`)

Copied on 2026-10-23 from `_archive/adr-code-pointer-poc/harness/` in the spacedock-state/dev2-poc checkout (committed verbatim first, then changed). Everything below is what differs.

- `harness/scenarios.json`: scenario S15 added (Mira's ruling in her own words that the read-back in `src/report_mailer.js` stays, and the task to record it; `Number guards ... ADR: 0024`). The prompt says nothing of Protects, pointers or the linter.
- `harness/run.py`: `setup_workspace` takes the scenario and builds the control world (no ADR 0024, no pointer comment) for S15 on every arm. Same argv, sandbox and isolation as before.
- `harness/expectations-s15.json`: the S15 pass rule.
- `harness/score_s15.py`: the S15 grader; it runs the candidate `adr_lint.py` (passed as `--linter`, its sha256 stored in the results) on the final mira-app and checks the listing and the pointer by its own regexes.
- `harness/falsifiers-s15.py`: 16 synthetic final workspaces the grader must grade as expected, each with its reason.
- Not changed: `world.py`, `specs.py`, `expected_world.json`, `graders/`, S1..S14, the other expectations and graders.
- Arms: `B1` with `KC_ADR_ROOT` at the candidate commit (results in `results/`); the same `B1` with `KC_ADR_ROOT` at `0701aa8` (the arm without the change; results in `results-base/`, run with `ADRPOC_RESULTS`).
