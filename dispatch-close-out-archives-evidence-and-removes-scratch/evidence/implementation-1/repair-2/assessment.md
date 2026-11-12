# Repair of validation-1

Candidate d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6 adds one commit on 223dbb6d1b5e895a45d11537b9494aa08610c8f8. Product publication remains with FO. All replay input is synthetic; no private repository was read.

## Finding dispositions

- F1: Material; kind=build; source=captain-ruling[2026-11-12], private repository evidence must never be archived; observation=the native builder on the old wording fails the new regression assertion (privacy-red.json/log), whereas the candidate emits the complete instruction in both its committed dispatch record and native dispatch artifact (replay/). Repair=scratch.notes_for instruction only, with a real-builder assertion. Removing just the private-repository phrase fails again (mutations/F1-private-repository-ban-removed.log). No scanner is added; generated instructions do not prove arbitrary workers obey them.
- F2: Needs decision; kind=aim or scope; source=Captain amendment 2; observation=the original global zero criterion conflicts with keeping another dispatch. Resolution=AC-3's complete original block moved verbatim to amendment 2; fresh AC-4's requirement is a verbatim substring of Asked (amendment-proof.json). Evidence=replay/replay.json, own registered count 0, one other dispatch registered and its uncommitted file preserved. Deletion logic is unchanged; no deletion is expanded to make the global count zero.

## Acceptance and falsifiers

- AC-1: test_dispatch_stage exercises the real native builder and checks exactly one Scratch line in the record/artifact. Removing the paragraph fails (mutations/AC1-paragraph-removed.log).
- AC-2: fresh-shell S4 replay exits 0: the removed report path passes, and the FO message with a missing path fails (s4.log). Restoring report scanning fails (mutations/AC2-reports-scanned.log).
- AC-4: ac4.log runs the exact named unittest command. The CLI replay closes one of two roots in the same synthetic repository and keeps the other. Leaving the own worktree registered fails; deleting the peer root fails (mutations/AC4-*.log). The whole-repository count of one is intentionally retained, not treated as failure.
- Compression, refusals, cap, archive/merged/idle behavior: the full current suites pass; the original ten mutations are rejected alongside the new privacy and two scoped-close mutations. All mutation runs use python3 -B and copies exclude caches. No pyc files were present in candidate scripts.

## Checks and limits

202 distinct tests pass (50 native dispatch; 152 watch/cleanup, including 13 scratch cases); fresh zsh -f acceptance gives 20 passing results (19 decisive tests and S4). These are current-round totals, not the old 333-test or validator's 337-check totals. The standalone dispatch_records suite is not rerun. All required package checks pass, with a fresh-ref number-guards rerun resolving the preserved initial sandbox fetch warning. Comment ratio is 0.9%, maximum 5%; worker paragraph is 52 words, maximum 66; idle text unchanged.

The original task evidence/implementation-1/acceptance.py was executed unchanged in a fresh zsh -f shell against the assigned worktree, SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock, with an owned output directory. Native dispatch fixtures require their candidate package path outside /tmp, because the approved scope-note boundary refuses Package root metadata under /tmp. This round needs no fixture adaptation. The runner, binary and output path were declared arguments; the binary reports Spacedock 0.27.2. Source-package lint and installed-package policy tools are intentionally distinct.

Document impact lists ADR 0079: its immutable accepted private-evidence and dispatch-only cleanup policies already match the repair, so no ADR edit is needed. ADRs 0070/0074/0077 are unaffected by the wording/test-only delta. No new decision, number, scanner, version or CI-trigger change. CI cost per PR is not measured. RoboRev, hosted CI, publication, second validation and post-release adopter proof remain FO-owned and are not claimed passed by this report.
