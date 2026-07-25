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

## Spike result, 2026-07-25 — the premise above is wrong, re-cut before building

A headless spike built the codemod and ran it over all 452 unique banned selector strings.
Artefacts and evidence: `.context/mini-spike/` (report, codemod, 38 tests). The tests were
independently confirmed non-vacuous — reintroducing the `nth` off-by-one turns 7 of 38 red and
restoring it returns them to green.

**Only 254 of 452 (56.2%) transform mechanically; 198 are refused.** The "~88% mechanical"
figure in the Problem section counted *occurrences* (~2,500); this counts *unique strings*, and
the unique count is the one that sizes the work, because each distinct string needs its own
decision. Both numbers are true and the earlier one is the misleading one.

Two findings invalidate "codemod, then flip the gate on" as the plan:

1. **The canonical replacement is not a semantic equivalent, and it governs 249 of the 254
   transforms.** Playwright's `role=X[name="Y"]` matches the *computed accessible name* and the
   *implicit* ARIA role; CSS `[role="X"][aria-label="Y"]` matches two *literal attributes*. For a
   plain `<button>Save</button>` the Playwright form matches and the CSS form matches nothing —
   the element carries neither attribute. Playwright's quoted name match is also
   case-insensitive and whitespace-normalised; CSS attribute matching is neither.

   Read this against the runtime that actually exists: agent-browser drives Chrome over CDP and
   is **not** Playwright, and the plugin's own docs say these Playwright forms are already
   "silently mishandled at runtime (fallback eval path -> false positive risk)". So the migration
   is not "working -> broken"; it is "silently mishandled -> matches nothing, loudly". That may
   be an improvement. It may also be a fresh crop of false negatives. **Selector text cannot
   settle it — only a browser against the real app can**, and the spike says so plainly rather
   than claiming the migration is safe.

   Consequence beyond this entity: `e2e-pipeline/CLAUDE.md` § Selector Priority documents
   `[role="<r>"][aria-label="<v>"]` as the canonical form. If that only holds for apps that
   literally spell out `role` and `aria-label`, the canon itself needs review — which is a
   bigger question than this entity and should be escalated, not absorbed.

2. **The largest refusal class is a schema change, not a rewrite.** 83 of the 198 refusals are
   bare `text=`, whose canonical target `find text "<v>"` is an agent-browser *subcommand*, while
   the mapping schema stores a `selector:` string. Twenty of those also carry an `nth=` chord.
   No text substitution reaches them.

Two smaller corrections to the framing: the `>> nth=N` off-by-one was named the riskiest
mechanism in this entity's brief, but only 11 of 452 selectors survive to a Transform-2 rewrite
— it governs 2.4% of the migration, not the bulk. And fixing the arithmetic does not make
Transform 2 correct anyway: Playwright's `nth=N` indexes into the *matched set*, while CSS
`:nth-of-type(N)` counts same-tag *siblings under a parent*. They coincide only in a special
case.

**What ideation should now decide**, given the above: whether this entity still belongs in
sprint 1 at all, or splits into a browser-verified migration (which needs a target app and
therefore a different sprint shape) plus a much narrower gate covering only the classes whose
replacement is genuinely equivalent.
