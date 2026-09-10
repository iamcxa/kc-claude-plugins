# Final bounded independent recheck — PASSED

The previously rejected AC-4 data-loss finding is corrected in the exact uncommitted candidate. This is an in-scope functional verdict, not all-green suite acceptance or delivery authorization. The original rejected report, unchanged reproducer and original before/after failure bytes remain preserved.

## Correction proof

- [Unchanged independent reproducer](unchanged-replay/result.json): actual archive commit failure remains rc1, archive contains the peer edit, live restoration retains it, and the test now passes. The instrument previously failed on rejected patch `cabbdd5221aec0b94597f4aeaca455810fe75b90922d76c4226fefda7547efe5`.
- [Fresh native focused run](focused.json): 77 pass, zero fail/skip on corrected patch. This includes approval/evidence/product refusal, whole-entity drift, native finalization/archive-once, consumed resume, committed publication recovery/conflict, later-intervening-edit refusal and existing product delivery/rollback tests.
- [Independent captured boundary checks](window-capture.json): both before-consume and after-consume cases execute a real rejecting pre-commit hook; live bytes after failure equal the captured archived bytes, including peer edit and consumed approval. Removing the hook and retrying natively finalizes PASSED with exactly the original attempt ID and Briefing digest. [Byte hashes](byte-proof.json) and all six state snapshots were preserved before fixture cleanup. A test-only overlay adds capture and exact identity assertions to the candidate's regression; production files remain untouched.
- Producer `correction-window-red.json` removes only the correction and observes both intervals failing. No broader suite or cask/base control was repeated during this recheck.

## Reviewed change and necessity

Only `internal/status/merge.go` and `internal/status/merge_guard_test.go` differ from the previously reviewed candidate. The knowledge call at merge.go:505 passes preserve-content mode to the existing rollback function at line 778; the condition near line 805 skips writing stale `snap.content`. Native location reversal and path-scoped index cleanup remain the same. Knowledge retry keeps the consumed approval and revalidates its identity/evidence; legacy product calls still restore pre-finalize bytes. The existing post-archive-content comparison/live-path refusal remains active, so a peer edit made by the failing hook still halts instead of being overwritten.

This is a smaller sufficient correction than introducing another preimage field or callback: it stops writing the stale bytes, uses the existing consumed-state retry, and is directly falsified by the retained tests. The new test covers the two observed write intervals, not a hypothetical new lifecycle. No additional file, dependency, schema, authority or service was introduced. Consumer documentation and other reviewed surfaces are unchanged. Bound project-context classification remains `none`: profile loading, plugin catalog and ownership claims are unchanged; current native tests and the two-file comparison validate that boundary.

## Acceptance criteria

- **AC-1 PASS:** fresh native knowledge finalization is finalized/PASSED/consumed with no live entity; output rc0 alone is not the assertion.
- **AC-2 PASS:** unchanged locked identity/frozen proof/product predicate and whole-entity expectation are freshly exercised; forbidden cases retain their state.
- **AC-3 PASS:** genuine merged PR/local-merge behavior and legacy rollback remain passing; open/malformed/missing proof stays nonterminal.
- **AC-4 PASS:** original failure corrected, both intervals retain bytes through commit failure, same consumed identity retries, and ordinary archive-once/publication retry/conflict/tamper checks pass. The inherited hard crash between rename and archive commit remains excluded.
- **AC-5 ACCEPTED RETAINED TEST-ONLY PROOF:** complete original-copy rebinding/publication evidence remains explicitly bound to predecessor patch cabbdd5221aec0b94597f4aeaca455810fe75b90922d76c4226fefda7547efe5. Its reviewed immutable declaration/consumer/archive/publication paths did not change; current tests prove the changed rollback/retry seam. This is not falsely relabeled as a fresh original-copy run. All 18 live original task, evidence, approval and pin files still match source hashes. No live original, cloud/resource operation, reauthorization, cleanup or final POC close claim.

## Exact candidate and residuals

[Readback](readback.json) includes roots, branches, HEAD/base, whole-patch hashes, per-file hashes, counts, formatting, full/race log audit, stage pin and preservation checks.

- Upstream `.context/spacedock-knowledge-delivery`, branch `spacedock-ensign/knowledge-output-cannot-terminalize`, HEAD/base `af70297ddae6ec64444849e8e3fcf57484bc16e1`; patch SHA-256 `6dc9e67966b29ba29eca9ce28a375081ff6c0345ac32f4ef13846bc8d0e2f93e`; 8 files/801 gross within 850.
- Local `.context/routine-coordinator/.worktrees/spacedock-ensign-knowledge-output-cannot-terminalize`, same branch, HEAD/base `c9c5752fda853737d4a937ad7f59564c5651ca53`; unchanged patch SHA-256 `2ffa88aaef51a4b482a71d190b5f3cbcbc2a5579d539a7cb87adfab12d685d0c`; 1 file/24 gross within 40. Both diff checks and changed Go formatting pass.
- Corrected full/race producer logs both bind the final patch and each recount 3,107 pass, 11 skip, one cask leaf failure plus parent; no data-race diagnostic. The unchanged failure is edge cask 0.27.1 below contract 0.28, already reproduced on untouched base. Both required suites are **red**. Acceptance of that release-state residual remains Captain-owned and is not delegated to this reviewer.
- No product commits/staging/reset, install, provider/model/cloud call, external posting or original live mutation. Object-based source map and optional RoboRev remain unavailable until an authorized candidate commit; no fabricated objects or provider requests. Captain exact-file commit confirmation and later PR/provider/delivery checks remain outstanding. No merge, release, install or closure authorization follows from this verdict.
