---
name: continue-dev-flow
description: Use when an adopted repository has an approved sprint or active work item and should autonomously resume or select the next committed item while preserving its local gates and authority boundaries.
---

# Continue Dev Flow

Move an approved sprint toward verified outcomes with the smallest sufficient
route. The procedure is the same in Claude Code and Codex; local repository
instructions decide the concrete tracker, runtime, and evidence tools.

## Start from live authority

1. Read the repository's dev-flow binding and `../../references/kernel.md`.
   If no binding exists, use `adopt-dev-flow` before proceeding.
2. Recheck branch/worktree identity, shared-state ownership, remote delivery
   state, and fresh instructions. Never inherit another session's validation.
3. Ask the work-item and iteration authorities for the active item. If none is
   active, select the next committed work item by the repository's declared
   sprint order and dependency rules.
4. If no committed item exists, report that the sprint needs scheduling. Do not invent or schedule work to keep the agent busy.

## Advance the work

- Use the defect route only for a bounded known defect with a mechanical
  acceptance test; otherwise use the normal lifecycle.
- Recover existing abstractions before greenfield planning.
- Within approved scope, implement, test, repair rejected evidence, and advance
  reversible green gates without asking the captain to repeat approval.
- Require a fresh-context EM/reviewer for judgment-heavy ideation and validation
  verdicts. Exact-head CI/runtime evidence remains delivery evidence.
- When every acceptance criterion has fresh validation and the repository's
  delivery authority is satisfied, durably terminalize/archive the work item,
  then continue without a captain pause to the next committed item.

Ask the captain only for new scope, an irreversible choice, acceptance of a
known red residual, or new spending/permission authority. Tool setup failure,
reviewer silence, and missing evidence are not passes.

## Improve the flow without hijacking the sprint

Capture repeated process friction as evidence. At each sprint boundary, if the
evidence repeats, remind the captain once and classify at most one proposal:

- Route a **repository-local** defect to the repository's existing work-item
  authority. Creating a proposal does not schedule it into the sprint.
- Route a **reusable kernel** defect to the source declared by
  `upstream_contribution`. Remove adopter-specific details and search for an
  existing issue or change first.

When the mode is absent or `propose_only`, produce a reviewable proposal or
patch handoff. When it is `pull_request`, use an isolated branch, add a failing
contract or behavior test first, implement the smallest portable repair, run
the upstream gates, and open a pull request.

Do not merge the upstream pull request. Do not add it to the adopter's sprint
or pause product work unless the existing flow makes safe delivery impossible.
With no repeated friction, add no reminder ceremony.
