# engineering-reviewer-1

Reviewer: kc-dev-flow-2:engineering-reviewer, opus, 2026-10-21. Read-only. Task at state adee32da; package origin/main c27e7659.

Bottom line: adjust, not hold. Hold A (round count) is sound and changes no authority. Hold C (owed special-role calls) is sound and fails closed, with one unobserved let-through. Hold B under D1's strict recommendation does not move merge authority (he is still asked, in text he approves), but it turns three grants he accepted as optional into words every passing merge ask must carry; that needs his explicit words at the ideation gate, and the D1 framing has to change first. AC-2 is falsified by the design's own pattern.

Verified: 23 merge/ask-N.json files across 10 archived tasks (PRs #670 to #689), none a Release PR. The design's A and B replay matches row for row. C (role_triggers.py at c27e7659, --rev each briefing commit) exits 1 only on fo-batch-sittings ("replacing amendments 1, 2, 3", 073bf8ba). Sources of the three sentences: the merge rests on the Captain's ADR 0023 amendment 1 「當我同意/核准驗證關卡時，等於授權你也合併 PR，除非我有顧慮暫時不合併」; worktree removal came through 「照建議」 on ADR 0023's D1 text ("lets a delivery gate question carry"); later rounds came from ruling #564(a) (commit 8134645d): "a delivery approval that says so covers later external-review repair pushes". Two of the three were accepted as optional; strict B makes all three mandatory.

B: strict B keeps ADR 0011's line but changes what FO may send: a plain merge-only ask, or one that keeps worktree removal or later rounds with him, no longer passes, though ADR 0023 and #564(a) allowed both, and ADR 0023's "fails safe" consequence is withdrawn. It leaves ADR 0023's reopen condition unchecked (a merge on an approval that never named it). AC-2's falsifier example "a later round" matches the proposed `\blater\b[^.?\n]{0,30}\brounds?\b` (probed). The relay case is a validation-only gate on a then-draft PR that the check would hold on draft first. The Release PR exemption has never run (0 of 23; a Release PR head cannot equal a Candidate: line). What B does when PR facts fail to load is unspecified. Cheapest alternative matching the class: hold a silent ask, but pass all three phrases or an explicit keep clause read with clause() (e.g. `Not carried: <which> (<reason>)`); it holds all four batch-4 asks and keeps ADR 0023's "may". Recommendation: adjust, confidence high.

C: no authority gap; folder tasks fail closed twice (exit 2 holds). One let-through visible in the sources: role_triggers.py reads committed HEAD while check() reads the task from disk, so an uncommitted replacing amendment passes C. A dated FO-written waiver clears C (ADR 0026's choice) and nothing shows it to the Captain on a passing run. D2-no changes no ruling, but the title "a task that owes a special-role call" overclaims (review-round case not held). Recommendation: proceed, confidence high.

ADRs: ADR 0023 under strict D1 withdraws an accepted consequence and turns "lets ... carry" into "must carry"; an Amended paragraph is adequate only if the gate question says so plainly. ADR 0026 changes no ruling. Recommendation: escalate (the Captain's), confidence high.

Must change before the ideation gate:
1. D1: add the explicit-keep variant as a real option; if strict stays recommended, the gate question says approval withdraws ADR 0023's "fails safe" and makes every checked merge ask carry all three grants, two accepted as optional.
2. Correct the relay sentence in D1 and Measurements.
3. AC-2: tighten the pattern or rewrite the falsifier.
4. Release PR exemption: state it has never run (synthetic fixture only); specify B when PR facts cannot load (no exit 2 turned into exit 1).
5. C: name the HEAD-versus-disk difference; hold on a dirty task file after measuring, or list it as a residual; optionally derive the slug from the parent folder for index.md.
6. Bound the title and headline to repair passes and replacing amendments read from the committed task.
7. Flowchart: A-no should not end the run.
