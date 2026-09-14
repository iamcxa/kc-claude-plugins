# Backlog admission: capture-oracle-never-caught-anything

## The usage record, which is the whole case

`kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` shipped in PR #433 as a
canonical manifest resource. Three recorded runs, zero findings:

| When | Result |
|---|---|
| implementation cycle 1 | generated `release-please-verdicts.tsv` from release-please `17.3.0` |
| validation cycle 2 | re-derived against `17.3.0`; all 13 rows identical, only the header date differed |
| validation cycle 2/3 | re-derived against `17.11.1`; all 13 rows agree |

The measured disagreement that motivated the design — release-please accepting
`feat(): x` where a hand-written grammar would not — was found at ideation by
requiring the parser directly out of `scripts/fixtures/release-please-runtime`,
before this file existed. The only recorded argument for keeping it is a
coordinated edit to both a fixture row and the checker's grammar, which has never
happened.

## Scope, measured

`git grep -n capture-oracle` on `origin/main` returns eight hits in six files, two
of them inside the file being deleted:

- `kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` — deleted
- `kc-dev-flow/contract-manifest.json:43` — resources entry
- `scripts/kc-dev-flow-contract-test.py:111` and `:490` — expected-resource sets
- `kc-dev-flow/references/pr-merge-extension.md:350` and its synced copy
  `docs/dev/_mods/pr-merge.md:468` — a descriptive clause, not a command
- `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv:10` — header comment

## Profile

`poc-exploration`, route `[build, prove]`, entering at implementation. The design
question is answered; an ideation stage would shape nothing. `poc_artifact` is
`retained` because this changes shipped bytes, so `poc_proof_path` resolves to
`fresh` and a fresh validation worker still runs. Verified: the loader resolves
both legs from this work item.

## What this does not touch

`check-pr-title.py`, any fixture row, the version-skew stop condition itself, the
release-please runtime, the released pr-merge body or its pin.
