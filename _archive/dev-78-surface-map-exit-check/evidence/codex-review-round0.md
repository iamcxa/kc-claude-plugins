SHA handling is correct: `git diff ... base candidate` does not inspect the working tree.

[P1] kc-dev-flow/scripts/surface-map-check.py:99 — Profile and retained paths come from caller-controlled flags, not the receipt’s profile depth or `poc_outcome`; `--profile poc` with no `--retained` checks zero files and succeeds.
[P1] kc-dev-flow/scripts/surface-map-check.py:88 — Only an exact unknown `AC-N` is rejected; arbitrary text such as `SURFACE: file.py -> anything` passes without naming an AC or any declared Brief obligation.
[P1] kc-dev-flow/scripts/surface-map-check.py:130 — A SURFACE entry contains only `path -> target`; the required without-it command and removed-variant pair are never parsed or validated.
[P1] kc-dev-flow/scripts/surface-map-check.py:101 — Caller-supplied `--exclude` accepts any regex, including `.*`; additionally, hardcoded path patterns let production files hidden under `tests/` or `fixtures/` escape checking.
[P1] kc-dev-flow/scripts/surface-map-check.py:138 — Production shape validation is optional, and even when supplied, a changed file absent from the shape mapping is accepted instead of reported missing.
[P2] scripts/kc-dev-flow-contract-test.py:1883 — The additions pin prose presence and compilation only; they never execute the checker, so AC-1–AC-3, the claimed failure observation, and recorded mutation behavior receive no contract-test coverage.

```text
Remaining: Fix the five enforcement bypasses and add behavioral contract tests.
Next: Revise the candidate (you)
Closable: no
```
