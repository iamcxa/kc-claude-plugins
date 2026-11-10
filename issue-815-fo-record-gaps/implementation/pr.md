fix(kc-dev-flow-2): close four FO record gaps

Captain gate reasons could pass without quoting the bound question, built-screen reports accepted one screenshot, folder-form dispatch coverage errored, and Captain steps could be stored outside the documented location. This binds the reason preflight to the single open attempt, accepts and checks each screenshot in a block sequence, resolves coverage folders, and enforces numbered Captain steps records. ADR 0073 records the approved pre-record hold and the two-word README budget increase.

Refs #815; addresses items 1, 4, 5 and 6. Items 2 and 3 remain separate tasks, so this does not close the issue.

Validation:
- All 28 repository CI commands exited 0 locally, with 11 conditional fixture skips; final design suite: 220 tests, four conditional skips. Native Spacedock CLI 0.27.2 checks used installed plugin root 0.27.3; exact CI plugin-root 0.27.2 parity remains for hosted CI.
- Ten reverse mutations were caught; fresh-shell acceptance passed.
- Real committed relay records: 11 of 12 Captain resolutions refused; this workflow since 2026-11-06: 8 of 63. The archived 14-picture report fails at base and passes at the candidate; archived folder coverage changes exit 2 to exit 0.
- Repository lint: README 5933/5933 words; ADR 0073 lint and number guards passed; added comment ratio 0.4%, below 5%.

roborev not run: FO runs RoboRev after this local handoff; the worker sandbox cannot reach the local daemon.
CI cost per PR not measured. No workflow or trigger change. Product branch push, Draft PR creation, hosted CI and review are FO-owned; no version bump.
