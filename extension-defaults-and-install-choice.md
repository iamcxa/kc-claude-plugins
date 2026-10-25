---
title: Required extensions are on by default and an adopter picks the recommended ones at install
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
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
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
