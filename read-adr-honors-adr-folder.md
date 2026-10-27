---
title: read-adr lists the ADR folder its caller names, and none means no records
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:read-adr-honors-adr-folder:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:read-adr-honors-adr-folder-backlog-1
              briefing:
                id: briefing:read-adr-honors-adr-folder:backlog:attempt-1:revision-1
                digest: sha256:de9d44dc4079f89275b7ff302e75cec8b363d063d3fce5724582faa9cc61b07d
                room-ref: ./read-adr-honors-adr-folder/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:read-adr-honors-adr-folder:backlog:1
                briefing: briefing:read-adr-honors-adr-folder:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:13:27.936586Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: FO, 2026-10-25. Codex review 5628338608 on iamcxa/kc-claude-plugins#713 head 037d2cf6 (2026-10-23T12:41:08Z), one P2, was not read before the merge: the merge ask named Codex as not read because `codex_review.py` reported `running` (a stuck security-review eyes reaction; see codex-review-hang-detected). The Captain approved the merge on that statement.
- Finding (P2, `kc-dev-flow-2/skills/read-adr/SKILL.md`, a byte copy of `kc-adr/skills/read-adr/SKILL.md`): when the caller passes an ADR folder other than `docs/adr`, or `ADR folder: none` (the design director does), the no-citation branch still lists `docs/adr/`, so it can miss the supplied rulings or apply rulings the caller declared absent.
- Shipped: the text is in kc-dev-flow-2 0.30.0 and kc-adr 0.2.0.
- Fix lives in kc-adr (the source); `scripts/kc-adr-copy-sync.sh sync` carries it to the dev2 copy in the same PR, per the D4 ruling of kc-adr-tools-with-dev2-copy.
- Non-goals: other read-adr wording.

## FO alignment

Alignment: not needed: a reviewer finding in shipped text, fixed in its source.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
