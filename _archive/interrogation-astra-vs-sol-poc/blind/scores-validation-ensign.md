# Blind scores (validation ensign), single list Z per task

Scored before opening report.md or the closed POC's scores.md. Rule: closed POC `blind/answer-keys.md` "Scoring rule" (hit = answering forces the key decision or gap to be stated; partial = same artifact, neighbouring decision, lenient column only; one question counts toward one key item; several questions may bear on one key, which then counts once). Tier 1 strict is split as the key splits it: askable `A` and late `L`.

## Per task

| Task | Qs | Tier 1 A strict | Tier 1 L strict | Tier 2 strict | Tier 1 A partial (lenient) | Tier 2 partial | Ungrounded |
|---|---|---|---|---|---|---|---|
| number-guards-readme-shrink | 10 | 0 of 2 | - | - | 1 (NG1) | - | 0 |
| fo-write-checks | 19 | 1 of 2 (FW1) | - | 0 of 5 A | 1 (FW2) | 2 (FW5, FW7) | 0 |
| chat-only-evidence-observer-blind | 18 | 2 of 4 (CO1, CO2) | - | 0 of 1 A | 1 (CO3) | 1 (CO5) | 0 |
| delivery-gate-settles-skipped-checks | 18 | 2 of 2 (DG1, DG2) | - | 0 of 0 A | 0 | - | 0 |
| special-role-calls-fire-when-needed | 20 | 1 of 3 (SR3) | 0 of 4 | 1 of 1 A (SR8) | 2 (SR1, SR2) | - | 0 |
| Total | 85 | 6 of 13 | 0 of 4 | 1 of 7 A | 5 | 3 | 0 |

L-item tier 2 (FW8, FW9, CO6, DG3, DG4): 0 hit. Partial on an L item: SR6 (Q11), lenient only.
Tier 1 strict, all items (A and L): 6 of 17. Tier 1 A strict plus partial: 11 of 13.
Grounded non-hit questions per strict hit, all tiers (the closed POC's metric): (85 - 7) / 7 = 11.1, none ungrounded.

## Hits (quote: question number and Q line)

- FW1: fo-write-checks Q7 "How must a decline reason be associated with its particular finding when a gate summary contains several findings and shared explanatory prose?"
- CO1: chat-only Q1 "Which of the seven cited checks must gain durable evidence, and which should remain chat-only?"
- CO2: chat-only Q10 "What must a recorded goal-sufficiency and minimal-necessity confirmation contain for the observer to assess compliance without judging product or design quality?"
- DG1: delivery-gate Q3 "Should a required check concluding SKIPPED or NEUTRAL be accepted when GitHub considers that requirement satisfied?" (Q7, the floor, and Q9, the adopter-declared list, bear on the same key and add nothing to the count)
- DG2: delivery-gate Q17 "What release acceptance evidence must demonstrate that the three reported cases proceed without overrides while an unexpectedly skipped required test still holds?" (Q15, no skip name in the saved record, bears on the same key)
- SR3: special-role Q2 "What evidence should establish that a design reverses an earlier Captain ruling when neither `Supersedes:` nor `Design:` names the replacement?"
- SR8 (tier 2): special-role Q10 "When stage reports, feedback-cycle entries and external-review verdicts describe the same work, what constitutes one consultation-triggering round?"

## Partials (lenient only)

- NG1: number-guards Q3 "May this task change failure messages to make more prose removable, or must eligibility be judged solely against the current messages?" (bounds what is cuttable, does not ask whether to build the task or fold it into fo-write-checks)
- FW2: fo-write-checks Q10 "What evidence must bind a passing `adr_lint --require` result to the exact delivery candidate and the complete set of required decision-record numbers?" (forces landing at the candidate, not the parked-form choice)
- FW5 (tier 2): Q9 "Which later dispatches must repeat reserved `ADR: NNNN` lines..." (which dispatches, not how the line is recognised)
- FW7 (tier 2): Q15 "Does the Captain's repository-only authorization cover strengthening shared checkers for existing adopters, or only enabling automatic invocation in this repository?" (rollout scope, not the re-pin gap)
- CO3: chat-only Q9 "Must durable acceptance evidence retain every command and output in full, or may it omit or redact sensitive material?" (presumes durable; does not ask chat-only versus a saved file)
- CO5 (tier 2): chat-only Q8 "If the observer consumes saved merge-check records, does the previously accepted risk of mixing revisions ... remain acceptable?" (same ask records, not the `time` rule)
- SR1: special-role Q3 "What distinguishes repeated findings that require consultation from unrelated findings that happen to concern the same file?"
- SR2: special-role Q8 "What new evidence should require another chief-engineer consultation after an earlier call has been satisfied?" (no question asks the threshold of three versus four)
- SR6 (L): special-role Q11 "Should an unrecognized or missing event format mean no consultation is needed, or that the need cannot be determined?"

## Misses, tier 1

NG2 (owner of the reserved-ADR scope-notes check); CO3 strict, CO4 (what makes a clause stated rather than mentioned; Q10 is spent on CO2); SR2 strict; SR4, SR5, SR7 (L).

## Ungrounded check

Snapshots rebuilt with `git archive <base> | tar -x` into empty directories under `/tmp/blindsnap.81tlxT/{ng,co,dg}` (ng = c60e89e1, co = 5a951034f270efe967f56d1d3c3c69436d37b8ad, dg = 891a9a24b51e5e9fda02a992c6a27910a216787d). Every backticked path and symbol in each Grounds line was grepped there (FIXES["applied-none"], check_task(seed=...), HoldTests.HOLDS, PartialRollupTests test name, pr_watch tasks() all found; `references/sd/adoption.md` resolves under `kc-dev-flow-2/`). Every quoted Story phrase was grepped in the key's source task file under `_archive/` and found (the story text is not in the snapshot). Result: 0 ungrounded in all five lists. special-role Q20 names `fo-batch-sittings/dogfood/` and says itself that it is absent from the snapshot; it is a story citation, so it counts as grounded.

## Judgment calls a second scorer could move

- DG2 on Q17 (and Q15): strict because the question names an unexpectedly skipped required test; a stricter reading would make it partial.
- FW1 on Q7: strict because the answer must state the per-finding form a decline carries.
- CO3 left partial: Q17 (cost of durable acceptance output) is the other candidate and is no closer.
- If DG2 and FW1 were both partial, the total is 4 of 13; if CO3 and FW2 were both strict, 8 of 13.

## Blinding limit

The assignment and the task title name the arm, and the checklist states the sol totals (6 and 5 of 13), so this scorer knew the arm and the bar before scoring. What was kept blind: raw/, report.md, the closed POC's scores.md and the implementation report were not opened until this file was written; every score above carries its quote so it can be re-scored.
