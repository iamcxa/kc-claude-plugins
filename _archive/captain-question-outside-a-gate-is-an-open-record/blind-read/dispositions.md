# Dispositions of blind read 1 and of the probe, into contract revision 2

Numbering follows `reader-1.md` top to bottom; P-items come from the probe.
Changed: the contract states a rule now. Declined: unchanged, with the reason.

## Contradictions
1. Withdraw then answer. Changed: the first closing line decides; later lines are writer errors (section 4).
2. `acted` after `withdraw` or without `answer`. Changed: `acted` is valid only once, after an `answer` (section 4).
3. Section 5 collapsing `holds`. Changed: the blocked-or-continuing row is gone; `holds` keeps three values.
4. `version`. Changed: dropped; a new line with the key is the change signal.
5. Revise and "last shown". Changed: a revise is not a showing; showing a revised question writes a `reask` (3.3).

## Under-specified
6. Omitted field in a revise. Changed: a revise carries the complete new value; omitted means empty.
7. `recommend` naming a removed option. Changed: `recommend` must be an id in that revision's `options`.
8. `answer.revision` for a Review answer. Changed: the revision current at the latest showing in the answering channel.
9. Acting on an answer to an older revision. Changed: valid against that revision's options; otherwise a new key.
10. Wordless answer on a multi-option list. Changed: `option` comes from `approve_means`; with none, no wordless answer can be written.
11. Older revisions readable. Changed: stated (3.3).
12. Unknown `asked_at` sorting and correction. Changed: show unknown with the lower bound `now − at`; never corrected.
13. Forward compatibility. Changed: rule added (section 3).
14. Answered rows and "what waits on the Captain". Changed: only open rows wait on him; answered waits on the FO.
15. Flat task files. Changed: table in section 2.
16. Archived tasks. Changed: `_archive/<slug>/asks.jsonl`; an open question there is a writer error.
17. Enumeration over a branch. Changed: path pattern in section 2.
18. Duplicate key from a second `ask`. Changed: ignored (section 4).
19. Events before their `ask`. Changed: ignored (section 4).
20. `asked_at` later than `at`. Changed: by definition `asked_at` is `at` or null, so it cannot be later.
21. Fractional seconds. Changed: whole seconds.
22. `refs.kind: record` resolution. Changed: a Spacedock id in the same branch; `file` is relative to the task folder.

## Gaps against the six defects of the first hand-run sample
23. No later correction of an ask time (defect 1). Declined: a correction is an estimate made later, the defect itself; the lower bound replaces it.
24. Which acceptance item is held (defect 2). Declined: no reader named a use beyond the three `holds` values; `grounds` carries it as text.
25. A reference becoming ready needs a whole revise (defect 3). Declined: a revise is one command; a separate event would add a seventh event for a case seen once.

## Never needed by the blind reader
26. `acted.refs`. Changed: dropped.
27. `by.agent_id`. Changed: dropped; `by` is the session name.
28. `said_at`. Changed: dropped.
29. Derived `version`, `kind`, `task`. Changed: dropped from section 5 (`version` as in 4).
30. The writer section. Changed: dropped.
31. `refs.kind` beyond display. Declined: the decision-table reader renders by kind, which is a use.

## The decision-table reader's missing items
32. Per-option effect. Changed: optional `effect` on each option.
33. What a plain approve accepts. Changed: `approve_means`, set only when the shown question says so.
34. A question that belongs to no task. Changed in part: filed under the task in progress when it arose; one raised with no task in progress is outside version 1 and is design decision D1.
35. Project identity. Changed: carried by the checkout (section 2).

## From the probe (not in the blind read)
P1. One question answered into several tasks (2 of 14 on the replayed day). Changed: `tasks`.
P2. Legacy lines and key numbers. Changed: legacy lines take no number.
P3. The 0.41.0 timeline crashes on v1 lines. Not a format change; the writer and the timeline change in one pull request (design).

Totals: 35 reader points, 31 changed (one in part), 4 declined; 3 probe points, 2 changed the format.
