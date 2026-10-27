# 0026. Role calls are owed on counts read from task records, and a dated call clears them whatever it says

Date: 2026-10-20

## Status

Accepted

## Context

`role_triggers.py` owed a chief-engineer call on a `- Cycle N` line under `### Feedback Cycles` and cleared a call only when its question named `Cycle 3` or `Amendment N`. Over 38 window tasks in four repositories it read 0 events in the two that record cycles in stage-report headings, and it refused 3 of the 4 calls FO had made (two worded "third repair cycle", one filed under another heading). The Captain's direction on 2026-10-20 was counts from structured records, not keywords. The measurement, the per-task table and the falsified alternatives are in the task's `## Design`. This supersedes the wording-match clause of the special-role-triggers design (PR #664), which has no ADR of its own to amend.

## Decision

**Words:** 「設計時不應該過度依賴關鍵字，而是可能要依靠犯錯字數觸發，合理嗎？」 — Captain, 2026-10-20, chat; 「先加第一個，第二個列入評估」 — Captain, 2026-10-20, chat, on the engineering-reviewer model rule and the security-reviewer evaluation; at the ideation gate, 2026-10-20, D1 「同意」, D2 「第四輪」, D3 「Ａ」, D4 「Ａ」, D5 「同意」, each as the gate question recommended.

**Options considered:**
- Chief-engineer is owed at four repair passes, read as `## Stage Report: implementation` headings minus one (chosen, D2); three passes fires one more false case (go-live-consent); a sent-back count added one case and needs a free-text verdict match that leaves 105 of 410 validation reports unreadable; same-path review rounds, holds or overrides, ADR-draft headings and cross-references added no unique true catch or false-fired
- Engineering-reviewer keeps its replacing-amendment event, one line per task, cleared by a call dated no earlier than the amendment on a model no lower than the one required, or by a dated waiver (chosen)
- Model: Fable when the frontmatter says `profile: prod` or the `Surfaces:` line lists `db`, else Opus, never lower (chosen, D4); path or secret signals were not chosen (the authority-path signal marks 31 of 38 tasks, secrets have no field)
- Review rounds, two review ids with inline findings on an open task PR, also owe chief-engineer, as a last separate slice (chosen, D1)
- The four engineering-reviewer cases no count sees stay with judgment and no `Reverses:` line is added (chosen, D3)
- ADR 0021 D1 stays: stage 1 of the evaluation reads saved reports and runs no model, stage 2 waits for its result (chosen, D5)

**Recommended:** each of D1 to D5 as the gate question stated, which the Captain accepted.

A call or a waiver counts only as a `Reviewer:` line under `## FO alignment`, and a call counts by its date and model, not by its question. Later work that changes what owes a role call reads counts from committed task records and does not match phrases.

## Consequences

FO is told once per task and role, in the line `pr_watch.py tasks` already prints, until the call is recorded. A call on another question dated after an amendment now clears it. A count cannot see an authority change, a ruling reversed in another task or a new authority surface; those stay with the Captain and FO. The thresholds are in-sample on one 38-task window judged by four observers. Reopen when a batch shows an owed case the count missed twice in the same shape, or a false fire on a task whose extra passes were phases.

Amended 2026-10-22 (Captain: 「可以」 at the ideation gate of the task `merge-ask-holds-missing-clauses`, narrowing it to this one hold; 「按建議**不算**」 on D2): `delivery_gate.py check` runs `role_triggers.py` on the task folder and stem, without `--review-rounds`, and holds the merge ask while the committed task owes a chief-engineer call (four repair passes) or an engineering-reviewer call (a replacing amendment): exit 1 adds one problem line and the script's `next:` lines, exit 2 holds with its message (「可以」). Review rounds do not hold the ask; idle still prints that call (「按建議不算」). The script reads the task as committed, so an amendment not yet state-committed is not seen and a call not yet state-committed does not clear. "Told once per task and role" above still describes the idle line; a skipped call now also refuses the merge ask until the call or a dated waiver is committed.

Amended 2026-10-25 (Captain: 「都開」 on 2026-10-23 and 「可以」 on 2026-10-25 for the task `role-triggers-owe-ce-on-review-drift`; 「全准」 at its ideation gate on 2026-10-25, accepting D1 and D2 as the gate question recommended): a review-round event is cleared only by a chief-engineer call or waiver dated no earlier than the UTC date of the newest review round, which `pr_watch.py tasks` reads from the one comment list it already fetches and passes as `--drift-date`; a call about something else made before that round no longer clears it, and no file-path test is used (D1). A call made earlier on the same date as that round still clears it. Without `--drift-date` any call or waiver clears, as before; the repair-pass event keeps its undated clear. The merge ask still does not count review rounds (D2).
