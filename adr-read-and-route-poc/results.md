| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Runs |
| --- | --- | --- | --- | --- | --- | --- |
| A0 | claude | 5/5 | 3/3 | 8/10 | 8/8 | 10 |
| A0 | codex | 5/5 | 3/3 | 6/10 | 8/8 | 10 |

Per scenario (consulted / handoff / placement / choice), rep 1. Y = met, - = not scored, N = not met.

| Scenario | A0 claude | A0 codex | A1 claude | A1 codex | A2 claude | A2 codex | A3 claude | A3 codex |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | Y/-/N/Y | Y/-/N/Y |  |  |  |  |  |  |
| S2 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |  |  |
| S3 | -/-/Y/- | -/-/N/- |  |  |  |  |  |  |
| S4 | -/-/Y/- | -/-/Y/- |  |  |  |  |  |  |
| S5 | Y/-/Y/Y | Y/-/N/Y |  |  |  |  |  |  |
| S6 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |  |  |
| S7 | Y/-/Y/Y | Y/-/Y/Y |  |  |  |  |  |  |
| S8 | -/Y/N/Y | -/Y/N/Y |  |  |  |  |  |  |
| S9 | -/Y/Y/Y | -/Y/Y/Y |  |  |  |  |  |  |
| S10 | -/Y/Y/Y | -/Y/Y/Y |  |  |  |  |  |  |

Placement errors by scenario (all arms and hosts, rep 1): forbidden homes written, required homes missing.

| Scenario | Required home | Runs missing it | Forbidden writes (home: count) |
| --- | --- | --- | --- |
| S1 | decision_space_new | 0/2 | app_adr_new: 1, instructions: 2 |
| S2 | task_file | 0/2 | - |
| S3 | instructions | 0/2 | decision_space_new: 1, other: 1 |
| S4 | story_map | 0/2 | - |
| S5 | app_adr_new | 0/2 | decision_space_new: 1 |
| S6 | none | 0/2 | - |
| S7 | none | 0/2 | - |
| S8 | agent_notes | 2/2 | - |
| S9 | none | 0/2 | - |
| S10 | none | 0/2 | - |
