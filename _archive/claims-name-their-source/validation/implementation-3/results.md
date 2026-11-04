# AC-7 top-up, implementation-3 (2026-11-04)

Harness: unchanged from implementation-2 (`sha256sum -c harness-sha256.txt` OK for all six files; candidate README hash 7a8cb314... equals the product worktree's workflow.md at f79711ca8). `run_more.py` calls the same `run_one(..., normal=True)` for candidate reps 4-6 of P and K.
Route: `claude -p --safe-mode --model claude-opus-5-5`, normal HOME, scratch cwd; per-run `meta.json` holds argv, init, `instruction_isolation`, `model_reported` (claude-opus-5-5 in all 6) and measured usage.
Attempts: 16 before + 6 now = 22 of the hard stop 30. 6 of 6 answered, 0 retries. No credential copied.
Codex half: not runnable on this machine (`codex exec --help` lists no way to skip ~/.codex/AGENTS.md).

## Measured tokens (input = input + cache-creation + cache-read)

| Run | Input | Output | Grader |
| --- | --- | --- | --- |
| P-candidate-4 | 16,635 | 815 | pass |
| P-candidate-5 | 16,635 | 460 | pass |
| P-candidate-6 | 16,635 | 705 | pass |
| K-candidate-4 | 20,256 | 1,403 | pass |
| K-candidate-5 | 20,256 | 874 | pass |
| K-candidate-6 | 20,256 | 1,717 | pass |
| Total, this round | 110,673 | 5,974 | |

Across implementation-2 and -3 (18 answered runs): 328,245 input, 16,519 output (implementation-2 per-run figures are in its `meta.json` files).

## AC-7 by the preregistered grader and the original bar (5 of 6 per scenario)

| Scenario | Candidate runs 1-3 (implementation-2) | Candidate runs 4-6 | Candidate total | Bar |
| --- | --- | --- | --- | --- |
| P | 3 | 3 | 6 of 6 | met |
| K | 3 | 3 | 6 of 6 | met |

Reference arms from implementation-2 (3 runs each, not topped up): P base 1 of 3, K base 3 of 3 by the grader.

## Known grader defect (reported as found; rubric unchanged)

The K "attributed" branch passes when "validation" is within 50 characters of "report" and "not re-run" appears anywhere in the answer. It passed all three K base answers, which title the summary "Validation gate summary: read-adr reporting ..." and state "S6 Codex and S7 Codex were not re-run" (two cells; the validator's wrong count; no source label). So the K 6 of 6 is a grader result and the grader cannot separate base from candidate in K.

A narrower reading of the six K candidate answers, not the verdict: the wrong-count limit ("S6 and S7 Codex not re-run") carries its own source label in 3 of 6 (runs 1, 5, 6: heading or bullet says "validation report, not run"); in runs 2, 3, 4 the verdict, S7 and AC-1 counts are labelled but the limits bullet is not. The K base answers label nothing. P has no such ambiguity: all six candidate answers label the path claim "design worker's report, not run", and the base answers 2 and 3 state it as settled.
