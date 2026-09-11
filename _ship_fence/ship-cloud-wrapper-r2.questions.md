# ship-cloud-wrapper-r2 — questions from cloud workers and the answers sent

## 2026-09-11 dispatch
Two workspaces created by dispatch.sh (main 96defe1d). Because the boot message still lacks identity/conn (fixed by 7z itself), the FO sent one follow-up to each session after `ready`: sender identity, dispatch token r2-7f3a9c1e, "no Captain message here", the Captain conn (backlog gate approve, 「確認」 2026-09-11), merge-never-rebase, PR body per mod incl. Residuals/without-it, design input path.

## 2026-09-11 outcomes of the identity/conn follow-up
- es (ship-verify-uat-close-round-2): cross-checked the conn against the gate record and the round-1 log, accepted, pushed, opened #420, prepared the gate. Zero questions.
- 7z (ship-dispatch-watch-round-2): judged the same message a prompt injection, prepared the gate without pushing; the Captain typed "push it" into the session; #423 opened. Same message, two sonnet FOs, two verdicts — the boot-header fix in 7z's own PR is the remedy.
- FO error: recorded approve on es's validation gate and told es "#420 merged" after misreading the Captain's question; corrected to es within minutes; #420 still open at that time.
