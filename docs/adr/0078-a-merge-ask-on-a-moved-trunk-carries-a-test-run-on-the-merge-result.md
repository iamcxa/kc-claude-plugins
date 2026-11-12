# 0078. A merge ask on a moved trunk carries a test run on the merge result

Date: 2026-11-12

## Status

Accepted

## Context

PR #841 passed on its own head but, after #843 landed, their combined tree failed
one of 226 design-surface tests. Its merge ask disclosed that acceptance had not
been rerun, without a hold. The task merge-ask-tests-the-merge-result rebuilt the
landed tree and measured 580 seconds for the 25 local unit scripts, excluding the
three requiring pinned Spacedock. Trunk had diverged for 24 of 40 sampled PRs.

## Decision

**Words:** 「五份都核准（建議）」 — Captain, host question dialog, 2026-11-12,
ideation gate of merge-ask-tests-the-merge-result.

**Asked:** 「決定：實驗的五份設計要不要都核准並開始實作。我建議五份都照各自設計的建議核准。」
The bound question included: 「三、合併後結果先測：main 的頂端不是 PR 的祖先時就要求一次測試紀錄，量到約六成的 PR 會觸發、整組測試一次約 10 分鐘（只量一次）；流程說明加一行指定要跑的指令。」
These are verbatim excerpts of the task's ideation gate record, not a new grant.

**Options considered:**
- D1: require a record matching the workflow README `merge-test:` command (chosen),
  rather than letting FO choose narrower tests at each ask.
- D2: trigger when trunk's tip is not an ancestor of the head (chosen), rather than
  recording the dispatch-time base and ignoring divergence before dispatch.
- D3: demonstrate the passing replay on the same head at its earlier CI trunk
  (chosen); the honest run on the actual ask trunk fails and must hold.
- GitHub strict branch protection or a merge queue: not chosen; repository-setting
  changes remain outside this task's authority.

**Recommended:** D1, D2 and D3 above, as the approved design recommends.

**Protects:**
- `kc-dev-flow-2/scripts/delivery_gate.py` — `merge_result_problem`, the command and trunk match at the merge ask

For a diverged or behind head, `check` requires a passing merge-result record at
the head and current trunk, with the configured command. Without that run, FO may
proceed only by putting `Merge result: not run: <reason>` in the question the
Captain reads; `question` checks that placement for a not-run ask record.
`merge-run` builds with `git merge-tree --write-tree`, runs in an archived temporary
tree, saves the exit and log, and removes that temporary tree. A conflict exits 2.
The merge-result point shares the existing display cap; ask records retain its
record name or `not run`. An ancestor trunk adds no merge-result requirement.

## Consequences

The workflow adds one command line; adopters add theirs at their next sync. Until
then, moved-trunk asks there need the explicit not-run line. The adopted command
runs the 25 local unit scripts; the three pinned-Spacedock integration scripts
remain separate checks. No CI definition or repository setting changes.

The initial measurement implies about six local minutes per PR averaged over
that sample, not CI billing minutes. The run binds the trunk observed at check
time; it cannot prevent trunk moving again before merge. Records are trusted,
not authenticated or recomputed by check. A live green ask remains unproven
until an eligible PR after release; D3's replay does not establish that event.
Reopen if these limits permit another observed combined-tree failure to pass
without the Captain seeing the omitted run.
