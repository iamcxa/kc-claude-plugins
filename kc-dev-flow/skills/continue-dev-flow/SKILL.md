---
name: continue-dev-flow
description: Use when an adopted repository has an approved sprint or active work item and should autonomously resume or select the next committed item while preserving its local gates and authority boundaries.
---

# Continue Dev Flow

Move an approved sprint toward verified outcomes with the smallest sufficient
route. The procedure is the same in Claude Code and Codex; local repository
instructions decide the concrete tracker, runtime, and evidence tools.

## Load only adopted policy

1. Discover the workflow README named by the nearest repository instructions and
   read its `## Local Profile`. If multiple candidates remain, stop and name the
   ambiguity. This profile is the repository binding and must bind project
   context, work items, iteration, execution state, delivery, gate verdicts, and
   scope changes; observation may be `none`. If a required role is absent, use
   `adopt-dev-flow` before proceeding.
2. Read the repository's vendored `_mods/kernel.md` completely. Do not fall back
   to the installed package reference: that would silently apply policy the
   repository has not adopted.
3. Recheck branch/worktree identity, shared-state ownership, remote delivery
   state, and fresh instructions. Never inherit another session's validation.
4. Resolve the active work item and current stage from live work-item,
   iteration, and execution-state authority. Read that stage's `Policy mods`
   declaration and then read only the named local `_mods/` files.
5. If the local kernel, a named policy mod, required authority, or shared-state
   owner is missing or ambiguous, stop with a named adoption/refit requirement.
   Installed source is never a runtime substitute.

## Advance the work

1. Ask the work-item and iteration authorities for the active item. If none is
   active, select the next committed work item by the repository's declared
   sprint order and dependency rules. Do not enumerate the execution-state tree
   on an ordinary continuation; read only the product-authority paths needed to
   resolve that route.
2. If no committed item exists, report that the sprint needs scheduling. Do not invent or schedule work to keep the agent busy.
3. Use the defect route only for a bounded known defect with a mechanical
   acceptance test; otherwise use the normal lifecycle. Recover existing
   abstractions before greenfield planning.
4. Within approved scope, implement, test, repair rejected evidence, and advance
   reversible green gates without asking the captain to repeat approval.
5. Require exactly one fresh-context EM verdict for every ideation and validation gate.
   A defect route that skips ideation still receives the validation verdict.
   Implementation opens no reviewer loop: when an approved premise changes, return
   it to its owning stage instead of adjudicating it inside implementation.
   Multi-model review is optional. Ask the captain only when that EM records it as
   `recommended` for a contested, irreversible, low-confidence, or unresolved
   call; otherwise record `not_needed` and proceed. Reviewer delay or captain
   silence is not approval. Exact-head CI/runtime evidence remains delivery
   evidence.
6. When every acceptance criterion has fresh validation and the repository's
   delivery authority is satisfied, durably terminalize/archive the work item,
   then continue without a captain pause to the next committed item.

Ask the captain only for new scope, an irreversible choice, acceptance of a
known red residual, or new spending/permission authority. Tool setup failure,
reviewer silence, and missing evidence are not passes.

## Harvest improvements only when explicitly requested

The resolved product route comes first. Only when the current invocation
explicitly asks to harvest unseen debrief evidence or prepare a dev-flow
improvement, read `../../references/improvement-harvesting.md` completely and
follow it before resuming the already-resolved product route. A debrief directory,
cursor, or old candidate is not a trigger.

Do not inspect `_debriefs/` or `_improvements/` on an ordinary continuation, and
perform no improvement-state reads or writes. If atomic improvement-state access
is unavailable during an explicit harvest, report `UNKNOWN` for that state and
continue the resolved product route; improvement work never blocks product work.
