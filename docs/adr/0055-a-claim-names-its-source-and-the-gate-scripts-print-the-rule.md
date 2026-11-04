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

**Amendment 1 words:** 「可以」 — Captain, chat, 2026-11-04.

**Asked (amendment 1):** 「決定：來源標註的 AC-3 改成只用 Claude，各情境新規則補到 6 次、照原本 6 次過 5 次判定（Codex 半場記為這台機器跑不了），可以嗎？」

**Amendment 3 words:** 「甲」 — Captain, chat, 2026-11-04.

**Asked (amendment 3):** 「決定：來源標註照現狀出貨，K 情境 3/6 記成已知限制，另開一張專門處理數字附出處的追蹤任務，可以嗎？」
These later rulings narrow the replay and accept the count-scenario limit
below; amendment 3 replaces amendment 1's acceptance criterion.

**Options considered:**
- Write the source rule and print it at both gate commands, without a new
  refusal (chosen, following ADR 0027 D4).
- Hold summaries matching a count pattern without a dated source bracket;
  the reported replay misses the wrong limit and holds correct statements.
- Ship on presence checks without the behavioral replay; cheaper, but it
  does not test what FO writes.

**Recommended:** The written rule, +55 words and bounded replay, narrowed to
Claude with the known count-scenario limit and follow-up accepted above.

**Protects:** none

Each number or factual claim in a gate summary or PR body names the command
that produced it and its date, or names whose report it repeats as
`<whose> report, not run` without stating it as settled. In a Captain message
the source follows the sentence answering him. The observer judges the
committed-summary half and lists the chat half as not judged under ADR 0024.
delivery_gate.py question and check print the reminder on entry; their existing
holds and exit codes remain. The WORKFLOW_BUDGET_STEPS entry records the
Captain's words and startup loading, raising 5836 to 5891 after ADR 0054.

The ruled proof uses Claude only: `claude-opus-5-5` through
`claude -p --safe-mode`, normal HOME and a scratch working directory. The
Codex half is not runnable on this machine: `codex exec --help` lists no
supported way to skip the global AGENTS.md with normal CODEX_HOME. The
original hard stop remains 30 attempts, with retries for no-answer runs only.

The task's retained `validation/implementation-2/results.md` and
`validation/implementation-3/results.md`, independently read again in
`validation/validation-2/`, distinguish the two historical scenarios:
- P, the preview-path claim: candidate 6 of 6 against base 1 of 3. Each
  candidate labels the claim as the design worker's report, not run.
- K, the unmeasured-cell count: the disputed limit itself is labelled in
  candidate runs 1, 5 and 6, hence 3 of 6 against base 0 of 3. The other
  candidate runs label other counts, leaving this limit unlabelled. This is
  the known limit amendment 3 accepts, based on reading the target claims.

The unchanged K grader instead reports candidate 6 of 6 and base 3 of 3.
Its attribution branch false-passes the base: a title containing
"Validation ... report" and "not re-run" elsewhere satisfy the regex while
the wrong two-cell limit has no source label. That score does not establish
count correction or reliable attribution. The Captain chose to ship the
written rule with this limit recorded and the follow-up task
`counts-name-the-run-that-produced-them`, for sourcing numeric claims.

## Consequences

Startup reads 55 more words and each gate invocation prints 27 more words,
counted by whitespace splitting. The reminder adds no source-pattern hold.
A command and date make a claim checkable; they do not establish truth.
An honestly attributed but incorrect report can still reach the Captain, and
chat still depends on FO following the rule. The replay uses one model, six
candidate and three base runs per scenario, and combines the README and
printed line in K. Excluding Kent's global CLAUDE.md rests on documented
`--safe-mode` behavior, not a file-open trace; daily FO behavior is unproven.
The K 3-of-6 limit and grader false-pass remain visible through delivery;
the named follow-up addresses numbers with sources. Reopen if delivery claims
reliable count correction or hides this accepted limit, or if a later
structured claim record supports a useful refusal.
