# validation-1
Dispatched: 429b4673e0cff4088adf5ee75db64830de441917 (workflow checkout)
Model: codex gpt-6-astra / xhigh
Roster: validation on Codex = Astra / xhigh
Candidate: 32901fe5f34fb17ae9a5741cff88471d55e81288

## Checklist
Independent PASSED or REJECTED verdict on candidate 32901fe5f34fb17ae9a5741cff88471d55e81288 (base 706b01fdb04b5d0b17b213562296dc95eaa60368) against AC-1 to AC-12 of owner-cancels-booking.md: one row per criterion with real evidence or an explicit unverified reason; re-check rather than trust evidence/implementation-1/
Close what the implementation report left open: the lost-reply recovery at the final candidate with a real pointer click (AC-9); office focus refetch and the read-only drawer at the final candidate (AC-5); staff complete or cancel forced interleavings against an owner cancel in real PostgreSQL 18 (AC-7); a competing second-owner confirmation for the released slot (AC-2)
Every PASS has a positive control that fails at the base or with the relevant hunk reverted in a scratch copy; say which
Run migration 0027 on a disposable database seeded with all six statuses and an old-code staff write after it, and confirm the narrow owner writer is the only path that can set cancel_source owner (no general UPDATE grant)
Pictures at 390, 834 and 1440 of the states you verify, phone text masked immediately before each capture after any viewport change, absolute paths in the report
Judge, under Review-finding disposition with the four evidence fields, the repeated sentence on the withdrawn and cancelled result cards (「您已撤回這筆預約，店家不會再確認。」 then 「已撤回預約，店家不會再確認。」) and the test-only /__fixture routes (confirm they exist only in apps/qnow-api/test-pg/support and are not reachable from any production entry)
Run the affected unit suites, the real PostgreSQL suites, type-checks and lint at the candidate

## Scope notes
Validation for owner-cancels-booking (profile pilot, Surfaces: ui, db). You are a fresh validator: you did not build this and you do not repair it. Read the task file (Scope, FO alignment, Design, Data change and migration shape, ADR amendment draft, Acceptance criteria, the implementation Stage Report) and design/pictures-4/ as the approved look. FO ran the journey lint at the candidate on 2026-11-10: exit 0, advisory long-card notes only.
Work in a scratch worktree of the candidate (git worktree add --detach /tmp/ocb-val1-wt 32901fe5f34fb17ae9a5741cff88471d55e81288, then pnpm install --frozen-lockfile there), never in the implementation worktree; remove it when done. Local API, throwaway PostgreSQL 18 (CLOSURE_GUARD_PG_BIN=/Applications/Postgres.app/Contents/Versions/18/bin) and Clerk development test numbers (fixed code 424242) only; run anything needing a development secret as scripts/with-dev-secrets.sh <command>; never print a secret or a real phone number; delete every Clerk test identity you create and confirm by re-query. Another worker may be running its own throwaway PostgreSQL and API: use ports other than 4300, 4391, 4392, 4394 and 9431, and stop only processes and data directories you created. Builds use web:build:prod --clear and you confirm the served asset hashes equal dist.
Browser: agent-browser --headed with your own session name; if a screenshot stalls, start one fresh session once, then record that evidence as not verified. A click exit line is not evidence: read the DOM or SQL. Never touch the system clipboard.
The design director's built-screen review is FO's to run after your report; do not create agents. Do not push, open a PR, comment, or change hosted services. Never git stash; never edit or skip hooks; no --no-verify; never raise a timeout. No new package installs beyond pnpm install --frozen-lockfile.
Write `## Stage Report: validation` with the verdict, per-criterion evidence, findings by Review-finding disposition and unverified obligations; extra output in owner-cancels-booking/evidence/validation-1/, large logs in /tmp. Commit with spacedock state commit owner-cancels-booking --workflow-dir /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2.
Codex sandbox: out-of-sandbox commands need permission; ask, and batch where you can.
Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here). Do not message anyone, and do not create or manage other agents.
