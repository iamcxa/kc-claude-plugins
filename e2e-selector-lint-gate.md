---
title: Refuse banned selectors at compile time, and migrate the ones already written
status: backlog
source: sprint-1 (compiler boundary) entity 4 of 5; split out of e2e-assertion-honesty-gate once the corpus violation count was measured
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: b4xpj6xrf8p7a9w0rvrxjchk
---

## Problem

`scripts/lint-mapping.sh` rejects five selector forms that the plugin's own mapper agent says
are "silently mishandled at runtime (fallback eval path -> false positive risk)". The compiler
never calls it. It is invoked only by `test/integration-smoke.sh` and documented as a CI step,
so the ban is enforced by restating it in 13 markdown files and by nothing that can refuse.

Measured over the corpus, the gap is not hypothetical: **26 of 32 unique mappings fail the
linter**, across roughly 2,500 occurrences. The distribution decides the shape of the work —
about 1,886 are Playwright attribute syntax (`role=button[name="X"]`, `role=textbox[name=...]`,
and friends) and 338 are the `>> nth=N` chord, both of which are mechanical rewrites to
`[role="X"][aria-label="Y"]` and `:nth-of-type(N)`. The remaining ~299 are bare `text=`, which
maps to a `find text "..."` subcommand rather than a selector string and therefore needs
judgment, not a rule.

So this entity is not "wire up a linter". It is a codemod for ~88% of the violations plus a
gate that keeps the rest from coming back, and the migration is the larger half.

## Notes for ideation

- Decide the gate's severity and its migration path together. A hard gate on day one reds 81%
  of existing mappings; a codemod that runs first and a gate that lands after is the obvious
  sequence, but it needs the codemod to be provably lossless before the gate can be trusted.
- The `>> nth=N` rewrite is off-by-one — `nth=0` is zero-indexed and `:nth-of-type(1)` is not.
  Any codemod that gets this wrong silently retargets elements, which is worse than the
  original violation. Treat it as the riskiest mechanism and spike it first.
- The 299 bare `text=` occurrences cannot be mechanically converted and should be reported for
  human decision rather than guessed at. Deciding what the gate does with them — reject,
  grandfather, or quarantine — is the load-bearing call.
- Ownership question for the gate: port the bash rules into the compiler, or shell out to the
  existing script? Porting removes a process boundary and lets the errors join the structured
  channel from [[e2e-json-diagnostics]]; shelling out keeps one implementation. Pick one and
  delete the other — two copies of a ban is the disease being treated.
- Falsification: a mapping carrying a banned form must fail compilation. Reverting the gate
  must make it compile again.
