# Changes to the harness copy (task `adr-hidden-reason-poc`)

Copied on 2026-10-23 from the archived dev2 task `adr-silent-undo-poc` (`harness/`). Everything below is what differs. Scenarios S1 to S13 are untouched and are not run by this task.

- `harness/world.py`: `mira-app` gains `src/store.js`, `src/mail.js`, `src/report_render.js` and `src/report_mailer.js` (the S14 code site) and accepted ADR `docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md`. `build(dest, control=True)` builds the same repositories without ADR 0024 (arm C). `mira-decisions` is unchanged.
- `harness/expected_world.json`: `A0` moved (521c2176... to 6b77e60e...) and `A0_control` added (371e689a...).
- `harness/run.py`: arm `C` (control world, no plugin) added; nothing else changed.
- `harness/scenarios.json`: scenario S14 added with S13's footer (the shared footer says "Do not implement the feature itself", which would stop a refactor).
- `harness/expectations-s14.json`, `harness/graders/mailer_probe.mjs`, `harness/graders/recording_store.js`, `harness/graders/recording_mail.js`, `harness/score.py --rule s14`, `harness/falsifiers-s14.py`: the pass rule, its grader and its falsifiers, committed before the first S14 run. The S13 rule, probe and falsifiers are left as copied.
- Not used here and left as copied: `falsifiers.py`, `compare.py`, `expectations-v3.json`, `falsifiers-output.txt`, `falsifiers-s13.py`, `falsifiers-s13-output.txt`. `compare.py` and `falsifiers.py` read `_archive/kc-decision-log-cli/results`, which does not exist in this state checkout.
- Needs `node` (v24.18.0 used) for `score.py --rule s14`: the grader runs the refactored functions against a recording `store.js` and `mail.js`.
