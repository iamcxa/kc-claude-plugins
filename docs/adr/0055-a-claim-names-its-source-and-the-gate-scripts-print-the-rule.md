# 0055. A claim names its source and the gate scripts print the rule

Date: 2026-11-03

## Status

Accepted

## Context

The task claims-name-their-source records two confirmed reporting errors. On
2026-10-22 FO told the Captain that design_surfaces.py printed preview paths,
then corrected the statement: it repeated the design worker's report without
checking the script. The read-adr-reporting-rule-followup gate summary and PR
body named two unmeasured cells; its engineering reviewer found three. The
task's Design names the original transcripts and state records, re-read by
ideation on 2026-11-03. These are the ideation report's findings, not a new
execution of those historical checks by implementation.

The ideation report's count-pattern replay (not run by implementation) read
committed validation briefings at these state revisions, pinned before
2026-11-03T08:00:26Z:

| State | Revision | Briefings | Would hold |
| --- | --- | --- | --- |
| kc-plugin dev2 | 37d56950f | 119 | 88 |
| relay | 54350ff14 | 122 | 65 |
| v0 | a392c74af | 17 | 5 |
| web | e009f7087 | 69 | 46 |
| qnow | aa5bb2e38 | 135 | 71 |
| Total | | 462 | 275 |

The proposed hold passed the wrong kc-adr limit while holding its correct
numeric result. A source bracket cleared the hold without correcting a count.
The chat claim did not reach a script. ADR 0027 D4 rejected a phrase check
because matching words cannot stop that class of error.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-03, ideation gate of
claims-name-their-source, gate attempt 1.

**Asked:** 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」
The task's gate record accepts its recommended decisions: a written rule
printed at both gates without a hold, the 55-word README raise required by
ADR 0020, and a 24-run behavioral replay with a hard stop at 30.

**Options considered:**
- Write the source rule and print it at both gate commands, without a new
  refusal (chosen, following ADR 0027 D4).
- Hold summaries matching a count pattern without a dated source bracket;
  the reported replay misses the wrong limit and holds correct statements.
- Ship on presence checks without the behavioral replay; cheaper, but it
  does not test what FO writes.

**Recommended:** The written rule, +55 words and bounded replay, as approved.

**Protects:** none

Each number or factual claim in a gate summary or PR body names the command
that produced it and its date, or names whose report it repeats as
`<whose> report, not run` without stating it as settled. In a Captain message
the source follows the sentence answering him. The observer judges the
committed-summary half and lists the chat half as not judged under ADR 0024.
delivery_gate.py question and check print the reminder on entry; their existing
holds and exit codes remain. The WORKFLOW_BUDGET_STEPS entry records the
Captain's words and startup loading, raising 5836 to 5891 after ADR 0054.

The behavioral replay compares the base and candidate on both historical
scenarios, Claude and Codex, three runs per cell. Candidate needs five of six
passes in each scenario. If the base also meets both bounds, FO returns the
unneeded README raise to the Captain; the printed reminder alone may ship.
Only no-answer runs may be retried, within the 30-run hard stop.

## Consequences

Startup reads 55 more words and each gate invocation prints 27 more words,
counted by whitespace splitting. The reminder adds no source-pattern hold.
A command and date make a claim checkable; they do not establish truth.
An honestly attributed but incorrect report can still reach the Captain, and
chat still depends on FO following the rule. The replay has three runs per
cell, combines the README and printed line in the count scenario, and excludes
Kent's global instructions; it does not establish behavior in his daily FO.
Reopen if the bounded replay does not meet its bar, if the base already meets
both bounds, or if a later structured claim record supports a useful refusal.
