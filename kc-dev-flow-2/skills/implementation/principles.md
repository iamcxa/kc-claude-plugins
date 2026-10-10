# Implementation principles

Work on the approved integrated outcome and record material changes to assumptions.
Use the smallest working mechanism, project conventions and existing tools.
Exercise changed behavior at its meaningful failure boundary; preserve evidence
and exact artifact identity. Before exit, compare every added or retained file,
dependency, abstraction, test and comment with the accepted goal, named falsifier,
safety boundary or required lifecycle obligation. Apply the goal check without
the candidate change and record the named failure or absence it exposes, at the
selected profile's depth. Compare removals on the same basis; absence of a consumer
alone does not authorize deletion. Cut unmapped surfaces within approved scope,
prefer a materially smaller equivalent route, and keep repeated explanations in
one home. Record temporary scaffolding's concrete removal condition when added;
an enduring guard instead names its invariant. Counts are diagnostic, not quotas.
Before reporting completion, run
`python3 <package>/scripts/comment_ratio.py <base> HEAD --workflow-dir <workflow-dir>`
and report its output with the stage report. Exit 1 is a trim: cut the comments
above the maximum, and cite an ADR or a greppable symbol instead of task numbering,
review provenance, a PR or issue number or a `file:line`. Exit 2 is a configuration
error that returns to FO.
When the task has a `## Number guards` section, use only the numbers it lists, run
`python3 <package>/scripts/number_guards.py check` as that section states and report its
output and base SHA; a migration on the base branch or recorded as applied is frozen,
so it is exempt from comment trims and from cutting unmapped surfaces.
One number per kind per task; a task needing more returns to FO. A migration on the base
branch must not change, comment-only edits included; the fix for an R1 or R2 finding is
reverting the edit and writing a new migration.
Do not use `git stash`: every worktree and session of a repository shares one
stash stack. Set work aside with a commit.
Do not invoke local fallback, push the trunk, merge, or clean up an owned worktree unless
the specific action is authorized.

When feedback requests repair, change the approved defect scope and identify
what needs rechecking. Return scope/profile changes or unresolved inputs to FO.
Report changes, evidence, limits and remaining work in the SD stage report;
a worker report is not a gate approval or stage transition.

Write one file per decision, `docs/adr/NNNN-short-title.md`, in the ADR format of the
kc-dev-flow-2 package's `references/adr-template.md`, with the decider's own words, the
options considered and the option recommended inside Decision;
`<package>/scripts/adr_lint.py --require` refuses a required record without the
recommended line. Create `docs/adr/` with this record if it is absent. A decision
document that predates this format may stay as one record marked `Status: Legacy`.
This is not the gate `resolution.reason` or the SD stage report. The implementation
worker writes the record into the candidate and names the ADR numbers it added or
changed in its report.


## Existing-code capability check

Apply only when existing-code work adds, replaces or removes a capability or
abstraction, or claims one missing. Skip greenfield work, repair of an already
named broken seam, and mechanical edits. POC performs this check before coding
when applicable, without adding ideation; do not repeat a completed design audit.
Trace the affected journey inside a named boundary. Distinguish completeness
(working through the journey, unit-only, broken seam, stub or not found) from need
(goal/consumer/contract, falsifier, safety or lifecycle obligation, unknown, or
none observed). Safety/lifecycle needs can exist without a consumer. Before any
missing/no-consumer claim, use two distinct bounded searches and state exclusions
and unknowns, including applicable external, dynamic, manual, compatibility or
dormant consumers.
Unit checks do not prove wiring; keep claims bounded by the observation that
could disprove them. Prefer use or repair, build only what is shown missing, and
send unapproved removal/redesign or an unplanned surface to FO for the scope
owner's decision.
Use the existing design/report; this adds no receipt, schema or audit artifact.
