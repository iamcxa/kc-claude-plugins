---
name: dev
description: Start or resume kc-dev-flow-2 work by resolving the project, task, approved profile and scope, then handing orchestration to Spacedock First Officer.
---

# Dev

Invocation: `kc-dev-flow-2:dev`

Read the [framework](../../README.md). This is a start/resume entry, not a worker
stage or a second workflow controller. Claude's packaged command is
`/kc-dev-flow-2:dev`; bare `/dev` is not a promised cross-host alias.

Resolve the absolute project root, explicit workflow directory and intended work
item from the request and authoritative project/task records. Reuse established
context; do not guess between projects or tasks. Read applicable project
conventions and the existing context needed for the requested work.

For existing work, preserve its recorded variant/profile, approved outcome,
scope, non-goals and stop condition. Read current state, reports and delivery
status instead of assuming a prior conversation is current. An invalid profile,
conflicting records or missing authority holds the dependent action; return only
the unresolved decision to the user. Do not restart approved design or ask again
for an unchanged selection.

For new work without a profile selection, establish the intended outcome and
recommend a profile using the framework's intended use and applicable shared
profile principles. Ask the user to select it before profile-dependent work.
An explicit valid selection is sufficient; FO records it with the variant in
the work item through the existing workflow. Recommendation is not selection.

Hand the resolved project root, explicit workflow directory, work item, approved
selection/scope and bounded outcome to `spacedock:first-officer`. Retain that
workflow directory as `--workflow-dir` on SD commands; cwd alone is not the
binding. If FO is already active, continue there. SD owns stage selection, live
worker availability, dispatch, reports, gates and recovery; a resumed FO does
not establish that its old worker still exists. Stage skills own profile routing
and load the selected references in each worker's context.

If the project has not adopted this variant, route setup through SD's existing
configuration/adoption responsibility before dispatch. Invoking this entry does
not migrate an old variant, rewrite a workflow or install a package. Keep existing
work on its recorded variant unless a migration is explicitly approved. This
entry grants no new repair, approval, delivery or route-exception authority.
