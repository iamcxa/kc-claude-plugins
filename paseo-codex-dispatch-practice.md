---
title: The paseo extension says how FO dispatches a Codex worker through Paseo; commit locally, FO pushes and opens the PR, and the worker's workspace is its worktree
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:paseo-codex-dispatch-practice:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:paseo-codex-dispatch-practice-backlog-1
              briefing:
                id: briefing:paseo-codex-dispatch-practice:backlog:attempt-1:revision-1
                digest: sha256:bbb9dbd400df56b0fd0e3110c9c7021cce95e6d93a26fd82653a5cd8ebe9f16f
                room-ref: ./paseo-codex-dispatch-practice/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:paseo-codex-dispatch-practice:backlog:1
                briefing: briefing:paseo-codex-dispatch-practice:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:38:51.707782Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「照建議」 (chat, 2026-10-27), answering FO's batch-7 retrospective list (items a to d).
- Bite: batch 7 (2026-10-26/27): Codex workers created with Paseo create_agent could not reach the GitHub API (sync and implementation workers; gh failed, git push worked) or the local RoboRev daemon, so FO pushed, opened PRs and ran RoboRev for them; the relay FO reported its Paseo Codex workers' cwd stays the FO's workspace, so every worktree write needs a permission prompt, dozens per task (interview round 2). FO's 0.32.0 sync briefs that said commit locally and leave delivery to FO ran with no failure.
- Upstream first: `extensions/paseo/EXTENSION.md` (0.32.0), Paseo's own `paseo` skill and `paseo agent --help` (workspace and cwd options), Codex sandbox docs.

## Non-goals

- Changing Paseo or the Codex sandbox; any Paseo-only rule in Spacedock core (the Captain's 2026-10-26 placement ruling); making FO-side push and PR the rule on hosts other than Paseo Codex.

## Budget

- One package PR editing `extensions/paseo`; no new script.

## Stop condition

- The extension states the practice batches 7 and 8 ran (worker commits locally; FO pushes, opens the PR and runs RoboRev; the worker's working directory is its worktree), with the working-directory option checked once against `paseo agent --help`. Return to the Captain if Paseo cannot set a worker's working directory.

## FO alignment

Alignment: needed before ideation; where the check or rule lives is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
