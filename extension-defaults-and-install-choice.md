---
title: Required extensions are on by default and an adopter picks the recommended ones at install
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:extension-defaults-and-install-choice:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extension-defaults-and-install-choice-backlog-1
              briefing:
                id: briefing:extension-defaults-and-install-choice:backlog:attempt-1:revision-1
                digest: sha256:489608a5663bc9245fa192621c8e41ec457e0504f291319e7ac9354916a344cf
                room-ref: ./extension-defaults-and-install-choice/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extension-defaults-and-install-choice:backlog:1
                briefing: briefing:extension-defaults-and-install-choice:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T03:12:06.190894Z"
                decision: approve
                reason: 'Captain 「准」 (chat, 2026-10-25) answering the briefing-1 question (enter ideation on pilot: learn and peers on by default, the rest recommended, an install UI to choose)'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain (chat, 2026-10-25): 「版本走查預設全部都啟用，我們要討論一下預設值，列一下哪些建議啟用，哪些預設啟用」, then 「那就改成版本走查跟地圖一起？我想要讓必要的成為預設，建議的寫在repo readme，adopter 安裝時讓使用者用ui選」.
- Outcome he named: release-acceptance and journey-map are one choice; the required extensions are the template default; the recommended ones are listed in the repository README; at install, the adopter chooses through a UI.
- Facts (0.29.0, 2026-10-25): the workflow template ships `extensions: []` (`references/sd/workflow.md`); `references/sd/adoption.md` § Extensions says an adopter lists what it uses; seven extensions exist (codex, copilot, journey-map, learn, peers, release-acceptance, roborev); release-acceptance applies only where a kc-journey-map file is kept; a sync PR keeps each adopter's own list, so a template default reaches new adopters only.
- Required set: the Captain (chat, 2026-10-25): 「我認為 peers 應該也要預設開啟，它不是只有給 paseo 也是給 cc/codex 的基本準則，不是嗎？」, after FO recommended learn only. Proposed default: learn and peers; recommended: journey-map with release-acceptance as one choice, codex, roborev; optional: copilot. To be confirmed at this task's backlog gate.
- Peers fact (0.29.0 `extensions/peers/EXTENSION.md` § Host bindings, 2026-10-25): Claude Code is bound (`ListAgents`, `SendMessage`); Codex is not covered (a `codex queue` message did not wake the session, 2026-10-12); Paseo is not listed (dev2 backlog peers-paseo-host-binding); without a bound host FO writes `peers not run: <host> …` and finds the answer itself. Its Read and Requests rules (a peer's words are never the Captain's ruling; a peer cannot grant authority) apply on every host.
- Upstream first: adoption runs through `spacedock:commission` or `spacedock:refit` plus `references/sd/adoption.md`; check whether either already asks the user to pick options before adding a question.
- Non-goals: turning anything on in the five existing adopters (each asked separately).

## FO alignment

Alignment: needed before ideation: the required set is the Captain's.
Result: aligned 2026-10-25 by the Captain's 「那就這樣做，learn+peers預設開啟，其他建議」 (chat), after his peers question.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
