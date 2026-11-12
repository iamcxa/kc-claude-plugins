feat(kc-dev-flow-2): report task stage times and recorded interruptions

FO currently reconstructs stage times by hand and cannot recover questions asked outside gates. Add `task_timeline.py` to read author-dated state records, separate before-gate time, Captain wait and after-gate time, and report dispatch counts and missing starts. Its `ask` command appends a UTC-stamped question to the task's `asks.jsonl` and attributes it to the stage running then; an absent file remains unknown.

The workflow adds the approved 25-word recording instruction and ADR 0080 records the four approved decisions. The existing package CI path filters are retained, with one new test step.

Validation at `188ba44f427a15bfff69d9d4e24b2446af0b69dc` (2026-11-12):
- 145 tests passed across the helper, lint, ledger and role-counter suites; 10 reverse mutations caught, with Python bytecode disabled and mutation caches removed.
- All 159 public archived tasks read successfully; 136 timed, all 23 untimed tasks lack a start stamp and dispatch folder. All 62 comparable dispatch counts match the existing budget counter; finished-task boundaries match the hand log.
- Repository skill lint passes at 6033/6033 words; ADR lint (`--require 0080`), number guards, design surfaces, comment ratio and diff checks pass.

Evidence is committed under `each-task-records-stage-time-revises-and-interruptions/implementation/` on the public state branch; only this repository's corpus was used. Hosted CI and RoboRev have not run and remain FO-owned. CI cost per PR was not measured. Three post-release hand-timed tasks, a real Codex First Officer and complete outside-gate ask capture remain unverified; fixture tests do not settle those observations.

Repair after validation: sum post-gate time separately for every dispatch interval of a repeated stage. The new CLI regression failed on the prior head; the validator probe now passes, and its real archived case recovers 23.2 minutes (7.1 to 30.3 post-gate minutes). Only task_timeline.py and its test change in the repair commit. The repair head has not been pushed; previous hosted CI evidence applies only to a3266ec91.
