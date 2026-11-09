# Independent validation of PR #817

Verdict: PASSED for product acceptance at `85f9a65928958f78a4eaf12b3ce38ca4e25e2ab0`, against `e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e` (origin/main and GitHub base). Profile: pilot. PR #794 remains outside this candidate. Product files were read and executed from Git archive exports; no git worktree was created or removed, and the assigned product worktree remains clean.

Merge-readiness answer: **not ready to merge immediately**. The product meets the accepted criteria, hosted checks pass, and no review finding stands unaddressed, but the PR is still Draft. The adopted workflow names Copilot as second reviewer, and this authority/merge-rule change triggers that review; no Copilot review or exception was observed. FO must settle that outcome, its delegated local RoboRev review, ready status, Captain acceptance steps and delivery checks before presenting the merge choice. This validation does not authorize a merge.

## Evidence and falsifiers

All paths below are relative to this validation directory.

- AC-1: `replay/baseline-control.json` runs the same missing-record fixture at the base (exit 0) and candidate (exit 1). The missing-hold mutant fails assertions in `replay/missing-hold.log`.
- AC-2: candidate tests exercise newest numeric selection, dispatched head, requested head, each clause, malformed/nonobject/missing/unreadable records, and another-text ad-hoc run. Oldest-record and four skipped-comparison mutants fail in `replay/mutations.json`; actual failures, not just error exits, were checked.
- AC-3: the passing question ends in the exact newest ask path; removing the reference output fails assertions. Non-merge legacy output remains identical. Full delivery suite: 184 tests, one optional historical approval replay skipped; targeted acceptance suite: all eight new tests pass.
- AC-4: `replay/commands.jsonl` exercises the installed Spacedock 0.27.2 binary in independent temporary product/state repositories. Uncommitted and post-commit edited references are refused (exit 1); state-committed unchanged reference prepares (exit 0), and the URI commit/path and sha256 match the actual bytes. These are synthetic tasks, not a real Captain approval. The implementation verifier was adapted only to read Git history from the assigned repository and use standalone temporary repositories instead of creating git worktrees.
- AC-5: repository lint passes with 5931/5931 words. The budget script is byte-identical to base. Appending an unbudgeted instruction makes lint exit 1, and the original export bytes are restored.
- AC-6: `replay/observer-replay.json` contains 12 replay results: valid reference ok; wrong digest/head/either clause and new-rule missing Reference violation; five historical batch-17 briefings can't tell; agent-reads-governing-adr remains ok through the pre-rule time fallback. Disabling that fallback changes the last case to can't tell. This executes the written comparison procedure; it is not a live observer-agent run.
- AC-7: separate validator-authored `independent-checks.py` selects and counts both delivery paragraphs, invokes base/candidate question commands, and compares check output using the existing provider stub: README 80/80, question 92/107, check 84/84. Adding one output word produces 108 and is rejected. Raw command outputs and the counts are in `independent/`.
- AC-8: read ADR 0071 against the task's recorded Captain answer and full ideation question. It amends ADR 0051's ordering consequence while retaining its round-count decision. Both selected package-root and dispatch-prescribed linter paths pass `docs/adr --since e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e --require 0071`, exit 0; both linter files have identical bytes. Removing 0071 from a temporary ADR directory makes the required-number check exit 1.

## Additional checks

`checks.json` records exit 0 for package ADR, design, dispatch records, comment ratio and document-impact checks. Number guards initially returned a warning that sandbox networking prevented a reservation refresh; the exact helper was rerun with authorized network access and `number-guards-refreshed.log` has no such warning. This is environment evidence, not a product failure.

Delivery tests (184, one optional skip), lint tests (47) and POC README tests (9) passed. The optional historical-approval fixture was not supplied; the required AC-6 historical records were replayed separately. No broader local whole-package claim is made. Hosted run 42577978797 independently reports success at the exact candidate head; `hosted-run.json` retains all job and step results.

The only added code comment links its governing ADR. Comment-ratio output is 1/127 (0.8%, maximum 5%). Affected documents are accounted for: ADR 0071 updated; ADR 0044 unaffected because optional-summary and reviewer rules remain; ADR 0051 retained immutable with consequence amended by 0071; ADR 0062 unaffected because quoted approval/grant rules do not change. Workflow and observer guidance are updated. No retained product diagram changed; the task has Surfaces: none.

## Review disposition

Read every entry from paginated PR reviews, inline comments and issue comments at the final snapshot: zero reviews, zero inline comments, three issue comments. The comments comprise the review request, completed Codex status tied to the full candidate hash, and its clean receipt naming 85f9a65928. No finding stands unaddressed. Files: `reviews-final.json`, `review-comments-final.json`, `issue-comments-final.json`, `pr-final.json`.

No new Material, Deferred risk, Polish or Needs decision product finding. Pending workflow delivery obligations are not silently marked complete. A missing Copilot result is not a clean review, and the delegated local RoboRev result was not independently observed.

## Scope and limits

Goal sufficiency: the command refuses preparation without matching evidence, native preparation binds the committed bytes, and the observer procedure distinguishes the accepted positive/negative/history cases. Minimal necessity: the helper/hold, reference instruction, workflow order, observer comparison/fallback, tests and decision record each serve an accepted criterion; no unrelated feature, record-schema change, Spacedock change or version bump was retained.

All implementation-report limits remain correctly bounded: merge-free questions are outside the new hold; omitting --reference is detected later by the observer rather than a prepare hook; equal cleaned 200-character clauses do not bind the entire briefing; fixture provider facts are synthetic, while real GitHub readiness was separately read; the first post-release observer-agent execution remains post-merge work. Published PR and hosted CI evidence now supersede the implementation report's earlier unrun state, without rewriting it.

CI cost per PR was not measured; this candidate changes no CI file or trigger.

## Captain acceptance script

Run this exact command in a fresh Bash shell:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-check-before-ask-is-provable/validation/acceptance.sh
```

The five numbered steps in that file declare every local dependency, export both pinned revisions, execute the eight new command tests, run native/historical/falsifier checks with an independent recount, and run lint plus required ADR validation. Expected: each step prints PASS; step 3 prints eight tests and OK; the replay prints its PASS line; lint prints 5931 of 5931; ADR lint prints 64 ADR file(s) checked, 0 legacy; process exit 0.

Executed exactly as written from a fresh `bash --noprofile --norc`; `acceptance.log` records the observed output. The same script content ran first from the temporary evidence directory; its committed-location run is recorded separately in `acceptance-published.log`. It creates only temporary exports and standalone fixture repositories, uses read-only source Git metadata, and needs no network, secrets, product mutation or real gate approval. It does not cover hosted readiness, real observer-agent behavior or Captain authorization.

