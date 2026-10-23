# Changes to the harness copy (task `adr-silent-undo-poc`)

Copied on 2026-10-23 from the archived dev2 task `read-adr-reporting-rule-followup` (`harness/`, including its README, which still describes S1 to S12). Everything below is what differs. Scenarios S1 to S12 are untouched and are not run by this task.

- `harness/world.py`: `mira-app` gains `src/db.js` and `src/report_queries.js` (the S13 code site). `mira-decisions` is unchanged, so D0, D1 and every digest in `harness/expected_world.json` are identical; only the `A0` commit id moved (dda0e111... to 521c2176...), updated in that file.
- `harness/scenarios.json`: scenario S13 added; it carries its own `footer` (the shared footer says "Do not implement the feature itself", which would stop a refactor). `harness/run.py` uses `sc.get("footer", data["footer"])`; nothing else changed.
- `harness/expectations-s13.json`, `harness/graders/`, `harness/score.py --rule s13`, `harness/falsifiers-s13.py`: the pass rule, its grader and its falsifiers, committed before the first S13 run.
- Not used here and left as copied: `falsifiers.py`, `compare.py`, `expectations-v3.json`, `falsifiers-output.txt`. `compare.py` and `falsifiers.py` read `_archive/kc-decision-log-cli/results`, which does not exist in this state checkout, so they do not run.
- Needs `node` (v24.18.0 used) for `score.py --rule s13`: the grader runs the refactored functions against a recording `db.js`.
