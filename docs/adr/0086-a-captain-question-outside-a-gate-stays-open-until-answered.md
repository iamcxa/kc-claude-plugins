# 0086. A Captain question outside a gate stays open until answered

Date: 2026-11-14

## Status

Accepted

## Context

ADR 0080 recorded interruptions in asks.jsonl but held no open-question state.
The approved Pilot probe found no records for nine questions asked after that
rule reached the workflow. Its blind read led to contract revision 2, including
an explicit approval option, option effects and affected tasks. The Captain
approved the five design recommendations, reopening the report-only choice for
missing amendment-question records.

## Decision

**Words:** 「開「待決定事項紀錄」任務，照這個範圍」 — Captain, chat,
2026-11-13, answering whether to open the question-record task; then
「核准待決定事項紀錄的設計，五項都照建議」 — Captain, chat,
2026-11-14, its ideation gate; then 「待決定事項紀錄的說明句補上 --by "<session>"，啟動字數從 39 改成 41」 — Captain, chat,
2026-11-14, Captain amendment 1.

**Options considered:**
- D1: first file a proposed task and use its backlog gate when no task is in
  progress (chosen); a second workflow-wide asks folder or unrecorded questions
  would create another writing location or omit them.
- D2: list unresolved native gate attempts beside questions with waits marked
  at least (chosen), rather than require every reader to merge them.
- D3: use the state branch as the common record, retaining Review for long
  questions and recording its resolution id (chosen), rather than publish every
  question as a briefing.
- D4: flag three showings without Review in the list (chosen), rather than add
  startup instructions or postpone the flag.
- D5: refuse an amendment with an unrecorded quoted question (chosen), allowing
  a late record with an unknown asking time, rather than keep report-only checks.

**Recommended:** D1 through D5 as the ideation gate recommended and the Captain
approved.

**Protects:**
- `kc-dev-flow-2/scripts/task_timeline.py` — question events, open listing and interruption counts
- `kc-dev-flow-2/scripts/design_surfaces.py` — dated amendment-question omission refusal

The record's format has one home in
`kc-dev-flow-2/references/captain-question-records.md`. A question remains open
until its answer or withdrawal is recorded; acted follows an answer once.
Legacy lines remain readable and do not imply an open state. The omission rule
starts from the adopted workflow's first commit introducing the ask sentence,
not from the state checkout's layout or a guessed date. Unavailable history
skips that rule with a diagnostic. This amends ADR 0080 only for this record and
its omission refusal; the ask sentence grows from 25 to 41 words at startup,
with its approved budget step under ADR 0020. Timing and missing-time reporting remain unchanged.

## Consequences

A declined no-task proposal leaves a closed task file. Native gate waits can be
understated because Spacedock does not stamp prepare time. FO still has to read
the list and record questions at asking time; the omission check proves only
that a record exists by the next gate. A live released day, a second blind reader
and a remote reader remain separate evidence. Reopen if those observations show
that the contract cannot represent the questions or preserve their ownership.
