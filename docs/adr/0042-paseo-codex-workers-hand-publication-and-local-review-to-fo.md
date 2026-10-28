# 0042. Paseo Codex workers hand publication and local review to FO

Date: 2026-10-28

## Status

Accepted

## Context

Paseo Codex workers in batches 7 and 8 could commit locally while GitHub API
and local RoboRev access were unavailable. Their First Officer (FO) carried
publication and review. A worker also inherited the FO workspace rather than
its assigned worktree. The task paseo-codex-dispatch-practice records these
observations, the supported placement routes and the approved extension text.
ADR 0015 assigns early Draft pull request (PR) creation to the implementation
worker; this host-specific exception needs its own ruling.

## Decision

**Words:** 「照建議」 — Captain, chat, 2026-10-28, at the batch-9 ideation
sitting, recorded in the task's ideation gate and Captain amendment 1.

**Asked:** 「決定：五張全照建議（四張准並照上面刪減，一張暫緩）；如果哪張要改，直接說。」
The accepted row was 「| 用 Paseo 派 Codex 工作者的做法 | 准，同時在本工作流啟用 paseo 外掛 | 本工作流目前沒列 paseo，沒列的話新寫的規則不會被任何人讀到；另寫一份 ADR，記下「FO 代為推送和開 PR」這個例外 |」.
The gate question explicitly coupled approval with listing `paseo` in this
workflow's `extensions:` and narrowing ADR 0015: the worker commits locally;
FO pushes, opens the PR and runs RoboRev.

**Options considered:**
- Adopt the scoped exception, enable paseo here and record the ADR (chosen).
- Keep ADR 0015's worker publication owner in this environment, retaining the
  observed access failures.
- Leave implementation at a local commit and create the PR only at delivery,
  losing the early review order retained by the accepted design.

**Recommended:** The scoped Paseo Codex exception, its decision record and
this workflow's explicit paseo selection, as the Captain accepted.

**Protects:** none

For a workflow listing paseo and a Codex worker dispatched through Paseo,
use `kc-dev-flow-2/extensions/paseo/EXTENSION.md`'s procedure. The worker starts
in the assigned worktree, commits the product candidate locally and hands FO
the branch, base, full candidate SHA and prepared PR text. FO reconciles that
candidate with any existing PR, then uses an applicable Captain publication
grant to push and open or update its Draft PR before fresh validation. FO runs
the existing exact-head RoboRev gate when roborev is listed; incomplete review
or a head mismatch holds the dependent step. Repairs need fresh head evidence.

This narrows ADR 0015's delivery actor for this enabled host/provider case;
other hosts retain their delivery owner. It grants no publication, ready or
merge authority. Spacedock's generated prompt, runtime fields, immediate spawn
order, independent validation, CI and Captain merge control remain. Split-root
state commits and sync remain the ensign's obligation. Placement does not widen
sandbox permissions or establish network or protected-metadata access.

## Consequences

FO gains publication and local review work, and fresh workers need supported
workspace placement. The optional extension's reading load increases; no time,
permission-prompt or CI-cost saving was measured. Listing paseo here enables
the procedure after the normal adoption path; a release alone does not update
other workflows. Native placement and exact-head publication/review still need
observed evidence. Revisit if the supported placement route cannot preserve
the dispatched fields or changes in access make this handoff unnecessary.
