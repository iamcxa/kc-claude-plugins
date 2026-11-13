## First action

Read this dispatch file directly and treat its content as your stage-specific assignment.

The outer fresh-worker prompt invokes `$spacedock:ensign` before this pointer. The installed skill supplies the shared ensign discipline (stage-report format, polling, worktree ownership, and completion signal protocol); this file supplies the stage-specific assignment. Do not try to invoke a Claude skill wrapper; Codex dispatch uses this file pointer after the outer bootstrap.

You are working on: Synthetic dispatch

Stage: ideation

This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state add /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5.md && git -C /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state commit -m "..." -- /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. Then push the state branch so peers see your entity/report: `git -C /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state push origin spacedock-state/dev2`; on a non-fast-forward rejection, `git -C /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state pull --rebase origin spacedock-state/dev2` then re-push.

Read the entity file at /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5.md for the current spec.

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1
Send your completion message to `main`.
Keep this second scope-notes line verbatim.

Scratch: /tmp/dev2/dispatch-code-bc71b4711b09dbfe/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5/ideation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/ideation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /private/tmp/close-854-validation2-20261112/candidate/kc-dev-flow-2/scripts/scratch.py close /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5 ideation-1` and paste its output.


### Completion checklist

Inspect the real dispatch seam
Keep the received second checklist line

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2 --stage ideation


### Completion Signal

When you finish (after all commits and stage report writes are done), send one concise final message in this Codex worker thread:

    Done: Synthetic dispatch completed ideation. Report written to /private/tmp/close-854-validation2-20261112/tmp/dispatch-stage-brjsfmrt/code/docs/dev2/.spacedock-state/dispatch-fixture-b40ebbb0e37b42ab9487c8ed34a3fdb5.md.

The first officer observes completion through the Codex final-status notification in the FO mailbox. Do not emit a Claude `SendMessage` call; the Codex mailbox notification is the completion signal.