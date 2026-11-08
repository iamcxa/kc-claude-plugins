# Chief engineer advice: preserve the complete dispatch commit scope

Recommendation: **adjust**. Add one fail-closed check for the complete task commit scope before the wrapper writes anything, then exercise that boundary through the real builder. Checking only the reused record's index would leave the same loss mechanism reachable through other task files.

```yaml
chief_engineer_advice:
  outcome: A Pilot stage dispatch records its actual inputs in the stamp commit without consuming or destroying pre-existing task work.
  next_step: Add a shared clean-task-scope precondition before select_record, covering fresh dispatch, retry and advance; prove preservation with the real pinned builder and scoped state comparisons.
  material_risk: Another writer can change a scoped file or index entry after a one-time check; the proposed check is not a transaction lock.
  decision_needed: FO owns routing the repair and ensuring exclusive same-task writes during dispatch; no new Captain decision is needed within that boundary.
  defer:
    - Upstream Spacedock changes or a general multi-writer transaction system, unless exclusive same-task writes cannot be established.
    - Model and roster derivation, separate version preflights, and automatic follow-up records, as already excluded.
  recommendation: adjust
```

## Evidence and route

Read at product head `0d84d5d1b96fd674dba3a442d69c2e7898cceccd`, branch `spacedock-ensign/dispatch-build-writes-the-dispatch-record`, in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record`; its working tree was clean. Assigned base: `334d91e3165953b2ca7191e3308d80b6c02c4a99`. Workflow checkout remains `ba055b8a7a55a787ac989c4cef52d07dd75661ad`. Task state is `validation`, profile `pilot` (bounded real use).

The accepted task design and architecture decision record (ADR) 0070 retain the package wrapper and Spacedock's existing commit seam. ADR 0027 places structured checks at the write; ADRs 0014, 0037 and 0048 retain separate preflights, work ownership and First Officer (FO) publication authority. This advice changes repair sequencing within those boundaries; it grants no gate, validation, merge or release approval.

At `kc-dev-flow-2/scripts/dispatch_stage.py:46–54`, identical retry returns before the new-path index check; exclusive creation protects only a new record. At lines 58–65, cleanup removes an invocation-created record and its index entry if absent from HEAD. Neither protects other paths the builder stages. The supplied `validation-2/retry-index-probe.json` shows success with a changed index blob, unchanged working bytes and unchanged HEAD; the refusal control preserves all three. I inspected these artifacts, not reran the probe.

The validator's retained Spacedock 0.27.2 source, `/tmp/pr812-validation2.gfsHcD/spacedock-4d158a484ec73e184861067f8ed1e20087fdc26a`, confirms the broader boundary: `internal/dispatch/stamp.go:247–264` runs path-scoped `git add -A` before commit; `entityCommitPaths` at lines 322–335 includes the flat task file plus its companion directory, or the entire folder-form task directory. Inline stamping uses the same pattern at lines 217–235. Advance's later state commit also stages its entity unit (`internal/cli/state_sync.go:359–433`). Thus a staged-only edit to the task file, an older dispatch or a review/report file can encounter the same mechanism. That broader reach is a source inference, not a newly executed reproduction.

## One precondition before any write

Require **the entire resolved commit scope to be clean against HEAD in both the index and worktree**, with no pre-existing untracked content that the stamp would add. Define the scope from the builder's entity unit, including the companion directory that record creation will introduce; do not reduce it to the chosen record or `dispatch/`.

- For every tracked path in that scope, HEAD, the index and the worktree must agree in content, existence and Git-relevant type/mode. Refuse staged changes, unstaged changes, staged-only changes with worktree restored to HEAD, partial staging, additions, deletions, renames and unresolved index entries. Even equal staged/worktree edits differing from HEAD are refused: they are pre-existing work, not owned by this dispatch.
- For paths absent from HEAD, refuse existing index entries or nonignored untracked files in the scope. Independently require the selected new record path to be absent, retaining exclusive creation; ignored files or dangling symlinks must not let that path be overwritten. Reuse is allowed only after the scope passes, and still requires the current adding-commit and expected-input rules.
- Resolve the actual state repository and canonical task layout; use literal, NUL-safe path handling. Inspect both comparisons (index versus HEAD and worktree versus index), plus untracked paths. A command failure or unresolved scope is a hold, not an empty result. Do not rely solely on a status shortcut that can hide `assume-unchanged` or `skip-worktree` entries: verify their content explicitly or refuse those scoped entries. Refuse an unsupported path escape/type instead of declaring it clean.

Call this once after read-only argument/scope resolution and **before `select_record`**, including its directory creation, so fresh, reused, changed-input and `--advance` paths all pass it. On refusal, name the path and staged/unstaged condition, return nonzero with `dispatch_stage: dispatch not built;`, emit no envelope and invoke neither builder nor cleanup. Preserve the existing ownership restriction on cleanup; do not add automatic reset, stash or commit as a remedy.

Why this closes the pre-existing-state class: every admitted pre-existing scoped version is already represented by HEAD, and there is no additional staged or worktree version for staging to replace. The wrapper then creates only its own record before the builder's authorized task mutation. This is deliberately more conservative than allowing any state where index happens to equal worktree.

**Concurrency limit:** no check performed only once can guarantee preservation against a writer acting after it. Exclusive same-task ownership must last through build/commit/cleanup. Git's transient `index.lock` retry in `stamp.go:353–371` does not provide that ownership across the sequence. If FO cannot establish it, hold and return that concrete constraint for an isolated state checkout or coordinated upstream transaction design; another record-specific condition cannot solve it.

## Cost to normal use

A clean task and clean immediate retry keep the same invocation and numbering. Local Git reads add unmeasured latency and no network request. Pending edits anywhere in this task now hold dispatch, even when they could safely have been committed together; FO must have their owner preserve/reconcile and intentionally commit them first. In particular, blindly running `state commit` on divergent staged/worktree content would repeat the loss and is not a safe recovery instruction. Do not require unrelated tasks or the whole code checkout to be clean. Explain the remedy in the refusal diagnostic; no new workflow gate or word-budget increase is needed.

## Proof required for the next repair

Extend the existing real-binary suite with a table-driven preservation matrix; retain the accepted success and failure tests.

1. **Locations and routes:** apply dirty-state cases to the new record path, reused committed record, older dispatch, task frontmatter and nested companion report. Exercise flat and folder-form tasks, fresh dispatch, immediate retry, new round and advance. A clean selected record with a dirty sibling must hold.
2. **States:** cover index-only change, worktree-only change, index/worktree equal but different from HEAD, index/worktree each different, and the reported worktree-equals-HEAD case. Include untracked files, staged additions with/without a worktree file, staged/unstaged deletions, renames across the scope boundary, conflicts and type/mode changes. Cover the special flags and literal-path cases used by the implementation. This derives cases from the three representations, rather than adding only another retry fixture.
3. **Refusal oracle:** snapshot HEAD, all scoped file bytes/existence/modes, semantic index entries (blob, mode, stage and relevant flags), and outside-scope sentinel state. Assert nonzero, named diagnostic, empty stdout, no builder call, no new record or frontmatter change, and preservation of every snapshot. Run dirty cases with otherwise valid inputs so refusal cannot be credited to the record checker.
4. **Allowed and recovery paths:** real 0.27.2 builder commits matching inputs from a clean scope; immediate retry reuses; changed inputs or a later commit mint the next number; advance commits before its envelope. Unrelated staged and unstaged task work stays intact and outside the dispatch commit. An owner-reconciled/committed task becomes dispatchable. Checker failure, staged-then-failed build, and committed-then-assembly failure retain the existing cleanup/retry contracts.
5. **Falsifiers and integration:** remove the guard; omit the index comparison; omit worktree/untracked inspection; narrow scope to the selected record or dispatch directory; place the guard after record creation; bypass it on retry or advance. Each mutant must fail the matching preservation assertion. Run the unchanged acceptance chain plus these cases on the new exact head, then obtain the existing hosted real-binary check. Use a controlled overlapping-writer probe to establish any concurrency claim; otherwise retain the exclusive-writer limitation explicitly.

## Unverified and handoff

This is read-only engineering advice, not independent validation of a repair. I ran no tests or Git writes and changed only this report. I inspected the named task, repair dispatch, evidence, candidate source/tests and retained upstream source; I did not independently refetch that source or refresh GitHub review/CI state. The latest supplied validation records hosted acceptance criterion 8 as unmet after an HTTP 504 download failure; that is missing hosted evidence, not a proven product defect. CI cost per PR remains unmeasured; keep existing narrow triggers. Current worker execution, concurrent-writer safety, post-release adoption and delivery remain unverified. FO owns repair dispatch, exact-head revalidation, hosted evidence and committing this report.
