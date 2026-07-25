---
title: Collapse the Teams-vs-subagent branching in e2e-flow
status: backlog
source: sprint-3 (skill-layer prose control flow) entity; deferred at the original audit as a measurement question, filed once the sprint boundary made it cohesive
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 4yw4cfvkrkj69cyj7k7chp9q
---

## Problem

`skills/e2e-flow/SKILL.md` is 548 lines, and 25 of its passages carry Teams-mode machinery:
spawning a pre-warm verifier before the writer, a liveness re-check before every SendMessage,
120-second timeouts on two separate awaits, a ROUND_1_STATUS parse with a three-branch decision
table, crash cleanup that must also delete the write sentinel, and a full fallback path to
subagent mode at each failure point. All of it is English prose the agent is expected to
execute as a state machine, and every branch exists in duplicate because subagent mode has to
work too.

The feature is gated behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` with graceful fallback,
so the fallback path is the one that always works and the Teams path is the one carrying the
complexity. Nobody has measured whether the pre-warm actually buys wall-clock.

## Notes for ideation

- This is a measurement question before it is a design question. Time `/e2e-flow` end-to-end
  with and without Teams on the same flow, several runs each. If pre-warm does not measurably
  beat the subagent path, deleting the branch is the whole entity and the rest of this is moot.
- If it does pay, the fix is not to keep the prose — it is to reduce the two paths to one
  described sequence with a single divergence point, rather than two interleaved narratives the
  reader must hold simultaneously.
- Sequence after [[e2e-retire-flow-sentinel]]: the sentinel's cleanup obligations are woven
  into the Teams crash paths, so removing the sentinel first makes this diff much smaller.
- Falsification for the delete case: with Teams disabled, every currently-documented outcome of
  `/e2e-flow` must still be reachable. If some outcome exists only on the Teams path, that path
  is load-bearing and the delete is wrong.
