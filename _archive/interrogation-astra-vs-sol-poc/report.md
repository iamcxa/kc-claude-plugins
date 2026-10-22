# Astra arm: run record (not scored)

One arm, five runs: Codex `gpt-6-astra`, effort high, with the engineering-reviewer lens prompt, on the five task snapshots of the closed POC `interrogation-replay-on-batch-3-poc` (arm 4's prompts). The implementer did not score the answers. A separate scorer reads only `blind/`.

## Commands (as run)

- Snapshots: `git -C <kc-claude-plugins worktree> archive <base> | tar -x -C <work-dir>/<task>/snap` into `mktemp -d /tmp/astra-ext-XXXXXX` (outside every repository; 1376, 1376, 1384, 1385, 1385 files, matching the closed POC's 1376 to 1385). Bases as the closed POC: number-guards-readme-shrink and fo-write-checks c60e89e1; chat-only-evidence-observer-blind 5a951034; delivery-gate-settles-skipped-checks and special-role-calls-fire-when-needed 891a9a24.
- Prompt: the closed POC's `raw/<task>/prompt-lens.md` with only the snapshot path replaced (`diff` after normalising that path: identical, all five). Copies are in `raw/<task>/prompt-lens.md` with the work dir shown as `<work-dir>`.
- Run (`raw/run-astra.sh`): `codex exec --sandbox read-only --skip-git-repo-check --cd <snap> --json -m gpt-6-astra -c model_reasoning_effort='"high"' -o <answer> -` with the prompt on stdin. All five started in the same second and ran concurrently; every exit code 0. Codex CLI 0.162.1.
- Saved per task in `raw/<task>/`: `astra-answer.md`, `astra-events.jsonl`, `astra.err`, `astra.start`, `astra.end`, `astra.exit`.
- Blind files: `raw/make_blind.py` writes `blind/<task>-Z.md` with the closed POC's normalisation (self-reported `Reads` line removed, `**` removed, trailing spaces and blank lines removed; question text, order and numbering untouched). No arm, model or tool name appears in a blind file name or body (`grep -il 'astra\|gpt\|codex'` finds none). `blind/READER.md` is the scorer's procedure.

## AC-1 pin check

The five Codex session rollouts (`~/.codex/sessions/2026/10/22/rollout-2026-10-22T02-41-40-*`, thread ids in the table) each carry only `"model":"gpt-6-astra"` and `"effort":"high"` (no other model or effort string anywhere in the file), and exactly one user message per rollout contains the lens text and that task's snapshot path.

| Task | Thread id | model | effort |
|---|---|---|---|
| number-guards-readme-shrink | 01a15fc4-da34-7bb3-bb2b-7697f23b0423 | gpt-6-astra | high |
| fo-write-checks | 01a15fc4-da3b-75e2-a957-cfa1f02c1796 | gpt-6-astra | high |
| chat-only-evidence-observer-blind | 01a15fc4-da3c-7e40-8db1-313ea6a0bd2f | gpt-6-astra | high |
| delivery-gate-settles-skipped-checks | 01a15fc4-da62-7742-9eaf-873139412c22 | gpt-6-astra | high |
| special-role-calls-fire-when-needed | 01a15fc4-da52-74a2-a177-0fb6df1a0034 | gpt-6-astra | high |

## Isolation audit

82 shell commands in the five event streams (8, 17, 17, 12, 28 in the table's order). 0 use `..`, `~`, `$HOME`, `git` as a command word, or an absolute path outside that task's snapshot; the only textual `git` hits are `rg -g '!.git/**'` and `-g '!*git*'` exclusion globs (5 commands). No MCP tool call in any stream; `astra.err` holds the same MCP transport errors at shutdown as the closed POC's. Not controlled, as before: Codex loads `~/.codex/AGENTS.md`, and the user's config enables an under-development feature (a warning line in each stream).

## Cost and wall time beside the closed POC (tokens only; USD not measured)

Wall time is `date +%s` around each run. Astra ran five at once; the closed POC ran ten at once (contention differs, not measured). `In` counts cached tokens.

| Task | Wall s (astra / sol plain / sol lens) | In tokens (astra / plain / lens) | Out tokens (astra / plain / lens) | Commands (astra / plain / lens) | Questions (astra / plain / lens) |
|---|---|---|---|---|---|
| number-guards-readme-shrink | 190 / 191 / 202 | 568,095 / 742,304 / 506,343 | 5,775 / 6,938 / 6,993 | 8 / 17 / 20 | 10 / 9 / 11 |
| fo-write-checks | 259 / 211 / 252 | 935,585 / 889,261 / 1,001,872 | 7,756 / 7,410 / 8,501 | 17 / 11 / 26 | 19 / 20 / 20 |
| chat-only-evidence-observer-blind | 224 / 186 / 229 | 832,141 / 542,100 / 921,306 | 5,822 / 6,314 / 7,308 | 17 / 11 / 13 | 18 / 21 / 19 |
| delivery-gate-settles-skipped-checks | 180 / 210 / 255 | 739,352 / 669,298 / 553,979 | 5,112 / 7,210 / 9,169 | 12 / 11 / 19 | 18 / 20 / 18 |
| special-role-calls-fire-when-needed | 217 / 159 / 211 | 628,329 / 361,489 / 664,278 | 5,939 / 5,975 / 6,743 | 28 / 18 / 8 | 20 / 23 / 21 |

Totals over five runs:

| | Wall, summed s | In | of which cached | Out | of which reasoning | Commands | Questions |
|---|---|---|---|---|---|---|---|
| Astra (this run) | 1,070 | 3,703,502 | 3,287,424 | 30,404 | 12,101 | 82 | 85 |
| Closed POC arm 3 (sol, plain) | 957 | 3,204,452 | 2,756,224 | 33,847 | 15,716 | 68 | 93 |
| Closed POC arm 4 (sol, lens) | 1,149 | 3,647,778 | 3,198,464 | 38,714 | 19,902 | 86 | 89 |

The closed POC's wall totals are summed per-run seconds from its table; this run's is the same sum (the longest single run was 259 s). Self-reported `Reads` lines (21, 38, 34, 25, 31) were removed from the blind files and are not used; stream command counts are used.

## Not done here

No scoring, no tier-1 hit counts, no ungrounded count, no reading of the answers against the keys: those belong to the blind scorer and to AC-2. The fo-write-checks stream carries a one-line agent message before its first command (other streams not checked for this); only the `-o` final answer is in `blind/`.
