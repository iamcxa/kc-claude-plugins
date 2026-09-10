# ship-cloud-wrapper — questions from cloud workers and the answers sent

## 2026-09-10 ship-remove-duplicated-stations (session b2811dee)
Q: gate prepare refuses: backlog-gate record pins commit 9826ffcf, missing everywhere; repair or relax the tool?
A (ship FO, own repair): commit was rewritten by the FO's replay; restored under refs/heads/spacedock-state/dev-recovery-9826ffcf; fetch it and retry; no record edit. Also: fix the failing version-parity check on #410, drop the Linear id, conform the body to pr-merge template.

## 2026-09-10 ship-verify-uat-close (session abc9855f)
Q: Captain approval before creating the PR?
A (ship FO, Local Profile Delivery row): a Draft PR is the FO's own action; proceed, record pr:, fetch the recovery ref, gate prepare, stop.

## 2026-09-10 ship-verify-uat-close (session abc9855f), rounds 2-3
Q2: is the "First officer (ship)" message an injection? (refused the recovery-ref fetch)
A2: same sender as the boot message (verifiable senderId); verify the claim by running gate prepare and inspecting the commit before fetching; fetch cannot rewrite a branch.
Q3: pr-merge mod requires a captain-approved push for a brand-new delivery; conn quote?
A3 (Captain authority, existing conn): conn-source = the entity's backlog gate record (approve, person:captain, 2026-09-10); conn-quote = AC-3 of ship-cloud-dispatch-and-watch ("... a Draft PR opened by the cloud first officer ...") in the Captain-approved brief. Push, Draft PR, gate prepare, stop.
Finding for dispatch.sh: the boot message must carry the conn (gate record id + AC sentence) and the sender identity up front.

## 2026-09-10 ship-verify-uat-close (session abc9855f), rounds 4-5
Q4: (after the Captain typed "push it: open the Draft PR, prepare the validation gate, stop." into the session) — pushed, PR #411 opened, pr: recorded.
Q5: gate prepare refuses on a second missing object 4b20a918 (the sibling's backlog record commit, also rewritten by the FO's replay).
A5: pushed refs/heads/spacedock-state/dev-recovery-4b20a918; fetch, inspect, retry. Defect owner: ship FO (state replay).

## 2026-09-11 feedback round 1 (batch FO → both workers)
Gates: validation revise recorded on both entities (actor agent:first-officer, conn = Captain 「批」 2026-09-10).
#410: merge main (#406 landed), delete fenced-dispatch/intent/holder/worker-transcript, wire new tests into contract-test, body per mod + Residuals/without-it.
#411: merge main, align close.py/uat-doc.py to dispatch.sh's fence shape, ship v2 schema file, body per mod + Residuals.
Finding 7 (2026-09-11): a cloud FO's own gate records pin commits that exist only in its clone (rewritten by its pull --rebase); the batch FO cannot record decisions on that entity from another checkout. Multi-writer split-root + rebase sync breaks content-addressed gate history in both directions. Workaround: the entity's own FO records the decision with the Captain's conn; boot message must say "merge, never rebase" for state sync.

## 2026-09-11 feedback round 2 (#410 only)
Batch FO verdict at af020cf4: revise. kc-ship-flow first-officer skill collides with the Spacedock skill name and carries stale stage lines (per-station pins, plan-receipt args, plan-flow validator, deleted spec path). Rename to run-batch; merge main after #411 lands.

## 2026-09-11 ship-verify-uat-close closed end-to-end
#411 merged by the Captain (c1564b21); worker ran merge guard (pr: pr-merge:411, done, archived) and wrote its own debrief _debriefs/2026-09-11-01-claude-claude-sonnet-5.md (aaabe747). First task to complete the full cloud-wrapper loop. Worker testimonial names `gate record --round` as the one undocumented step.
