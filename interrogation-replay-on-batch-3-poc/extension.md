# Extension to the other five batch-3 tasks (arms 3 and 4 only, no scoring here)

Captain's extension: 「擴大」 at the validation gate (briefing `review/validation/briefing-1`): repeat the interrogation on number-guards-readme-shrink, fo-write-checks, chat-only-evidence-observer-blind, delivery-gate-settles-skipped-checks and special-role-calls-fire-when-needed, with Codex plain (arm 3) and Codex with the engineering-reviewer lens (arm 4), one run each, then a blind second reader. This file records method and cost only; the arms are not scored by the implementer.

## Method (as run)

- Snapshots: `git archive <base> | tar -x` from the kc-claude-plugins worktree into `/tmp/replay-ext-ycemcP/<task>/snap` (no history; 1376 to 1385 files). Bases, from each archived task's `dispatch/implementation-1.md` and its Verified-by lines: number-guards-readme-shrink c60e89e1 (PR #670 base); fo-write-checks c60e89e1 (PR #671 base); chat-only-evidence-observer-blind 5a951034 (the checklist names it); delivery-gate-settles-skipped-checks 891a9a24 (checklist); special-role-calls-fire-when-needed 891a9a24 (checklist; PR #682 two commits on it).
- Story: each task's first committed version (state commits 4756c3bc, f80be84e, af547306, fbcb7a9e, 0b938414): title as Card, the intro paragraph if any, and the `## Scope` section verbatim. Dropped: `## FO alignment`, `## Peers` (session ids), `## Acceptance criteria` (a placeholder). Prompts are generated from the first run's `prompt-plain.md` and `prompt-lens.md` by `raw/gen_prompts.py`: only the snapshot path and the story block change; the lens block is byte-identical in all five lens prompts and in the first run's.
- Command (`raw/run-ext.sh`; flags as the first run established): `codex exec --sandbox read-only --skip-git-repo-check --cd <snap> --json -m gpt-6.1-sol -c model_reasoning_effort='"high"' -o <answer> -`, prompt on stdin. All ten started in the same second and ran concurrently; every exit code 0.
- Pin check, new in this run: the ten Codex session rollouts (`~/.codex/sessions/2026/10/20/`) each carry `"model":"gpt-6.1-sol"` and `"effort":"high"`, and exactly one prompt per task contains the lens text.
- Isolation audit, all ten event streams: 0 commands with `..`, `~`, `$HOME`, a `git` command word or an absolute path outside that task's snapshot (155 commands in all: 17, 20, 11, 26, 11, 13, 11, 19, 18, 8 in the order of the table below, arm 3 then arm 4 per task). No MCP tool call in any stream; `a3.err`/`a4.err` hold the same MCP transport errors at shutdown as the first run (the user's Codex config loads its MCP servers; none was called). Not controlled, as before: Codex loads `~/.codex/AGENTS.md`.
- Order of work: prompts, snapshots and runs first; the archived task files were opened for bases only (`grep base`, with a few stage-report fragments) before the runs, and read for the keys only after all ten answers were saved under `raw/<task>/`.
- Blinding: `raw/make_blind.py` writes `blind/<task>-X.md` and `blind/<task>-Y.md` from the saved answers after `secrets.randbelow(2)` per task decided which arm is X; the map is in `sealed/coin.json` (mode 600) and was not printed. Normalisation applied to both lists alike: removed the self-reported `Reads: n, minutes: n` line (it disagreed with the streams in the first run), removed `**` bold markers, trailing spaces and blank lines (the two arms formatted differently in some tasks). Question text, order and numbering are untouched.

## Cost and wall time (Codex reports tokens only; USD not measured)

Wall time is from `date +%s` around each run with all ten running at once, so it includes contention that was not measured. `In` counts cached tokens.

| Task | Arm | Wall | In | of which cached | Out | of which reasoning | Commands | Questions |
|---|---|---|---|---|---|---|---|---|
| number-guards-readme-shrink | 3 plain | 191 s | 742,304 | 652,288 | 6,938 | 3,586 | 17 | 9 |
| number-guards-readme-shrink | 4 lens | 202 s | 506,343 | 429,184 | 6,993 | 3,613 | 20 | 11 |
| fo-write-checks | 3 plain | 211 s | 889,261 | 776,192 | 7,410 | 3,808 | 11 | 20 |
| fo-write-checks | 4 lens | 252 s | 1,001,872 | 887,424 | 8,501 | 4,279 | 26 | 20 |
| chat-only-evidence-observer-blind | 3 plain | 186 s | 542,100 | 458,496 | 6,314 | 3,053 | 11 | 21 |
| chat-only-evidence-observer-blind | 4 lens | 229 s | 921,306 | 810,624 | 7,308 | 3,604 | 13 | 19 |
| delivery-gate-settles-skipped-checks | 3 plain | 210 s | 669,298 | 578,560 | 7,210 | 3,409 | 11 | 20 |
| delivery-gate-settles-skipped-checks | 4 lens | 255 s | 553,979 | 500,352 | 9,169 | 5,527 | 19 | 18 |
| special-role-calls-fire-when-needed | 3 plain | 159 s | 361,489 | 290,688 | 5,975 | 1,860 | 18 | 23 |
| special-role-calls-fire-when-needed | 4 lens | 211 s | 664,278 | 570,880 | 6,743 | 2,879 | 8 | 21 |
| Arm 3 total (5 runs) | | 957 s | 3,204,452 | 2,756,224 | 33,847 | 15,716 | 68 | 93 |
| Arm 4 total (5 runs) | | 1,149 s | 3,647,778 | 3,198,464 | 38,714 | 19,902 | 86 | 89 |

All ten ran in 255 s of wall time together. Setup probes: none beyond the first run's. Cost in USD: not measured.

## What is in the blind set

`blind/answer-keys.md` (five tasks, 29 items: tier 1 assigned key 17, of which 13 askable before the build and 4 not; tier 2 secondary 12, of which 7 askable and 5 not), `blind/READER.md` (procedure), and ten anonymised lists.
