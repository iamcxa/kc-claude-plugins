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
- Declined by FO at the #675 delivery gate (validation cycle 3 F7, Deferred risk): `delivery_gate.py` prints the carried-merge `next:` line on every exit-0 run, including runs whose own record says `verdict: ask` (`class: never`, a `point:` line, prod, db). Every task PR still reaches its validation gate question, which is the ask that verdict calls for, so no merge happens without his approval today; it becomes Material if a merge is ever carried without that question. Fix sketched: print the carried line only when `verdict == "merge"` (the `verdict` assignment in `check`), else the old ask line.
- Polish (validation F6): ADR 0023's Options text says "merging the head" without the `--match-head-commit` binding the README now carries.
- Polish (captain-question-load validation F5, declined at the #675 delivery gate): the three documents `doc_impact.py` lists (kc-dev-flow-2/README.md, references/sd/adoption.md, learning.md) carry no `updated` or `unaffected` line in the implementation reports; each names only the `test_sd_dispatch.py` command.

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: its two live items (the carried-merge next: line printed without reading the approved question or a hold, and printed even when the verdict is ask) were taken into fo-write-rules-checked, whose design answers them as D2 and D3; the other items are closed with reasons in that triage.
