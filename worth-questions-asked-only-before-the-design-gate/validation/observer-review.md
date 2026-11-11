# Independent scoped Observer replay

Candidate: `78905b08d6f38817ccdda5d2e91be478fd75dfc7`. This is the validator independently executing the design-check paragraph of the candidate Observer skill, not a full task-lifecycle Observer run or a model-compliance claim.

The second ideation briefing, independently read from the pinned state, binds `git-root://state/d57ed9b75ba539019052d5352ab982190d8cab24/merge-guard-stops-unasked-merges.md`. The exported task's SHA-256 matches the briefing artifact. The briefing artifact is still in ideation. The event-time README was independently selected with `git log -1 --until=<artifact commit time> <base> -- docs/dev2/README.md`, yielding `04809c3c6146c9f4a8f2f0b916fe84c94bfaa1a3`; its bytes are saved in `observer-readme.md`.

observed | rule: "For seed-field failures or `design needs '### Worth questions'` on historical copies, report current-schema incompatibility." (Replay the design check) | evidence: "merge-guard-stops-unasked-merges.md: design needs '### Worth questions': Captain words served, what breaks without each part, and the premise's cheap test" (candidate CLI exit 1; `observer-evidence.json`).

Verdict: **current-schema incompatibility**, not a historical violation. The event-time README does not require worth answers. Its absence is established by reading that saved README's ideation gate requirements, not by assuming the current template applied in November 6 history. Current workflow text explicitly requires worth answers at ideation (`kc-dev-flow-2/references/sd/workflow.md:192`).

Falsifier executed as the same check and evidence evaluated against the baseline skill's unchanged sentence: "For seed-field failures on historical copies, report current-schema incompatibility." The Worth diagnostic is outside that seed-only exception, so its exit-1 rule yields **violation**. Both checker commands produced the same Worth diagnostic; the changed observer instruction is the necessary part of the compatibility behavior. With an event-time README requiring the form, the next sentence still calls it a historical violation; without the event-time README it still says `can't tell`. Neither branch is waived.

Coverage: exact task and task-folder export, bound artifact hash, native CLI runs at baseline and candidate, event-time README, and both full design-check paragraphs. No observer process on a newly archived live adopter, other lifecycle rules, or general agent instruction-following is claimed. Raw outputs retain all diagnostics; the archive export is outside a Git checkout, and the scope-check skip line is recorded as such.

