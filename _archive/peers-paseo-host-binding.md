---
title: The peers extension carries a Paseo host binding, so an FO under Paseo can list and wake a peer FO
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
verdict: REJECTED
completed: 2026-10-27T15:13:47Z
archived: 2026-10-27T15:13:47Z
---

## Scope

- Source: the Captain, batch-5 sitting 2026-10-21: 「應該寫成，按照peers ext做，如果沒啟用或是沒有可用的peers就發issue。或是做一個paseo ext讓fo知道怎麼用paseo cli。合理嗎？因為不是每個人都用paseo 作為harness」 and 「對，就照這樣。任務也要開」, approving FO's proposal 「不另做 paseo 擴充功能，改成在 `peers` 裡加一份 Paseo 的說明」.
- Verified 2026-10-21: kc-dev-flow-2 0.27.0 `extensions/peers/EXTENSION.md` § Host bindings covers Claude Code only ("Codex: not covered", "Other hosts: not covered"). On 2026-10-20 and 2026-10-21 FOs in this fleet listed sessions with the Paseo MCP `list_agents` and woke peers with `send_agent_prompt` (the kc-paseo-plugins, subspace-web and decision-log FOs reached this FO, and this FO reached the qnow and decision-log FOs); the sender is stamped by the Paseo envelope.
- Shape asked for: one Paseo binding under Host bindings (list, address, wake, read the sender), harness-neutral wording elsewhere, so the codex-reader upstream line ("report through `peers`, otherwise a drafted issue the Captain approves") works under Paseo and under Claude Code alike.
- Upstream first: `peers` EXTENSION.md, the Paseo skill and MCP tool contracts (read their own docs), memory of peer messaging limits (a peer can answer another agent's permission prompt; never approve one).
- Non-goals: a separate Paseo extension; a Codex binding.

- Added 2026-10-25: the Captain (chat): 「可先建這些設定檔。未來如果要做 SD paseo plugin 可能不會有這些設定檔，因為這是 dev2 專有的，所以 paseo ext可能還是必要」, after FO proposed Paseo agent profiles (dev2 general worker, dev2 special role, Codex worker, Codex reviewer, Gemini picky user) set up by hand before any extension. This reopens the 2026-10-21 choice above (no separate Paseo extension; a Paseo binding inside `peers`): a dev2 Paseo extension may be needed to map dev2 roles to Paseo profiles, which a Spacedock Paseo plugin would not carry. Paseo facts (2026-10-25): `list_profiles` returned none; the paseo skill says to read every profile's `notes` before `create_agent` and fall back to provider discovery when none fits; the paseo-advisor, paseo-committee and paseo-handoff skills all pick by profile notes.
- Added 2026-10-25: Paseo offers no supported way for an agent to create a profile (MCP has `list_profiles` only; the CLI has no profile command; `~/.paseo/config.json` has no profiles key); the Captain created the five profiles in the app, and `list_profiles` read them back the same day (Codex profiles use mode `auto-review`). A dev2 Paseo extension can point users at the app, not create profiles.

## FO alignment

Alignment: not needed before ideation; the Captain chose the shape.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Closed

Closed 2026-10-27, the Captain 「全准」 (chat) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」. Done by peers-rules-name-each-host-binding (iamcxa/kc-claude-plugins#730, merged 2b3e505c): peers binds by how a peer reaches the session, so an FO under Paseo lists and messages peers through Paseo, and the optional paseo extension covers proactive asks.
