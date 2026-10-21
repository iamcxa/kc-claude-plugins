# Changes after the first scenario run

## 2026-10-21 — world rebuilt (Captain's Amendment 2, 「可以」)

Reason: the first 20 runs (arm A0, no help, small world of 4 ADRs per repository) scored consulted 10/10, handoff 6/6, placement 14/20, so arms could not be told apart on two measures. Kept as `results-small-world/`; not in the main table.

Changed before any further run: world.py (23 ADRs per repository, two-step supersession chain 0002 -> 0014 -> 0023, near-duplicate titles; ADR numbers move: decisions 0001->0007, 0003->0009, app 0001->0008, 0002->0011), expectations.json (governing ADR numbers; S6 governing is now 0023 only), scenarios.json (handoff footer no longer says to confirm), score.py (a reported digest must appear in a tool output), task files (the line "Confirm it before relying on it" removed). Scenario prompts S1 to S10 and the skill and hook templates are unchanged. Arm A3 on Codex is dropped (Amendment 2).

Smoke runs (scenario ids SMOKE and SMOKE2) are in probes/ and are not part of the count of scenario runs; the ledger counts every scenario run.

## 2026-10-21 — grader accepts the ruling in force for S9 (after the 20 redo-A0 runs, before any A1 to A3 run)

Reason: the handoff prompt asks for "the ruling you relied on". In S9-A0-codex-r1 the agent followed the supersession chain and reported ADR 0023 with its own true digest, `digest_matches_cited` false and `in_force` true; the grader scored it as a miss against the cited record 0002. That reading is licensed by the prompt wording, so score.py now also accepts it for S9 (`handoff.alt` in expectations.json). The prompt was not changed, which would have cost 6 more runs of the 96 cap. Effect on A0: S9 codex moves from N to Y.
