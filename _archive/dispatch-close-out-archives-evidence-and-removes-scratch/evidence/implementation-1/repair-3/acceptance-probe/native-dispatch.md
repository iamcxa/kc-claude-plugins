## First action

Read this dispatch file directly and treat its content as your stage-specific assignment.

The outer fresh-worker prompt invokes `$spacedock:ensign` before this pointer. The installed skill supplies the shared ensign discipline (stage-report format, polling, worktree ownership, and completion signal protocol); this file supplies the stage-specific assignment. Do not try to invoke a Claude skill wrapper; Codex dispatch uses this file pointer after the outer bootstrap.

You are working on: Synthetic dispatch

Stage: validation

Your working directory for CODE is /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/.worktrees/spacedock-ensign-dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18
All CODE reads and writes MUST use paths under /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/.worktrees/spacedock-ensign-dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18.
Your git branch for CODE is spacedock-ensign/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18. All CODE commits MUST be on this branch in the worktree. Do NOT switch branches or commit code to main.
This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state add /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18.md && git -C /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state commit -m "..." -- /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. Then push the state branch so peers see your entity/report: `git -C /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state push origin spacedock-state/dev2`; on a non-fast-forward rejection, `git -C /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state pull --rebase origin spacedock-state/dev2` then re-push.

Read the entity file at /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18.md for the current spec.

Package root: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-close-out-archives-evidence-and-removes-scratch/kc-dev-flow-2
Send your completion message to `main`.
Keep this second scope-notes line verbatim.
Use /private/tmp/dev2/dispatch-code-6298d87e42466f9e/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18/validation-2/checkout

Scratch: /tmp/dev2/dispatch-code-6298d87e42466f9e/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18/validation-2
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/validation-2/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-close-out-archives-evidence-and-removes-scratch/kc-dev-flow-2/scripts/scratch.py close /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18 validation-2` and paste its output.


### Completion checklist

Inspect the real dispatch seam
Keep the received second checklist line

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2 --stage validation


### Completion Signal

When you finish (after all commits and stage report writes are done), send one concise final message in this Codex worker thread:

    Done: Synthetic dispatch completed validation. Report written to /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/dispatch-close-out-archives-evidence-and-removes-scratch/implementation-1/repair-3/acceptance-candidate/tmp/dispatch-stage-bd9tgu1l/code/docs/dev2/.spacedock-state/dispatch-fixture-a2702d81f50b4bff98eb0e8b75919a18.md.

The first officer observes completion through the Codex final-status notification in the FO mailbox. Do not emit a Claude `SendMessage` call; the Codex mailbox notification is the completion signal.