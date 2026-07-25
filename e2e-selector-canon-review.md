---
title: Re-decide the canonical selector grammar — it has been declared for three months and adopted zero times
status: backlog
source: captain approval 2026-07-25, escalated out of e2e-selector-lint-gate when the codemod spike showed the canonical form is unsupported by the target apps
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: rd55vfpddtyvsbfqxqecj6cx
---

## Problem

Release 2.7.0 (2026-05-04, "Selector Grammar Alignment") established
`[role="<r>"][aria-label="<v>"]` as the canonical selector form, banned the Playwright
`role=X[name="Y"]` alternative in `scripts/lint-mapping.sh`, instructed `agents/e2e-mapper.md`
to emit the canonical form, and restated the rule across 13 markdown files.

Measured over 32 unique real mapping files, the newest written **today, 2026-07-25** — almost
three months after the canon shipped:

| Form | Occurrences |
|---|---|
| canonical `[role="…"][aria-label="…"]` | **0** |
| banned `role=X[name="…"]` | **2,183** |
| `data-testid` | 167 |
| `find role` subcommand | 1 |

This is not a corpus that predates the rule. Mappings generated today still emit the banned
form exclusively and the canonical form not once. **The canon has been in force for three
months and has changed nothing.**

The reason is structural, not disciplinary. In the primary target app, `aria-label` appears in
21 of 741 component files (2.8%) and an explicit `role=` in 10 (1.3%). CSS
`[role="button"][aria-label="Save"]` matches two *literal attributes*; for a plain
`<button>Save</button>` it matches nothing. The mapper cannot emit the canonical form for
elements that do not carry the attributes, so it emits what the accessibility tree gives it —
which is shaped like the banned form. Meanwhile Playwright's `role=X[name=Y]` matches the
*computed accessible name* and the *implicit* role, which is why it reads correctly off an a11y
snapshot even though agent-browser (CDP, not Playwright) then mishandles it at runtime.

So the pipeline is in the worst of both states: the form that describes what the mapper can see
does not execute, and the form that executes cannot describe what the mapper can see.

## Why this is the thesis of the whole programme in one artefact

An invariant was declared in prose — in a linter nothing calls, in an agent body, and in 13
restatements — and never placed at a boundary that could refuse. Three months later it is
provably not true, and nobody noticed, because nothing was ever in a position to notice.

## Notes for ideation

- Blocks [[e2e-selector-lint-gate]], which was pulled from sprint 1 on this finding. That entity
  as written would reject 26 of 32 mappings in favour of a form the apps structurally cannot
  support — it would break the pipeline rather than repair it. Do not restart it until this
  entity concludes.
- The candidate answers are visibly different in cost: `data-testid` already has 167 real uses
  but requires editing application source; the `find role|text` subcommand path matches what the
  mapper can observe but is a *subcommand*, not a `selector:` value, so adopting it is a mapping
  schema change (this is the same wall the codemod spike hit — 83 of its 198 refusals were bare
  `text=` for exactly this reason).
- Whatever is decided, the decision must land somewhere that can refuse it, or this recurs.
  Prefer the outcome that [[e2e-schema-contract]] can enforce over the one that reads best in
  CLAUDE.md.
- Before deciding, settle the empirical question the codemod spike could not: does the CSS form
  resolve against the real app at all? That needs a browser and a running target — a static
  read of selector text cannot answer it, and the spike said so explicitly rather than guessing.
- Check whether the mapper verifies that the selector it writes resolves. Exploration clicks via
  ephemeral `@ref` handles and then writes a separately derived selector string; nothing in
  `agents/e2e-mapper.md` requires confirming the written string matches anything. If so, that is
  the seam that let this run for three months.

---

## Decision — captain approved `narrow`, 2026-07-25

Three independent passes converged. The framing in the Problem section above was
half right and located the defect in the wrong place; the correction below is the
ruling.

**The defect is the executability premise, not the schema.** `compiler/lib/selector-translate.js`
emits byte-identical output for the canonical form (`:47-50`) and the banned form
(`:74-76`) — both become the a11y pattern `<role> "<name>"`, which `codegen.js:1572`
feeds to `_poll_snapshot_contains` for a `grep -Fq` against the accessibility
snapshot. **The compiler never executes the selector string; it translates it.** So
the 2,183 "violations" were never broken on the compiled path, and PR #8 chose a
syntax to satisfy a "must be directly executable" constraint that its own compiler
already contradicted.

### Empirical record (settled here, previously assumed by everyone)

Against a live `agent-browser` 0.21.4 and a fixture of three buttons — two with no
`role` and no `aria-label`, one with both:

```
- button "AlphaBtn" [ref=e1]        # no attributes; snapshot still emits role + computed name
- button "GammaLabel" [ref=e3]      # aria-label wins over text content
  - StaticText "GammaBtn"

grep -Fq 'button "AlphaBtn"'        # HIT
[role="button"][aria-label="Save"]  # count 0 against <button>Save</button>
find role button click --name BetaBtn   # clicks BetaBtn — matches the computed name
```

This settles the one condition the engineering-judgment review named as its single
point of risk: had the grep missed, the whole a11y path would have been broken for
97.2% of components and a schema rewrite would have been justified. It hit, so the
narrow route holds and its confidence rises from medium to high. The `aria-label`
line also shows the snapshot carries the *computed* accessible name — which is
exactly what `role=X[name="Y"]` encodes. The banned form was a faithful encoding of
the snapshot all along.

### Why it survived three months

PR #8 solved a real defect — issue #7 reproduced `is visible 'role=tab[name="Lineage"]'`
returning false, falling through to an `eval` fallback, and reporting a **false PASS**.
The fixes that actually solved it are `selector-translate.js` + `_poll_snapshot_contains`
and the Eval-Fallback Removal Policy. **Neither depends on the syntax choice, and
neither may be reverted** — see [[e2e-guard-eval-fallback-removal]].

The syntax ban was cargo cult layered on top. The only form issue #7 verified as
working was `[role="tab"]` — role only. PR #8 generalised that to the *combined*
`[role][aria-label]` form, which no live app ever exercised: its three runtime
verification checks were all deferred on a missing `SNOWFLAKE_ACCOUNT`, and the
review stage elevated "static contract review is equivalent to a runtime check"
into a standing principle. The 0-versus-2,183 measurement is the bill for that
substitution. PR #8 also filed `docs/ship-flow/todos/compiled-vs-llm-divergence-baseline.md`,
which predicted this exact divergence and was never run.

### Approved scope — zero mappings migrate

1. State in `CLAUDE.md` and `agents/e2e-mapper.md` that `selector:` is a
   plugin-internal locator DSL, not an agent-browser argument. Remove the
   executability claim.
2. Un-ban `role=X[name="Y"]` — delete `lint-mapping.sh` CLASS 1 or drop it to warn.
   Keep CLASSES 2, 4, 5.
3. Add a `text=V -> "V"` branch to `selector-translate.js`, fixing CLASS 3, which
   currently points at a form CLASS 5 forbids.
4. Demote `[role][aria-label]` to a secondary form, used only where the component
   genuinely carries `aria-label`.
5. Document the existing but unrecorded `css_selector:` field (read at
   `resolver.js:62`, required by the runtime_ref fill path) — today it is dead code
   for any mapping `/e2e-map` produces.
6. Collapse the rule's 13 restatements to one authority plus the translator.

Resolve while editing: `CLAUDE.md` Selector Priority §8 prescribes the very form §9
and lint CLASS 5 forbid; `agents/e2e-test-runner.md:550` calls `find …` the
"canonical NATIVE form" while five other files call it deprecated; the `CLAUDE.md`
v2 example writes `selector: 'data-testid="value"'`, which is missing its brackets
and is not valid CSS.

**AC-1 — the rule and the corpus agree.** A mapping written by `/e2e-map` against a
real app passes `lint-mapping.sh` without edits. Verified by: linting a freshly
generated mapping. Falsified by: restoring CLASS 1, which returns 26 of 32 corpus
mappings to failing.

**AC-2 — the executability claim is gone and cannot silently return.** No shipped
doc asserts `selector:` is executed directly. Verified by: grep across the plugin's
markdown for the claim. Falsified by: any surviving restatement.

**AC-3 — the `text=` class resolves.** The 83 corpus selectors refused by the codemod
spike as `text-engine-not-a-selector` translate to a snapshot pattern that greps.
Verified by exercising them against a real snapshot, not by reading the branch.

Path item 4 of the reviewed route — replacing raw `is visible` in the runner and
verifier with the compiler's snapshot-grep — moved to
[[e2e-guard-eval-fallback-removal]], which owns the divergence question.
