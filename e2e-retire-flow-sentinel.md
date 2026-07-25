---
id: zeyd93m1v1vtfrzxstxga01p
title: Retire the prose-managed flow-write sentinel
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

`/e2e-flow` runs a hand-rolled mutex written in English. `skills/e2e-flow/SKILL.md`
instructs the agent to create `.claude/e2e/.flow-write-authorized` before dispatching a
flow-writing agent and delete it after the last one returns, across roughly six exit paths
including crash and timeout handling, with a 10-minute TTL as the leak backstop. Reading
the hook it authorizes changes the picture: `hooks/scripts/pre-write-flow-guard.sh:42`
does not block — it prints a warning and exits 0, and its own comment says blocking was
rejected because "block is trivially bypassed via Bash". So the entire sentinel apparatus,
its TTL, and its crash-cleanup prose exist to suppress an advisory message. The skill's own
description of it ("A PreToolUse hook blocks direct writes") does not match the hook's
behavior.

That inverts the fix. The abstraction worth keeping is write-time validation of a
hand-written flow, which is what the warning gestures at but never performs — it lists
consequences ("element names may not match the mapping") rather than checking them. Wire
the hook to run the real validator against the file being written and report actual errors,
and the authorization state has nothing left to protect: the sentinel, its six prose
lifecycle points, and the TTL all delete.

## Notes for ideation

- The cross-model reviewer called deferring this the largest strategic blind spot and
  proposed replacing the orchestration prose with a new native CLI (`e2e flow lock`,
  `e2e doctor`). Its supporting argument was wrong in direction — it claimed a leaked
  sentinel halts the agent loop for 10 minutes, when a leaked sentinel is fail-open and
  merely suppresses the warning — but the underlying objection stands. Record the cheaper
  alternative above as the first candidate and require proof that it cannot express the
  need before commissioning a new binary.
- Touches only `skills/` and `hooks/` — zero overlap with the compiler files the rest of
  the batch rewrites, so it can run as a parallel worktree lane rather than queueing.
- Consumes the validator from [[e2e-schema-contract]]; sequence after it or stub the call.
- Out of scope: whether Teams-mode pre-warm earns its complexity. That is a measurement
  question about wall-clock, not a design question, and belongs in its own seed.
