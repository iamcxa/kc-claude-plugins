# AC-3 replay, implementation-2 (2026-11-03)

Harness: copied unchanged from implementation-1 (`harness-sha256.txt`; `replay.py`, `scenarios.json`, `protocol.json`, `grader-falsifiers.json` byte-identical). Grader falsifiers re-run first: P/K original FAIL, P/K corrected PASS (4 of 4 matched).
Route: `claude -p --safe-mode --model claude-opus-5-5`, normal HOME, scratch cwd per run. Per run, `meta.json` holds argv, the stream-json init (no user skills, built-in plugins only), `instruction_isolation`, and measured usage. No file-open trace exists, so "CLAUDE.md not loaded" rests on the documented `--safe-mode` behavior (`claude-help.txt`).
Codex half: not run. `codex exec --help` lists no supported way to skip ~/.codex/AGENTS.md.
Attempts: 4 earlier (no answer) + 12 now = 16 of the hard stop 30. 12 of 12 answered, 0 retries, every run signed in.
Measured tokens (sum of input + cache-creation + cache-read, and output, over the 12 runs): 217,572 input, 10,545 output.

| Cell (3 runs) | Preregistered grader | Reading the answers |
| --- | --- | --- |
| P base | 1 of 3 (run 1 pass; runs 2, 3 fail) | same |
| P candidate | 3 of 3 | same |
| K base | 3 of 3 | 0 of 3 |
| K candidate | 3 of 3 | 3 of 3 |

Grader defect (not corrected; the rubric is preregistered): K's "attributed" branch passes when "validation" appears within 50 characters of "report" and "not re-run"/"unverified" appears anywhere. All three K base answers open with a title like "Validation gate summary: read-adr reporting ...", which satisfies the first half by itself, and their limits bullet "S6 Codex and S7 Codex were not re-run" (two cells, the validator's wrong count, no source label) satisfies the second. Checked per run with the grader's own regexes: attributed = True for K-base 1, 2 and 3; the "three" branch is True only for 1 and 2 (an unrelated "three"), and the command branch is False for all. The four falsifier texts could not catch it because none starts with such a title.

Verdict per the preregistered grader: Claude half only, candidate P 3/3 and K 3/3; the bar (5 of 6 per scenario) needs the Codex half and is not evaluable. Base: P 1/3, K 3/3 by the grader, so the base README does not saturate; the "README raise not needed" branch is not triggered. n=3 per cell.
