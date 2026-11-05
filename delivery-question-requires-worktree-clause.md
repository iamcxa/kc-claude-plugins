---
title: The delivery question check requires the worktree-removal clause the README's delivery authority names
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

`delivery_gate.py question` holds a validation gate question that omits "removing its clean, pushed worktree", so an approval cannot be read as covering a cleanup it never named.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 14 retrospective ask 「Should I open these two backlog tasks?」, whose second item was this check gap.
- Bite: the batch 14 merge questions for #786 and #787 omitted the clause; `delivery_gate.py question` and `check` both exited 0 on them; FO then removed both clean, pushed worktrees without that authority, and the extension-instruction-check-sees-every-listed-extension observer recorded it as a Delivery authority violation (observer.md, 2026-11-05).
- Upstream first: README Delivery authority ("removing its clean, pushed worktree"); `delivery_gate.py` question clause checks (`ASK_FORM` and the existing clause list).
- Non-goals: changing who may remove a worktree.

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- Replays of the #786 and #787 questions are held by `delivery_gate.py question`; the #788 question, which carries the clause, passes.

## FO alignment

Alignment: not needed: the clause is already the README's rule; the check only reads it.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
