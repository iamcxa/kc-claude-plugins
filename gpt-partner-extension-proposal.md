---
title: An optional GPT partner extension runs beside chief-engineer, design-director and engineering-reviewer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「astra 輔助這裡，我想是否可以設計一個 ext 是 gpt peer partner？等於會有平行的 CE, 「設計總監」, ER 在同階段並行跑，使用者可以選擇是否開，這件事很可能可以稍微抵銷 pr 時等待 codex 審查的輪數」, then 「如果要加 GPT 同伴，那就要把 codex 跟 copilot 明確改成 codex-review and copilot-review，新的就叫做 codex-peers 之類的？」, then 「GPT 同伴仍保留提案，之後再討論」 (chat, 2026-10-22). A proposal held for later discussion, not approved work.
- Evidence so far: dev2-poc roborev-threshold-catches-pr-findings-poc (closed 2026-10-22): the local roborev Codex review caught 1 of 5 Codex PR findings at medium and low, so a pre-PR GPT code pass did not remove most PR rounds; the UI design review measurement (dev2 task design-director-runs-ui-design-review, intake) found the sonnet review's gap was declines, not misses.
- Naming noted by FO, not ruled: `peers` is already the session-messaging extension, so a name such as `gpt-partner` or `codex-partner` avoids reading as its variant; renaming `codex` and `copilot` to `codex-review` and `copilot-review` would change the four adopters' `extensions:` lists, so it would ship in the same PR as the new extension with the old names still accepted.
- Upstream first: kc-dev-flow-2 extensions codex, copilot, roborev, peers (none pairs a GPT run with a role); `codex exec` (`-m`, `-i` images).
- Added 2026-10-23: the Captain on release-walk-picky-reviewers-and-director D3: 「可以先用同模型。我在想這裡其實應該要用類似 ext 做法，我之前提過的，等於該 ext 會啟用不同模型的支援能力，這樣比較能排除問題」. The extension's scope now includes enabling release-walk reviewers (picky users) on non-Claude providers; that the release walk needs this is evidence for reopening the discussion. Unverified: a non-Claude reviewer operating a product from a Claude-hosted FO (dev2 workers follow the FO's host; codex exec --sandbox read-only reads code only).
- Non-goals: anything before the Captain reopens the discussion.

## FO alignment

Alignment: needed before ideation; the Captain holds this as a proposal to discuss later.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
