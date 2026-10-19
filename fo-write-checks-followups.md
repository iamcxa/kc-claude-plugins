---
title: fo-write-checks follow-ups declined at the #671 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #671 delivery gate (head 13ceb00d, 2026-10-19); reasons also in that gate summary.

- P2 (Codex round 3, review:5568056809): an amendment range such as `Captain amendments 1-3` or `1 to 3` names only its two ends, so `--names` and L2 report amendment 2 as unnamed. A false hold, not a missed one; on 2026-10-19 `--names` over the 8 committed dispatch records that write a range printed no amendment line. Fix: expand an inclusive range before building the named set.
- Deferred risk (validation-2 F2): a prose line that begins with the reserved text (`ADR: 0042 is not used here ...`) satisfies the anchored reserved-line match. Material if FO leaves a reserved number unrecorded behind such a line.
- Deferred risk: a two-word bracket proves a bracket, not a reason (ADR 0025 records it).
- Deferred risk: any `amendment N` phrase in any checklist line of the task folder satisfies the amendment check.
- Polish: AC-4's text says 12 declined items; the true count is 13.
