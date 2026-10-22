---
title: A prod task whose design splits into slice tasks owes a chief-engineer route review before its ideation gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「建議開」 (chat, 2026-10-22), answering FO's 「要開一張任務來做「prod 任務拆片前必須先找 CE」的強制嗎？我建議開。」, on the qnow dev2 FO's relayed experience and the Captain's request relayed with it, 「2直接把這個經驗交給 dev2 fo 讓他評估是否改進。也要他跟我說明目前設計審查是怎麼做的，因為我沒看到 designer-direcitor 角色，以及是否非設計審查就走 ce or er 審查」 (relayed by the qnow dev2 FO, Paseo, 2026-10-22).
- Bite (relayed by the qnow dev2 FO, 2026-10-22, not re-read here): qnow task qnow-release-migration (prod) passed six ideation gate attempts, then split into three slice tasks, each with its own reviews. After Slice 1 was built and validated, an FO step-back found four route problems no per-slice review could see: no change reaches any site between Slice 2's trunk flip and Slice 3's repoint; a false FO claim to the Captain that merging to `next` deploys nothing; `main` promoted with leftover top-level files; a new `v0.x` tag line colliding with legacy `v4.*` tags.
- Shape asked for: `scripts/role_triggers.py` owes a `kc-dev-flow-2:chief-engineer` call when a `profile: prod` task's design splits into two or more slice tasks, cleared by a dated call or waiver under `## FO alignment` before its ideation gate is prepared.
- Upstream first: the chief-engineer skill's existing trigger "a Pilot or Production transition needs delivery sequencing" (the rule exists; nothing enforces it); `role_triggers.py` events (repair passes, Captain amendments); `delivery_gate.py` hold C (PR #703) as a later reader; Spacedock `gate prepare`.
- Non-goals: a new reviewer role; a design-director role (measured separately, see the Captain's request above); changing engineering-reviewer triggers.

## FO alignment

Alignment: needed at ideation; how a split is read from task records is the design's to propose and his to accept.
Surfaces: none
Visible change: none
