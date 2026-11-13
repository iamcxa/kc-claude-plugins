feat(kc-dev-flow-2): try Pilot designs on a local probe

Pilot ideation currently carries a blanket write ban, so FO must hand-write probe instructions. The workflow now expects a bounded local probe unless the design explains why not, carries each criterion's proof run and `Not provable now`, and asks FO to hold a third ideation dispatch for the Captain. Pilot reuses the POC proof paragraph by pointer; implementation reads and then deletes the recorded probe branch after committing its candidate.

The duplicate ban and its lint exception are removed. The approved 66-word raise is recorded with the Captain's words and loaded moments; ADR 0084 supersedes only ADR 0005's Pilot write ban. POC derivation, Prod's ban and the design gate are preserved. Budget grammar and per-round timing remain the approved follow-up.

Validation: repository lint, all 47 lint tests, two candidate/base dispatch replays, POC derivation, the native dispatch contract suite, timeline count, ADR lint, number guard and design-surface check passed. The listed falsifiers were exercised with bytecode disabled: the base substituted as candidate, an edit outside ideation, a copied ban, a missing raise step and a 6100-word README each fail. The comment-ratio check exits 0 under its fewer-than-20-code-lines exemption (4 code lines, 1 required ADR pointer).

Evidence deviation: the original AC-3 command exits 1 because `grep -c "repeats"` counts the successful lint line "no unlisted passage repeats it". Its failing output is retained. The task-evidence copy changes only that match to `grep -c "^FAIL:.*repeats"` and passes. The approved Acceptance criteria remain unchanged; validation and the Captain decide whether to amend the evidence clause. Both commands and outputs are recorded in the task's implementation evidence.

AC-8 (a live ideation worker) and AC-9 (post-release implementation cleanup) remain not provable now. This dispatch deleted its own local probe branch after committing the candidate. RoboRev, hosted CI, publication and release checks are delegated to FO and were not run here. CI cost per PR was not measured; no CI trigger changes. No speed or defect-reduction claim.
