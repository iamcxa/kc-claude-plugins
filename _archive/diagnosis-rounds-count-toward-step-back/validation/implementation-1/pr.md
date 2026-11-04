feat(kc-dev-flow-2): count diagnosis rounds by symptom

Repeated worker dispatches chasing one symptom inside a stage previously escaped the step-back reminder. Read a normalized `Symptom:` dispatch header, ask the three questions from round two, and owe chief-engineer at round three until a qualifying dated call or waiver clears it.

Keep dispatch reminders and missing-header hints on stderr, and hold a missing header only in `--names --strict`. Reuse the committed-state idle and merge paths, preserve the other event counts, and amend ADR 0026. No version or workflow-budget change.

Validation: full package unittest discovery; targeted dispatch and role tests; real idle/merge integration; the historical qnow replay; ten killed mutations; unchanged L2 tests and a real parser probe; per-moment word counts; a 443-check committed corpus comparison; repository skill lint, ADR lint, number guards and comment ratio. See the implementation stage report for exact results and candidate SHA.

CI cost per PR was not measured. Hosted CI and exact-head RoboRev remain FO-owned after publication.
