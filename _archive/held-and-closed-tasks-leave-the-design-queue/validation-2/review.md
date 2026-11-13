# Independent validation cycle 2

Verdict: PASSED at 455846c6d30d4ab650c1c4503bc591722231586d, against the accepted Pilot outcome and Captain amendments 1–4. This is a worker recommendation; live Held body edits, gate approval, stack integration and delivery remain separate First Officer/Captain obligations.

## Independent observations

- AC-1/AC-2: native Spacedock query selects the original ten ideation holds; no held slug enters the scheduler. Row removal and scheduler injection are detected (recheck-results.json).
- AC-3: full frozen public state eae5ea47 plus legacy source 8ce0eb60 yields zero of the ten names; command exits 0. Current output is 1287 words because public PR state is read live, so the historical 1353 total is not asserted invariant (legacy-full-state.log, native-summary.json). Appending a held name fails the same predicate.
- AC-4: native dispatch build of a held task exits 0 and produces the recorded artifact; this proves build only, not worker startup (ac4-dispatch.log).
- AC-5: native merge guard, terminal set and archive all exit 1; the first two explicitly say not-applicable. Only scratch state is targeted. No forced close is attempted (ac5-*.log).
- AC-6/AC-7: the real recorded same-stage successor remains present; seven proposed quotes are verbatim. Removing the successor and modifying each quote are detected. This proves recorded provenance, not semantic correctness of labels.
- NP-1/NP-2: real candidate tasks entrance exits 0, prints one fact naming fourteen held tasks exactly once, and requests their missing Held sections. Copy projections and eleven held tests exercise missing/false/amended/fenced/stale quotes, empty results and failed/partial queries. Five source mutations plus replacing the change with the stacked base each fail the held tests. Candidate bytes are restored (recheck-results.json, candidate-live-network.log, source-hashes.json).
- NP-3: independently measured by native queries plus unchanged formatter and wc -w: one 17/21, fourteen 32/34, fabricated 125 spanning all five configured stages 145/145. The implementation's commands were also rerun in fresh assigned scratch/output locations: one 17/21, fourteen 32/34, fabricated 100 120/120. All real cases exit 0 and all one-word-over-bound cases exit 1 (measurements.json, implementation-command-rerun/commands.json, bound-falsifiers.json).
- NP-4: scratch-only projections accept fourteen Held sections with unchanged frontmatter; a frontmatter mutation is detected. Live valid sections remain zero of fourteen and are explicitly FO-owned after delivery. No live held task was edited.
- NP-5: plain upstream status display remains unchanged, as the approved design states. No upstream work, forced archive or new dispatch guard was authorized.
- A fresh bash ran captain-acceptance.sh exactly as recorded: four steps, eleven tests, three independently counted cases and three rejected counterexamples; exit 0 (captain-acceptance.log).
- Related tests pass 164/164 with zero failures/errors/skips; this is test_pr_watch.py plus test_scratch.py, not the entire package suite (tests.xml, test-counts.json).
- Skill lint, ADR lint since pinned stack base with required 0081 from both installed paths, fresh number guards, comment ratio, dispatch records, design surfaces and doc-impact pass. One added ADR pointer comment is necessary provenance; ratio 0.7% <= 5%. ADR 0081 is the only affected retained document and its quoted passage is in the accepted gate (checks-exit-codes.json, number-guards-fresh.log, native-summary.json).
- Source identity is unchanged in all three task files. The stack-base diff contains only the two named Python files and the permitted ADR; removing the code change fails the held tests, establishing the bounded necessity. No CI configuration change; cost per PR was not measured.

## Ruling and declined-review judgment

NP-3 repeats the exact approved bound, 「每張擱置的任務最多多 1 個字，另加固定 20 個字」, and 「可以，照列名稱（建議）」. It retains name listing and introduces no new product requirement. Its one-line/startup/idle and projected-complete-Held qualification already existed in the accepted design; the five-stage larger case is a formatter probe, not a claim that terminal done can natively be held. Amendment 1 permits ADR 0081; amendment 2's numbers are replaced by amendment 4, and amendment 3 supplies this second validation cycle.

The chief-engineer decline is adequate under ADR 0026's repair-pass plain-decline rule: the product remains the initial candidate, the repeated work concerns one word formula and report/evidence handling, and the Captain already chose the correction and last validation. Independently there are five implementation report headings (four counted repair passes), not four reports: initial build/word stop, role-call stop, amendment-2 recount, amendment-4 recount and a cleanup-description correction. The imprecise count does not hide a second product mechanism or change the authorized next step; role_triggers exits 0. No chief-engineer review is claimed.

## Non-rejecting findings

- F1 Polish — kind: evidence or form. PR #856's body still states amendment 2's 3N+6 formula. Workflow: a reviewer reads the public PR. Harm: stale explanatory text; no demonstrated product or protected-boundary loss. Protected value: none, because this report and the task use the current Captain ruling. Trigger: pr-856.json. FO should update the PR body before presenting the delivery gate.
- F2 Polish — kind: evidence or form. FO alignment says four implementation reports while five are present. Workflow: reading the decline rationale. Harm: an inaccurate count, with the correct four repair-pass trigger and unchanged-source rationale independently verified. Protected value: none presently lost. Trigger: task-at-entry.md and role-triggers.log. The corrected count is recorded above; no fresh role call or product repair is needed on this evidence.

## Limits and setup corrections

The candidate's full real entrance succeeded after the same authorized public GitHub reads were allowed outside the network-restricted sandbox; original exit-2 logs remain. An initial sparse legacy state export omitted dispatch records and named held tasks in unrelated missing-record diagnostics. That setup was corrected to the full same frozen state; the zero-held-name predicate did not change. The first number-guard command lacked a main ref in the archive and exited 2; passing reruns explicitly name the pinned stack base and refresh public state refs only in the export.

Quote matching is substring provenance checking, not an interpreter of Captain intent. The scaling proof is for the adopted five-stage workflow, not arbitrary custom stage counts. No private repository was read or retained. PR #856 remains Draft/open at the requested head and still targets PR #854's branch; its provider base snapshot and #854's fetched head are newer than the recorded stack base (pr-856.json, pr-854.json). This pass does not validate those sibling changes, a rebased candidate, merged result, hosted CI or the report's historical RoboRev claim. Those are FO delivery work.

