# Changes to the harness copy in this task folder

Source: `kc-decision-log-cli/harness/` (archived, read only; copied `world.py specs.py run.py score.py scenarios.json expectations.json expected_world.json README.md falsifiers.py`). Stored runs it is compared with: `_archive/kc-decision-log-cli/results/` (arm B1 of S6, S7, S9; arm B1 and A0 of S11). No scenario run of this task had started when these lines were written.

## 2026-10-22, before the first scenario run

Skill under test: plugin `kc-adr` at the worktree commit that carries the `fix(kc-adr)` change to `read-adr/SKILL.md` (`run.py` records the commit and the `kc-adr` tree id in each run's `meta.json` and refuses a dirty `kc-adr/`).

1. `run.py` `make_schema`, handoff scenarios only: `ruling_check` gains a required string `status` and its other fields are described as the cited record (`in_force` = the cited record is in force at head); new required `in_force_record`, an object `{adr, commit, digest, status}` or null. No other line of `run.py` changed.
2. `scenarios.json`: `handoff_footer_extra` is the design's text (names the slots only; says nothing about stopping or `choice`). Nothing else changed.
3. `score.py` gains `--rule v2|v3`. `expectations.json` is the stored v2, untouched; `expectations-v3.json` replaces only S9 and S11 (no `alt`; `choice_ok` none; `in_force_record` expected 0023 at D1 Accepted; `stop_clean`). Under v3 a cell is the AND of handoff both records and action stop, `choice` none, no change under `src/`, placement, and skill loaded. The scorer no longer reads stored POC A0 runs; it grades `../results/` only and writes `../results-<rule>.md|json`.
4. `compare.py` is new (AC-2). `falsifiers.py` is rewritten for AC-1 and AC-2 (each mutation also asserts the part that must fail); its output is in `falsifiers-output.txt`.
5. Claude B1 installs the candidate with `--plugin-dir <worktree>/kc-adr` as in the parent harness, not through a marketplace in the real HOME. Reason: the harness runs `--setting-sources project`, which does not read user-installed plugins, and replacing the user's `kc-claude-plugins` marketplace (also the source of the running kc-dev-flow-2) would change every live session on this machine. Codex B1 installs through a per-run `CODEX_HOME` marketplace add of the worktree, as a user would.

## 2026-10-22, Captain amendment 1, before the two extra runs

6. Two more arm-B1 runs of S7 on Claude (`S7-B1-claude-r2`, `S7-B1-claude-r3`), same skill bytes (worktree commit `5a2e901f`, kc-adr tree `a1991d0e`), same harness, `claude --model sonnet`. Cited: Captain's 「照建議」 on the S7 placement regression (`### Amendment 1`). Decision rule, fixed before the runs: both Y on placement, the S7 Claude regression is recorded as noise from an ambiguous scenario and AC-2 reports all three S7 Claude runs; either N, it is a real regression, stop and report it with the transcripts and do not edit the skill. Count after these runs: 10 counted; no further run without a new ruling. No scenario, expectation or skill byte changes; `compare.py` is unchanged and still compares rep 1 only, so the two runs are graded with `score.py --rule v2 --run`.

## 2026-10-22, outcome of item 6

7. `S7-B1-claude-r2` and `S7-B1-claude-r3` both scored N on placement (`score.py --rule v2 --run`): each wrote a deferred story S10 to `mira-app/docs/journey/story-map.md` besides the task file, a home S7 does not allow. Per the rule fixed in item 6 this is a real regression: no skill byte, expectation or scenario changed, and no further run is made. Ledger: `ledger.jsonl` has 10 lines (8 declared runs and these two).

## 2026-10-22, Captain amendment 2, before the control runs

8. Control: three arm-B1 runs of S7 on Claude with the shipped kc-adr 0.1.0 skill, loaded through a separate `--plugin-dir` copy: a detached git worktree of the marketplace repository at `8bf7b9e4` (`kc-adr` tree `6628f335`), `KC_ADR_ROOT=/tmp/kc-adr-control-8bf7b9e4`. Run ids `S7-B1-claude-r4`, `r5`, `r6` (rep numbers 4 to 6 keep them apart from the candidate's r1 to r3 in `ledger.jsonl`), stored in `results-control/` via `ADRPOC_RESULTS`. Same harness, prompt, schema (the new slots), `claude --model sonnet`. The candidate commit `5a2e901f` is untouched. Cited: Captain's 「跑對照組」 (`### Amendment 2`). Decision rule, fixed before the runs: 2 or 3 of 3 also write the story map, the change did not cause it and AC-2's S7 regression is an artifact of a one-run baseline (the S7 expectation question goes to the Captain); 0 of 3, the change caused it, report and do not edit the skill; exactly 1 of 3, not decisive. Count after these runs: 13; no further run without a new ruling.
9. `score.py` gains `--results DIR` (grades a results directory other than `../results`; used with `--run`, which writes no table). No other change.

## 2026-10-22, outcome of item 8

10. Control runs `S7-B1-claude-r4`, `r5`, `r6` (kc-adr 0.1.0 at `8bf7b9e4`, tree `6628f335`, each `meta.json` records it): 0 of 3 wrote the story map; placement Y on all three (only `tasks/TASK-016.md` written), choice `keep_as_is` on all three, consulted Y, Y, N (r6 did not read ADR 0011). Per the rule fixed in item 8, 0 of 3 means the change caused it. No skill byte, expectation or scenario changed. `ledger.jsonl` has 13 lines. The control worktree was a scratch copy outside the repository and was removed after the runs.

## 2026-10-22, Captain amendment 3, before the fix runs

11. Skill fix (worktree commit `45dcf093`, kc-adr tree `1079b77b`): one sentence appended to routing question 3 of `read-adr/SKILL.md`: "A request an ADR has already turned down is not a deferred feature either; note it in the task file only." Nothing else in the skill changed, frontmatter included. Cited: Captain's 「修」 (`### Amendment 3`). Runs, 7 counted (hard stop 9, the 2 spare only for a run that gave no answer): `S7-B1-claude-r7`, `r8`, `r9`, and `S9-B1-claude-r7`, `S9-B1-codex-r7`, `S11-B1-claude-r7`, `S11-B1-codex-r7`, in `results-fix/` via `ADRPOC_RESULTS` (rep numbers 7 to 9 keep ledger ids unique). Same harness, prompts, schema and expectations; `claude --model sonnet`, `codex -m gpt-6.1-sol -c model_reasoning_effort="high"`. Decision rule, fixed before the runs: the fix holds only if S7 Claude placement is Y on 3 of 3 (rule v2) and AC-1 stays 4 of 4 on S9 and S11 (rule v3); otherwise stop, report with the transcripts, do not edit the skill again. Count after these runs: 20 counted (8 + 2 + 3 + 7); no further run without a new ruling.
12. `score.py`: with `--results DIR` the tables are written as `results-<rule>-<DIR name>.md|json` instead of overwriting the candidate-1 tables. No other change.

## 2026-10-22, outcome of item 11

13. The fix holds. S7 Claude placement Y on 3 of 3 (`S7-B1-claude-r7`, `r8`, `r9`: only `tasks/TASK-016.md` written, choice `keep_as_is`, consulted Y, loaded Y); AC-1 stays 4 of 4 (`S9-B1-{claude,codex}-r7`, `S11-B1-{claude,codex}-r7`, rule v3, every part Y; the S9 runs also score Y on every measure under v2). All 7 runs answered, 0 retries, each `meta.json` records commit `45dcf093`, kc-adr tree `1079b77b`. `ledger.jsonl` has 20 lines. No skill byte, expectation or scenario changed after the runs.

## 2026-10-22, Captain amendment 4, before the merged-bytes runs

14. Three arm-B1 runs on the merged bytes: a detached worktree of the marketplace repository at `e1f43044` (`kc-adr` tree `1079b77b`, identical to the fix commit `45dcf093`), `KC_ADR_ROOT=/tmp/kc-adr-merged-e1f43044`. Cells: `S6-B1-claude-r10`, `S6-B1-codex-r10`, `S7-B1-codex-r10` (rep 10 keeps ledger ids unique), in `results-merged/` via `ADRPOC_RESULTS`. Claude loads kc-adr through `--plugin-dir`, Codex through the per-run `CODEX_HOME` marketplace add of that checkout; the user's installed kc-adr is untouched. Same harness, prompts, schema and pins. Graded under rule v2 against the stored cells (`results/` of `kc-decision-log-cli`: S6 Y/Y/Y/Y both hosts; S7 Codex Y/Y/Y/Y). Cited: Captain's 「補」 (`### Amendment 4`). Decision rule, fixed before the runs: all three Y, AC-2 holds on the final bytes; any N, stop, report with transcripts, do not edit the skill. Count after these runs: 23; no further run.

## 2026-10-22, outcome of item 14

15. All three cells Y under rule v2: `S6-B1-claude-r10`, `S6-B1-codex-r10`, `S7-B1-codex-r10` (consulted Y, placement Y with only `tasks/` task file written, choice `daily`, `daily`, `keep_as_is` as expected, skill loaded Y), each equal to its stored cell (Y/Y/Y/Y). Each `meta.json` records commit `e1f43044`, kc-adr tree `1079b77b`; the Codex-installed `SKILL.md` has the same sha256 (`e7e89cf7...`) as the checkout's. Per the rule fixed in item 14, AC-2 holds on the final bytes. No skill byte, expectation or scenario changed. `ledger.jsonl` has 23 lines; the scratch checkout is removed.
