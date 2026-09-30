# 0003. The package documents secret-read enforcement and ships no hook

Date: 2026-09-30

## Status

Accepted

## Context

Two workers in an adopting project printed a development secret key despite dispatch
notes banning it. A user-level `PreToolUse` Bash guard has held since, but its
patterns match the whole command text, so it also refused a read-only command that
only mentioned a guarded tool name as test data. A plugin `hooks/hooks.json`
`PreToolUse` hook was probed on Claude Code 2.1.284 and fired in an unrelated
project's working directory, so a shipped hook would fire wherever the package is
enabled, including repositories with no dev2 adoption and machines that already
carry the user's own guard. The patterns depend on the adopter's stack, and Codex
has no `PreToolUse` equivalent. Read 2026-09-30 in the task's ideation.

## Decision

**Words:** 「准」 — Captain, 2026-09-30, at the ideation gate of `dispatch-and-report-hygiene` (document the secret guard, do not ship it)

**Options considered:**
- document the guard contract in `references/sd/adoption.md` and name one run-time wrapper in the dispatch's `Secrets:` line, shipping no hook
- ship a `hooks/hooks.json` `PreToolUse` entry in the package — rejected: it fires in every project where the plugin is enabled, doubles the user-level guard, cannot carry per-adopter patterns, and is Claude-only
- list the forbidden commands in each dispatch — rejected: two leaks happened despite such bans

The package does not ship a secret-read hook. Secret-read enforcement belongs to the
adopter or the user; the package states the contract in `references/sd/adoption.md`
and the workflow's `## Dispatch facts` names one wrapper as the only route to a
development secret. Facts only the package knows are stated by its skills (the
`Package root:` line and the FAILED rule); facts about the runtime and the adopter
are stated by that one inlined section.

## Consequences

An adopter that never reads `adoption.md` and installs no guard stays protected only
by the `Secrets:` line, which failed twice. A worker that splits or encodes a command
to pass a guard is forbidden by the sentence and detected by nothing. Reopen if a leak
is observed in an adopter that followed the contract, or if Codex gains a pre-tool
hook the package could target.
