## Stage Report: implementation

- DONE: Implement the approved one-file design on origin/main e7c9381f2; use only the named file, no version bump, and no ADR in this PR (D2).
  Candidate: 7f47317bb278931a873c0ec63302fbc70fc53fc4; branch spacedock-ensign/validation-reads-pr-review-comments; base e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e. Wording 1; worktree-final.json proves clean assigned root/branch; PR #794 was not used.
- SKIPPED: One Draft PR in iamcxa/kc-claude-plugins.
  No PR opened: no push grant; FO owns publication. Prepared title/body: /tmp/impl-validation-reads-pr-review-comments-pr.md and implementation/prepared-pr.md; no product push, review comment, ready or merge.
- FAILED: Every acceptance criterion green, with each named evidence and falsifier exercised.
  AC-3 is not met: final-verdict.json/results.md retain 14 raw attempts, the 12 scheduled cells, 10 scheduled reports and only 7 valid reports; Claude base already finds 3/3, so strict improvement is impossible for this baseline.
- DONE: Required repository lint, installed adr_lint.py, number_guards.py check, comment_ratio.py and design_surfaces.py.
  implementation/checks: lint.log 5931/5931; adr.log 63 records/exit 0; numbers.log exit 0 with local-ref freshness warning (no numbered surfaces); comments.log 0 code/0 comments, maximum 5%; design-surfaces.log exit 0; product-diff-check.log clean. CI cost per PR unmeasured; triggers unchanged.
- DONE: AC-1 — the package diff changes only principles.md and carries the approved opening and closing sentence.
  words.json: 826→877; workflow hash unchanged at 5931. The executed one-word throwaway workflow mutation exits 1 at 5932 (workflow-budget-mutation.*); no other product file changed.
- DONE: AC-2 — preregister before provider calls, preserve fixture rewrites, prove the shim and grader, and compare dispatch arms.
  e7e7b74b4 committed preregistration before runs; normalized dispatches identical and package delta only principles.md. grader-falsifiers.json: validation-3/4 negative, synthetic F1 positive; id-anywhere mutant wrongly finds validation-4. Unrecorded-call refusal exits 1; grader-integrity.json proves original grader bytes unchanged.
- FAILED: AC-3 — meet candidate > base and candidate ≥2/3 separately on both registered hosts.
  Codex valid counts: base 1/2, candidate 2/2; Claude: base 3/3, candidate 0 valid. Five scheduled fixture gaps include both Claude candidate timeouts (no report, exit 124 at registered 1800s). Remaining two attempts could yield only 9 valid reports of required 12; no futile retries.
- DONE: AC-4 — the reword path stays bounded.
  Every run used original wording or wording 1. No wording 2, third wording or second fixture extension; incomplete samples, saturated Claude baseline and remaining budget cannot justify more calls. secondary-falsifiers-final.log rejects an unregistered wording and a found report without comment response.
- DONE: AC-5 — precision is reported rather than gated.
  precision-review.json/results.md: no completed candidate report calls repaired comment 4505536959 unaddressed (Codex 0/3, Claude 0/1); two Claude attempts have no report. The excluded base-2 automatic precision signal is explicitly corrected as a fixed-disposition mention; raw signal retained.
- DONE: FO message-1 — rebuild from historical evidence and record every substitution/removal with its source, record id and timestamp.
  fixture/rewrites.json and README use validation-3/hosted-refresh pr/run captures and the pre-cutoff committed prepared body; updated bot summary 6719156954 and all post-cutoff records removed. Live sources retained; target 4505793059 frozen at 778367add.
- DONE: FO message-2 — repair command resolution and probe it; then attempt both hosts with D1 retained.
  Shell guards plus allow_login_shell=false and absolute-shim instructions pass zsh/bash login/non-login preflights. First fixed Codex completed, so no Codex route-failure or Claude-only claim. Logs moved inside scratch; one registered metadata extension used. Two preliminary attempts remain excluded and charged to the 16-call cap.
- DONE: FO message-3 — keep the registered primary count and add a separately labeled post-hoc manual column for every completed report.
  manual-semantic.json quotes all 11 completed reports, explicitly defined after the first valid result. On the available Codex subset primary 1/2→2/2 beats base, post-hoc 2/2→2/2 ties; results.md and prepared PR say this plainly. Neither subset satisfies AC-3; Captain retains interpretation.
- DONE: Record document impact, necessity and words FO reads at each moment.
  doc-impact.json is []; only the approved principles document changes. Startup/dispatch/idle/merge inputs +0; worker +51 words. results.json records report-word means by arm, including missing data and full appended reports. Without the edit, Claude finds 3/3: additional behavioral benefit/necessity is not demonstrated.
- SKIPPED: roborev not run: FO runs RoboRev because the Codex sandbox cannot reach its daemon.
  Hosted CI, external reviewer disposition, publication, independent validation, adoption, merge and release remain FO/Captain-owned; no clean delegated result is implied.
- DONE: Commit the local product candidate and preserve complete report/shim/token evidence before cleaning owned replay worktrees.
  All provider attempts ended; per-run meta/events/report/gh logs and partial usage snapshots retained. cleanup.json removes all 15 helper-created replay worktrees; assigned product worktree remains clean. Task frontmatter is unchanged; workflow state stays implementation.

### Findings

- F1 Needs decision: AC-3 cannot be claimed; hold publication and return the evidence route to FO/Captain. No third wording is proposed. Registered versus post-hoc Codex conclusions differ on the available subset; the Captain rules on that distinction before accepting a revised proof.

### Summary

HOLD: the proposed one-file change is committed locally, but its required behavioral proof failed. Both prescribed hosts were exercised within 14 of 16 attempts; fixture gaps, timeouts and a 3/3 Claude baseline prevent the accepted improvement claim. FO receives the pinned branch/base/candidate, prepared PR text and retained evidence; this report grants no publication or merge authority.
