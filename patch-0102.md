---
title: A goal change marks a release changed, any shared non-production database freezes its migrations, and five workflow gaps close
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:patch-0102:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:patch-0102-backlog-1
              briefing:
                id: briefing:patch-0102:backlog:attempt-1:revision-1
                digest: sha256:4d758e558ed98c10fb64213b9f75657770cd87cd85b4ae91fd03ceabaa4c283a
                room-ref: ./patch-0102/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:patch-0102:backlog:1
                briefing: briefing:patch-0102:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T17:15:34.507831Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「准」 — fix the five package findings as 0.10.2 with the collision rule: applied task keeps its number, the unapplied one renumbers; recreate only when both are applied to a non-resettable database'
              application:
                target-stage: ideation
                state: consumed
started: 2026-09-30T17:15:41Z
---

Five gaps in kc-dev-flow-2 0.10.1 `references/sd/workflow.md`, found by an external review of an adopter's workflow sync (qnow PR #1248, round 2, 2026-10-01); patch release 0.10.2.

## Scope

Captain 2026-10-01: 「准」 to the FO's proposal: fix the five package findings in one patch release, fill the adopter's secret-wrapper value in qnow #1248 separately, then re-sync #1248; and the collision rule below.
Findings (text at kc-dev-flow-2-v0.10.1):
- P1, release review skip check: a Captain ruling that changes a release's goal (or a task's or story's goal) without changing the release's story ids is seen as "unchanged" by the skip shortcut, which defeats signal 2 ("changes its goal"). The freshness check must include a goal or scope revision, not only membership.
- P1, Number guards Applied bullet: freezing is limited to "a non-production database branch", but an adopter's staging can be a separate hosting project whose database is that project's production database; it is then never frozen, and the renumber recovery (reset a non-production branch) cannot apply to it. Captain's ruling on the design: every shared non-production environment freezes its migrations, whether a database branch or a separate project; on a number collision the task whose migration is already applied keeps its number and the other, unapplied task renumbers, so no reset is needed; only when both are applied to a database that cannot be reset does the Captain delete and recreate that database.
- P2, release fields: when signal 2 moves a task out of a release, no step clears `journey`, `journey-release` and `journey-story` or repairs an affected story's `journey-required-tasks` declaration.
- P2, backlog gate revise: a revise at the backlog gate is routed to "that stage's worker", but backlog dispatches no worker; route it to FO or the proposal's author.
- P2, number guards fetch: bare `git fetch` before `reserve` and before the pre-merge `check` updates the current directory's repository, not the `--repo` the script inspects; use `git -C <repo> fetch`.
Non-goals: the adopter secret-wrapper value (adopter-owned, fixed in #1248); any Spacedock change; `number_guards.py` logic changes beyond what the wording requires.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: replacement wording for each of the five passages; which asserted phrases in `test_sd_dispatch.py` change and a falsifier holding the 0.10.1 text for each; whether `number_guards.py` or `journey-progress` needs any change for the collision rule and the field clearing; whether ADR 0002, ADR 0004 or the #520 ADR (0006) needs an amendment line.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
