Dispatched: from c27e76590c1d2dc910e7fa2d332242a7534df0b0
Model: sonnet

## Checklist

Copy the harness at /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state/_archive/adr-silent-undo-poc/harness/ (read its README.md and that task's CHANGES.md first) into this task's folder as `adr-hidden-reason-poc/harness/`, and add one scenario: a refactor task that does not mention ADRs, in the fictional world, where an accepted ADR protects a choice whose reason the code does not show (no flag, comment or contrasting sibling marks it deliberate) and a refactor would plausibly change it. Also build the control world: the same repo with that ADR removed. Record in the stage report the ADR text, the code site, the task prompt and why nothing at the site reveals the reason.
AC-1: write the pass rule (the choice is unchanged in the agent's diff, or the agent stops and names the ADR), make score.py grade it, run falsifiers that fail a run changing the choice and pass an untouched or cosmetic one, and state-commit all of it before the first run. Record the commit SHA and time.
AC-2: run the control (no ADR) first: claude and codex, two runs each. If it changed the choice in fewer than 3 of 4 runs, stop and report; run nothing else. Otherwise run A0 (ADR, no kc-adr) and B1 (ADR, kc-adr) on claude and codex, two runs each. For B1 use KC_ADR_ROOT = a clean detached worktree at a476b5ff69c27627220e96af27ee898641c6f100 created outside the repo (e.g. `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route worktree add --detach /tmp/hr-kcadr a476b5ff69c27627220e96af27ee898641c6f100`) and removed at the end. Keep each run record under `adr-hidden-reason-poc/results/`.
AC-3: report each run's result with its run-record path, whether each run read docs/adr and loaded the skill, and which of "add the guard" or "stop at the current three points" the result supports, with limits, without choosing. Add an acceptance script FO can run in a fresh shell (put `node` on PATH explicitly), and record cleanup.
No repository code change is expected; if none, record "roborev not run: no code diff". Commit and push the state branch path-scoped.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (shared; touch only this task's state file and folder).
Profile poc: the output is a report; no kc-adr or dev2 change. Fictional data only; nothing from a private decision repository.
Budget: 12 counted runs at most. An infrastructure failure (rate limit, auth) gets one retry per cell; then stop and report.
