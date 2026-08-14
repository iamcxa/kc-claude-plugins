---
name: continue-dev-flow
description: Resume an adopted repository's approved sprint or active item while preserving local gates and authority.
---

# Continue Dev Flow

Claude Code and Codex continue by the smallest sufficient route using
repository-bound authority.

## Load only adopted policy

1. Read the workflow README named by nearest repository instructions; never enumerate a workflow parent to discover it.
   Read `## Local Profile`; name ambiguity. It binds local authorities and
   optional observation. Use `adopt-dev-flow` when a required role is absent.
2. Read vendored `_mods/kernel.md` completely; installed policy never substitutes.
3. Recheck branch/worktree, shared-state ownership, and remote delivery state.
   Never inherit another session's validation.
4. Resolve the active work item and stage from live authority. Read that stage's
   `Policy mods`, then read only the named local `_mods/` files.
5. A missing local kernel, selected mod, authority, or owner requires a named
   adoption/refit requirement, not installed fallback.

Reuse the already-loaded instruction chain; batch the workflow README and complete vendored kernel;
batch iteration, identity, ownership, and delivery reads. Defer project context
until execution; a stop-before-action invocation does not read it.

## Advance the work

1. Read iteration authority first. If it declares no active or committed item,
   report scheduling immediately; do not inspect work-item or execution state.
   Otherwise read its exact bound entity path; never discover it with `rg --files`, `find`, `ls`,
   or a tree walk. Select the next committed work item
   by declared order when none is active. Do not enumerate the execution-state tree.
2. With no committed item, report that scheduling is needed. Do not invent or schedule work.
3. At normal ideation entry, perform the receipt gate. Re-read the exact work item and its `## Work profile receipt`.
   Reuse it when valid and unchanged. If missing or its basis changed, invoke
   `kc-dev-flow:choose-work-profile`; the authorized actor records, syncs, and
   re-reads it. Only after the committed receipt is re-read may inherited criteria be normalized or acceptance criteria be expanded.
   Do not reopen later stages without a
   promotion trigger; bounded mechanical defects keep their valid skip.
4. Use the defect route only for a known one-seam defect with a mechanical test;
   otherwise use the normal lifecycle. Recover existing abstractions first.
5. Implement, test, repair rejected evidence, and advance reversible green gates
   within approved scope without repeated captain approval.
6. Require exactly one fresh-context EM verdict for every ideation and validation gate;
   defect routes keep validation. Implementation opens no unbounded or adjudicating reviewer loop:
   return changed premises. Multi-model review is optional; ask the captain only
   when EM records `recommended`; otherwise record `not_needed`. Reviewer
   silence is not approval. Exact-head evidence remains delivery evidence.
7. After fresh validation and satisfied delivery authority, durably
   terminalize/archive, then continue without a captain pause to the next item.

At implementation exit, a Local Profile declaration of `review_convergence`,
`observe`, and `roborev` loads its local contract after tests, exact tip, and
changed-file map. `../../references/roborev-implementation-exit.md` is the
adoption source, not runtime fallback. Omission performs no RoboRev probe or
invocation. The result remains input to fresh validation.

Ask the captain only for new scope, irreversibility, accepted red residuals, or
new spend/permission. Setup failure, reviewer silence, and missing evidence are
not passes.

## Harvest improvements only when explicitly requested

Product routing comes first. Only an explicit request to harvest unseen evidence
or prepare an improvement loads `../../references/improvement-harvesting.md`.
Before opening the harvest reference or enumerating improvement evidence, read
the selected item and name its stage and first product action. Stored evidence
is not a trigger.

Do not inspect `_debriefs/` or `_improvements/` during ordinary continuation. If
atomic improvement-state access is unavailable during explicit harvest, report
`UNKNOWN` and continue product routing; improvement work never blocks it.
