# Task scoreboard, 2026-11-14

Five numbers per task, read from two public state branches by `scripts/task_scoreboard.py` (which calls `task_timeline.timeline`).
Day boundary: 2026-11-14 local time (+08:00), which is 2026-11-13T16:00:00Z.

Commands, run once each, output below unedited:

    python3 -B -I scripts/task_scoreboard.py <state checkout of spacedock-state/dev2-poc> --since 2026-11-13T16:00:00Z
    python3 -B -I scripts/task_scoreboard.py <state checkout of spacedock-state/dev2> state-branch-writes-carry-no-private-identifiers gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo extracted-package-says-five-rules-that-worked

The `--since` run took every task on the first branch whose first stage started today (7 of 26; of the other 19, one has no stage and 18 started 2026-09-22 to 2026-10-26).

Limits: times come from state-commit author dates and gate resolution timestamps; machine time includes idle time between a stage's start and its gate; a gate the FO resolved under a standing grant counts as waiting; a task marked (running) is measured to the read time shown, so its row changes on the next run; minutes between one stage's end and the next stage's start are in neither column; column 3 sees an edit to a `**AC-n**` block, not an amendment that changes a criterion without editing it.

## spacedock-state/dev2-poc

state: spacedock-state/dev2-poc @ de67f8c52af7; read 2026-11-14T12:23:01Z

| task | 1 first report (min) | 2 dispatches | 3 criterion changed | 4 questions | 5 minutes |
|---|---|---|---|---|---|
| extracted-package-real-use-routes-probe-poc | not recorded | backlog 0, implementation 1 | no: 2 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 4.7 total = 4.6 machine + 0.1 waiting (running) |
| method-reading-code-and-tables-on-the-private-remote-poc | 12.8 | backlog 0, implementation 1, validation 1 | no: 2 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 13.1 total = 12.9 machine + 0.2 waiting |
| private-cell-selfcheck-passes-on-a-fresh-clone-poc | 17.7 | backlog 0, implementation 1, validation 1 | no: 2 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 17.9 total = 17.7 machine + 0.2 waiting |
| readme-rule-retirement-audit-poc | 149.0 | backlog 0, implementation 2, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 154.6 total = 149.1 machine + 5.5 waiting |
| shared-assumption-replay-on-archived-tasks-poc | 125.0 | backlog 0, implementation 1, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 130.7 total = 125.1 machine + 5.6 waiting |
| task-scoreboard-five-numbers-poc | not recorded | backlog 0, implementation 1 | no: 2 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 4.6 total = 4.5 machine + 0.1 waiting (running) |
| test-value-pass-on-route-trial-prs-poc | 124.4 | backlog 0, implementation 1, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 130.4 total = 124.7 machine + 5.7 waiting |

Not recorded:
- extracted-package-real-use-routes-probe-poc: minutes to the first Captain-facing report: no gate briefing or ask after the first dispatch; record needed: a gate briefing or an asks.jsonl entry after a worker dispatch record
- extracted-package-real-use-routes-probe-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- method-reading-code-and-tables-on-the-private-remote-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- private-cell-selfcheck-passes-on-a-fresh-clone-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- readme-rule-retirement-audit-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- shared-assumption-replay-on-archived-tasks-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- task-scoreboard-five-numbers-poc: minutes to the first Captain-facing report: no gate briefing or ask after the first dispatch; record needed: a gate briefing or an asks.jsonl entry after a worker dispatch record
- task-scoreboard-five-numbers-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- test-value-pass-on-route-trial-prs-poc: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate

## spacedock-state/dev2

state: spacedock-state/dev2 @ 76fa1cccb514; read 2026-11-14T12:23:02Z

| task | 1 first report (min) | 2 dispatches | 3 criterion changed | 4 questions | 5 minutes |
|---|---|---|---|---|---|
| state-branch-writes-carry-no-private-identifiers | 28.1 | backlog 0, ideation 1, implementation 1, validation 1 | no: 5 criteria unchanged since ideation approval | 3 gate briefings; asks outside a gate: 1 | 203.5 total = 178.9 machine + 24.6 waiting |
| gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo | 29.2 | backlog 0, ideation 1, implementation 1, validation 1 | no: 5 criteria unchanged since ideation approval | 2 gate briefings; asks outside a gate: not recorded | 150.0 total = 149.8 machine + 0.2 waiting (running) |
| extracted-package-says-five-rules-that-worked | not recorded | backlog 0, ideation 1 | no: 3 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 4.8 total = 4.7 machine + 0.1 waiting (running) |

Not recorded:
- gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
- extracted-package-says-five-rules-that-worked: minutes to the first Captain-facing report: no gate briefing or ask after the first dispatch; record needed: a gate briefing or an asks.jsonl entry after a worker dispatch record
- extracted-package-says-five-rules-that-worked: asks outside a gate: no asks.jsonl; record needed: asks.jsonl written when the FO asks outside a gate
