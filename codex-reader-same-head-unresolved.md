---
title: The Codex reader does not call a head clean while a finding on that head is unresolved
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:codex-reader-same-head-unresolved:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:codex-reader-same-head-unresolved-backlog-1
              briefing:
                id: briefing:codex-reader-same-head-unresolved:backlog:attempt-1:revision-1
                digest: sha256:bd1dfd93a625b2697560df7463c9977af324c65cacd268a4612eeaa8d9f11436
                room-ref: ./codex-reader-same-head-unresolved/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:codex-reader-same-head-unresolved:backlog:1
                briefing: briefing:codex-reader-same-head-unresolved:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-26T15:37:39.908924Z"
                decision: approve
                reason: Captain 「准」 (chat, 2026-10-26) answering 「需要你決定：第 7 批三張任務的待辦關卡，要不要一起批准進入設計階段？我建議全部批准。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-26), answering FO's ask to file this and the journey-probe task after learn backfill job caa9b488 (extension-defaults-and-install-choice) found #716 merged with an unaddressed Codex P2.
- Bite (verified 2026-10-26): on iamcxa/kc-claude-plugins#716 head 8340c3ba, Codex posted a P2 line comment at 2026-10-25T04:30:35Z and its summary state `has_unresolved_findings: true`; a second Codex run on the same head posted "Didn't find any major issues" at 05:22:39Z. `python3 <package 0.31.0>/extensions/codex/codex_review.py iamcxa/kc-claude-plugins 716` prints `clean on 8340c3baa ... evidence=comment:6393874798` and exits 0. FO relayed "#716 clean" to the Captain and the P2 shipped.
- Shape asked for: a later no-issues receipt on a head does not clear an earlier unresolved finding on the same head; the reader reports that finding instead of clean.
- Upstream first: `extensions/codex/codex_review.py` (the #722 reader: summary state decides over eyes), `extensions/codex/EXTENSION.md`.

## FO alignment

Alignment: not needed: the bite and the shape are recorded facts; the reader's verdict rule is the package's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
