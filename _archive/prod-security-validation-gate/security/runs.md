# Measurement runs, 2026-10-17

Agent `kc-pr-flow:tob-security-reviewer` (kc-pr-flow 1.12.0, `model: sonnet` declared), unmodified, dispatched from an ensign through the Agent tool with `model:` set per run (`sonnet`, `opus`, `fable` resolved to `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1` in each transcript's `message.model`). Every run `security_tier: full`. Reports under `reports/`, prompts under `prompts/` (`baseline-*` is the agent's own contract plus an environment note; `reach-*` adds one paragraph, the Reach brief).

Inputs (read only, machine-local, rebuilt by these commands):
- relay #347 at 1c5b1870: `git -C <relay checkout> diff a5af7e3c...1c5b1870 > pr347-1c5b1870.diff` (440 lines, 14 files, byte-identical to the earlier worker's copy by `cmp`) and `git archive 1c5b1870 | tar -x -C tree`.
- control, kc-claude-plugins #555 (merge commit a822c3e3, 5 files, 83 additions, a Python workflow check script, no public surface): `git diff a822c3e3^ a822c3e3` and `git archive a822c3e3`.

Cost columns. Tokens are summed per request from the transcript `usage`: fresh input, cache write, cache read. The transcript records output tokens only at stream start (under 1,000 per run while the reports are 6,000+ characters), so output is an estimate from characters at 3.5 per token, not a measurement. Dollars use the task file's price table ($ per million input/output: Sonnet 5.5 2/10, Opus 5.5 4/20, Fable 5.1 10/50). Two figures: ceiling = every input-side token at the full input price (no cache discount); assumed = cache write at 1.25x and cache read at 0.1x input price, multipliers not verified for these models. `tools/cost.py` reproduces both.

| Run | Findings | Names unbounded outsider write | Refusal | Seconds | Harness tokens | Cache write / read tokens | Ceiling $ | Assumed $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sonnet relay 1 (baseline) | MEDIUM injection, LOW | no | none | 104 | 56,380 | 96,084 / 880,058 | 2.00 | 0.46 |
| sonnet relay 2 | MEDIUM injection, LOW | no | none | 108 | 55,949 | 103,243 / 1,011,819 | 2.27 | 0.50 |
| opus relay 1 | MEDIUM injection | no | none | 314 | 74,877 | 128,421 / 2,241,205 | 9.63 | 1.69 |
| opus relay 2 | MEDIUM injection | no | none | 267 | 65,963 | 121,895 / 1,839,837 | 7.98 | 1.48 |
| fable relay 1 | MEDIUM injection, LOW | no | none | 368 | 82,939 | 229,405 / 1,934,828 | 22.02 | 5.18 |
| fable relay 2 | MEDIUM injection, LOW | no | none | 293 | 81,175 | 218,090 / 1,769,103 | 20.21 | 4.83 |
| sonnet control | MEDIUM, LOW | n/a | none | 57 | 47,442 | 99,151 / 281,371 | 0.79 | 0.33 |
| opus control | 3 LOW | n/a | none | 257 | 63,601 | 83,290 / 956,744 | 4.30 | 0.93 |
| fable control | 3 LOW | n/a | none | 269 | 64,374 | 249,572 / 1,093,239 | 13.77 | 4.55 |
| sonnet relay 1 (reach) | HIGH unbounded writes, MEDIUM injection, LOW | yes, HIGH | none | 139 | 92,488 | 172,326 / 1,832,880 | 4.07 | 0.86 |
| sonnet relay 2 (reach) | MEDIUM unbounded writes, MEDIUM injection, LOW | yes, MEDIUM | none | 133 | 103,680 | 183,075 / 1,952,596 | 4.33 | 0.91 |
| opus relay 1 (reach) | MEDIUM unbounded writes, LOW | yes, MEDIUM | none | 249 | 102,320 | 181,475 / 2,826,574 | 12.17 | 2.18 |
| fable relay 1 (reach) | HIGH unbounded writes, MEDIUM injection, LOW | yes, HIGH | none | 359 | 137,642 | 615,759 / 4,088,017 | 47.53 | 12.28 |
| sonnet control (reach) | none (`findings: []`) | n/a | none | 20 | 43,265 | 84,096 / 127,430 | 0.43 | 0.25 |

Harness tokens and seconds are the `subagent_tokens` and `duration_ms` of each run's completion notice. "Names unbounded outsider write" means the report says an outsider can create sessions or comments with no total cap (per-session cap only), read from each report by me; the 6 baseline relay reports name only per-session caps as facts or ignore the topic, and none flags the missing total.

Whole measurement, 14 runs: assumed about $36, ceiling about $150, of which Fable 5.1 is about three quarters of the assumed total (4 runs).

`tools/refusal_fixture.py` runs the 0.24.0 `design_surfaces.py check` on refusal-shaped saved reports; `proto/validation_fixture.out` runs the prototype on 14 validation-gate cases.

Tokens and seconds per run are reproducible only from this session's subagent transcripts (`tools/extract.py` and `tools/cost.py` read them under `~/.claude/projects/`); the table above is the record. The reports, prompts and fixtures are in this folder.
