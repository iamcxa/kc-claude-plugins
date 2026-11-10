fix(kc-dev-flow-2): exclude the exact PR attribution line from step links

When a gate message names `review/pr-body.md`, its generated Claude Code attribution link currently holds the ask as an unrecorded Captain step. `links()` now discards a line whose complete whitespace-normalized content equals the allowlisted attribution line before extracting URLs.

Every other URL still requires a recorded step, including the attribution URL in an ordinary instruction or an attribution line with additional text. The `steps` usage text describes this bounded exemption.

Validation on 2026-11-10 at `2a72c89b9aa9d114e45aeb16b746b8ca9f747bb8`:
- Full `test_delivery_gate.py` suite: 205 passed, 1 existing environment-dependent replay skipped (stdlib unittest loader; saved `implementation/run-suite.py` and `implementation/tests.json` in the task's state folder).
- Three `variant_of` falsifiers exercised with `python3 -B` and cleared script caches: removing the line exemption, exempting the URL everywhere, and using substring matching each fail the corresponding regression assertions.
- Repository `lint-skills.py`, package `adr_lint.py docs/adr --since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`, `number_guards.py check`, `design_surfaces.py check`, and `comment_ratio.py` passed. Added comments: 0 of 93 code lines, within the 5% maximum.
- Both `question` and `steps` pass the attribution-only PR body; real Captain links still hold until recorded. Startup document bytes and merge-check output remain unchanged; `--help` grows by the designed 11 words.

Only `delivery_gate.py` and `test_delivery_gate.py` change. No version or CI workflow change. CI cost per PR was not measured. RoboRev and hosted CI have not run; FO owns publication and those checks.
