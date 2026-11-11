# pending-booking-cap — implementation cycle 1

Dispatched: 2026-10-23 from state commit d0270c05af744bc7055fbbef7992bcc7269387e2; base origin/main a8793b938deb12ff4d599a427998c28b4fe080f1
Model: codex gpt-6.1-sol, reasoning xhigh (Paseo agent), at the Captain's request 「派 sol 6.1 xhigh 作為 worker 實作」

## Checklist

The approved pending-booking-cap design is built API-only on a branch from origin/main: constant 3, early refusal-only count before the branch lock and vehicle insert, authoritative post-lock count with one database timestamp shared with the slot check, 422 TOO_MANY_PENDING, owner app unchanged
AC-1 to AC-9 each have a test or check at the stated layer, run with exit codes; real-Postgres cases run in the existing test-pg harness only, and each test is shown to fail when its guarded line is removed
Affected type-checks, booking tests, lint, adr_lint (if an ADR is written) and the roborev gate run with exit codes; nothing pushed, no PR

## Scope notes

Implementation for pending-booking-cap (profile prod), admitted by the Captain's 「准」 on ideation attempt 1 (2026-10-23), who asked for Codex gpt-6.1-sol xhigh as the worker. Build exactly the approved Design in the task file (Smallest change 1-7, Implementation order layers 1-7, AC-1..AC-9), API-only; do not change owner-app code. Read the task file first, then the nearest AGENTS.md/CLAUDE.md for every path you touch.
Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion to `main` as your final reply summarising the result; Paseo delivers it to the first officer when you finish. Do not message anyone.

Work in the worktree and branch the dispatch stamp created (see the task's worktree: field) from base a8793b938deb12ff4d599a427998c28b4fe080f1. If the design's decision-record draft becomes an ADR, reserve its number with <package>/scripts/number_guards.py reserve and run adr_lint with --require for it. Run each test within the one-minute limit; do not raise a timeout. Real-Postgres tests only against the existing throwaway test-pg harness, never a hosted database.
Before reporting, commit your changes and run `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base a8793b938deb12ff4d599a427998c28b4fe080f1`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
Write `## Stage Report: implementation` in the task file and commit it with spacedock state commit pending-booking-cap --workflow-dir /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2.
Hard limits: no push, PR, Netlify, Clerk or hosted database change; no messages; never git stash.
