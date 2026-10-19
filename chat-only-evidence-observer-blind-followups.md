---
title: chat-only-evidence-observer-blind follow-ups declined at the #679 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #679 delivery gate (head 59fc3d12, 2026-10-19); reasons also in that gate summary.

- Deferred risk (validation cycle 2): `clause()` in `delivery_gate.py` reads a label after an abbreviation as a stated clause (`add a clause, e.g. Necessity: y` returns `y`), and does not read a markdown bullet or bold label (`- Sufficiency: x`, `**Sufficiency:** x`), which holds the ask until the label is on its own line. Material if a gate text that only mentions a label passes and the observer then reads `ok` from it.
- Polish: the shortened list phrase "FO answers a question the Captain asks at a gate" leaves "before dispatching on it" unwatched by the chat-only-rules lint (the full phrase trips the lint's 12-word duplicate check).
- Polish: AC-7's candidate observer run left 5 `can't tell` rows against the design's "at most four"; the two extra rows (a Captain ruling whose question is in chat, observing the PR merge) are outside the listed rule set. One sample, not re-run at 59fc3d12.
- Polish: the chat-only-rules lint matches a phrase as a substring of the joined words, so a phrase also passes inside a longer sentence.
