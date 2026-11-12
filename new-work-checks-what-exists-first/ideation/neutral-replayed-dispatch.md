## First action

Read this dispatch file directly and treat its content as your stage-specific assignment.

The outer fresh-worker prompt invokes `$spacedock:ensign` before this pointer. The installed skill supplies the shared ensign discipline (stage-report format, polling, worktree ownership, and completion signal protocol); this file supplies the stage-specific assignment. Do not try to invoke a Claude skill wrapper; Codex dispatch uses this file pointer after the outer bootstrap.

You are working on: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file

Stage: ideation

This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state add /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state/design-surfaces-task-dir-crash.md && git -C /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state commit -m "..." -- /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state/design-surfaces-task-dir-crash.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. Then push the state branch so peers see your entity/report: `git -C /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state push origin spacedock-state/wf`; on a non-fast-forward rejection, `git -C /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state pull --rebase origin spacedock-state/wf` then re-push.

Read the entity file at /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state/design-surfaces-task-dir-crash.md for the current spec.

Package root: /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/package/kc-dev-flow-2
Controlled same-worker replay, not independent validation. Observe only; the original caller retains its authority and will save the result in its own task evidence. Do not mutate this replay task or any remote.
TEST HARNESS (isolated replay): do not invoke the kc-dev-flow-2 skill through the Skill tool; read /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/package/kc-dev-flow-2/skills/ideation/SKILL.md and follow it, resolving every package path against /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/package/kc-dev-flow-2. Do not run the application unit, integration or e2e suites and do not start servers, databases or browsers; say in the report they were not run. Run the package's own scripts as your instructions require. Do not push, merge or commit to any remote. The state checkout is /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state; write your stage report there only. Never git stash.


### Completion checklist

Prepare the smallest ideation proposal for the assigned task Scope. Do not implement, write another task, contact another session or perform external writes.

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf --stage ideation


### Completion Signal

When you finish (after all commits and stage report writes are done), send one concise final message in this Codex worker thread:

    Done: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file completed ideation. Report written to /private/tmp/dev2-new-work-checks-what-exists-first-20261113/neutral-replay/wf/.spacedock-state/design-surfaces-task-dir-crash.md.

The first officer observes completion through the Codex final-status notification in the FO mailbox. Do not emit a Claude `SendMessage` call; the Codex mailbox notification is the completion signal.