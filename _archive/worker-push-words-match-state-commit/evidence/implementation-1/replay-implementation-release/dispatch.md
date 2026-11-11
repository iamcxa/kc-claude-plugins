## First action

Read this dispatch file directly and treat its content as your stage-specific assignment.

The outer fresh-worker prompt invokes `$spacedock:ensign` before this pointer. The installed skill supplies the shared ensign discipline (stage-report format, polling, worktree ownership, and completion signal protocol); this file supplies the stage-specific assignment. Do not try to invoke a Claude skill wrapper; Codex dispatch uses this file pointer after the outer bootstrap.

You are working on: An owner account cannot flood a shop with pending bookings

Stage: implementation

Your working directory for CODE is /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.worktrees/spacedock-ensign-pending-booking-cap
All CODE reads and writes MUST use paths under /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.worktrees/spacedock-ensign-pending-booking-cap.
Your git branch for CODE is spacedock-ensign/pending-booking-cap. All CODE commits MUST be on this branch in the worktree. Do NOT switch branches or commit code to main.
This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state add /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state/pending-booking-cap.md && git -C /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state commit -m "..." -- /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state/pending-booking-cap.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. Then push the state branch so peers see your entity/report: `git -C /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state push origin spacedock-state/wf`; on a non-fast-forward rejection, `git -C /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state pull --rebase origin spacedock-state/wf` then re-push.

Read the entity file at /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state/pending-booking-cap.md for the current spec.

Package root: /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/package/kc-dev-flow-2
Implementation for pending-booking-cap (profile prod), admitted by the Captain's 「准」 on ideation attempt 1 (2026-10-23), who asked for Codex gpt-6.1-sol xhigh as the worker. Build exactly the approved Design in the task file (Smallest change 1-7, Implementation order layers 1-7, AC-1..AC-9), API-only; do not change owner-app code. Read the task file first, then the nearest AGENTS.md/CLAUDE.md for every path you touch.
Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion to `main` as your final reply summarising the result; Paseo delivers it to the first officer when you finish. Do not message anyone.

Work in the worktree and branch the dispatch stamp created (see the task's worktree: field) from base a8793b938deb12ff4d599a427998c28b4fe080f1. If the design's decision-record draft becomes an ADR, reserve its number with <package>/scripts/number_guards.py reserve and run adr_lint with --require for it. Run each test within the one-minute limit; do not raise a timeout. Real-Postgres tests only against the existing throwaway test-pg harness, never a hosted database.
Before reporting, commit your changes and run `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base a8793b938deb12ff4d599a427998c28b4fe080f1`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
Write `## Stage Report: implementation` in the task file and commit it with spacedock state commit pending-booking-cap --workflow-dir /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf.
Hard limits: no push, PR, Netlify, Clerk or hosted database change; no messages; never git stash.
TEST HARNESS (isolated replay): do not invoke the kc-dev-flow-2 skill through the Skill tool; read /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/package/kc-dev-flow-2/skills/implementation/SKILL.md and follow it, resolving every package path against /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/package/kc-dev-flow-2. Do not run the application unit, integration or e2e suites and do not start servers, databases or browsers; say in the report they were not run. Run the package's own scripts as your instructions require. The state checkout's origin is a disposable bare repository; push nothing else. The state checkout is /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state; write your stage report there only. Never git stash.


### Completion checklist

The approved pending-booking-cap design is built API-only on a branch from origin/main: constant 3, early refusal-only count before the branch lock and vehicle insert, authoritative post-lock count with one database timestamp shared with the slot check, 422 TOO_MANY_PENDING, owner app unchanged
AC-1 to AC-9 each have a test or check at the stated layer, run with exit codes; real-Postgres cases run in the existing test-pg harness only, and each test is shown to fail when its guarded line is removed
Affected type-checks, booking tests, lint, adr_lint (if an ADR is written) and the roborev gate run with exit codes; nothing pushed, no PR

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf --stage implementation


### Completion Signal

When you finish (after all commits and stage report writes are done), send one concise final message in this Codex worker thread:

    Done: An owner account cannot flood a shop with pending bookings completed implementation. Report written to /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/wf/.spacedock-state/pending-booking-cap.md.

The first officer observes completion through the Codex final-status notification in the FO mailbox. Do not emit a Claude `SendMessage` call; the Codex mailbox notification is the completion signal.