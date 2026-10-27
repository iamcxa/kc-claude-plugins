---
title: The Codex reader's same-head rule is recorded as an ADR quoting the Captain's ruling
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「補」 (chat, 2026-10-27), answering 「需要你決定：要不要開一張小任務，補一份 ADR 記下 D1？我建議補。」.
- Bite: observer report on codex-reader-same-head-unresolved (_archive/codex-reader-same-head-unresolved/observer.md, 2026-10-27): its ideation D1 is an enduring ruling, and the README's FO steps: decision records require it landed as an ADR before the next gate; none was reserved or landed before #728 merged (d8e9204b).
- The ruling: the Captain 「全准」 (chat, 2026-10-27) accepted D1 as recommended in the ideation gate question of codex-reader-same-head-unresolved: a person's resolved mark on a GitHub thread does not clear a Codex finding on an unchanged head; the finding holds until the head moves or FO declines it in the gate summary.
- Outcome: one ADR file under docs/adr quoting his words from that gate record, and nothing else; no code change.
- Upstream first: docs/adr (ADR 0004 and ADR 0013 on reading Codex), `extensions/codex/EXTENSION.md`, `scripts/adr_lint.py`.

## FO alignment

Alignment: not needed: the ruling and its words are recorded in the archived task's gate records.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
