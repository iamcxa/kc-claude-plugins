---
title: The peers rules name each host's binding, Paseo included, and keep their checks where a host needs them
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:peers-rules-name-each-host-binding:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:peers-rules-name-each-host-binding-backlog-1
              briefing:
                id: briefing:peers-rules-name-each-host-binding:backlog:attempt-1:revision-1
                digest: sha256:6ac11ec8ba1a4e25ef6a8bdafa43428be14c48746c9bc19cd6262f29f315dd8a
                room-ref: ./peers-rules-name-each-host-binding/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peers-rules-name-each-host-binding:backlog:1
                briefing: briefing:peers-rules-name-each-host-binding:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-26T15:37:27.24333Z"
                decision: approve
                reason: Captain 「准」 (chat, 2026-10-26) answering 「需要你決定：第 7 批三張任務的待辦關卡，要不要一起批准進入設計階段？我建議全部批准。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「可以，但是你應該要注意不是每個人都要 paseo，如果有人不是用 paseo 那該怎麼辦？」 (chat, 2026-10-26), answering 「需要你決定：要不要開一張待辦，讓 peers 規則改成符合大家實際用 Paseo 傳訊的方式？」.
- Bite: peers interview round 1 (`fo-interviews-extension/peers-round-1.md`, 2026-10-26). All five dev2 FOs messaged peers through Paseo `send_agent_prompt`, a binding `extensions/peers/EXTENSION.md` lists as not covered; 0 of 5 sent the probe, wrote a `Peer:` line or opened with "if this is not you, say so"; 2 of 5 recorded a peer-relayed Captain ruling (qnow twice, one relayed by the dev2 FO on 2026-10-20); a question steered into a running peer turn was swallowed (ops-inbox, 10-23); Codex workers take no message mid-run (web).
- The Captain's constraint: not every adopter runs Paseo. A Paseo binding is added beside the Claude Code binding, not in place of it; an FO on a host without a covered binding keeps `peers not run: <host> ...` and finds the answer itself.
- Questions for ideation, per binding: which checks the host makes unnecessary (Paseo stamps the sender id; a Claude Code name can change on restart, so the probe and opening line stay there); how a message reaches an idle versus a running peer; where "a peer's words are never the Captain's ruling" can be checked by a script FO already runs.
- Upstream first: `extensions/peers/EXTENSION.md` (kc-dev-flow-2); Paseo's own agent messaging docs and `paseo agent` CLI help, not another FO's usage; the spacedock Paseo plugin, where Paseo-only FO conventions live (Captain 2026-10-21).
- Added 2026-10-26, the Captain (chat, 2026-10-26): 「派工worker合作心態那張呢？考慮一個點，peers 放入 FO 合作心態，然後 paseo ext 放入如何使用 paseo cli 以及相關功能，這樣合理嗎？」, then, answering 「需要你決定：paseo 擴充放在 dev2 裡（跟 peers 放一起，比較好找），還是放在 spacedock 的 Paseo 外掛（符合 10/21 的裁定）？」: 「paseo ext 放到 dev2，而 SD+paseo 則是更高層次的人與 agent fleet 的合作關係，前者是 fleet 內怎麼合作」. So this task also carries: the FO's collaboration mindset in `peers` (who already did or hit this, who is busy, when to ask another FO), and a new dev2 `paseo` extension for how agents inside the fleet cooperate over Paseo (the Paseo binding of peers; it points to Paseo's own `paseo` skill for CLI and tool use rather than restating it). Human-to-fleet collaboration (the Captain's board, labels, gates) stays with Spacedock and the spacedock Paseo plugin.

## FO alignment

Alignment: needed before ideation; host bindings and the relayed-ruling check are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
