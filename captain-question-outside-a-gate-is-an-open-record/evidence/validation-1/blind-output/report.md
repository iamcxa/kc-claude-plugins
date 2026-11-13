# Independent blind reader report

## Result

PASS for independent contract interpretation on the supplied fixtures: 14 files, 28 events, 56 declared clocks, 20 nonempty snapshots, and 23 open-question rows. Every requested field is present: key, by, waiting_since, waiting_min, waiting_bound, holds, interruptions, state. An independent interval oracle checked the key membership at all 56 clocks and all eight fields of all 23 rows. The implementation-under-review was not read or run, so this report does not assert product equivalence.

`reader.py` creates `output.json` (one snapshot per clock), and `counterexamples.json`. `interval-check.json` records the separate check. Output paths are local under this report's directory.

## Exactly what I read

Task evidence was limited to the following supplied contract, clocks, and fixture contents. I also read `/Users/kent/.codex/RTK.md` as general operating instructions. No repository/product code, tests, implementation reports, task entity, other validation evidence, history, or memory files were read. I read the outputs I generated in this directory to verify this report. Input filenames were enumerated only using the `*/asks.jsonl` scope.

- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/contract.md` — SHA-256 `606531b6032830b93b0675c1068da5e0d169fae3b846381050b458a07383a30a`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/clocks.json` — SHA-256 `25846220f78dfcc0e629275b585c4fcbcf73feb4427da7d977c967a4703b3102`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-1/asks.jsonl` — SHA-256 `10349eb10c5aad8d1d48658f8f65b0d321521922da2f9828ff93b53d1558fd96`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-10/asks.jsonl` — SHA-256 `1918e34b6bb7b9fd88d8043c68b3daabe78d9747d889cba8435cfb64476f60b9`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-11/asks.jsonl` — SHA-256 `3afd55630eb37bec10889875fe59a473ed421c91c15c91b1c3482154378b98bb`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-12/asks.jsonl` — SHA-256 `6ddd91ea8385c729ccdf71e4ab3535e48b42ebf2952791f12a7dfced79db1595`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-13/asks.jsonl` — SHA-256 `bc5dc18e3fcf00ccb110831c9f3303c50dd02f5784a7dd55c39a50ee9d13647b`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-14/asks.jsonl` — SHA-256 `e8a45c1300af8f1085a4837ff4c3b508d6c82898f3cb497142ace4d8e388e3de`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-2/asks.jsonl` — SHA-256 `8873c111a2f8350f4c3f07ce8212e43117f318c22b31c091c734775040716099`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-3/asks.jsonl` — SHA-256 `e8f28b048ed99c063e2f64e5f0a5c4278b4bd82b8d413c410d4e981396ad1cd7`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-4/asks.jsonl` — SHA-256 `8218e3d8df2c09f352f1c251953bc8530c96d65d0d32caeb852d3397c8351641`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-5/asks.jsonl` — SHA-256 `02879c53761627b6a4f002371b34e15a72410e1604fcb3de88fd42e60bec4420`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-6/asks.jsonl` — SHA-256 `21283189cd312dc9bb133070a533ce33ec112026c56712ffbf02201af7d712fe`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-7/asks.jsonl` — SHA-256 `0ca41bd64034d4b1a46beb5dd5369f57301a6f2a3684b01b3eaa6ed5e08e8cf4`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-8/asks.jsonl` — SHA-256 `f69f365122e8c233b8b88789a832d27c154d842ff160eda7d8774371b046e8f0`
- `/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1/blind-input/replay-9/asks.jsonl` — SHA-256 `c5def5ac8ef589a31bf4f4725c730dc664855bd12492ce8a3a4baabe38cc6d73`

## Questions, ambiguities, and choices

1. Does “by that instant” include an event exactly at the clock? Chose inclusive `at <= clock`; therefore an answer closes the record at that exact second. This follows the contract's command wording and the state definition. No question to the author is needed for the provided fixtures.
2. The contract does not state elapsed-minute rounding. Chose exact elapsed seconds divided by 60, retaining fractional minutes rather than rounding or truncating. Some clocks intersect other fixture intervals at fractional minutes, so this affects the supplied output. A display rounding convention is unspecified; the numeric output is the unrounded elapsed value.
3. Output order and JSON envelope are unspecified. Chose declared clock order, objects with `clock`, `open`, and `diagnostics`, and lexicographic key order within `open`. Comparison checks row content by key and does not depend on row order.
4. The supplied fixture directory is a local export, not a Git branch. Chose the explicitly supplied direct-child `*/asks.jsonl` inputs as the complete observation set. Did not read any Git tree, task file, or archive. Missing records still do not prove that no unrecorded question exists.
5. For events ignored by the state machine, interpreted interruption counts as accepted ask/reask showings only: a duplicate ask or post-closure reask does not add an interruption. No such events occur here.
6. Forward-version “unknown” state recovery is not specified. Chose to retain unknown for that key after a future-version line, rather than infer a later known state. The fixtures contain no future-version or legacy lines; this choice does not affect results and is not validated here.
7. No semantic interpretation of the question prose was necessary. Some text appears truncated; the contract supplies explicit state fields, so prose completeness does not change the list. No outside source was used to repair or reinterpret it.

No other questions or ambiguities were encountered. No clarification was obtained from another agent or author, and no product-derived expected output was supplied to this reader.

## Deliberate wrong-list comparisons

The comparison detects missing keys, unexpected keys, changed row fields, and duplicate keys. A copy of a correct list passes as a positive control. Both deliberate mutations fail:

- At `2026-11-05T09:35:56Z`, remove the still-open `replay-5#1`: comparison reports it missing.
- At `2026-11-05T09:40:56Z`, retain `replay-5#1` even though its answer is recorded at that exact clock: comparison reports it unexpected.

`counterexamples.json` preserves complete expected and wrong lists and comparison results. These prove the comparison notices both failure modes; they are not evidence of a product defect.

## Limits

All provided fixture lines are version 1, and every file has exactly one ask followed by one answer. All have known asking times, one showing, and the same asking session. The three distinct holds values occur and are preserved. These data do not exercise late recording, unknown times, reasks, revisions, withdrawals, acted, stale-channel answers, duplicate keys, invalid transitions, legacy records, future-version records, archived tasks, push latency, or gates. The reader includes some contract-derived handling of additional events, but this fixture run establishes none of those branches. It is a reader, not a full writer-schema validator. Git enumeration and gate records are outside the authorized input set. No repository or external state was changed.

## Reproduction

```sh
python3 reader.py ../blind-input .
```

Run from this report's directory. Python 3 standard library only. This produces the primary output and counterexample evidence; the separate interval-check evidence was generated by direct interval comparisons against the same allowed fixtures.
