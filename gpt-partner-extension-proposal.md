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
- Added 2026-10-23: the Captain (chat): 「codex 夥伴任務新增一個點，可以按狀況選用派 astra/sol 當 ensign worker，目前 qnow fo 正在 dogfood。如果效果跟本來一樣好，那我希望 codex 夥伴要納入來做，這樣可以明顯分攤額度消耗，提升並行效率，因為他們額度較便宜，所以同樣等級模型可以開更高的推理」. Conditional on the qnow FO's dogfood showing results as good as the Claude ensigns; that comparison is the evidence to read when the discussion reopens. Related backlog: dispatch-sets-reasoning-effort.
- Added 2026-10-25: the Captain (chat): 「可以」, answering 「需要你決定：kc-paseo-plugins 第一次真的版本走查，挑剔使用者可以用 Codex（astra）加 Antigravity（gemini）這兩家嗎？還是照現在的規定，只用兩個 Claude 模型？我建議這一次破例用兩家，並記成例外。」 An exception for that first release-acceptance walk only; its record is evidence for this task. Also seen 2026-10-24: the Bridge FO (a Claude FO) launches gpt-6-astra and gpt-6.1-sol ensigns and picky users as Paseo Codex agents, so a Claude FO reaches Codex workers through Paseo `create_agent`.
- Added 2026-10-27: the Captain (chat): 「既然是這樣多測試一次 gemini，用 agy，也許之後可以跟 codex 一樣出一個 gemini ext」, while validating worker-knows-the-team-and-asks-early (#729), whose worker replays then ran on Claude, Codex and Gemini through agy 1.4.7. A Gemini extension like `codex` is a further candidate for this proposal's discussion, not approved work.
- Added 2026-10-27: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat), placing multi-model review here. Evidence (relayed by the kc-ops-inbox FO, data not a ruling): on PR #727 at 36973c77 (a contract two adopters will pin) engineering-reviewer (opus) found no P1, Codex gpt-6-astra (`codex exec -s read-only`, scoped file list) 2 P1 and Gemini 4 Argon (`agy --print`, files inlined) 3 P1, each finding something the others missed. That FO's proposed shape: one shared brief at a frozen SHA, trigger on hard-to-reverse surfaces (pinned contract, auth or security boundary), FO cross-tabulates and probes every disputed claim; `/paseo-advisor` as a possible launcher. Cost measured there: ER 112k subagent tokens and 523 s; Codex and agy token cost not measured.
- Added 2026-10-27: the Captain (chat): 「不加。但是長期來說不是要加到長期記憶，而是要加到使用它的地方，例如 gemini 夥伴ext 內」, declining a learning.md entry from learn job 229f31f6 (worker-knows-the-team-and-asks-early). Requirement for a Gemini extension: `agy --print` run headless needs a HOME whose MCP config has no unauthenticated servers; in the real HOME every turn timed out while linear-mcp-server and notion-remote kept connecting (validation-2 of that task, agy 1.4.7, 4 smoke attempts), and with HOME pointing at a copy of ~/.gemini with an empty MCP config all 12 replays ran. `--mode auto` printed 'not available for this account' and ran with permission_mode always-proceed; `run_command` is terminal-sandboxed, so writes outside the workspace fail.
- Added 2026-10-27: the Captain (chat): 「不須要，但這裡有一個概念，我們做了peer插件，也討論過codex夥伴跟gemini夥伴，但還沒討論過一個點是何時使用多模型在關鍵時刻彼此支援。其他全照建議」. An open question for this proposal: at which moments different models support each other (for example a batch review by a model of another family than the workers, a hard-to-reverse contract reviewed by two or three families as on #727), as distinct from a partner that runs beside a role.
- Non-goals: anything before the Captain reopens the discussion.

## FO alignment

Alignment: needed before ideation; the Captain holds this as a proposal to discuss later.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
