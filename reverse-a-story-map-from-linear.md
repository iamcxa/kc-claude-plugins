---
id: 20w9we1wvtdy500nf9rc3a65
title: Reverse a story map out of a Linear project, and see whether it survives contact
status: implementation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-09T03:45:05Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-reverse-a-story-map-from-linear
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:20w9we1wvtdy500nf9rc3a65:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:20w9we1wvtdy500nf9rc3a65-backlog-1
              briefing:
                id: briefing:20w9we1wvtdy500nf9rc3a65:backlog:attempt-1:revision-1
                digest: sha256:fd087955f59c08344668c6da75bd585963b41d5332092b60b4c9bf59a9406a39
                room-ref: ./reverse-a-story-map-from-linear/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:20w9we1wvtdy500nf9rc3a65:backlog:1
                briefing: briefing:20w9we1wvtdy500nf9rc3a65:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-09T03:43:59.766489Z"
                decision: approve
                reason: 'Captain approved the seed at the backlog gate: the POC question, the falsifier against an independently drawn map, and the stop point at a story map plus an unattachable-issue list. Constraint recorded as AC-1 and Non-goals: draw into a separate room and file, leave the existing planning board untouched.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

Every board `kc-journey-map` has drawn so far was drawn by its author, for its author. The
tool's own risk register covers whether it breaks; nothing covers whether it is useful. The
untested assumption is that these boards get a team to aligned value faster than talking
without them, and no second person has drawn one.

The captain has supplied a Linear project and will supply a second map of the same project
drawn independently from another engineer's angle. Two independent readings of one project
are the cheapest thing that can falsify the assumption: if they are noticeably orthogonal,
comparing them is the alignment work the tool claims to accelerate. If the reversed backbone
is unrecognisable to the people doing the work, reversing from a tracker is the wrong input
and that branch closes cheaply.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether a journey map reversed from a tracker is a usable starting point
for a value-alignment conversation, or whether the backbone must come from people.

**Cheapest credible falsifier:** draw one story map from the named Linear project, then set
it beside the independently drawn map the captain supplies. The captain judges whether the
invented backbone is recognisable.

**Budget:** one worker dispatch to draw, one comparison round.

**Observable stop point:** a story map for the project plus a list of issues that attach to
no activity, presented to the captain. Stop there. Do not draw a journey board or a function
map for it.

## Accepted outcome

A story map reversed from the project, and a named account of what was invented rather than
read.

## Non-goals

- Do not modify the existing planning board or the worked example. This work draws into its
  own room and its own file.
- No journey board, no function map, no plan-flow handoff.
- No change to the reversing mechanism itself unless drawing proves impossible without one.

## Acceptance evidence

**AC-1** A story map file exists for the Linear project, rendered to a room of its own, with
the existing `draw-a-journey` room and `journey.example.yaml` unchanged.

**AC-2** Every backbone activity is marked as read from the tracker or invented by the
worker. A map that does not distinguish them fails this criterion.

**AC-3** Every issue in the project is either attached to an activity or listed as
unattachable, with a reason. No issue is silently dropped.

**AC-4** The captain, shown the map beside the independently drawn one, states whether the
invented backbone is recognisable. This is the value criterion the other three serve.

## Route-back conditions

Return `poc_outcome` to planning. Create no delivery work from this task.

## Measurement

Count of issues that attach to no activity, and the captain's verdict on AC-4.

## Stage Report: implementation

- FAILED: Read the captain's named Linear project and draw one story map from it, into its own room and its own journey file, leaving the existing draw-a-journey room and journey.example.yaml byte-identical.
  The CODE worktree this dispatch assigned (montpellier-v1/.worktrees/spacedock-ensign-reverse-a-story-map-from-linear, cut from bb6f737b) carries no kc-team-ops/skills/kc-journey-map at all — `find kc-team-ops -iname "*journey*"` returns nothing there. origin/main carries an older kc-journey-map (SKILL.md, board-template.html, cell-contract.md only). The three files this dispatch names (map-from-conversation.md, canvas.md, journey.example.yaml) plus lib/journey-render.mjs exist only on origin/iamcxa/journey-map-skill-merge @ ba9625ce, unmerged. Escalated via `SendMessage(to="team-lead", ...)`: no agent named team-lead was reachable (tool returned "No agent named 'team-lead' is reachable"), and no `ListAgents`-class tool is available in this session either, so the standard escalation channel is not live here. Did not merge, rebase, or reset any branch myself — re-pointing the worktree's base is a call that belongs to whoever built the dispatch, not to the ensign. `journey.example.yaml` and the `draw-a-journey` room were never touched by this session (verified: no commit or write against tacoma or origin/main; the worktree's own git status is clean).
- DONE: Mark every backbone activity as read-from-the-tracker or invented, so the captain can tell which is which without asking.
  Drafted in reverse-a-story-map-from-linear.journey-draft.yaml (this directory) against the schema read from canvas.md/journey.example.yaml/map-from-conversation.md (read-only, from tacoma's iamcxa/journey-map-skill-merge branch — no writes made there). All 6 backbone activities are marked INVENTED in their `note:` field, with the specific tickets each was synthesized from named. The persona line is marked read-from-tracker (the project's own summary field, quoted verbatim). This satisfies the marking requirement even though rendering is blocked — the file itself carries it, per the AC's own wording.
- DONE: Account for every issue in the project: attached to an activity, or listed as unattachable with a reason. None silently dropped.
  Read all 48 issues in the project via `list_issues(project=..., includeArchived=true)`, `hasNextPage: false`. 41 attached across the 6 invented activities, 7 listed under `unattachable:` with a one-line reason each (process/governance/decision/theme tickets that don't correspond to one step). Verified by extracting every `DRC-####` id the draft file references and diffing against the full id list pulled from Linear: zero missing, zero duplicated.

### Summary

The Linear-read half of this task is complete and durable (48/48 issues accounted for, backbone drafted with explicit tracker/invented marking) in `reverse-a-story-map-from-linear.journey-draft.yaml`. The draw-half is blocked: the dispatched CODE worktree does not carry the kc-journey-map tool at all — it exists only on tacoma's unmerged `iamcxa/journey-map-skill-merge` branch, which is also this dispatch's own session id per the checkpoint refs, suggesting the dispatch was authored against tacoma's state but the worktree was cut from montpellier-v1's older HEAD. Needs a decision: re-point/rebuild the worktree from that branch, or another source for the tool, before the file can be rendered into a room and AC-1/AC-4 can be judged. No Linear writes made; no existing journey-map files or rooms touched.
