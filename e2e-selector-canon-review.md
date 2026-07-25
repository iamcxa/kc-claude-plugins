---
title: Re-decide the canonical selector grammar — it has been declared for three months and adopted zero times
status: implementation
source: captain approval 2026-07-25, escalated out of e2e-selector-lint-gate when the codemod spike showed the canonical form is unsupported by the target apps
started: 2026-07-25T13:47:31Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-e2e-selector-canon-review
issue:
pr:
design: required
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

## Stage Report: implementation

- DONE: `compiler/lib/selector-translate.js` — add the `text=V` branch.
  RED recorded (10 tests, 7 failing on the new behavior) before implementing;
  GREEN after — commit `4f72e49`. `compiler/test/selector-translate.test.js`
  exercises `text=AlphaBtn`/`text=GammaLabel` against the entity's own
  empirical-record snapshot fixture via a real `grep -F` subprocess (not a JS
  string compare) plus a negative control (`text=NotPresent` must NOT hit) —
  satisfies AC-3 by exercising, not by reading the branch.
- DONE: `scripts/lint-mapping.sh` — remove CLASS 1, fix CLASS 3.
  Both enforcement blocks deleted (kept CLASSES 2/4/5); header comment,
  `usage()`, and the two test fixtures/smoke script that quoted the old class
  list updated to match. Empirically re-verified against the 5 real carlove
  mapping files: 3/5 pass outright, the 2 remaining failures are exclusively
  `>> nth=N` (CLASS 2, still correctly banned) — zero failures from CLASS 1/3.
- DONE: Full suite once at the exit, after scoped tests are green.
  `npm test` (`node --test compiler/test/*.test.js`): 637/637 passing,
  including the 122 backward-compat `role=X[name=Y]` assertions in
  `codegen.test.js` (unchanged behavior — falsified by any edit to the
  existing role-form branches, which were not touched).
- DONE: Remove the executability claim.
  `CLAUDE.md` § Selector Priority now states `selector:` is a locator DSL
  translated by the compiler for `expect:`/visibility checks — and precisely
  scopes the one place that's still literal: `click`/`fill` pass the raw
  value to `agent-browser` unless `css_selector:` is set (verified by reading
  `codegen.js`'s click/fill cases, not assumed — see Summary). Same statement
  added to `agents/e2e-mapper.md`. AC-2 grep swept clean outside `CHANGELOG.md`
  (release-please-owned, not hand-edited per repo convention).
- DONE: Demote `[role][aria-label]`.
  Now priority item 4 in `CLAUDE.md` and `agents/e2e-mapper.md`, "use ONLY
  when the DOM genuinely carries a literal `aria-label`" — `role=<r>[name=…]`
  and `text=<v>` are the new items 2-3 (primary/native).
- DONE: Document `css_selector:`.
  `CLAUDE.md` § Selector Priority: field, read site (`resolver.js:62`), and
  both consumers (`click` eval-path, required for `runtime_ref` SC-1032
  sensitive fills) — traced from `codegen.js:1291,1343,1363`.
- DONE: Collapse the restatements.
  `CLAUDE.md` is the sole authority; `agents/e2e-mapper.md` and
  `references/common-patterns.md` now point at it (mapper.md keeps a short
  emit-order summary since it's a live agent prompt, not idle prose — its
  own executability/priority claims were still required to be correct
  in-place, not just cite elsewhere). `agents/e2e-flow-verifier.md`,
  `docs/ci-integration.md`, `docs/debugging.md`, `skills/e2e-compile/SKILL.md`,
  `skills/e2e-walkthrough/reference.md` corrected in place (small, table-row
  restatements). `CHANGELOG.md` left untouched (historical + release-please
  owned). See Summary for one deliberately-deferred file.
- DONE: Resolve the contradictions.
  CLAUDE.md §8/§9 resolved by the priority-list rewrite (bare `text=` no
  longer sits under the nth-chord/find-subcommand items). `e2e-flow-verifier.md`
  Critical Rule 9 and the `data-testid="value"'` example (`:324-325`) fixed.
  `e2e-test-runner.md:550` — narrow wording-only fix (dropped "canonical",
  clarified CLI-only scope); lines 548-561 (Rule 1c, Rule 2, the guarded
  Eval-Fallback Removal Policy) otherwise untouched per the Do-Not-Touch
  boundary.

### Summary

Code: `selectorToA11yPattern()` gained a `text=V` → `"V"` branch (RED→GREEN,
commit `4f72e49`), and `lint-mapping.sh` stopped banning `role=X[name=Y]`/bare
`text=` while keeping CLASS 2/4/5 (nth chord, has-text, find-subcommand-as-
value) banned. Docs: `CLAUDE.md` is now the single Selector Priority
authority; the false "selector: is executed directly / silently mishandled"
claim is gone from every live doc (commit `70926ed`). Zero mapping files
touched — verified via `git status` in the external carlove corpus used for
empirical checks.

One finding surfaced during implementation, not in the approved scope: the
"`selector:` is never executed directly" framing in the entity body is true
for `expect:`/visibility checks (`codegen.js:1572`) but **not** for `click`/
`fill` — those pass the raw `selector:` value straight to `agent-browser
click|fill` unless `css_selector:` is set (`codegen.js` click/fill cases,
unchanged, "Do NOT touch"). I wrote the CLAUDE.md claim scoped to what's
actually true rather than repeat the broader claim as given — restating a
false invariant is the exact defect class this entity exists to fix. Whether
`role=X[name=Y]`/`text=V` reliably resolve on the click/fill path was not
covered by this entity's browser spike (which tested a11y-grep and `find
role … click`, not `agent-browser click 'role=…'` directly) and is worth a
follow-up spike — possibly under [[e2e-guard-eval-fallback-removal]] or a new
entity, captain's call.

Also deliberately deferred: `agents/e2e-test-runner.md` still calls
`role=X[name=Y]`/bare `text=` "BANNED Playwright forms" at line 557 (inside
the guarded 548-561 Rule 2) and restates that at Critical Rules 9/601 and
observability line 491. Only line 550 was named in the contradiction list;
fixing 596/601 without touching the guarded Rule 2 would have split the file
against itself, so I left all four in place. Flagging for the captain rather
than silently leaving it invisible.

## Feedback Cycles

- Cycle 1: return — SO/EM gate; surface 2 commits / 14 files / +263-133 vs estimate none-declared (ideation recorded no appetite — a gap in this entity's own ideation, noted rather than back-filled); AC unchanged (scope not narrowed; the three findings are all inside approved scope).

### AC re-score — the FO's earlier scoring was wrong, corrected here

**AC-1 → PARTIAL** (was recorded PASS). The criterion reads "the rule and the corpus
agree". New lint moves the corpus from 6/32 passing to 13/32; **19 still fail**. That is
progress, not agreement. The residue is `>> nth=` (339 lines) and `has-text(` (25), both
correctly still banned — ownership of the nth residue sits with
[[e2e-nth-chord-widening]]. The hand-built login-page mapping that "passed" was written
to the very rules under test and could not have failed; it evidences that the lint
change works as intended, not that the criterion is met.

**AC-3 → PARTIAL** (was recorded PASS). The headline "81/81 translate, zero pass
through raw" is true by construction: `selector-translate.js:108` matches `^text=(.+)$`,
so a non-null return is guaranteed and the metric cannot go below 100%. Re-measured
against what the patterns can actually match: **28 of 81 compile to patterns that can
never match** — 10 regex forms (`text=/Every \d+h/` → `"/Every \d+h/"`) and 18 chorded
(`text=取消預約 >> nth=0` → the whole chord inside the quotes). The 6/6 live-snapshot
round-trip with a negative control stands and is real, but it exercised only the
plain-literal class.

The sharp edge: the new lint **passes** those 28, where old CLASS 3 refused them. This
commit removed a refusal without adding the matching translation — one fresh instance
of the exact defect class the entity exists to remove.

**AC-2 → PASS**, independently confirmed by the reviewer.

### Return list (closed — no redesign; do NOT re-open the un-ban, the demotion, or the premise correction)

1. **`compiler/lib/selector-translate.js` — make the `text=` branch refuse what it
   cannot faithfully translate.** Either mirror the literal-prefix extraction the
   `role=` branch already has at `:86-91`, or return `null` for regex and chorded forms
   so they take the documented fallback. Invariant to restore: **a non-null return is a
   pattern that can actually match.** Add the corpus regex and chorded cases to
   `selector-translate.test.js`.
2. **`agents/e2e-test-runner.md` — MOVE `role=<r>[name="<v>"]` and `text=<v>` into Rule
   1's NATIVE list at `:550`; do not merely delete them from Rule 2's banned list at
   `:557`.** Deleting alone leaves them matching neither rule, which re-opens the eval
   bypass. Then fix `:596` (it still says *prefer* `[role][aria-label]`, contradicting
   the demotion, and advises `find text "<v>"` as a selector value, which CLASS 5 bans)
   and `:601`'s form list. The earlier justification for leaving these — that they sit
   inside or adjacent to the guarded Eval-Fallback block — does not hold: `## Critical
   Rules` starts at `:584`, so `:596` and `:601` are 35-45 lines outside the guard at
   `:548-561`. Only `:557` is inside. Falsifier: `git diff` must show no change to any
   sentence containing "fall back to eval", "--allow-eval-fallback", or "eval bypass".
3. Nothing else. `codegen.js` stays untouched.

**Check the reviewer named that the FO missed:** `codegen.js` being absent from the diff
is necessary but not sufficient for "compiled behaviour unchanged". Branch selection
depends on the translator's return value, so every `text=` selector moved from the
`null → _poll_visible` fallback to `_poll_snapshot_contains` (`codegen.js:1572-1597`)
without that file changing a line. Any future translator change needs this check.
