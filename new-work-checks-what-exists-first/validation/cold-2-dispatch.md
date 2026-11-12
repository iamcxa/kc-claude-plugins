## First action

Read this dispatch file directly and treat its content as your stage-specific assignment.

The outer fresh-worker prompt invokes `$spacedock:ensign` before this pointer. The installed skill supplies the shared ensign discipline (stage-report format, polling, worktree ownership, and completion signal protocol); this file supplies the stage-specific assignment. Do not try to invoke a Claude skill wrapper; Codex dispatch uses this file pointer after the outer bootstrap.

You are working on: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file

Stage: ideation

This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state add /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state/design-surfaces-task-dir-crash.md && git -C /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state commit -m "..." -- /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state/design-surfaces-task-dir-crash.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. This state checkout has no `origin` remote — commit path-scoped locally as above; do NOT run `git push`/`git pull` (there is no remote to sync). State is local-only and will not survive on a shared remote until an `origin` is configured.

Read the entity file at /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state/design-surfaces-task-dir-crash.md for the current spec.

Package root: /tmp/validate-new-work-checks-20261113/cold-replay-2-2/candidate/kc-dev-flow-2
TEST HARNESS (isolated replay): read /tmp/validate-new-work-checks-20261113/cold-replay-2-2/candidate/kc-dev-flow-2/skills/ideation/SKILL.md and follow it, resolving every package path against /tmp/validate-new-work-checks-20261113/cold-replay-2-2/candidate/kc-dev-flow-2. The CODE root is /tmp/validate-new-work-checks-20261113/cold-replay-2-2/candidate, exported from the selected revision and intentionally without Git metadata. The state snapshot is /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state. Work read-only; do not change state, product, private repositories, Git metadata or remotes, and do not start servers, browsers or databases. Save your observations and proposal as separate files in /tmp/validate-new-work-checks-20261113/cold-replay-2/subject-output as you work. No application unit/integration/e2e run is required for this ideation. Completion is one final reply to your caller; do not contact other sessions. These harness limits override generated commit/push instructions.


### Completion checklist

Prepare the smallest ideation proposal for the assigned task Scope. Do not implement, write another task, contact another session or perform external writes.

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /tmp/validate-new-work-checks-20261113/cold-replay-2/wf --stage ideation


### Completion Signal

When you finish (after all commits and stage report writes are done), send one concise final message in this Codex worker thread:

    Done: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file completed ideation. Report written to /tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state/design-surfaces-task-dir-crash.md.

The first officer observes completion through the Codex final-status notification in the FO mailbox. Do not emit a Claude `SendMessage` call; the Codex mailbox notification is the completion signal.