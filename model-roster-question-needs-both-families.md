---
title: Model roster question asks only when Paseo, Codex and Claude are all available, and offers Claude models
status: backlog
variant: kc-dev-flow-2
profile: pilot
---

## Scope

- Source: the Captain, chat 2026-11-02: 「應該預設是用 claude 做 fo 時，就是都預設 claude 家族，codex 亦同，是只有使用者提出時才要寫入 .dev2/model-roster.json」, 「主動詢問不必拿掉，但是應該是條件式的，也就是必須要是有 paseo + codex +cladue 都存在時才可以用」, 「構思改用 opus high」 and 「開，可以」. Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」.
- Bite: 0.34.0 asks with Codex alone and its roster rejects Opus, so the Captain's chosen ideation model cannot be recorded (`model_roster.py`, MODELS and the provider check, read 2026-11-02).
- Consumer: this repository's stage dispatches, through Draft PR iamcxa/kc-claude-plugins#762.
- The question's condition adds Claude available to the existing paseo listed and Codex available; otherwise nothing is asked or written and workers follow the FO's family.
- The recommended set becomes ideation Opus high, implementation Sol xhigh, validation Astra xhigh. FO verified on 2026-11-02 with Paseo list_models that claude-opus-5-5 offers high and that gpt-6.1-sol and gpt-6-astra offer xhigh.
- The roster accepts Claude and Opus. `max` and `ultra` stay accepted and are not recommended; the recommendation stops at xhigh.
- #762 is updated to that set after release, then asked for merge. The interim directive to dispatch on Sol and Astra ends for repositories with no roster.
- Upstream first: `references/model-roster.md`, `references/model-roster-defaults.json`, `scripts/model_roster.py`, `references/sd/adoption.md`; Paseo's list_models.

## Non-goals

- Native dispatch model passthrough (spacedock-dev/spacedock#845); capacity automation; usage measurement.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A repository lacking any of the three asks nothing and writes nothing; one with all three is asked once; a roster naming Opus resolves and dispatches a real Claude ideation worker with the requested settings. If Paseo cannot apply them, stop and return to FO.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
