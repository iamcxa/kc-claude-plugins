# 0080. Stage times come from state records and outside-gate questions are recorded when asked

Date: 2026-11-12

## Status

Accepted

## Context

The First Officer could recover stage times only by reading state commits by hand,
and questions outside gates had no record. The local proof of concept read times
for 135 of 157 archived tasks and matched the budget counter on all 62 comparable
tasks. The ideation gate of each-task-records-stage-time-revises-and-interruptions
accepted its four recommended decisions; Captain amendment 1 permitted this record.

## Decision

**Words:** 「五份都核准（建議）」 — Captain, 2026-11-12, host question dialog,
ideation gate of each-task-records-stage-time-revises-and-interruptions.

The timing portion of the bound question was 「一、計時紀錄：「重做」算同一階段第二次以後的派工；「打斷」算我在關卡以外問你的每一題，由我在問的當下記一筆；工具只報告缺漏、不擋任務；流程說明多 25 個字。」.

**Options considered:**
- Read stage boundaries from existing state records; count each dispatch after the
  first by the highest plain dispatch-record number, including gaps (chosen).
- Count gate revise decisions or follow-up messages as revises instead; those are
  different events and do not match the existing per-stage budget counter.
- Record each First Officer question outside a scheduled gate when asked (chosen),
  rather than infer interruptions from machine-local host transcripts or amendments.
- Report missing times without refusing work (chosen), rather than add a time gate.
- Add 25 workflow words for the ask-and-read commands (chosen), rather than leave
  the recording step outside the document the First Officer reads at that moment.

**Recommended:** The four chosen options, as the design recommended and the Captain approved.

**Protects:**
- `kc-dev-flow-2/scripts/task_timeline.py` — revise count, ask recording and missing-record reporting
- `kc-dev-flow-2/scripts/lint-skills.py` — the approved 25-word workflow budget step

Stage times use author dates of state commits and gate resolution or withdrawal
stamps. Before-gate time includes First Officer idle and is not a measurement of
worker execution alone. Each question outside a scheduled gate is appended to
`<task>/asks.jsonl` when asked. Gate revise decisions, withdrawn attempts and
amendments remain separate from the interruption count. A missing ask file means
unknown, not zero. The helper reports missing records; it imposes no work hold.
The workflow budget rises by 25 words under ADR 0020. ADR 0077's cycle budgets
remain in force; minutes do not spend them.

## Consequences

One command recovers stage times and counts on either host from shared state.
A dispatch after worker failure counts as a revise; follow-up messages do not.
An omitted ask silently undercounts, and unprompted Captain messages are not asks.
Startup reading grows by 25 words. Comparison against hand records for three
post-release tasks, a real Codex First Officer and its questions remains owed.
Reopen if those observations show that the shared records cannot supply reliable
boundaries or that manual ask recording misses the approved interruption measure.
