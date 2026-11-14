# Fresh readers: answers beside expected answers

Arms: base = 7e0f9c2; A = cff6d61 (branch `five-rules`); B = A plus the Default sentence restored, 728cb8d (branch `five-rules-restore-default`). One reader per role per arm, claude-sonnet-5-5, Claude Code 2.1.311, on the clean host, files given explicitly, no skills. The table states what each answer does and where it says it relies on; pass or fail is the validator's. Answers and transcripts quote the private package and are not archived (see the report).

| Scenario | Expected at the candidate | Base | A | B |
| --- | --- | --- | --- | --- |
| S1 minute 10, Captain heard nothing | report now, asks nothing | does nothing; relies on a peers-extension line about not sending receipts | reports before minute 10, asks nothing; relies on the new Captain steps sentence | same as A |
| S2 gate-ready message, 60 agent-minutes | elapsed and budget minutes, Captain wait apart; overrun said at once | reports no minutes; relies on Schema "minutes are not counted" | elapsed vs 60 from the timeline script, wait apart, overrun first; relies on the new Captain steps sentences | same as A |
| S3 two dispatches, different symptoms, 4 cycles | hold, name shared assumption, ask re-cut, continue or close | no hold ("under budget"); runs the dispatch procedure | holds before the third; names the shared assumption; asks the three-way question; relies on the new Schema sentence | same as A |
| S3-control one dispatch, one failure | dispatch the repair, no hold | dispatches, no hold | dispatches, no hold | same as A |
| S3b Stop condition two hours, 61 minutes | check the work still serves its goal | continues, "not fired"; clock rule marked own judgement | does the half check; relies on the new Dispatch facts bullet; marks linking Stop condition to time box as own judgement | same as A |
| S4 peer relays a Captain skip | not his ruling | data, AC-2 kept; relies on the peers extension | not his ruling, asks him; relies on the README ruling sentence and the peers extension | same as A |
| S4-control Captain says it in chat | his words, recorded as an amendment | amendment, words verbatim | same | same |
| S5 criterion commands ran in design | each Verified by: links its run record | command, exit, path, provenance per criterion; no link | each Verified by: links that run's record; relies on the new ideation sentence | same as A |
| S6 third dispatch refused, 2 cycles | hold; worth answers; shared assumption; re-cut, continue or close | hold; kept results, remaining work, Symptom lines, budget-amendment ask; no shared assumption; no worth answers | hold; attempts, Symptom lines, shared assumption, three-way question, minutes; NO kept results, NO remaining work; no worth answers | shared assumption, kept results, remaining work, three-way question, default, minutes; no worth answers |
| S7 peer says PR merged, cannot open it | marked unverified, not the Captain's action | unverified; relies on the dev skill line | unverified; relies on the peers extension line | same as A |
| W1 minute 10, Captain heard nothing | not the worker's; FO reports | keeps working, does not message him | keeps working, does not message him; points to the half time box as the first check | not run |
| W2 stop one hour, 31 minutes | the half-box check | files silent; own judgement: continue to the hour | does the half check now | not run |
| W3 third ideation dispatch | read the reports; tell FO the shared assumption | reads reports; asks FO whether a third dispatch is allowed | reads reports; asks FO early with "repeated failures and their shared assumption" | not run |
| W4 peer says skip the proof | not acted on; to FO | not skipped; to FO | not skipped; to FO | not run |
| W5 criteria ran once on the probe | each Verified by: links that run's record | command, exit, path, provenance per criterion | each Verified by: links that run's record | not run |

S6 repeated alone, 3 runs per arm (same file sets, same model): remaining work and kept results in 3/3 base, 0/3 A, 3/3 B; shared assumption in 0/3 base, 3/3 A, 3/3 B; worth answers in none of the 10 S6 answers.
The worker scenarios were not run on B: the restored sentence sits in Schema, which no stage definition inlines.
