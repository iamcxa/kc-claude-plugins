# 0079. Dispatch close-out retains public evidence and removes scratch

Date: 2026-11-12

## Status

Accepted

## Context

Finished dispatches left large temporary checkouts and reports cited temporary
paths that later disappeared. The task's ideation gate selected a dispatch-owned
scratch root and close-out command; amendment 1 permits this decision record.
ADR 0070 and ADR 0074 already place dispatch writing in dispatch_stage.py.
ADR 0072 keeps cited evidence readable on the state branch.

## Decision

**Words:** 「五份都核准（建議）」 — Captain, host question dialog,
2026-11-12, ideation gate attempt 1 of
`dispatch-close-out-archives-evidence-and-removes-scratch` on `spacedock-state/dev2`.

The accepted question's cleanup item was:
「五、收尾清理：每次派工有自己的暫存資料夾，結束時把報告引用的證據存進任務資料夾、超過 256 KiB 的檔才壓縮、然後刪掉暫存；私人 repo 的證據一律不存，只留一行重現指令；允許不問就強制移除暫存資料夾裡的工作目錄並記下遺失的檔案數。」

**Options considered:**
- D1: retain evidence in the state branch's task folder (chosen), rather than
  merge it into the product branch or create separate evidence branches.
- D2: retain plain files and gzip each file over 256 KiB (chosen), rather than
  hide the evidence in one tarball.
- D3: do not archive private evidence; keep a reproduction command (chosen),
  rather than retain a separate private scratch store.
- D4: force-remove registered worktrees inside the dispatch root and record
  their uncommitted-file counts (chosen), rather than leave dirty scratch behind.

**Recommended:** D1 through D4 as chosen above, accepted by the ideation gate.

**Protects:**
- `kc-dev-flow-2/scripts/scratch.py` — notes_for privacy instruction, evidence compression and close worktree removal

Each dispatch owns `/tmp/dev2/<origin-repository-name>/<slug>/<record>`;
message continuations share their original dispatch's root. Cited public evidence
belongs in `evidence/<record>/` in the task folder. The close command checks the
record and derived root, refuses symlinked roots or parents, applies the 256 KiB
compression threshold and 1 MiB retained-folder cap, and saves original SHA-256
digests. It removes scratch after those checks and logs the removal and dirty
worktree file counts. Private evidence is deleted with scratch; the report keeps
`Not archived (private): <what>; reproduce: <command>`.

## Consequences

State-branch evidence is public, small files stay plain, and private evidence
requires a new run. Forced scratch removal can lose uncommitted work without a
question; the removal record supplies the count afterwards. The idle sweep
prompts older, merged or archived dispatch roots; a newest root left by a worker
can remain while its task waits at a gate. Other sessions' scratch and branch
retention remain outside this decision.
