| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Skill loaded before first ADR access | Stop leaves no code change | Runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A0 | claude | 5/5 | 3/3 | 7/10 | 8/8 | n/a | 1/1 | 10 |
| A0 | codex | 5/5 | 3/3 | 6/10 | 8/8 | n/a | 1/1 | 10 |

Per scenario (consulted / handoff / placement / choice, then L = skill loaded for B1), rep 1. Y = met, - = not scored, N = not met. Arm A0 = no skill on the v2 scenarios (stored POC runs where the prompt is unchanged, new runs for S1, S5, S11, S12); A0p = every stored POC A0 run, graded under v2 expectations.

| Scenario | A0 claude | A0 codex | A0p claude | A0p codex | B1 claude | B1 codex |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Y/-/N/Y | Y/-/N/Y |  |  |  |  |
| S2 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |
| S3 | -/-/N/- | -/-/N/- |  |  |  |  |
| S4 | -/-/Y/- | -/-/Y/- |  |  |  |  |
| S5 | Y/-/N/Y | Y/-/N/Y |  |  |  |  |
| S6 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |
| S7 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |
| S8 | -/Y/Y/Y | -/Y/N/Y |  |  |  |  |
| S9 | -/Y/Y/Y | -/Y/Y/Y |  |  |  |  |
| S10 | -/Y/Y/Y | -/Y/Y/Y |  |  |  |  |
| S11 |  |  |  |  |  |  |
| S12 |  |  |  |  |  |  |

Placement errors by scenario (all arms and hosts, rep 1): forbidden homes written, required homes missing.

| Scenario | Required home | Runs missing it | Forbidden writes (home: count) |
| --- | --- | --- | --- |
| S1 | app_adr_new | 1/2 | decision_space_new: 2, instructions: 2 |
| S2 | task_file | 0/2 | - |
| S3 | instructions | 0/2 | decision_space_new: 1, task_file: 1 |
| S4 | story_map | 0/2 | - |
| S5 | app_adr_new | 0/2 | decision_space_new: 2 |
| S6 | none | 0/2 | - |
| S7 | none | 0/2 | - |
| S8 | none | 0/2 | other: 1 |
| S9 | none | 0/2 | - |
| S10 | none | 0/2 | - |
