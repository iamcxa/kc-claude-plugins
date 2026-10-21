| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Skill loaded before first ADR access | Stop leaves no code change | Runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A0 | claude | 5/5 | 4/5 | 9/12 | 10/10 | n/a | 2/2 | 12 |
| A0 | codex | 5/5 | 4/5 | 8/12 | 10/10 | n/a | 2/2 | 12 |
| A0p | claude | 5/5 | 3/3 | 7/10 | 8/8 | n/a | 1/1 | 10 |
| A0p | codex | 5/5 | 3/3 | 6/10 | 8/8 | n/a | 1/1 | 10 |
| B1 | claude | 4/5 | 5/5 | 11/12 | 10/10 | 12/12 | 2/2 | 12 |
| B1 | codex | 5/5 | 5/5 | 8/12 | 10/10 | 12/12 | 2/2 | 12 |

Per scenario (consulted / handoff / placement / choice, then L = skill loaded for B1), rep 1. Y = met, - = not scored, N = not met. Arm A0 = no skill on the v2 scenarios (stored POC runs where the prompt is unchanged, new runs for S1, S5, S11, S12); A0p = every stored POC A0 run, graded under v2 expectations.

| Scenario | A0 claude | A0 codex | A0p claude | A0p codex | B1 claude | B1 codex |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Y/-/N/Y | Y/-/N/Y | Y/-/N/Y | Y/-/N/Y | Y/-/N/Y/LY | Y/-/N/Y/LY |
| S2 | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y/LY | Y/-/N/Y/LY |
| S3 | -/-/N/- | -/-/N/- | -/-/N/- | -/-/N/- | -/-/Y/-/LY | -/-/N/-/LY |
| S4 | -/-/Y/- | -/-/Y/- | -/-/Y/- | -/-/Y/- | -/-/Y/-/LY | -/-/Y/-/LY |
| S5 | Y/-/N/Y | Y/-/N/Y | Y/-/N/Y | Y/-/N/Y | Y/-/Y/Y/LY | Y/-/N/Y/LY |
| S6 | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y/LY | Y/-/Y/Y/LY |
| S7 | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | Y/-/Y/Y | N/-/Y/Y/LY | Y/-/Y/Y/LY |
| S8 | -/Y/Y/Y | -/Y/N/Y | -/Y/Y/Y | -/Y/N/Y | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S9 | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S10 | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S11 | -/Y/Y/Y | -/Y/Y/Y |  |  | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S12 | -/N/Y/Y | -/N/Y/Y |  |  | -/Y/Y/Y/LY | -/Y/Y/Y/LY |

Placement errors by scenario (all arms and hosts, rep 1): forbidden homes written, required homes missing.

| Scenario | Required home | Runs missing it | Forbidden writes (home: count) |
| --- | --- | --- | --- |
| S1 | app_adr_new | 3/6 | decision_space_new: 5, instructions: 4, other: 1, task_file: 1 |
| S2 | task_file | 0/6 | story_map: 1 |
| S3 | instructions | 0/6 | decision_space_new: 2, task_file: 3 |
| S4 | story_map | 0/6 | - |
| S5 | app_adr_new | 0/6 | decision_space_new: 4, task_file: 1 |
| S6 | none | 0/6 | - |
| S7 | none | 0/6 | - |
| S8 | none | 0/6 | other: 2 |
| S9 | none | 0/6 | - |
| S10 | none | 0/6 | - |
| S11 | none | 0/4 | - |
| S12 | none | 0/4 | - |
