---
title: A factual claim in a question FO puts to the Captain has been checked against the record before he reads it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:gate-question-facts-are-checked-before-the-captain-reads-them:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-question-facts-are-checked-before-the-captain-reads-them-backlog-1
              briefing:
                id: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-1:revision-1
                digest: sha256:ab7abf3920dd5c06228fc87eabeee3a493b7bb32aea8b905da77f71bffdcd594
                room-ref: ./gate-question-facts-are-checked-before-the-captain-reads-them/review/backlog/briefing-1
---

## Scope

- Source: FO's own misses, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite, three times in two days, each found after the Captain had answered: the #843 merge ask said already-filed tasks would not be asked to add a Story line, while the approved design has the idle look name them (observer report, 2026-11-11); the #841 merge ask said only designs not yet through the design gate would be refused, while release 0.39.0 refused approved ones and an adopter found it after release (2026-11-11); a question of 2026-11-12 described five tasks as waiting in design when the Captain had held or closed all five.
- What exists: the delivery check counts unchecked numbers in gate text and the workflow says each claim names the command and date that produced it; none of the three claims was a number, and the check passed each time.
- Outcome: a sentence in a gate or decision question that says what a change does or what state a task is in either names the record or run that shows it, or is marked as unverified where the Captain reads it.
- Open for the design: whether this can be checked at all by a script, or is a step with a record; what the cheapest version is that would have caught the three cases; what it costs FO per question in words and minutes.
- Non-goals: checking the Captain's own words; a second reviewer for every question; rewriting the question form.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- Replaying the three questions named under Bite at their recorded state, the candidate flags each false sentence, and three questions that were true are not flagged. Return to the Captain if the design finds no mechanism cheaper than a second agent reading every question.

## FO alignment

Alignment: not needed: one observed defect with one outcome; whether and how it can be checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
