Re-review fails: four prior P1 areas remain bypassable.

- [P1] Profile/retained — **new bypass**. Profile now comes from the receipt, but any nonempty, nonexistent `retained_surfaces` list produces zero checked files and passes. `kc-dev-flow/scripts/surface-map-check.py:185-190`
- [P1] Free-text target — **closed**. Targets outside the allowed forms are rejected. `kc-dev-flow/scripts/surface-map-check.py:221-227`
- [P1] Without-it pair — **new bypass**. Only nonempty strings are required; `true | true` is accepted without executing or associating either value with the surface. `kc-dev-flow/scripts/surface-map-check.py:211-220`, `kc-dev-flow/scripts/fixtures/surface-map/free-text-target-evidence.md:4-8`
- [P1] Exclusions — **open**. Caller regexes are removed, but hardcoded `test`, `tests`, `fixture`, and `fixtures` paths still hide changed files—including production changes. `kc-dev-flow/scripts/surface-map-check.py:42-43,88-89`
- [P1] Production shape mapping — **new bypass**. The file and path entry are required, but the shape obligation is never compared with the evidence target; any value maps successfully. `kc-dev-flow/scripts/surface-map-check.py:199-203,228-229`
- [P2] Contract test only pinned prose — **closed**. It now invokes the checker for two negative cases. `scripts/kc-dev-flow-contract-test.py:1959-1985`

New findings:

- [P1] Deleted files are silently omitted by `--diff-filter=ACMR`, violating production’s “every changed file” contract. `kc-dev-flow/scripts/surface-map-check.py:73`
- [P2] The contract test has no successful checker case and does not exercise POC retention, exclusions, production mapping, or a missing/false without-it pair. `scripts/kc-dev-flow-contract-test.py:1973-1985`

Review was static because the supplied commit is not checked out and this workspace is read-only.

```text
Remaining: Four P1 bypasses and one P2 coverage gap.
Next: Fix the open bypasses and add positive plus branch-specific checker tests. (you)
Closable: no
```
