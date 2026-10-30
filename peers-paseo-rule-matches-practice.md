---
title: The peers rule on new Paseo asks matches what FOs do, either by listing paseo where peers run inside Paseo or by relaxing the clause
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:peers-paseo-rule-matches-practice:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:peers-paseo-rule-matches-practice-backlog-1
              briefing:
                id: briefing:peers-paseo-rule-matches-practice:backlog:attempt-1:revision-1
                digest: sha256:206116b487a362fb351755204e68648f11d9af26e6c9b1910980350bd8c11024
                room-ref: ./peers-paseo-rule-matches-practice/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peers-paseo-rule-matches-practice:backlog:1
                briefing: briefing:peers-paseo-rule-matches-practice:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:26.672769Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: interview round 004 finding (state .notes/fo-feedback/round-004.md, 2026-10-28), proposed by FO; the Captain chose theme B for batch 11 (「那就 B 可以」, chat, 2026-10-30), whose row named 「「沒列 paseo 就不能主動問」的規則跟實際做法矛盾」.
- Bite: all five interviewed FOs initiated Paseo asks with paseo unlisted and none recorded `peers not run`; qnow's Captain-directed ask had no compliant path; web did not know the clause existed; default sends steer into running peers and web received about 15 no-action finish notices on 2026-10-28.
- Upstream first: `extensions/peers/EXTENSION.md` § Paseo binding, `extensions/paseo/EXTENSION.md`, `references/sd/adoption.md`, Paseo `send_agent_prompt` defaults.

## Non-goals

- Changing Paseo; a hook that blocks sends.

## Budget

- One package PR to the peers and paseo extensions and adoption text; adopters' README listing follows through the normal sync.

## Stop condition

- Each round-004 event replays as allowed or as refused by a stated rule, with no FO left without a compliant path for a Captain-named ask.

## FO alignment

Alignment: needed before ideation; list paseo everywhere or relax the clause is the Captain's.
Result: aligned at backlog: the Captain 「對，全准且全確認」 (chat, 2026-10-30) to FO's batch-11 backlog sitting, which asked 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」, approved the outcome and bounds in this file. List paseo everywhere or relax the clause stays his: ideation returns it as a decision at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
