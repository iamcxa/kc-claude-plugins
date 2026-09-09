---
id: 20w9we1wvtdy500nf9rc3a65
title: Reverse a story map out of a Linear project, and see whether it survives contact
status: backlog
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
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
