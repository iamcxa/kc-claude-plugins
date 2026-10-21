---
title: The peers extension carries a Paseo host binding, so an FO under Paseo can list and wake a peer FO
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain, batch-5 sitting 2026-10-21: 「應該寫成，按照peers ext做，如果沒啟用或是沒有可用的peers就發issue。或是做一個paseo ext讓fo知道怎麼用paseo cli。合理嗎？因為不是每個人都用paseo 作為harness」 and 「對，就照這樣。任務也要開」, approving FO's proposal 「不另做 paseo 擴充功能，改成在 `peers` 裡加一份 Paseo 的說明」.
- Verified 2026-10-21: kc-dev-flow-2 0.27.0 `extensions/peers/EXTENSION.md` § Host bindings covers Claude Code only ("Codex: not covered", "Other hosts: not covered"). On 2026-10-20 and 2026-10-21 FOs in this fleet listed sessions with the Paseo MCP `list_agents` and woke peers with `send_agent_prompt` (the kc-paseo-plugins, subspace-web and decision-log FOs reached this FO, and this FO reached the qnow and decision-log FOs); the sender is stamped by the Paseo envelope.
- Shape asked for: one Paseo binding under Host bindings (list, address, wake, read the sender), harness-neutral wording elsewhere, so the codex-reader upstream line ("report through `peers`, otherwise a drafted issue the Captain approves") works under Paseo and under Claude Code alike.
- Upstream first: `peers` EXTENSION.md, the Paseo skill and MCP tool contracts (read their own docs), memory of peer messaging limits (a peer can answer another agent's permission prompt; never approve one).
- Non-goals: a separate Paseo extension; a Codex binding.

## FO alignment

Alignment: not needed before ideation; the Captain chose the shape.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
