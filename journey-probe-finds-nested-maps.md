---
title: The journey-extension install probe finds maps in nested product folders
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-26), answering FO's ask to file this and the Codex-reader task.
- Bite: Codex P2 on iamcxa/kc-claude-plugins#716 (head 8340c3ba, 2026-10-25T04:30:35Z), unaddressed at merge: `kc-dev-flow-2/references/sd/adoption.md` probes `docs/journey/*.yaml`, but kc-journey-map's README documents `docs/journey/<product>/<journey>.yaml` for multi-product adopters, so the probe rejects valid maps and leaves both journey extensions off. Still on origin/main c70f1b22 (`git show origin/main:kc-dev-flow-2/references/sd/adoption.md`, 2026-10-26).
- Upstream first: kc-journey-map README (map locations) and its own map-finding code, before writing a new glob.

## FO alignment

Alignment: not needed: a recorded review finding against the documented map layout.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
