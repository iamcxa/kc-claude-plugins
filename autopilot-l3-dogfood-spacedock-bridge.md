---
title: The spacedock-bridge L3 grant is read as the first dogfood of dev2's authorization framework, and its findings decide whether ADR 0011 gains an L3 route
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source (relayed by the Bridge FO, Paseo agent a88dedae, 2026-10-23; not a ruling in this session): the Captain 「我覺得這個 ADR 是基礎，但是我需要 dogfood 這個 pattern 讓它成為 dev2 的授權框架，因為最終的自駕路徑還不知道具體是怎樣，所以才需要找 dev2 FO 再給一次意見」, then his approval of the experiment design with one change: 「同意，就用這個方式。但改成每一輪摘要寫到一個 dev2 fo 可以存取的地方，不要讓它一直被你們打斷」.
- The experiment (adopter side, run by the Bridge FO): an L3 grant ADR for spacedock-bridge POC gates (task l3-grant-adr in kc-paseo-plugins docs/dev2-poc; in effect only when its ADR PR merges); per-round summaries appended to `_l3-dogfood/rounds.md` on branch spacedock-state/dev2-poc of iamcxa/kc-paseo-plugins (local: /Users/kent/Project/kc-paseo-plugins/docs/dev2-poc/.spacedock-state/_l3-dogfood/rounds.md): gates with ledger rows, the UAT line, Overrides, what UAT caught that validation missed, the observer result, cost, package gaps.
- FO's proposed exit (not measured, his to set): a 10-round or 2-week window; promote to a dev2 package ADR extending ADR 0011 only if each granted class has at least 5 decisions with 0 reversals and 0 observer violations on conn-recorded gates; demote a class to L0 on any reversal or violation; drop the pattern if two classes demote or UAT keeps catching what validation missed at the unchanged rate.
- This task: FO reads rounds.md when it chooses, files package gaps it shows, and at the exit proposes the package change (or none).
- Upstream first: ADR 0011 (delegation ladder; L3 not built), decision_ledger.py, the observer, backlog override-recorded-when-captain-departs.
- Non-goals: messaging the Bridge FO per round (the Captain's change).
- Added 2026-11-05: the Bridge experiment ended after 10 rounds (2026-10-23 to 2026-11-05; outcome report `_l3-dogfood/OUTCOME.md`, branch spacedock-state/dev2-poc of iamcxa/kc-paseo-plugins, commit a94f9cd; relayed by the kc-paseo-plugins dev2 FO, Paseo 8b2c2fc2, 2026-11-05). It lists 8 package gaps; FO spot-checked 3 against 0.35.0 on 2026-11-05 (the role_triggers.py model-rank gap no longer holds, `RANK` includes astra; the `spacedock new` empty-id gap does not apply under `id-style: slug`; the number_guards.py R4 POC gap holds) and owes the other 5.
- Added 2026-11-05: the Captain 「開」 (chat, 2026-11-05), answering 「要不要開一張待辦，把第 2 類做成套件裡可以選擇開啟的授權？」, after FO recommended making it an opt-in package grant rather than a dev2 default. Class 2 is project-env ADR 0007's merge-and-reload after his validation approval, renewed alone on his 「可以第二類」 (chat, 2026-11-05); relayed record: about 7 uses, no reversal. FO filed this here rather than as a new task because this task already owns the package proposal at the experiment's exit. Preconditions FO proposed for the grant: the validation approval quotes the bound question (see gate-presentation-asks-one-thing-plainly), the delivery check exits 0, and the Captain has not asked to hold merges for a batch release (counter-example in this repository: #766, 「先不合併，我想要把這些也評估修復後，再一起發版」).

## FO alignment

Alignment: needed at ideation; whether and how ADR 0011 gains an L3 route is his, after the exit.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
