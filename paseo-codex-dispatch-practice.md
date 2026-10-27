---
title: The paseo extension says how FO dispatches a Codex worker through Paseo: commit locally, FO pushes and opens the PR, and the worker's workspace is its worktree
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「照建議」 (chat, 2026-10-27), answering FO's batch-7 retrospective list (items a to d).
- Bite: batch 7 (2026-10-26/27): Codex workers created with Paseo create_agent could not reach the GitHub API (sync and implementation workers; gh failed, git push worked) or the local RoboRev daemon, so FO pushed, opened PRs and ran RoboRev for them; the relay FO reported its Paseo Codex workers' cwd stays the FO's workspace, so every worktree write needs a permission prompt, dozens per task (interview round 2). FO's 0.32.0 sync briefs that said commit locally and leave delivery to FO ran with no failure.
- Upstream first: `extensions/paseo/EXTENSION.md` (0.32.0), Paseo's own `paseo` skill and `paseo agent --help` (workspace and cwd options), Codex sandbox docs.

## FO alignment

Alignment: needed before ideation; where the check or rule lives is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
