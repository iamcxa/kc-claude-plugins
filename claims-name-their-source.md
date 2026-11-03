---
title: A number or factual claim in a gate summary, PR body or Captain message names the command and date that produced it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:claims-name-their-source:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:claims-name-their-source-backlog-1
              briefing:
                id: briefing:claims-name-their-source:backlog:attempt-1:revision-1
                digest: sha256:5fc821bff866f954480662f5b6db9adc7bc642ef5766125966b3278c635a5343
                room-ref: ./claims-name-their-source/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, "Give a number only if you measured it", "Re-verify any factual claim against the current implementation before it goes into a PR, issue, review, or third-party message", and the artifact rule "Point at the source".
- Bite: 2026-10-22, FO relayed a worker's claim that design_surfaces.py prints Preview paths to the Captain; the checker prints only the review report path (FO corrected it when he asked). The kc-adr FO reported a gate summary and PR body that said two cells were unmeasured where it was three (its read-adr-reporting-rule-followup task). The package has no such rule (grep of 0.28.0 markdown for "measured it", "enforcement point": 0 files).
- Upstream first: kc-dev-flow-2 delivery_gate.py (checks clause presence, not claim sources); the repository CLAUDE.md rule that an absolute names its enforcement point.
- Non-goals: checking claims in code comments.
- Batch 13: the Captain 「可以」 (chat, 2026-11-03), answering 「決定：這批加入那 3 張，共 7 張一起進 backlog gate 嗎？」, which named this task.
- Further bite: the Paseo agent-observatory reports of 2026-11-03 (sampled transcripts, not yet checked against the source): the relay FO told the Captain a concern "should not hold" before the validator found the script printed the record, then corrected it; the web FO designed four test workers on a count measured in another repository, and the two-core runner timed out until it went back to two.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The design names the point that catches an unsourced number or factual claim before it reaches the Captain, a PR body or a gate summary; replays of the 2026-10-22 relay and the kc-adr count are caught there, and a claim naming its command and date passes.

## FO alignment

Alignment: needed at ideation; whether this is a written rule or a checked one is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
