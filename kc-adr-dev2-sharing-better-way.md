---
title: A better way for kc-adr's tools and skill to reach dev2 users than a copied directory and a two-plugin PR
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以，除非找到更好的做法。這裡可以立一張票未來再繼續研究有沒有更好的做法」 (chat, 2026-10-23), on kc-adr-tools-with-dev2-copy D4 (a kc-adr tool change is one PR touching both plugins, released with the next dev2 version).
- Current way (kc-adr-tools-with-dev2-copy, Captain Amendments 1 and 2, D1 to D4): kc-adr is the source; dev2 keeps byte-identical copies of the template, adr_lint.py and the read-adr skill folder, made by a sync script and compared in the required parity check; a kc-adr change cannot ship alone.
- Known facts: dev2-poc kc-adr-dependency-poc (2026-10-22): Claude Code plugin dependencies work, Codex has none, symlinks fail on both; run-time resolution worked on both hosts. ideation of kc-adr-tools-with-dev2-copy (2026-10-23): a nested plugin directory is not discovered; a skill folder in dev2's skills/ resolves as kc-dev-flow-2:read-adr. Under OMP, two plugins with the same skill name collide (deprecate-kc-dev-flow-v1).
- Bite: none yet; study when the copy's cost shows (two-plugin PRs, forced dev2 releases, OMP duplicates).
- Non-goals: changing the current way before a better one is shown.

## FO alignment

Alignment: needed at ideation; whether a better way replaces the copy is his.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
