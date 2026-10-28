---
title: An ideation preview the Captain judges is one static file with a switch bar
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: proposal from the subspace-web dev2 FO (Paseo agent 295b873d), 2026-10-24, sent with the Captain's approval as relayed by that FO (「同意把提案送給 dev2 fo」); the Captain's words that started it, as relayed: 「之後能夠做成，預覽切換是有按鈕的嗎？問一下 relay FO 它有做一個原型是最頂端統一有版本切換按鈕的，這說不定可以回饋給 dev2 fo 讓它規範最小的原型實作與展示契約，逐步可搭配 relay FO 正在規劃的 static-prototype release 2.1a，可納入原型在 SD review 用來呈現 gate」. Relayed words, not a ruling in this session; the Captain decides adoption.
- Bite: a Web design gate served three local previews chosen by `?query` parameters; on his phone over a tailnet they showed the desktop layout (no viewport tag). Relay's ideation prototypes (pair-once/prototype/, owner-decides-before-sign-in/prototype/ on relay's spacedock-state/dev2 at d51058ee, each a standalone.html plus REPLAY.md) were easier to judge.
- Proposed minimum for any ideation preview the Captain is asked to judge: (1) one static HTML file, CSS and script inline, no network, no server (relay's Release 2.1a static-prototype definition, relay draft PR #430); (2) a fixed top bar of buttons switching every option the gate asks about, light/dark and desktop/phone width, no URL parameters needed; (3) a `width=device-width, initial-scale=1` viewport tag; (4) a REPLAY.md beside it (reopen, pictures, rebuild from the dispatch record, design and review files); (5) built from the product's real stylesheet at a named commit, labelled a design artifact; (6) until Release 2.1a lets Spacedock Review publish it, the gate briefing names the file path.
- Upstream first: dev2 today has `design_surfaces.py check` requiring a `Preview:` line that exists for a `ui` task and a `design_review` naming it (origin/main, 2026-10-24); it says nothing about the preview's form. Spacedock Review publishing is relay's Release 2.1a, not built.
- Open for the Captain: whether to adopt, which points, and in which release; whether the design-surfaces check enforces any of them.

- Added 2026-10-28: the subspace-web dev2 FO (Paseo 295b873d) relayed the Captain's preference from its session: 「之後預覽組合統一使用類似的 layout，這樣比較方便讀，請跟 dev2 fo 講一下」. The layout he saw that day on web task decided-review-shows-amber's spike (six options): a left menu listing today and each option with a one-line description, then screen (desktop, widths, phone, real page), theme and state, with combinations that have no picture disabled; the chosen picture on the right with today beside it by default (toggle); arrow keys up/down for option and left/right for state; on a phone the menu becomes a sticky top bar; generated from picture file names `<option>-<screen>-<theme>-<state>.png`, with the long measurement table one link away. Reference copy: spacedock-dev/subspace-web, branch spacedock-state/dev2, decided-review-shows-amber/preview/viewer/index.html (about 45 lines, one file, no dependencies). Relayed words, not a ruling in this session; it refines point (2) above (a left menu, not a top bar, on a wide screen).

## Non-goals

- Spacedock Review publishing of the preview (relay's Release 2.1a); judging a design's content.

## Budget

- One package PR: the preview form in the ideation and design-director guidance, plus the viewer file if the package ships one; a `design_surfaces.py` check only if the Captain asks for enforcement.

## Stop condition

- web decided-review-shows-amber's six-option spike and one relay prototype replay as readable through the agreed form; return to the Captain on which points are required and whether a check enforces them.

## FO alignment

Alignment: needed before ideation; adoption is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
