# Changes to the harness copy in this task folder

Source: `kc-decision-log-cli/harness/` (archived, read only; copied `world.py specs.py run.py score.py scenarios.json expectations.json expected_world.json README.md falsifiers.py`). Stored runs it is compared with: `_archive/kc-decision-log-cli/results/` (arm B1 of S6, S7, S9; arm B1 and A0 of S11). No scenario run of this task had started when these lines were written.

## 2026-10-22, before the first scenario run

Skill under test: plugin `kc-adr` at the worktree commit that carries the `fix(kc-adr)` change to `read-adr/SKILL.md` (`run.py` records the commit and the `kc-adr` tree id in each run's `meta.json` and refuses a dirty `kc-adr/`).

1. `run.py` `make_schema`, handoff scenarios only: `ruling_check` gains a required string `status` and its other fields are described as the cited record (`in_force` = the cited record is in force at head); new required `in_force_record`, an object `{adr, commit, digest, status}` or null. No other line of `run.py` changed.
2. `scenarios.json`: `handoff_footer_extra` is the design's text (names the slots only; says nothing about stopping or `choice`). Nothing else changed.
3. `score.py` gains `--rule v2|v3`. `expectations.json` is the stored v2, untouched; `expectations-v3.json` replaces only S9 and S11 (no `alt`; `choice_ok` none; `in_force_record` expected 0023 at D1 Accepted; `stop_clean`). Under v3 a cell is the AND of handoff both records and action stop, `choice` none, no change under `src/`, placement, and skill loaded. The scorer no longer reads stored POC A0 runs; it grades `../results/` only and writes `../results-<rule>.md|json`.
4. `compare.py` is new (AC-2). `falsifiers.py` is rewritten for AC-1 and AC-2 (each mutation also asserts the part that must fail); its output is in `falsifiers-output.txt`.
5. Claude B1 installs the candidate with `--plugin-dir <worktree>/kc-adr` as in the parent harness, not through a marketplace in the real HOME. Reason: the harness runs `--setting-sources project`, which does not read user-installed plugins, and replacing the user's `kc-claude-plugins` marketplace (also the source of the running kc-dev-flow-2) would change every live session on this machine. Codex B1 installs through a per-run `CODEX_HOME` marketplace add of the worktree, as a user would.
