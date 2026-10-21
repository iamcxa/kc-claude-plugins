Effort and tool use per arm and host (rep 1 only; tokens are the host's own usage counters, cache reads included for Claude, input plus output for Codex).

| Arm | Host | Runs | Mean tool calls | Mean seconds | Mean tokens | Skill opened | CLI used | git show used | Hook text in context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A0 | claude | 10 | 5.3 | 19 | 126112 | 0/10 | 0/10 | 5/10 | 0/10 |
| A0 | codex | 10 | 9.1 | 68 | 104843 | 0/10 | 0/10 | 3/10 | 0/10 |
| A1 | claude | 10 | 5.5 | 18 | 119883 | 10/10 | 0/10 | 6/10 | 0/10 |
| A1 | codex | 10 | 9.9 | 60 | 103640 | 10/10 | 0/10 | 9/10 | 0/10 |
| A2 | claude | 10 | 6.5 | 23 | 139384 | 10/10 | 7/10 | 1/10 | 0/10 |
| A2 | codex | 10 | 11.4 | 64 | 125653 | 10/10 | 9/10 | 0/10 | 0/10 |
| A3 | claude | 10 | 5.9 | 23 | 132746 | 10/10 | 8/10 | 1/10 | 10/10 |

Homes written (rep 1, count of runs that wrote each home), by arm and host.

| Arm | Host | decision_space_new | app_adr_new | task_file | story_map | instructions | agent_notes | other | ruling_edit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A0 | claude | 3 | 1 | 6 | 1 | 2 | 0 | 0 | 0 |
| A0 | codex | 2 | 2 | 7 | 1 | 2 | 1 | 1 | 0 |
| A1 | claude | 1 | 1 | 6 | 2 | 1 | 1 | 0 | 0 |
| A1 | codex | 1 | 1 | 9 | 3 | 1 | 1 | 0 | 0 |
| A2 | claude | 1 | 1 | 6 | 3 | 1 | 1 | 0 | 0 |
| A2 | codex | 1 | 1 | 8 | 3 | 1 | 1 | 0 | 0 |
| A3 | claude | 1 | 1 | 6 | 3 | 1 | 1 | 0 | 0 |

Post hoc, not pre-registered: placement if S2 and S7 also accept the story map as a home. Both scenarios mention work that is put off (non-ASCII file names 'after Friday'; an XLSX request), so a deferred-feature reading is defensible.

| Arm | Host | Placement as pre-registered | With story map allowed in S2 and S7 |
| --- | --- | --- | --- |
| A0 | claude | 6/10 | 6/10 |
| A0 | codex | 6/10 | 6/10 |
| A1 | claude | 9/10 | 10/10 |
| A1 | codex | 5/10 | 7/10 |
| A2 | claude | 8/10 | 10/10 |
| A2 | codex | 5/10 | 7/10 |
| A3 | claude | 8/10 | 10/10 |

Repeat runs (rep 2) against rep 1 of the same cell. Flipped = the measure came out differently.

| Cell | Measure | Rep 1 | Rep 2 | Flipped |
| --- | --- | --- | --- | --- |
| S2 A2 claude | consulted | True | True | no |
| S2 A2 claude | placement | False | False | no |
| S2 A2 claude | choice | True | True | no |
| S2 A2 codex | consulted | True | True | no |
| S2 A2 codex | placement | False | False | no |
| S2 A2 codex | choice | True | True | no |
| S3 A2 claude | placement | True | True | no |
| S3 A2 codex | placement | False | True | yes |
| S5 A2 claude | consulted | True | True | no |
| S5 A2 claude | placement | True | True | no |
| S5 A2 claude | choice | True | True | no |
| S5 A2 codex | consulted | True | True | no |
| S5 A2 codex | placement | False | False | no |
| S5 A2 codex | choice | True | True | no |

1 of 14 scored measures flipped between rep 1 and rep 2 (6 repeat runs).
