---
title: Ideation checks standards and known patterns before designing a mechanism
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「是否可以讓 dev2 在構思階段時，傾向先找 RFC 有沒有類似解決方案？避免發明很接近但考慮沒那麼全的方案？」 (chat with the qnow dev2 FO, 2026-11-10), relayed by Paseo 519ab4c8 with his 「把這個想法和案例送給開發流程負責人」 (relayed, not a ruling here; the backlog gate confirms it).
- Bite (the qnow FO's report, not re-run here): on qnow task booking-attempt-identity (ideation 2026-11-10; first dispatch record dispatch/ideation-2.md, pinned base 706b01fdb04b5d0b17b213562296dc95eaa60368, state branch spacedock-state/dev2 of iamcxa/qnow) the ideation worker designed a client-side attempt-ownership mechanism and duplicate-send key handling from scratch; asked afterwards, the qnow FO found the WHATWG AbortController/AbortSignal primitive and the IETF Idempotency-Key header draft unmentioned, and on sibling task owner-cancels-booking the design director's MAJOR race finding has RFC 9110 conditional requests as the standard answer.
- Package fact (FO read 2026-11-10, kc-dev-flow-2 0.37.0 `skills/ideation/principles.md`): it asks for the bounded existing-code check and for research when missing facts can change the decision; it does not ask for standards or known library patterns, nor for adopt, adapt or reject.
- Suggested direction (qnow FO, not a ruling): one ideation principle line, perhaps a short prior-art part of the design (standards, drafts, library patterns considered; adopt, adapt or reject with a reason), bounded so ideation is not a literature survey; shown by a Behaviour replay of that ideation dispatch at the release tag versus the change, plus a control task with no relevant standard.
- Process asked by the qnow FO: send it the proposal and the replay plan, and get its confirmation against the case, before any package edit.
- Non-goals: changing qnow's designs; a mandatory survey on every task.

## Budget
- One package PR to the ideation skill text and its tests; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The replay's changed arm names the relevant standards for the qnow case and the control stays short and cites none, or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; how far ideation looks outside the repository, and what it costs each task, are the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
