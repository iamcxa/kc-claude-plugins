Failed: one prior P1 remains open; two new P1 bypasses found.

- Closed — POC retained surface absent from diff: `kc-dev-flow/scripts/surface-map-check.py:219-225`
- Closed — literal `true | true`: `kc-dev-flow/scripts/surface-map-check.py:154-166`
- Open — hardcoded test/fixture exclusion still silently skips undeclared changed files by default: `kc-dev-flow/scripts/surface-map-check.py:228-232`
- Closed — production shape obligation compared with evidence target: `kc-dev-flow/scripts/surface-map-check.py:251-258`
- Closed — deleted files included and validated: `kc-dev-flow/scripts/surface-map-check.py:76,142-148`
- Closed — positive checker case added: `scripts/kc-dev-flow-contract-test.py:2058-2063`

New P1:

- [P1] Type changes remain omitted. `--diff-filter=ACMRD` excludes Git’s `T` status, so replacing production code with a symlink or submodule can pass without evidence: `kc-dev-flow/scripts/surface-map-check.py:76`
- [P1] Arbitrary no-op commands satisfy the without-it pair. For example, `echo <changed-path> | git status -- <surface-path>` passes because validation checks only substrings and the `git` prefix, not mutation semantics: `kc-dev-flow/scripts/surface-map-check.py:154-166`

```text
Remaining: Three P1 findings
Next: Fix the remaining bypasses and re-review (you)
Closable: unverified
```
