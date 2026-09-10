# ship-cloud-wrapper — questions from cloud workers and the answers sent

## 2026-09-10 ship-remove-duplicated-stations (session b2811dee)
Q: gate prepare refuses: backlog-gate record pins commit 9826ffcf, missing everywhere; repair or relax the tool?
A (ship FO, own repair): commit was rewritten by the FO's replay; restored under refs/heads/spacedock-state/dev-recovery-9826ffcf; fetch it and retry; no record edit. Also: fix the failing version-parity check on #410, drop the Linear id, conform the body to pr-merge template.

## 2026-09-10 ship-verify-uat-close (session abc9855f)
Q: Captain approval before creating the PR?
A (ship FO, Local Profile Delivery row): a Draft PR is the FO's own action; proceed, record pr:, fetch the recovery ref, gate prepare, stop.
