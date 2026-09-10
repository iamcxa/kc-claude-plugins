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
