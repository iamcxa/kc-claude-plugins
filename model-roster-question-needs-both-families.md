---
title: Model roster question asks only when Paseo, Codex and Claude are all available, and offers Claude models
status: backlog
variant: kc-dev-flow-2
---

The roster question appears only when Paseo, Codex and Claude are all available; otherwise nothing is asked or written and workers follow the FO's family.

Source: the Captain, chat 2026-11-02: 「應該預設是用 claude 做 fo 時，就是都預設 claude 家族，codex 亦同，是只有使用者提出時才要寫入 .dev2/model-roster.json」, then 「主動詢問不必拿掉，但是應該是條件式的，也就是必須要是有 paseo + codex +cladue 都存在時才可以用」, and 「構思改用 opus high」. He approved opening this task: 「開，可以」, answering FO's list below.

Scope, as FO stated it and he approved:
- The question's condition adds Claude available to the existing paseo listed and Codex available.
- The recommended set becomes ideation Opus high, implementation Sol high, validation Astra high.
- The roster accepts Claude and Opus; first verify that Paseo can set Opus to high.
- Draft PR iamcxa/kc-claude-plugins#762 is updated to that set after release, then asked for merge.
- The interim directive to dispatch on Sol and Astra ends for repositories with no roster.

Bite: 0.34.0 asks with Codex alone and its roster rejects Opus, so the Captain's chosen ideation model cannot be recorded (`model_roster.py`, MODELS and the provider check, read 2026-11-02).

Consumer: this repository's stage dispatches, through #762.
