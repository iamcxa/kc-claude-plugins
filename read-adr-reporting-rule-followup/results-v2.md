| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Skill loaded before first ADR access | Stop leaves no code change | Runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | claude | 2/2 | 2/2 | 3/4 | 4/4 | 4/4 | n/a | 4 |
| B1 | codex | 2/2 | 2/2 | 4/4 | 4/4 | 4/4 | n/a | 4 |

Per scenario (consulted / handoff / placement / choice, then L = skill loaded for B1), rep 1. Y = met, - = not scored, N = not met. Arm A0 = no skill on the v2 scenarios (stored POC runs where the prompt is unchanged, new runs for S1, S5, S11, S12); A0p = every stored POC A0 run, graded under v2 expectations.

| Scenario | A0 claude | A0 codex | A0p claude | A0p codex | B1 claude | B1 codex |
| --- | --- | --- | --- | --- | --- | --- |
| S1 |  |  |  |  |  |  |
| S2 |  |  |  |  |  |  |
| S3 |  |  |  |  |  |  |
| S4 |  |  |  |  |  |  |
| S5 |  |  |  |  |  |  |
| S6 |  |  |  |  | Y/-/Y/Y/LY | Y/-/Y/Y/LY |
| S7 |  |  |  |  | Y/-/N/Y/LY | Y/-/Y/Y/LY |
| S8 |  |  |  |  |  |  |
| S9 |  |  |  |  | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S10 |  |  |  |  |  |  |
| S11 |  |  |  |  | -/Y/Y/Y/LY | -/Y/Y/Y/LY |
| S12 |  |  |  |  |  |  |

Placement errors by scenario (all arms and hosts, rep 1): forbidden homes written, required homes missing.

| Scenario | Required home | Runs missing it | Forbidden writes (home: count) |
| --- | --- | --- | --- |
| S6 | none | 0/2 | - |
| S7 | none | 0/2 | story_map: 1 |
| S9 | none | 0/2 | - |
| S11 | none | 0/2 | - |
