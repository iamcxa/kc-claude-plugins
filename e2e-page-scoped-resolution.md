---
title: Make the page qualifier bind, or drop it from the grammar
status: ideation
source: sprint-1 (compiler boundary) entity 3 of 5; split out of e2e-typed-operands so the sprint stays inside the compiler
started: 2026-07-25T15:42:55Z
completed:
verdict:
worktree:
issue:
pr:
design:
id: 3tp0ym1mj0gcwssfxq9s4b0y
---

## Problem

`resolver.js:6-42` parses `"Click <element> on <page>"` and captures the page group — then
discards it. Element resolution goes against `buildSymbolTable` (`resolver.js:44-70`), which
flattens every page's elements into one mapping-wide table, so the page a step names has no
bearing on which element it resolves to. A step that says `on login-page` while naming an
element that only exists on `dashboard-page` compiles clean and drives the wrong element.
Collisions are tracked but only raised when an ambiguous name is actually referenced, so the
error surfaces on some corpora and not others for the same defect.

This is worse than an unsupported feature. The grammar advertises page scoping, authors write
it believing it constrains, and it constrains nothing — enforcement theatre. Either the
qualifier binds or it leaves the grammar; parse-and-discard is the one option that must not
survive.

## Notes for ideation

- Spike DONE, 2026-07-25 (`.context/spike-page-binding.js`, run over the 100-flow corpus). It
  answers the sizing question and surfaces a design constraint that was not anticipated:

  | | |
  |---|---|
  | page-bearing steps | 437 |
  | supply the qualifier | **307 (70%)** |
  | qualifier resolvable against the mapping | 288 |
  | steps whose element is not on the stated page | 38 |
  | — of those, element lives on `_global` | **36 (legitimate)** |
  | — **genuine mismatches** | **2** |
  | elements ambiguous across pages | 13 |

  So: **this is cheap insurance, not a bug fix.** The live defect count is 2 — both the same
  `back_button`, named on `booking-confirm` and `task-execution` while mapped only under
  `service-order-detail`. Removing the qualifier from the grammar instead is not cheap: 70% of
  qualified steps use it.

- **The load-bearing design constraint, and it is not in the original brief.** 36 of the 38
  apparent mismatches are elements stored under a shared page key (`_global`) and referenced by
  the page the user is visiting — correct authoring, not error. A binding implementation that
  compares the stated page against the element's own page key rejects all 36. That is **18×
  more damage than the 2 defects it catches.** Shared/global page keys must resolve against any
  stated page, and the set of such keys must be defined rather than pattern-matched on a leading
  underscore.
- The 13 ambiguous-across-pages elements are where binding buys something structural: today they
  are only caught when a step happens to reference them, so the same defect errors on one corpus
  and passes on another.
- Binding it means element lookup becomes page-scoped with a defined fallback for steps that
  omit the qualifier — decide whether omission means "any page" (today's behaviour, kept for
  compatibility) or is itself rejected. The second is stricter and belongs with
  [[e2e-assertion-honesty-gate]]'s migration wave if chosen.
- Expect strings have the same shape (`<element> visible on <page>`) and the same question.
  Decide both together or the grammar stays inconsistent.
- Falsification: a fixture step naming a real element under the wrong page must fail to
  compile. Reverting the binding must make it compile again.

## FO-authored scope (recorded verbatim per dispatch, not captain-authored — captain delegated the conn for this sprint)

**What gets worse without this.** The grammar advertises page scoping, authors write it
believing it constrains, and it constrains nothing. `resolver.js:6-42` captures the page group
and discards it; `buildSymbolTable` (`resolver.js:44-70`) flattens every page into one
mapping-wide table. A step naming `on login-page` while referencing an element that exists only
on `dashboard-page` compiles clean and drives the wrong element. That is enforcement theatre,
worse than an absent feature because it buys false confidence.

**What to keep if forced to cut.** The `_global` / shared-key handling is not an enhancement —
it decides whether this entity is net-positive at all: a naive stated-page-vs-element-page-key
comparison rejects 36 legitimate authorings to catch 2 defects. If the budget bites, cut the
*scope of what binds* (e.g. action side only), never the shared-key rule. The set of shared
keys must be explicitly defined, not pattern-matched on a leading underscore.

**What we are happily NOT doing.** (1) Not rejecting qualifier omission — steps that omit the
page keep today's "any page" behaviour; making omission itself an error belongs to
[[e2e-assertion-honesty-gate]]'s wave. (2) Not removing the qualifier from the grammar — 70% of
qualified steps supply it. (3) Not inventing an error-code vocabulary — [[e2e-schema-contract]]
owns that, still backlog. (4) Not fixing the 2 genuine defects as corpus data — they live in
`carlove`, not this repo; report them, do not edit `carlove`.

**One-sentence pre-mortem (class: hidden assumption).** "If this ships exactly per spec and
still fails, the most likely cause is that the shared-key set was enumerated correctly for
today's mappings and then silently decayed — a new shared page key added months later falls
outside the enumeration and starts rejecting legitimate authoring, with no signal that the list
went stale." The Design section below is built specifically to answer this: the shared-key
declaration is data-driven (lives in the mapping file itself, evaluated structurally), not a
resolver-side enumeration that can go stale, and the one hardcoded exception is a single
literal name already baked into two other places in this codebase (see Design, point 2).

## Design — page-scoped resolution with an explicit `shared` page flag

**The rule, stated once, for both the action side and the expect side** (xn deferred the expect
element-form specifically so it could be decided here, together — see "New evidence from xn"
above):

1. **Symbol table becomes page-scoped in addition to the existing flat table.**
   `buildSymbolTable` (`resolver.js:44-70`) gains `byPage: Map<pageName, Map<elemName, entry>>`
   alongside the existing `table`/`collisions`. The flat table is kept **byte-identical** — it is
   what omitted-qualifier steps use, so today's "any page" behaviour does not change (Non-goal 1
   above; also `resolveMultiSite`'s per-site symbol table gets the same shape, since it already
   calls the same `buildSymbolTable`).
2. **A page is "shared"** — its elements resolve regardless of which page a step states — **when
   `pages.<name>.shared === true`**, OR when its name is the literal string `_global` and
   `shared !== false` (a grandfathered compatibility default, not a prefix pattern: a page named
   `_footer` gets zero special treatment without the explicit flag). This default is not invented
   for this entity — `agents/e2e-mapper.md:150` already instructs the mapper to name detected
   cross-page elements `_global`, and `skills/e2e-test/SKILL.md:83`'s runtime warning-only
   element-reference check already special-cases `_global.elements.<name>` by the same literal
   name. Grandfathering it means the two real corpus mappings (`secha-app.yaml`,
   `secha-office.yaml`) need **zero data migration** to keep working; any *new* shared page must
   set the flag explicitly, closing the pre-mortem's drift class structurally — the declaration
   lives with the mapping data that needs it, not in a resolver-side list an author has to
   remember to update in a different file.
3. **Resolution, when a step states a page** (`Click X on P`, `Fill X on P`, `X visible on P`,
   `X is visible on P` (new form, point 6), `X (is )not visible on P`): look up `X` in `P`'s own
   table; if absent, look up `X` in every shared page; if still absent and `X` exists elsewhere
   in the mapping, raise `"element 'X' not found on page 'P' (found on: Y)" -- if it should be
   visible from any page, mark page 'Y' with shared: true in the mapping` (an actionable hint,
   never a bare rejection — this is the pre-mortem's "signal that the list went stale," not a
   promise that staleness can't happen); if `X` exists nowhere, the existing "not found in
   mapping" error, unchanged. If `P` itself is not a real page key, `"page 'P' not found in
   mapping"` — reusing `resolveNavigate`'s existing message shape for the same defect class
   (verified live: `booking-confirm` / `task-execution`, see Corpus evidence, are exactly this
   case, not "wrong page for a real element").
4. **Omitted-qualifier steps: untouched.** Flat table + collisions + referenced-only-ambiguity,
   byte-for-byte as today.
5. **Both `resolve()` (`resolver.js:335-354`) and `resolveMultiSite()` (`resolver.js:558-576`)
   get the identical fix**, via one shared `resolveElementOnPage` helper. The bug being fixed is
   itself an asymmetry (page captured, then discarded); fixing only one of the two structurally
   identical call sites would reproduce the same class of bug one level up. Cross-site `site:`
   selection is untouched — only the page-qualifier resolution *within* a site's own mapping
   changes.
6. **One new `EXPECT_PATTERNS` row**, xn's deferred 4th form: `^(\w+) is visible on ([\w-]+)$` →
   `element-visible`. Unsafe before this entity (2 clean flows would flip to ambiguity errors,
   per xn's measurement); safe now, because ambiguity collapses via point 3 the moment the page
   is looked at instead of discarded.
7. **Known refinement, not blocking:** when the "found on: Y" hint (point 3) names an element
   that is *also* ambiguous across 2+ non-shared pages, the prototype patch below reports only
   the first-registered page, not the full list the existing ambiguity error already knows how
   to print (`collisions.get(elemName)`). Implementation should union `collisions.get(elemName)`
   into the hint when present, for the same completeness the pre-existing ambiguity error has.

## Corpus evidence — measured this session

Working prototype of the exact patch above, built by anchored string-replacement against
`origin/main @ 529296d`'s real `resolver.js` (same patch-survival-safe technique as xn's
harness — never requires whatever happens to be checked out on disk) and run over the real
corpus: `.context/spike-3t-page-binding-before-after.js` (git-excluded, same convention as
`spike-deferred-rate.js` / `spike-xn-*.js`).

    node .context/spike-3t-page-binding-before-after.js .context/flow-corpus.txt

    (100 unique flows by content hash, 87 scored against their mapping)
                          BEFORE    AFTER     DELTA
    active expects        426       432       +6
    deferred expects      368       365       -3
    resolve errors        630       627       -3
    flows compiling clean 20        20        0

    RECOVERED strings (3): "email_input is visible on login",
      "data_table is visible on customer-profiles", "heading is visible on operations-overview"
    NEW errors (0)
    RESOLVED-AWAY errors (3): 'tab_all' ambiguous (2 click steps, service-schedule/
      employee-profiles), 'data_table' ambiguous (1 expect step, 9-way collision) — all 3
      collapse because the stated page now disambiguates instead of erroring
    FLOWS FLIPPED clean -> error (0); FLOWS FLIPPED error -> clean (0)

**Every number reconciles**: +6 active = 3 recovered (deferred→active) + 3 unerrored
(error→active, previously counted in neither bucket); −3 deferred = the 3 recovered strings;
−3 errors = the 3 collapsed ambiguities. Zero flows newly broken — the shared-page design costs
nothing measured against this corpus, matching xn's precedent of "no new rejection" for a
widening change.

**Correction to the ideation-stage spike's framing — measured, not assumed.**
`spike-page-binding.js`'s "2 genuine mismatches, live defect count 2" is a **static**
mapping-vs-string comparison; it does not run the real resolver or check `step.type`. Doing that
now: both `back_button` steps (`verify-12.1-booking-flow.yaml`'s
`go-back-to-services-for-addon-test`, `verify-12.1-task-execution.yaml`'s
`navigate-back-from-task`) are **v1-format, un-migrated flows** — every real `resolve()` call
today already errors on them with `"has no type field — run migration tool first"`, unrelated to
page binding. So the corpus-wide run above shows resolve errors *decreasing* (630→627), not
gaining 2 — the 2 known mismatches never reach the page-binding check today, because an
unrelated pre-existing defect masks them first.

Demonstrated the real value anyway, on a **scratch in-memory copy only** (never written to
`carlove`), by setting `type: 'click'` on that one step (exactly what `migrate.js`'s regex
classifier — `/^Click\s+\w+_\w+/i` — would do) and re-resolving both BEFORE and AFTER:

    BEFORE (unpatched, migrated): resolves silently, zero errors — operands.selector picks
      whichever page's back_button happens to be in the flat table ("[aria-label='返回']"),
      regardless of the stated "booking-confirm" / "task-execution"
    AFTER (patched):  "Step '...': page 'booking-confirm' not found in mapping"

**Further correction: it is not "wrong page for a real element" — `booking-confirm` and
`task-execution` are not page keys in `secha-app.yaml` at all.** The mapping's real pages are
`welcome, login, home, profile, service, tasks, history, service-order-detail, _global`; the two
strings read like flow/feature names, not mapped pages. So the design's "page not found in
mapping" branch (point 3) is what actually fires, not the "found elsewhere" branch — a more
precise, more correct diagnosis than the original ideation draft assumed, and proof the design's
two distinct error messages (page-not-found vs. element-wrong-page) earn their keep.

**Also verified directly** (synthetic, not corpus-live — the corpus has no live case of a real
page stating a real-but-wrong page for an existing element): `Click tab_all on branches` (a real
page, where `tab_all` is not defined) →
`"element 'tab_all' not found on page 'branches' (found on: service-schedule) -- if it should be
visible from any page, mark page 'service-schedule' with shared: true in the mapping"`; and
`Click sidebar_dashboard on branches` (a `_global` element stated under an unrelated real page)
resolves cleanly to its `_global` selector — the exact 36-corpus-case shape, now proven against a
real mapping (`secha-office.yaml`) rather than only counted.

## Acceptance Criteria

**AC-1 (value, enforcement) — a step naming an existing element under the wrong stated page
fails to compile instead of silently resolving to a different page's element.**
Verified by: the scratch-migration demonstration above (BEFORE silently resolves to
`[aria-label='返回']` with zero errors; AFTER raises a page-not-found error) plus the synthetic
`tab_all on branches` case (BEFORE would silently resolve via the flat table; AFTER raises the
named "not found on page" error with the shared-flag hint). Falsified by: reverting the patch
and re-running either case returns to silent zero-error resolution.

**AC-2 (no regression, corpus-measured) — resolve-error count and clean-flow count do not
regress, and every delta is accounted for by shared-page ambiguity collapsing, never by breaking
legitimate authoring.**
Verified by: `node .context/spike-3t-page-binding-before-after.js .context/flow-corpus.txt`
reproduces the table above exactly. Falsified by: any entry under "FLOWS FLIPPED clean -> error",
or "NEW errors" containing a `_global`-referencing step, or the resolve-error delta not matching
the 3 named collapsed ambiguities.

**AC-3 (shared-page correctness, proven on real data) — an element defined only under a
shared-marked page (or the grandfathered `_global`) resolves correctly regardless of which real
page a step states.**
Verified by: none of the corpus's `_global`-referencing steps appear in "NEW errors" (AC-2's
harness); independently, the synthetic `sidebar_dashboard on branches` case above resolves to the
`_global` selector against the real `secha-office.yaml` mapping. Falsified by: any `_global` step
newly erroring, or the synthetic case failing to resolve.

**AC-4 (page-not-found is distinct from element-wrong-page) — a stated page absent from the
mapping produces `"page 'P' not found in mapping"`; an element present under a different real
page produces `"element 'X' not found on page 'P' (found on: Y)"` with the `shared: true` hint —
never the same message for both.**
Verified by: `resolver.test.js` cases (implementation stage) against the existing
`EXTENDED_MAPPING` fixture (`compiler/test/resolver.test.js:412-437`, already has `login` +
`dashboard` + `_global` pages) — e.g. `sidebar_dashboard visible on login` (real page, wrong page
→ "found on: dashboard" branch), `heading visible on nonexistent-page` (page-not-found branch),
`sidebar_home visible on login` (shared fallback, must resolve clean). Falsified by: either
branch producing the other's message shape, or the existing `EXTENDED_MAPPING` test at
`resolver.test.js:456` ("element visible on page" with matching page) changing behavior.

**AC-5 (omission unaffected) — steps that omit the page qualifier keep byte-identical behavior:
same resolution, same referenced-only-ambiguity semantics, same error text.**
Verified by: AC-2's corpus diff — the only deltas are the 3 recovered strings and 3 collapsed
ambiguities, all page-qualified; every omitted-qualifier step's output is unchanged between
BEFORE and AFTER. Falsified by: any qualifier-omitting step's resolved selector or error text
changing.

## Reverse-recovery audit (layer trace, against `origin/main @ 529296d`)

**Fetch note.** `origin/main` in this shared repo is already at `529296d` (fetched earlier
today by a concurrent session — this checkout's `.git` object store is shared across the
`kc-claude-plugins` worktrees). A fresh `git fetch origin main` this session timed out
(`ssh: connect to host github.com port 22: Operation timed out` — the network flap the dispatch
note warned about, still ongoing) but did not need to succeed: `529296d` already matches the
tip the dispatch note named as "the remote," and `git diff origin/main -- e2e-pipeline/`
against this checkout's `HEAD` (`3b7a1be`) is **empty** — `resolver.js`, `resolver.test.js`, and
`docs/writing-tests.md` are byte-identical to the merge target. The audit below is current, not
stale, and does not need a retry.

| Layer | File:line | Verdict | Note |
|---|---|---|---|
| Parser | `compiler/parser.js` | WORKING, out of blast radius | `expect:`/`action:` strings pass through raw; unrelated to this grammar (same finding as xn's audit) |
| Resolver — the seam being fixed | `resolver.js:44-70` (`buildSymbolTable`), `157-173` (`resolveElement`), `335-354` & `558-576` (click/fill in `resolve`/`resolveMultiSite`) | EXISTS_BROKEN — parse-and-discard, now measured with a live prototype | Page group captured by the action regex (`resolver.js:11,15`) and by 3 of 7 expect patterns (`resolver.js:124,130,131`), discarded in every case; confirmed silently misrouting on a real (scratch-migrated) corpus flow above |
| Codegen | `codegen.js` (`element-visible`/`element-not-visible`/`active` branches) | WORKING, unaffected | No new `type`, no codegen diff — only the *resolution* step changes, matching xn's zero-codegen precedent |
| Compiler tests | `compiler/test/resolver.test.js:412-437` (`EXTENDED_MAPPING`, already has `_global`) | WORKING harness | Needs new cases per AC-4, not new fixture infra — the fixture already has the 3-page shape (2 real + 1 shared) this entity needs |
| Mapper agent template | `agents/e2e-mapper.md:150,231` | WORKING (emits `_global` today), EXISTS_BROKEN re: the new flag | Already instructs "global elements... go into `_global` page"; doesn't yet emit `shared: true` — 1-line template addition so newly-generated mappings are self-documenting and don't lean on the grandfather default |
| Test-runner warning check | `skills/e2e-test/SKILL.md:83` | WORKING (informal, warning-only), EXISTS_BROKEN re: consistency | Already special-cases `_global.elements.<name>` by literal name for its own (separate, non-blocking) element-reference validation; doesn't know about `shared: true` — 1-line prose update for consistency, not required for correctness since this check is warning-only |
| Corpus baseline / spike harness | `.context/spike-3t-page-binding-before-after.js` (new, this session) | WORKING (git-excluded) | Modeled on `spike-xn-before-after.js`; reproduces every number above from the tracked file, not a reimplementation |
| Docs | `docs/writing-tests.md` | MISSING (page-binding + `shared` schema never documented) — see Doc diff | The `_global` convention itself was never documented anywhere before this session (verified by grep); this entity is the first to write it down |

Boundary with sibling entities: no new `type`, no codegen change, no semantics change for
omitted-qualifier steps. Leaves [[e2e-assertion-honesty-gate]]'s hyphenated-element class and
free-form-prose class untouched (different defect shapes). Does not touch `carlove`'s mapping or
flow files — the `back_button` page-name typos and the un-migrated `type:` fields are reported,
not fixed, per Non-goal 4.

## Doc diff

**`e2e-pipeline/docs/writing-tests.md`** — two edits, both sequenced **after xn's PR merges**
(xn's `## Expect Grammar Reference` section exists today only on the unmerged
`spacedock-ensign/e2e-expect-grammar-permutations` branch, not on `origin/main`; if 3t's
implementation starts before xn merges, rebase this diff onto xn's branch instead of writing it
twice):

1. **Step 1 (mapping structure example, `writing-tests.md:13-26`)** — add one line + one
   sentence showing the shared-page flag on the `_global` block, e.g.:
   ```yaml
     _global:
       shared: true   # elements here resolve regardless of which page a step states
       elements:
         nav_home: { selector: "[data-testid='nav-home']" }
   ```
   *"Elements that appear on every page go in a page marked `shared: true` (by convention named
   `_global`, as `/e2e-map` already generates) — a step naming any other page still resolves
   them."*
2. **`## Expect Grammar Reference` table** (currently at `writing-tests.md:340` on xn's branch)
   — add a row for the new `<element> is visible on <page>` form, and replace the sentence
   `"on <page>` is accepted but not verified -- element resolution is mapping-wide, not
   page-scoped (tracked separately)."` with: *"`on <page>` is verified: the element must be
   defined on the stated page, or on a page marked `shared: true` (e.g. `_global`) — a step
   naming the wrong page fails to compile instead of silently resolving to a different page's
   element. Omitting the qualifier keeps the mapping-wide 'any page' lookup."* Also fix the
   "Caution" paragraph's clause *"even there it is parsed and discarded rather than verified
   (previous paragraph)"* → *"even there it is now verified against the stated page (previous
   paragraph)"* — that sentence becomes false the moment this entity ships and must not be left
   stale (the exact failure mode this stage-def clause exists to prevent).

**`agents/e2e-mapper.md:231`** — add `shared: true` to the `_global:` block in the Phase 3
structure template, so every newly-generated mapping is self-documenting from day one rather than
depending on the grandfathered literal-name default.

**`skills/e2e-test/SKILL.md:83`** — one clause added to the existing sentence: "...or `_global`
(or any page marked `shared: true`)..." for consistency with the compiler's new behavior; this
check is warning-only, so the edit is a consistency nice-to-have, not a correctness requirement.

## E2E-first acceptance

This session's spike exercised `resolve()`/`resolveMultiSite()` directly against the real corpus
and real mapping files — strong evidence for the counts, including one demonstration against a
scratch-migrated copy of a real project flow — but it never touched the tracked codebase (every
patch was built into a temp directory, matching xn's ideation-stage discipline: design-only
stage, zero diffs to `e2e-pipeline/`). Implementation must additionally run the real CLI path:
`/e2e-compile --verbose <flow>` against a real `.claude/e2e/flows/*.yaml` that has at least one
correctly page-qualified step (must show `active`, not `deferred` or an error) and, in a
throwaway copy, one deliberately wrong-paged step (must show the compile fail with the new error
text) — proving the CLI entry point, not just the `resolve()` function signature, carries the
fix end to end.

## Falsification

Demonstrated, not hypothetical, in three independent ways this session: (1) the scratch-migrated
`back_button` flow — reverting the patch returns it to silent zero-error resolution; (2) the
corpus-wide run — reverting any of the anchored edits reproduces the exact BEFORE numbers
(630 errors, 368 deferred, 20 clean flows); (3) the synthetic `tab_all`/`sidebar_dashboard`
cases against real `secha-office.yaml` data. The AC set is falsifiable in the harmful direction
too: AC-2's "flows flipped clean→error" and "NEW errors" checks are exactly what would catch a
naive stated-page-vs-element-page-key comparison — the failure mode the FO's scope notes priced
at 18x damage (36 legitimate rejections to catch 2 defects) — and both currently read zero.

## Design determination

`design: required` (not `trivial-pass`) — the page qualifier is a flow-authoring interface and
the binding rule (page-scoped resolution + the `shared` flag schema addition) is the concrete
design decision, per the Design section above. Frontmatter `design:` left blank per ensign rules
(no frontmatter edits) — gate to set it.

## Non-goals

1. Not rejecting qualifier omission (FO-authored, Section captain-delegated scope above).
2. Not removing the qualifier from the grammar (FO-authored).
3. Not inventing an error-code vocabulary — [[e2e-schema-contract]]'s job, still backlog.
4. Not fixing the 2 genuine defects, and not migrating `carlove`'s un-migrated v1 flows that
   currently mask them — both are corpus-owner actions in another repo (FO-authored, extended:
   the masking discovery this session makes it doubly clear this is `migrate.js`'s job, not this
   entity's).
5. Not deepening the 3-way consistency between the compiler's `shared` flag, the mapper's
   template, and the test-runner's warning-only check beyond the two 1-line doc/template edits
   above — full unification (e.g. teaching the test-runner check to read `shared: true` from a
   real mapping object instead of matching the literal string) is a follow-up, not a 1-session
   item.
6. Not adding a dedicated corpus fixture for the explicit `shared: false` opt-out — no mapping in
   the corpus uses it; covered only by the design's structural correctness, defensive rather than
   corpus-driven.
7. Not touching `resolveMultiSite`'s `site:` qualifier semantics — only the page-qualifier
   resolution *within* a site's own mapping changes, for symmetry with `resolve()`.

## Appetite, cut priority, pre-mortem

- **Appetite: 1 session**, per dispatch — same as xn, and the spike above (a working prototype
  of the full patch, not just a measurement script) makes this a high-confidence estimate rather
  than a guess.
- **Cut priority (FO-authored):** keep the `shared`-flag handling above everything else; if the
  session runs long, cut the *scope of what binds* (e.g. ship the action side, defer the expect
  side's new `is visible on <page>` form to a follow-up) — never cut or simplify the shared-key
  rule itself, and never fall back to a leading-underscore prefix match.
- **Pre-mortem (FO-authored, class: hidden assumption):** restated above in FO-authored scope;
  answered by making the shared declaration data-driven (lives in the mapping, not a resolver
  enumeration) and by the "mark page 'Y' with shared: true" hint on every wrong-page error, so a
  future drift case is at minimum self-explanatory rather than a silent, unexplained rejection.

## Dispatch sizing

**ONE implementation worker session.** Scope, all measured against the working prototype above,
not estimated:
- `resolver.js`: `buildSymbolTable` (+`byPage`, `+sharedPages`, `+DEFAULT_SHARED_PAGES`), new
  `resolveElementOnPage` helper, `resolveElement` signature change, `resolveExpects` signature
  change + page-threading for `element-visible`/`element-not-visible`, 3 `EXPECT_PATTERNS`
  capture-group edits + 1 new row, the click/fill branch in both `resolve()` and
  `resolveMultiSite()` — a ~150-line diff, already exercised end-to-end by
  `.context/spike-3t-page-binding-before-after.js`, so implementation is substantially "land the
  validated patch," not open-ended design work.
- `resolver.test.js`: new cases per AC-4 against the existing `EXTENDED_MAPPING` fixture (no new
  fixture infrastructure needed) — wrong-real-page rejection, shared-page/`_global` resolution,
  page-not-found-in-mapping distinct message, the new `is visible on <page>` form, one
  `resolveMultiSite` symmetry case, and a full-suite regression run for AC-5.
- `docs/writing-tests.md` (2 edits, sequenced onto xn's branch or after xn merges),
  `agents/e2e-mapper.md:231` (1 line), `skills/e2e-test/SKILL.md:83` (1 clause).
- E2E-first: one real `/e2e-compile --verbose` run per the E2E-first acceptance section above.

Well under the 90-minute / 3-independent-behaviors split threshold — action-side and expect-side
binding share one helper and one symbol-table shape, so they are one behavior, not two.

## Stage Report: ideation

- DONE: Reverse-recovery audit against merge target
  `origin/main @ 529296d` (already the shared repo's fetched tip; `git diff origin/main --
  e2e-pipeline/` empty against HEAD `3b7a1be`) — layer trace table in "Reverse-recovery audit".
- DONE: Design determination
  `design: required`, concrete rule recorded in "Design — page-scoped resolution with an
  explicit `shared` page flag" (frontmatter left blank per ensign rules).
- DONE: Spike the riskiest unverified mechanism first
  Built a working prototype patch (`.context/spike-3t-page-binding-before-after.js`, anchored
  against `origin/main@529296d`'s real `resolver.js`) and ran it over the real 100-flow corpus —
  not a re-run of the prior static spike, a live measurement of the actual proposed diff.
- DONE: AC are end-state properties with falsifiable proof
  AC-1..AC-5 in "Acceptance Criteria", each with Verified-by/Falsified-by citing the corpus
  harness, a scratch-migration demonstration, and a synthetic real-mapping case.
- DONE: E2E-first acceptance
  Recorded as an implementation obligation (real `/e2e-compile --verbose` run) in "E2E-first
  acceptance" — ideation itself stayed CLI-real but resolve()-direct, matching xn's precedent of
  keeping every patch off the tracked codebase during design.
- DONE: Doc diff proposed here
  Two `writing-tests.md` edits (sequenced onto xn's unmerged branch) plus 1-line consistency
  edits to `agents/e2e-mapper.md` and `skills/e2e-test/SKILL.md`, in "Doc diff".
- DONE: Size the implementation dispatch here
  ONE session, scope enumerated in "Dispatch sizing" against the working prototype.
- DONE: Appetite is a forcing budget / one-sentence pre-mortem / captain scope discipline
  FO-authored scope (Sections 4-7 of dispatch) transcribed verbatim in "FO-authored scope";
  appetite and cut-priority recorded in "Appetite, cut priority, pre-mortem".

### Summary

Designed page-scoped element resolution with a data-driven `shared: true` page flag (grandfathered
default for the literal `_global` key already used by `agents/e2e-mapper.md` and
`skills/e2e-test/SKILL.md`), built a working prototype patch, and measured it against the real
100-flow corpus: +6 active / -3 deferred / -3 errors / 0 flows newly broken. Corrected the prior
static spike's "2 live defects" claim — both known `back_button` mismatches are currently masked
by an unrelated pre-existing "no type field" error in un-migrated `carlove` flows, and turned out
to be page-*name* typos (`booking-confirm`/`task-execution` are not real page keys), not
wrong-page-for-a-real-element cases; demonstrated the actual silent-misroute-to-loud-error value
on a scratch-migrated copy instead. Five ACs, a full reverse-recovery audit, and a doc diff
(deliberately sequenced after xn's unmerged grammar-permutations PR) are recorded for the gate.
