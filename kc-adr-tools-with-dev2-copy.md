---
title: kc-adr holds the ADR writing tools, and dev2 ships a CI-synced copy so a dev2 user installs one package
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain, 2026-10-22: 「可以」 to FO's recommendation 「工具搬到 kc-adr，但用 dev2 的人只要裝 dev2 一個」: kc-adr is the source of the ADR template, the ADR format check and the ADR part of numbering; before each dev2 release CI copies them from kc-adr into dev2; CI fails when the copy and the source differ. Earlier the same day: kc-adr is the package for agents reading and writing ADRs, dev2 its first consumer and moneyflow its second (ruled in the kc-adr session, relayed), and 「安裝方式要再想想，我不想要那麼麻煩」.
- Evidence: dev2-poc task kc-adr-dependency-poc (validated, closed 2026-10-22): run-time resolution met all four bars on both hosts; Claude's native dependency works but Codex has none; symlinks are frozen on Claude and dropped on Codex. The copy-at-release shape was not tested there.
- First step, a test before any move: a real copied directory (not a link) inside dev2 installs on Claude Code and Codex from the marketplace with isolated configs, and a kc-adr change reaches dev2 users only through a dev2 release.
- Constraints: `number_guards.py` reserves ADR and migration numbers in one script and one reservation file (ADR 0002); the move states who owns the reservation file. The four adopters' README lines that call `adr_lint.py`, `number_guards.py` or the template change only if the copy's path changes.
- Partners: the kc-adr session (Paseo agent 1bcf070c) designs its side; this FO owns dev2's side and the CI copy.
- Upstream first: kc-adr's boundary contract (PR #691), release-please extra-files, version-parity-check.sh.
- Non-goals: run-time resolution; Claude native dependencies; changing any adopter's install.

## FO alignment

Alignment: needed at ideation; the reservation-file owner and the copy's path are the Captain's to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
