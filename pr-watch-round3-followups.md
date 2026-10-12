---
title: pr_watch.py keeps its lock file distinct from any --state path
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #594, 2026-10-11. The finding is neither P1 nor Material, so it started no repair cycle there and is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

Resolved 2026-10-12 by #601 (0.16.1): the lock and temp files append to the state file's name, so a `--state` ending in `.lock` keeps its list. Nothing left to build here.

- Finding (P2, `pr_watch.py` lock path): `state.with_suffix(".lock")` equals the state file when `--state` already ends in `.lock`, and opening the lock with mode "w" truncates the watch list. Decline reason: it needs a caller to pick a `.lock` name for the state file; the default path ends in `.json`, and FO's rule passes no `--state`.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: none beyond the finding.
Surfaces: none
Visible change: none
