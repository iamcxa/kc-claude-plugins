feat(kc-dev-flow-2): count symptom rounds across dispatch follow-ups

Repeated diagnosis dispatches on one symptom previously escaped the step-back reminder. Count both plain records and supported follow-up message records per stage and normalized symptom: round two prints the three questions, and round three owes chief-engineer until a qualifying dated call or waiver clears it.

Keep dispatch messages on stderr, preserve the strict-only missing-header hold, and order records numerically by stage round then message number so named checks exclude later follow-ups and the third record dates clearing. Reuse the existing idle and merge paths. ADR 0026 records the Captain ruling; no version or workflow-budget change.

Candidate: 7aad891353a973c7fbda2ad4214a3aadea71d2a6; base: 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb.

Validation: the three-record regression fails before the repair and passes after it; four message-specific mutations and all ten prior controls are rejected. Full package discovery passed: 882 tests, six skips, zero failures. The historical replay, L2 parser probe, per-moment word limits, committed-corpus comparison and structural checks also pass; exact evidence is in the implementation report.

The one local exact-head RoboRev attempt returned incomplete because the daemon is unavailable here. First Officer owns the PR update, hosted checks and independent validation. CI cost per PR was not measured.
