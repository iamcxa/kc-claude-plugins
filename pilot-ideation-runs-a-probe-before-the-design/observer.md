Observer report: 2 violations; independent merge verification remains incomplete.

Task: `pilot-ideation-runs-a-probe-before-the-design`. Window: `3bf964c47..2b22ba91f`. FO means First Officer; AC means acceptance criterion.

violation | rule: “FO adds no words of its own and does not move or rewrite a criterion” (Captain amendments) | evidence: “FO corrected its replacement to fresh AC-10”; “this worker edited no criteria” (task:464, `2b22ba91f`; criterion changed in `16f3a8a16`).

violation | rule: “never reuses an id” (Captain amendments) | evidence: “**AC-3** Amended by Captain, amendment 2.” (`7bf79fd79`, task:305). Subsequently corrected to “**AC-10** Amended by Captain, amendment 2.” (`16f3a8a16`); the historical violation remains.

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: backlog question “決定：要不要讓” matches reason “answering 「決定：要不要讓”; full whitespace-normalized match (`2b22ba91f`).

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: ideation question “決定：要不要核准” matches reason “answering 「決定：要不要核准”; full match (`2b22ba91f`).

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: validation question “決定：合併 #864” matches reason “answering 「決定：合併 #864”; full match (`2b22ba91f`).

ok | rule: “FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`” (backlog) | evidence: “seed fields and FO alignment recorded”; replay exit 0 (`f98d61ece`).

ok | rule: “FO runs `python3 <package>/scripts/design_surfaces.py check <task>`” (ideation) | evidence: “design surfaces presentable”; replay exit 0 (`66eba253d`).

ok | rule: “gate prepare`, which takes `--reference <check record>`” (Delivery authority) | evidence: “reference:pilot-ideation-runs-a-probe-before-the-design:validation:attempt-1:revision-1:item-2”, time “2026-11-13T09:04:12Z”, head “45d5ebb9d24665c0904aca5412123a7224d056cc”; digest, head and confirmation clauses match (`f23154e31`).

ok | rule: “FO confirms both goal sufficiency and minimal necessity” (validation) | evidence: sufficiency “an ideation dispatch built from the candidate carries the probe permission”; necessity “the workflow text, the ideation principles and Pilot profile texts” (`f23154e31`, merge/ask-1.json).

ok | rule: “FO counts rounds and records the count in the committed gate summary” (FO steps: review findings) | evidence: “External rounds: 3.” and three named verdict sources (`2b22ba91f`, validation briefing).

ok | rule: “A merge ask names each listed reviewer that was not read” (Extensions) | evidence: “Copilot 因額度不足沒有審” (`2b22ba91f`, validation question).

can't tell | rule: “Observe the actual repository-qualified PR merge” (Delivery authority) | evidence: “error connecting to api.github.com” (merge audit); hosted merge is outside verified state.

Coverage: Read README, task history, FO changes, eight dispatches, three briefings, amendments and delivery records; sampled worker evidence without judging it. Ledger and role checks exited 0. Historical archives replayed in memory without files; ideation reported “scope check not run: not in a git checkout”. Merge audit’s own exit was 2, captured without piping; no `carried:` result. Fetch was suppressed under read-only scope; local references may be stale. Missing records may reflect chat approval or state elsewhere. Unrecorded dispatch-check timing, publishing grants and hook verification remain unverifiable. State stayed clean at the pinned commit. No files written.

```text
Remaining: Report preservation and owning First Officer disposition.
Next: Save this report unedited (you).
Closable: no
```
