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
- Waived by the Captain at captain-question-load (#675, amendment 2, 2026-10-19), from Codex round 2 (review:5569986438): a merge-time `delivery_gate.py check` rerun writes a second `merge/ask-N.json` for an ask that never happened; nothing in the package reads the record (`git grep ask-` at 1704ec80). Fix sketched in phase 1: about 6 lines in `write_record` reusing the latest record when all but the time match.
- Waived by the Captain at the same point: roborev:875/878 High, `delivery_gate.py` prints the merge line without reading the approved question or a hold. Reopen per ADR 0023: a merge on an approval whose question did not name the merge, or after he said to hold. Fix sketched: at merge time read the approved gate entry and its question (`decision_ledger.py` `gate_entries`), about 12 code and 30 test lines (estimate); the hold stays FO's reading.
