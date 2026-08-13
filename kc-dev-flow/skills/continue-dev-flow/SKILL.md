---
name: continue-dev-flow
description: Resume an adopted repository's approved sprint or active item while preserving local gates and authority.
---

# Continue Dev Flow

Claude Code and Codex continue by the smallest sufficient route using
repository-bound authority.

## Load only adopted policy

1. Read the workflow README named by nearest repository instructions; never enumerate a workflow parent to discover it.
   Read `## Local Profile` and name
   ambiguity. It binds project context, work items, iteration, execution state,
   delivery, gate verdicts, and scope changes; observation may be `none`. If a
   required role is absent, use `adopt-dev-flow`.
2. Read vendored `_mods/kernel.md` completely; installed policy never substitutes.
3. Recheck branch/worktree, shared-state ownership, and remote delivery state.
   Never inherit another session's validation.
4. Resolve the active work item and stage from live authority. Read that stage's
   `Policy mods`, then read only the named local `_mods/` files.
5. A missing local kernel, selected mod, authority, or owner requires a named
   adoption/refit requirement, not installed fallback.

Minimize calls without skipping authority: reuse the already-loaded instruction
chain; batch the workflow README and complete vendored kernel; batch iteration,
identity, ownership, and delivery reads. Defer project context until product
execution; a stop-before-action invocation does not read it.

## Advance the work

1. Read iteration authority first. If it declares no committed item, report
   scheduling immediately; do not inspect work-item or execution state.
   Otherwise request the active item and read its exact bound entity path; never
   discover it with `rg --files`, `find`, `ls`, or a tree walk. If none is active,
   select the next committed work item by declared order and dependencies.
   Do not enumerate the execution-state tree.
2. With no committed item, report that scheduling is needed. Do not invent or schedule work.
3. At normal ideation entry, perform the receipt gate.
   Re-read the exact work item and its `## Work profile receipt`.
   If it is valid and its basis is unchanged, consume
   it without another question. If it is missing, or the audience, lifespan,
   mutation boundary, authority need, or operational commitment changed, invoke
   `kc-dev-flow:choose-work-profile`. The authorized work-item actor compares,
   records, syncs, and re-reads the exact receipt.
   Only after the committed receipt is re-read may inherited criteria be normalized or acceptance criteria be expanded.
   Tasks already beyond ideation are not reopened without a promotion trigger;
   the bounded mechanical-defect route keeps its valid skip.
4. Use the defect route only for a known one-seam defect with a mechanical test;
   otherwise use the normal lifecycle. Recover existing abstractions first.
5. Implement, test, repair rejected evidence, and advance reversible green gates
   within approved scope without repeated captain approval.
6. Require exactly one fresh-context EM verdict for every ideation and validation gate.
   A defect route that skips ideation still receives the validation verdict.
   Implementation opens no reviewer loop: return changed premises to their owning
   stage. Multi-model review is optional; ask the captain only when EM records
   `recommended` for a contested, irreversible, low-confidence, or unresolved
   call; otherwise record `not_needed` and proceed. Reviewer delay or captain
   silence is not approval. Exact-head evidence remains delivery evidence.
7. After fresh validation and satisfied delivery authority, durably
   terminalize/archive, then continue without a captain pause to the next item.

Ask the captain only for new scope, irreversibility, accepted red residuals, or
new spend/permission. Setup failure, reviewer silence, and missing evidence are
not passes.

## Harvest improvements only when explicitly requested

Product routing comes first. Only when this invocation explicitly asks to
harvest unseen debrief evidence or prepare an improvement, read
`../../references/improvement-harvesting.md` completely and follow it before
resuming product work. Before opening the harvest reference or enumerating improvement evidence,
read the selected work-item record and name its item,
stage, and first product action. A debrief directory, cursor, or old candidate is
not a trigger.

Do not inspect `_debriefs/` or `_improvements/` during ordinary continuation. If
atomic improvement-state access is unavailable during explicit harvest, report
`UNKNOWN` and continue product routing; improvement work never blocks it.
