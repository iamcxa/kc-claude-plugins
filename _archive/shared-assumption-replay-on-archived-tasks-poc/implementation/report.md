# Shared-assumption replay on archived tasks

## Result

**Literal causal-quote k = 2 of 5**: `dev2-laws-check` and `delivery-gate-verdict-form` (`evidence/implementation-1/counts.json`, derived from `comparison.json`). The specified stop is k below 2, so the literal comparison does **not** trigger it. Each counted match covers one cause named by dispatch 3, not every clause of the hypothesis or every repair in that dispatch.

**This does not establish that the prompt helps.** Demonstrated independent blind predictions: 0 of 5 (evidence coverage, not measured predictive accuracy). Both matching rows have later-work information in the allowed second worker report; the verdict-label defect is also already explicit in dispatch 2. The required pair of two failed fixes for the same check is not identified by the first two dispatches in any counted row (`applicability.json`). No rework reduction, time saved, live efficacy or success rate was measured.

## Inputs and ordering

The counted set is the original four (`fo-lifecycle-mod`, `merge-gatekeeper`, `prod-security-review-gates`, `dev2-laws-check`) plus `delivery-gate-verdict-form`. All use implementation, the earliest eligible implementation/validation stage with at least three saved dispatches; no alternate-stage substitution was needed. Dispatch numbers include follow-up messages and are not completed-attempt counters.

The required current-worktree `learning.md` read disclosed the later fence-blind `Surfaces:`-count/corpus-verdict repair for `ui-design-review-in-ideation`. That row is retained as contaminated and excluded. Per `dispatch/implementation-1-message-1.md`, the first replacement was `delivery-gate-verdict-form`: it is not named in the learning note read. No replacement was skipped; the remaining listed alternatives were not reached. The laws report had separately mentioned this task implementation-4 as a bare-script-name example; that exposure is disclosed in its frozen hypothesis and was not used as the verdict hypothesis.

Only implementation dispatch files 1 and 2 and the first two implementation Stage Report sections were supplied to hypothesis writing. The task-body reader streamed and returned only those report spans; it stopped after report 2. Directory filenames and Git identities/status were metadata. The manifests preserve dispatch hashes and report spans/hashes; the allowed second reports nevertheless contain later historical work, described per row below.

The original set, including the excluded UI row, was committed at `9bc6c6e699def6958069d85e4374bb344b95e4e3`. Before the FO changed the commit procedure, the exact task-scoped command succeeded through a narrow sandbox escalation after an initial linked-worktree index denial. No git-add fallback, product commit or archive mutation occurred.

The **final five** hypotheses and checks are frozen together at `c24854032f31aa6281810d7d0c492ebb206d1f6d` in `implementation/assumptions.md` and `evidence/implementation-1/assumptions-v2.json`. FO committed and synced them, then sent `committed c24854032f31aa6281810d7d0c492ebb206d1f6d`. The worker verified committed bytes and the state-branch ancestry before opening any third dispatch. The final hypotheses were not edited after that commit.

Freeze verification: `2026-11-14T02:50:03.251081+00:00`; first third-dispatch open: `2026-11-14T02:50:14.799391+00:00`. See `freeze-receipt-v2.json` and `third-dispatch-read-log.json`. This is Git identity plus a self-recorded read sequence and the session tool order; it is not an operating-system file-access audit or proof of absent prior knowledge.

## Per-task comparison

### fo-lifecycle-mod

Frozen shared assumption:

> Moving lifecycle instructions into mods and testing their hook order is enough to make every real merge path run the intended observer/watch work before a sentinel is written.

Proposed check (not executed): In a throwaway workflow, run the real merge guard with pr empty and pr populated, force the observer check to fail, then inspect whether any pr-merge path still writes the merged sentinel or starts a second watch. Failure of either ordering refutes the premise.

Dispatch 3:

> Bring kc-dev-flow-2/references/sd/workflow.md to at most 5501 words by trimming at least 12 words

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod/dispatch/implementation-3.md:10`.

**Literal causal match: no.** Dispatch 3 repairs the accepted word bound and leaves the observer/sentinel High as a recorded design limit. It does not repair the hook-order premise named in the frozen hypothesis.

Recorded outcome: The third implementation report (lines 495-508) records commit 33295355: workflow text trimmed to 5495, lint budget lowered, and the observer/sentinel limit left for validation.

Worker-outcome quotation:

> AC-2's bound is met: 5495 words against 5501.

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod.md:508`.

Temporal leakage / prediction limit: Report 2 precedes this third-dispatch budget correction and already discloses the exact 5513-versus-5501 miss. The named hook-order hypothesis instead follows its separate unresolved review finding.

### merge-gatekeeper

Frozen shared assumption:

> A passing delivery check and a merge line pinned to the current head remain sufficient authorization until the head changes, even if a failure record or a grant changes at that same head.

Proposed check (not executed): After producing a passing head-pinned merge line in a throwaway repository, add a failure record or remove the grant without moving the product head; attempt the supported merge entrance and require refusal. A still-runnable line refutes the premise.

Dispatch 3:

> Update FIXES["readme-keeps-delivery-rules"] need and swaps

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper/dispatch/implementation-3.md:8`.

**Literal causal match: no.** Dispatch 3 authorizes synchronizing pinned workflow sentences in test_sd_dispatch.py, not revoking a previously emitted merge line after same-head record/grant changes.

Recorded outcome: The already-permitted second implementation report (377-387) is the response to dispatch 3: head fdeee5e5 updates the pins and reports CI green, while retaining the merge-line validity-window High.

Worker-outcome quotation:

> The test_sd_dispatch.py pins follow the rewritten paragraph and keep one pin per delivery rule

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper.md:386`.

Temporal leakage / prediction limit: The first report already states the CI pin failure; the second report quotes the later dispatch-3 checklist and completes it. File ordinal 2 therefore leaks the later outcome.

### prod-security-review-gates

Frozen shared assumption:

> Changing the brief or splitting the review by gate can make an unchanged reviewer find the same runtime write-limit defect when validation is confined to a diff that does not touch the responsible handlers.

Proposed check (not executed): On the saved design and validation diff, identify the public entrance and trace it to the session/comment write handlers; compare whether the existing validation review scope includes those handlers. If they are out of scope, another brief-only attempt cannot establish that runtime coverage; return the scope decision instead of patching the wording again.

Dispatch 3:

> the ideation-gate review names prompt injection; the validation-gate review names unbounded comment or session writes

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates/dispatch/implementation-3.md:8`.

**Literal causal match: no.** Dispatch 3 amends/splits acceptance by gate and orders another diff replay. It does not expand the unchanged validation reviewer to the handlers outside that diff, which is the causal premise named by the hypothesis.

Recorded outcome: The already-permitted second report (388-406) records the amended criterion but no candidate-byte change, no push, and a replay returning no findings; the validation-scope cause remains.

Worker-outcome quotation:

> the finding lives in handlers the diff does not touch and standard tier does not trace them

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates.md:405`.

Temporal leakage / prediction limit: Dispatch 2 only supplies an ADR reservation. The second report already contains amendment 1 and the validation replay that dispatch 3 orders; it explicitly explains the out-of-diff handler cause.

### dev2-laws-check

Frozen shared assumption:

> A latest representation, or just the newest addition of a dispatch-record path, is a sufficient proxy for all historical additions that the law must judge.

Proposed check (not executed): In a throwaway history, add a violating record, correct it, delete it, and re-add a corrected record at the same path; judge the original event and require it to stay a violation. Compare this with judging only the tip or newest add; either erasing the original violation refutes the premise.

Dispatch 3:

> L2 judges a record by its bytes and folder at the commit that added it

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check/dispatch/implementation-3.md:8`.

**Literal causal match: yes.** Causal match on the historical-record representation: later corrections/deletions must not replace the bytes/folder at the judged adding event. The other dispatch-3 cause (exit-1 checker with no parseable line) was not named by this hypothesis. Its stronger delete-and-re-add check is not fully fixed by the later newest-add implementation.

Recorded outcome: Dispatch 3 is investigation/proposal only and explicitly allows no commit or push. The already-permitted second report (451-469) records the later authorized 096ce885 as-added fix and separately leaves newest-add/delete-re-add as an unresolved limit.

Worker-outcome quotation:

> L2 writes each record and its folder from its newest adding commit

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check.md:456`.

Temporal leakage / prediction limit: Dispatch 2 only reserves an ADR. The second implementation report already quotes and implements the P1/P2 findings introduced by dispatch 3, so the causal match is not independent prediction.

### delivery-gate-verdict-form

Frozen shared assumption:

> A syntactically recognizable Verdict/PASSED label is enough to recover the current validation decision, even when the label is qualified as prior or candidate lookup can fall back to an older passing section.

Proposed check (not executed): On throwaway report strings, put Prior Verdict: PASSED before the real Verdict: REJECTED, then put a same-head later REJECTED section over an older PASSED section and a latest PASSED without a candidate over an older one with a candidate. Require no current passing candidate in all three cases; accepting one refutes the premise.

Dispatch 3:

> forms after a word skipped, first counting form decides

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form/dispatch/implementation-3.md:10`.

**Literal causal match: yes.** Causal match on distinguishing a qualified Prior/Independent label from the operative verdict; anchoring skips a form after a word. The hypothesis also names cross-section fallback, but dispatch 3 explicitly leaves AC-4 to a later Captain ruling; that part is not credited as a dispatch-3 fix. The template-skip repair is an additional cause not predicted.

Recorded outcome: Dispatch 3 authorizes anchors and skipping a both-outcomes template, with no push before the AC-4 ruling. The allowed second report (503-518) preserves two prior unpushed commits and implements the later AC-4 amendment; it is not a contemporaneous report of dispatch 2.

Worker-outcome quotation:

> The latest validation section with a counting Verdict form now decides

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form.md:517`.

Temporal leakage / prediction limit: Dispatch 2 already names the qualified-label failure explicitly. Report 2 is a later cycle-3 recovery/AC-4 repair and supplies the other half of the frozen hypothesis. The record order is correct, but this is not independent evidence that the prompt discovered an unknown cause.

## Verification and limits

`verify_replay.py` exited 0 on the final evidence. It checks frozen bytes against the Git commit, five counted task identities, first-two source hashes/report spans, dispatch-3 hashes and quoted lines, worker-outcome quoted lines, recorded timestamp order and recomputed counts. Negative controls altered one frozen hypothesis and one dispatch-3 quote in scratch copies; both were refused (`integrity-controls.json`). These controls test evidence integrity, not the semantic match judgments or the benefit of the prompt.

Reproduce from the workspace root, with Python 3, Git and the two declared state checkouts present:

```sh
python3 .context/dev2-poc-route/docs/dev2-poc/.spacedock-state/shared-assumption-replay-on-archived-tasks-poc/evidence/implementation-1/verify_replay.py --workspace-root . --state-root .context/dev2-poc-route/docs/dev2-poc/.spacedock-state
```

The source archive was clean for the inspected task paths at intake; its captured Git identity is `7af9ca4fc1d779cdafc436421f9f3b8c44764b76` (`first-two-manifest-v2.json`). The verifier requires the declared archive layout; a product-only clone does not supply it. `source-excerpts.md` retains the decision-relevant quotations for manual review. Historical test counts, CI claims and model outcomes quoted by archived workers were not independently rerun.

Product boundary: branch `spacedock-ensign/shared-assumption-replay-on-archived-tasks-poc`, base and unchanged candidate `c2f035b6612f5edb42220576b3414e993531ffd6`. No product/test/README/script changes, product push, pull request, review request or merge. Prepared PR text: not applicable to this approved read-only outcome. Repository rulings consulted for workflow boundaries: ADR 0048, 0072 and 0079; no new ruling or ADR is proposed.

Current-worker checks: comment ratio reports 0 code lines, 0 comment lines, 0.0%, threshold not enforced below 20 lines; document impact reports 0 affected documents. Number guards returns PASS with a warning that fetch was unavailable and local refs may be stale; no migration or number is introduced. The generic design-surfaces check emitted missing `Surfaces:`/`Visible change:` markers (raw exit 1 retained), but FO explicitly ruled it not applicable to this four-stage POC route; it is not reported as a failed acceptance criterion or repaired. See `checks.json` and the individual logs.

roborev: not run, as dispatched (no code candidate to review). CI and CI cost per PR: not measured; no CI change or PR. No live model runs or historical code replays were launched. The proposed diagnostic checks in the five hypotheses remain proposals, not executed results.

## Close-out

The one implementation cycle produced the read-only comparison within the recorded minute budget. Scratch close exited 0 and removed the dispatch scratch; exact output is retained at task-root `scratch-removed.txt` and `evidence/implementation-1/close.log`; independent validation, gate decisions, final report commit/sync and the copy beside the study remain with FO. No new workflow rule is activated by this report.

The stdout receipt was populated after the close command enumerated evidence hashes. The original checksum list is retained as `evidence/implementation-1/SHA256SUMS.before-stdout`; the final `SHA256SUMS` was regenerated and verified after stdout completed (`close-checksums.md`). Frozen hypotheses and source evidence are unchanged.
