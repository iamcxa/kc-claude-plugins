# Changes to the harness copy (task `adr-code-pointer-poc`)

Copied on 2026-10-23 from the archived `_archive/adr-hidden-reason-poc/harness/` (committed verbatim first, then changed). Everything below is what differs; `world-diff.txt` shows the world difference between arm A0 and arm P.

- `harness/world.py`: `POINTER_LINE` and `REPORT_MAILER_JS_POINTER` (the archived mailer with one comment line inserted after its header comment); `build(..., pointer=False)` writes it when `pointer=True`. Nothing else in the world changes.
- `harness/expected_world.json`: `A0_pointer` added (077fd76b...), the world commit id of arm P.
- `harness/run.py`: arm `P` added to `ARMS`; `setup_workspace` passes `pointer=(arm == "P")`. Same prompt, same sandbox, same argv as arm A0.
- `harness/score.py`: `"P"` added to `S14_ARMS` so the table sorts it. The pass rule, probe and diagnostics are unchanged.
- Not changed: `scenarios.json` (S14 task text), `expectations-s14.json`, `graders/`, `falsifiers-s14.py`.
- `comment_check.py` (task folder, outside the harness) reports whether the run kept, moved or deleted the comment; it is a diagnostic, not part of the verdict.
- Needs `node` for `score.py --rule s14`.
