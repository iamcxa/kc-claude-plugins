---
title: pr_watch.py tasks round-3 follow-ups (frontmatter list form, stale reviewer flags)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third Codex review round of iamcxa/kc-claude-plugins PR #643 (head 5b280387, review:5513822090), 2026-10-14, task `fo-lifecycle-mod`. Neither is P1 or Material, so neither started a repair cycle there; the same round's P1 is repaired in that task.

## Scope

- Codex P2 (`scripts/pr_watch.py`, frontmatter read): `extensions:` written as an indented YAML block sequence (`- codex`, `- learn`) is read as empty, so `tasks` silently skips the configured reviewers and the learn observer and archive path. Decline reason: every adopter workflow on this machine writes the flow form `[...]` (checked in docs/dev2, qnow, relay and ss-web READMEs), and the README template ships `extensions: []`.
- Codex P2 (`scripts/pr_watch.py`, `read_flags()`): a PR kept in the watch file keeps its stored `watch-codex` or `watch-copilot` flag after that extension is removed from the README, so `tasks` still runs its reader. Decline reason: no workflow has removed a listed reviewer; the effect is an extra read, not a missed one.
- Codex round 4 P2 (review:5514369233, head 5eb6bf05, `scripts/pr_watch.py` around line 271): a restart after `pr-merge` writes `pr: pr-merge:N` but before the `after pr-merge:` lines run leaves the archived task with no observer check or learn, since `tasks` scans only live task files. Decline reason: the design records it as a limit; candidate fix: recognize the sentinel or scan archived tasks with no learn job.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
