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

## Consume debrief evidence once

Before routing product work, resolve one authoritative `_debriefs/` home through
execution-state authority. If no debrief home is bound, treat that as no unseen
debrief: perform no analysis, write no improvement state, and continue to product
routing. If multiple candidates remain, stop with `UNKNOWN`, name the ambiguity,
and require adoption/refit before continuing. When one home resolves, read its
sibling `_improvements/state.yaml` when present; absence means there is no cursor
yet. This is derived coordination state with the following minimum shape:

```yaml
schema: kc-dev-flow-improvements/v1
newest_processed_debrief: <immutable debrief name or none>
last_run:
  consumed: [<debrief names>]
  skipped_superseded: [<older unseen debrief names>]
  disposition: none | repository-local | reusable-kernel
  candidate: <work-item or handoff reference, or none>
```

1. Consider only immutable debriefs newer than `newest_processed_debrief`. If
   there is no cursor, take at most the most recent three in the authority's
   stable order. When more than three are unseen, record the older names under
   `skipped_superseded`; this bounded scan deliberately retires them instead of
   queueing them for a later launch. If there is no unseen debrief, perform no
   analysis and do not rediscover or re-propose an older issue.
2. From the consumed set, classify at most one narrow candidate as
   **repository-local** or **reusable kernel**. Its reviewable record names the
   observations, expected value, cost, disproof hook, duplicate search, and
   disposition.
3. Advance `newest_processed_debrief` to the newest consumed record even when no
   candidate is proposed. Record the consumed names and disposition. This
   prevents the next launch from treating the same evidence as new.
4. Use the execution-state authority's existing single-writer transaction or
   compare-and-swap for the cursor update. Inside the same transaction that
   writes the new state, resolve the debrief home again and verify the locator is
   unchanged, then re-read and compare the live cursor. A home or cursor mismatch
   aborts the write and recomputes from live authority; if the authority provides
   neither atomic comparison nor exclusive ownership, report `UNKNOWN`, skip the improvement write, and continue to product routing.
5. Route a repository-local candidate to the existing work-item authority. A
   reusable kernel candidate becomes a sanitized handoff to the installed
   dev-flow source. Detection does not create or schedule a task, grant sprint
   membership, merge anything, or pause product work.

## Advance the work

1. Ask the work-item and iteration authorities for the active item. If none is
   active, select the next committed work item by the repository's declared
   sprint order and dependency rules.
2. If no committed item exists, report that the sprint needs scheduling. Do not invent or schedule work to keep the agent busy.
3. Use the defect route only for a bounded known defect with a mechanical
   acceptance test; otherwise use the normal lifecycle. Recover existing
   abstractions before greenfield planning.
4. Within approved scope, implement, test, repair rejected evidence, and advance
   reversible green gates without asking the captain to repeat approval.
5. Require a fresh-context EM/reviewer for judgment-heavy ideation and validation
   verdicts. Exact-head CI/runtime evidence remains delivery evidence.
6. When every acceptance criterion has fresh validation and the repository's
   delivery authority is satisfied, durably terminalize/archive the work item,
   then continue without a captain pause to the next committed item.

Ask the captain only for new scope, an irreversible choice, acceptance of a
known red residual, or new spending/permission authority. Tool setup failure,
reviewer silence, and missing evidence are not passes.
