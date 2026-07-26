---
title: Make the page qualifier bind, or drop it from the grammar
status: validation
source: sprint-1 (compiler boundary) entity 3 of 5; split out of e2e-typed-operands so the sprint stays inside the compiler
started: 2026-07-25T15:42:55Z
completed:
verdict:
worktree: mini:~/mini-legs/dev-3tp0ym1m-page-scoped-impl
issue:
pr: "#69"
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

Working prototype of the exact patch above, built by anchored string-replacement against the
real `resolver.js` at the merge target (same patch-survival-safe technique as xn's harness —
never requires whatever happens to be checked out on disk) and run over the real corpus:
`.context/spike-3t-page-binding-before-after.js` (git-excluded, same convention as
`spike-deferred-rate.js` / `spike-xn-*.js`).

**Re-baselined after xn merged.** xn landed on `main` as PR #60 (`ed15247`) after this entity's
first ideation run, moving the merge target. Re-ran against it (`XN_BEFORE_REF=ed15247`) rather
than assuming the earlier numbers still held:

    XN_BEFORE_REF=ed15247 node .context/spike-3t-page-binding-before-after.js .context/flow-corpus.txt

    (100 unique flows by content hash, 87 scored against their mapping)
                          BEFORE    AFTER     DELTA
    active expects        434       440       +6
    deferred expects      360       357       -3
    resolve errors        630       627       -3
    flows compiling clean 20        20        0

    RECOVERED strings (3): "email_input is visible on login",
      "data_table is visible on customer-profiles", "heading is visible on operations-overview"
    NEW errors (0)
    RESOLVED-AWAY errors (3): 'tab_all' ambiguous (2 click steps, service-schedule/
      employee-profiles), 'data_table' ambiguous (1 expect step, 9-way collision) — all 3
      collapse because the stated page now disambiguates instead of erroring
    FLOWS FLIPPED clean -> error (0); FLOWS FLIPPED error -> clean (0)

**The deltas are identical to the pre-xn run** (against `529296d`: 426→432 active, 368→365
deferred, same 630→627 errors, same 20→20 clean flows, same 3 recovered strings). Only the
baseline moved, by exactly xn's +8 recovered expects (426→434 active, 368→360 deferred) — which
is independent evidence that the two changes compose cleanly and are genuinely orthogonal, as
both entities predicted. The 3 strings this entity recovers are precisely the 3 xn was forced to
defer.

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

**Machine-local verification boundary — read before scoring any corpus-measured AC.** AC-1,
AC-2, AC-3, and AC-5 are verified by harnesses in `.context/`, which is git-excluded and
**stays** git-excluded by captain ruling: `flow-corpus.txt` is 3286 absolute paths under
`/Users/kent/Project` and `/Users/kent/conductor`, i.e. other repos on this machine. Committing
the scripts would make these ACs *look* CI-reproducible when they cannot be. Each affected AC
therefore reproduces **on this machine, at the stated absolute paths — not on a fresh clone and
not in CI.** This is a deliberate, recorded limitation, not an oversight. **AC-4 is the
CI-reproducible one** (`resolver.test.js`, tracked in-repo) and is what actually gates the merge;
the corpus ACs are evidence for the gate's judgment, not automated merge protection.

The limitation is **tracked, not merely disclaimed** — [[corpus-fixture-for-reproducible-acs]]
owns the question of whether a vendored fixture corpus is worth building, and correctly flags
that a maintainable fixture may be too clean to catch what the live distribution caught. This
entity does not pre-empt that call. Its own contribution to closing the gap is narrower and
already scoped: porting AC-3's shared-key case into the tracked `resolver.test.js` (see Dispatch
sizing), so the one rule the FO ruled must never be cut is CI-protected even while the corpus
measurement stays machine-local.

**AC-1 — a wrong-paged step fails to compile instead of silently resolving (value, enforcement).**
A step naming an existing element under a stated page that element is not on is rejected, rather
than resolving to a different page's element.
Verified by: the scratch-migration demonstration above (BEFORE silently resolves to
`[aria-label='返回']` with zero errors; AFTER raises a page-not-found error) plus the synthetic
`tab_all on branches` case (BEFORE would silently resolve via the flat table; AFTER raises the
named "not found on page" error with the shared-flag hint). Reproduces on this machine at the
stated `carlove` / `secha-*.yaml` paths only. Falsified by: reverting the patch and re-running
either case returns to silent zero-error resolution.

**AC-2 — no corpus regression: every delta is ambiguity collapsing (no regression, corpus-measured).**
Resolve-error count and clean-flow count do not regress, and every delta is accounted for by
shared-page ambiguity collapsing, never by breaking legitimate authoring.
Verified by: `XN_BEFORE_REF=ed15247 node .context/spike-3t-page-binding-before-after.js
.context/flow-corpus.txt` reproduces the table above exactly. Reproduces on this machine at the
stated paths only (`.context/` is git-excluded; the corpus is 3286 absolute paths into other
local repos). Falsified by: any entry under "FLOWS FLIPPED clean -> error", or "NEW errors"
containing a `_global`-referencing step, or the resolve-error delta not matching the 3 named
collapsed ambiguities.

**AC-3 — shared-page elements resolve from any stated page (shared-page correctness, real data).**
An element defined only under a shared-marked page (or the grandfathered `_global`) resolves
correctly regardless of which real page a step states.
Verified by: none of the corpus's `_global`-referencing steps appear in "NEW errors" (AC-2's
harness); independently, the synthetic `sidebar_dashboard on branches` case above resolves to the
`_global` selector against the real `secha-office.yaml` mapping. Reproduces on this machine at
the stated paths only. Falsified by: any `_global` step newly erroring, or the synthetic case
failing to resolve. **Implementation must additionally port the synthetic case into
`resolver.test.js`** against the tracked `EXTENDED_MAPPING` fixture (which already has a
`_global` page), so the shared-key rule — the one thing the FO ruled must never be cut — has
CI-reproducible protection and does not rest solely on a machine-local harness.

**AC-4 — page-not-found and element-wrong-page are distinct errors, never the same message.**
A stated page absent from the mapping produces `"page 'P' not found in mapping"`; an element
present under a different real page produces `"element 'X' not found on page 'P' (found on: Y)"`
carrying the `shared: true` hint.
Verified by: `resolver.test.js` cases (implementation stage) against the existing
`EXTENDED_MAPPING` fixture (`compiler/test/resolver.test.js:412-437`, already has `login` +
`dashboard` + `_global` pages) — e.g. `sidebar_dashboard visible on login` (real page, wrong page
→ "found on: dashboard" branch), `heading visible on nonexistent-page` (page-not-found branch),
`sidebar_home visible on login` (shared fallback, must resolve clean). Falsified by: either
branch producing the other's message shape, or the existing `EXTENDED_MAPPING` test at
`resolver.test.js:455` ("element visible on page" with matching page) changing behavior.

**AC-5 — steps omitting the page qualifier keep byte-identical behavior (omission unaffected).**
Same resolution, same referenced-only-ambiguity semantics, same error text as before the change.
Verified by: AC-2's corpus diff — the only deltas are the 3 recovered strings and 3 collapsed
ambiguities, all page-qualified; every omitted-qualifier step's output is unchanged between
BEFORE and AFTER. Reproduces on this machine at the stated paths only; the tracked
`resolver.test.js` suite passing unchanged (AC-4's run) is the CI-side half of this claim.
Falsified by: any qualifier-omitting step's resolved selector or error text changing.

**AC-6 — `--json` emits both new errors in gz's landed shape, with a usable `candidates` list.**
`e2e-compile --json` emits, for the wrong-page case, a tier-1 detail
`{step_id, field: "element", got: <element>, candidates: [<pages the element is on>], message}`
whose `message` carries the `shared: true` remedy; and for the absent-page case, the same shape
with `field: "page"`, `got: <stated page>`, and `candidates` listing the mapping's real page keys.
No field outside gz's landed `{step_id, field, got, candidates, message}` is introduced.
Verified by: a `compiler/test/cli.test.js` case (tracked, CI-reproducible — **not** machine-local)
that compiles a fixture flow with one wrong-paged step and one absent-page step, parses stdout as
JSON, and asserts both details key-by-key, including that `candidates` is non-empty. Falsified by:
the remedy appearing only in `message` with `candidates: []` (the machine-actionable half lost —
the exact regression this AC exists to catch); any key outside the landed five; or the wrong
`field` discriminator, which would make the two error classes indistinguishable to a consumer and
silently defeat AC-4 at the JSON layer.

## Reverse-recovery audit (layer trace, against `origin/main @ ed15247`)

**Re-audited after xn merged.** The first ideation run audited `529296d`; `git fetch origin main`
succeeded this round (the network flap has cleared) and the merge target is now `ed15247`
("Close the expect-grammar permutation holes (#60)"). Every line anchor below was **re-verified
against `git show origin/main:...`**, not carried forward:
`buildSymbolTable` (44-70) and the three page-bearing expect patterns (124, 130, 131) are
unchanged — xn's 2 added rows land in the text-pattern block below them, so this entity's
anchors were not disturbed. `resolveElement`, `resolveExpects`, and both click/fill branches
shifted **+2** and are corrected in the table. `resolver.test.js`'s `EXTENDED_MAPPING` is still
412-437; the pre-existing "element visible on page" test is at **455** (the first draft said 456
— corrected). No verdict in the table changed; only line numbers moved.

| Layer | File:line | Verdict | Note |
|---|---|---|---|
| Parser | `compiler/parser.js` | WORKING, out of blast radius | `expect:`/`action:` strings pass through raw; unrelated to this grammar (same finding as xn's audit) |
| Resolver — the seam being fixed | `resolver.js:44-70` (`buildSymbolTable`), `159-175` (`resolveElement`), `337-356` & `560-578` (click/fill in `resolve`/`resolveMultiSite`) | EXISTS_BROKEN — parse-and-discard, now measured with a live prototype | Page group captured by the action regex (`resolver.js:11,15`) and by 3 of 7 expect patterns (`resolver.js:124,130,131` — unchanged by xn), discarded in every case; confirmed silently misrouting on a real (scratch-migrated) corpus flow above |
| Codegen | `codegen.js` (`element-visible`/`element-not-visible`/`active` branches) | WORKING, unaffected | No new `type`, no codegen diff — only the *resolution* step changes, matching xn's zero-codegen precedent |
| Compiler tests | `compiler/test/resolver.test.js:412-437` (`EXTENDED_MAPPING`, already has `_global`) | WORKING harness | Needs new cases per AC-4, not new fixture infra — the fixture already has the 3-page shape (2 real + 1 shared) this entity needs |
| Mapper agent template | `agents/e2e-mapper.md:150,231` | WORKING (emits `_global` today), EXISTS_BROKEN re: the new flag | Already instructs "global elements... go into `_global` page"; doesn't yet emit `shared: true` — 1-line template addition so newly-generated mappings are self-documenting and don't lean on the grandfather default |
| Test-runner warning check | `skills/e2e-test/SKILL.md:83` | WORKING (informal, warning-only), EXISTS_BROKEN re: consistency | Already special-cases `_global.elements.<name>` by literal name for its own (separate, non-blocking) element-reference validation; doesn't know about `shared: true` — 1-line prose update for consistency, not required for correctness since this check is warning-only |
| **Direct test-runner resolution order** — **MISSED by this audit's first two cycles; caught by the ratification gate** | `agents/e2e-test-runner.md:176,177,238` | **EXISTS_BROKEN — the material gap.** Hardcodes the literal `_global` in the LLM runner's own resolution order | This is a **second, independent resolver**: `/e2e-test` drives flows directly from the mapping without going through `compiler/resolver.js` at all. A page marked `shared: true` would compile clean under this entity's new contract, be documented as valid, and then fail to resolve here. Fixed in this entity's PR — see Doc diff |
| Corpus baseline / spike harness | `.context/spike-3t-page-binding-before-after.js` (new, this session) | WORKING (git-excluded) | Modeled on `spike-xn-before-after.js`; reproduces every number above from the tracked file, not a reimplementation |
| Docs | `docs/writing-tests.md` | MISSING (page-binding + `shared` schema never documented) — see Doc diff | The `_global` convention itself was never documented anywhere before this session (verified by grep); this entity is the first to write it down |

**Audit self-correction, recorded rather than quietly patched.** The first two cycles of this
table listed `skills/e2e-test/SKILL.md:83` and concluded the runner side was a
consistency-only nicety. That was wrong, and the error was structural, not clerical: I traced
*the compiler's* layers thoroughly and treated "the test runner" as one box, so I audited the
skill that wraps it and never opened the agent prompt that **is** it. `agents/e2e-test-runner.md`
is a second resolver implementing the same lookup independently, and a semantic change to
mapping data has to land in both. The layer trace is only as good as its layer list — a box
labelled with a component name, rather than with the behavior it performs, hides everything
inside it. Verified complete this cycle: `git grep -n "_global" -- e2e-pipeline/` returns exactly
4 files (mapper, test-runner, e2e-test skill, and the compiler), and all 4 are now in this
entity's scope.

Boundary with sibling entities: no new `type`, no codegen change, no semantics change for
omitted-qualifier steps. Leaves [[e2e-assertion-honesty-gate]]'s hyphenated-element class and
free-form-prose class untouched (different defect shapes). Does not touch `carlove`'s mapping or
flow files — the `back_button` page-name typos and the un-migrated `type:` fields are reported,
not fixed, per Non-goal 4.

## Doc diff

**xn has MERGED — this diff is a REQUIRED edit in this entity's own PR, not a sequencing note.**
PR #60 landed on `main` as `ed15247`, adding `## Expect Grammar Reference` to
`e2e-pipeline/docs/writing-tests.md:340`. That section contains a sentence **this entity makes
false**. Wording below was read from `git show origin/main:e2e-pipeline/docs/writing-tests.md`,
not paraphrased. Note the landed prose uses ASCII `--`, not an em-dash; match it.

**`e2e-pipeline/docs/writing-tests.md`** — three edits:

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

2. **`## Expect Grammar Reference` table (`writing-tests.md:347-362`)** — add one row, placed
   directly after the existing `<element> visible on <page>` row to match the table's
   more-specific-first ordering:

   | `<element> is visible on <page>` (new) | `element-visible` |

3. **The false sentence (`writing-tests.md:369-370`) — REQUIRED, this is the one that breaks.**

   Landed text, verbatim:
   > ``on <page>`` is accepted but not verified -- element resolution is mapping-wide, not
   > page-scoped (tracked separately).

   Replacement:
   > ``on <page>`` is verified -- the element must be defined on the stated page, or on a page
   > marked ``shared: true`` (by convention ``_global``). A step naming a page the element is not
   > on fails to compile instead of silently resolving to a different page's element. Omitting the
   > qualifier keeps the mapping-wide "any page" lookup.

**The Caution paragraph (`writing-tests.md:372-381`) — checked empirically, mostly SURVIVES.**
The coordinator asked whether page binding changes the `text 'Created' on items-page` behavior.
**It does not** — verified by running that exact string through both the stock and patched
resolver (`/tmp/3t-text-check.js`, quoting-safe file rather than a shell `-e` one-liner, which
silently ate the inner single quotes on the first attempt and produced a misleading result):

    "text 'Created' on items-page"      BEFORE: deferred     | AFTER: deferred
    "text 'Created' on page"            BEFORE: text-visible | AFTER: text-visible
    "text 'Created' is visible"         BEFORE: text-visible | AFTER: text-visible   (xn's)
    "email_input is visible on login"   BEFORE: deferred     | AFTER: element-visible (3t's)

So the Caution's substance stands unchanged: `on page` remains a fixed literal for text
assertions, that example still silently defers, and *"There is no page-scoped text assertion in
this grammar; only the element forms accept a qualifier"* stays true — this entity binds the
element forms only, and deliberately does not add a page-scoped text form (Non-goal 4 of xn's
list, unchanged here). **Only its final cross-reference clause goes stale:**

   *"...and even there it is parsed and discarded rather than verified (previous paragraph)."*
   → *"...and even there the qualifier is now verified against the stated page (previous
   paragraph)."*

**`agents/e2e-mapper.md:231`** — add `shared: true` to the `_global:` block in the Phase 3
structure template, so every newly-generated mapping is self-documenting from day one rather than
depending on the grandfathered literal-name default.

**`skills/e2e-test/SKILL.md:83`** — one clause added to the existing sentence: "...or `_global`
(or any page marked `shared: true`)..." for consistency with the compiler's new behavior; this
check is warning-only, so the edit is a consistency nice-to-have, not a correctness requirement.

**`agents/e2e-test-runner.md` — REQUIRED, and the material one. 3 edits.**

`/e2e-test` resolves elements from the mapping **directly**, never calling
`compiler/resolver.js`. It is a second implementation of the same lookup, so making
`shared: true` a mapping semantic without updating it would ship a page that compiles clean,
is documented as valid, and then fails to resolve at runtime.

1. **Resolution order, item 3 (`:176`)**
   `3. `pages._global.elements.<element>` -- global shared elements`
   → `3. `pages.<name>.elements.<element>` for any page marked `shared: true` -- shared
   elements (by convention `_global`, which is treated as shared even without the flag)`
2. **Resolution order, item 4 (`:177`)**
   `4. For location-less references, use the current action's page context, then fall back to
   `_global``
   → `4. For location-less references, use the current action's page context, then fall back to
   any shared page`
3. **Expect table row (`:238`)** — `Resolve from action's page context, fallback to _global.`
   → `Resolve from action's page context, fallback to any shared page.`

**Why carry it rather than narrow the entity (the two options, and the choice).** The
alternative was to declare `shared: true` compiler-only, document the divergence, and file a
follow-up. Rejected, for a reason specific to *this* entity rather than a general preference for
thoroughness: this entity exists to kill enforcement theatre — a grammar that advertises a
constraint it does not enforce. Shipping it with a *known* runtime divergence would create a
second instance of exactly the defect it is closing, one layer over: the mapping would advertise
`shared: true`, the compiler would honor it, and the runner would silently not. The cost of
avoiding that is 3 line-level edits to an LLM prompt — no code, no tests, no new behavior. Paying
a documented-divergence tax to save 3 doc lines would be a false economy, and it is the same
trade [[e2e-json-diagnostics]] got wrong at a cost of ~1.9M tokens and a validation rejection.

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

## Structured diagnostics — the exact shape, against gz's LANDED contract

gz ([[e2e-json-diagnostics]]) has **merged**. Its contract was read from source this cycle
(`compiler/resolver.js:81-87` on `origin/main@ccaf028`), not assumed:

    tier1Detail(stepId, field, got, candidates, message)
      -> { step_id, field, got, candidates, message }
    tier2Detail(message)
      -> { message }

**There is no `repair` field, and no `code` field** (the latter a captain ruling). The previous
draft of this section promised the `shared: true` remedy would ride "a structured repair field."
**That promise is withdrawn** — it named a field that does not exist, which is precisely the
unmet-guarantee failure the gate flagged. Corrected below to use only landed fields.

**The remedy needs no new field.** `candidates` is already the "did you mean" channel, and its
existing semantics are an exact fit: at `resolver.js:179` the ambiguity error populates
`candidates` with `colPages` — *the list of pages an element actually lives on*. That is the
machine-actionable half of this entity's hint. The `shared: true` advice is the human half and
belongs in `message`.

Both new errors therefore map onto the landed shape with **zero contract change**:

**Wrong-page (element exists, not on the stated page)** — mirrors the `:179` ambiguity precedent:

    { step_id:   "select-all-tab",
      field:     "element",
      got:       "tab_all",
      candidates: ["service-schedule"],
      message:   "Step 'select-all-tab': element 'tab_all' not found on page 'branches' (found on: service-schedule) -- if it should be visible from any page, mark page 'service-schedule' with shared: true in the mapping" }

**Stated page absent from the mapping** — mirrors `resolveNavigate`'s page error at `:114`,
which uses `field: 'page'`:

    { step_id:   "go-back-to-services-for-addon-test",
      field:     "page",
      got:       "booking-confirm",
      candidates: ["welcome","login","home","profile","service","tasks","history","service-order-detail"],
      message:   "Step 'go-back-to-services-for-addon-test': page 'booking-confirm' not found in mapping" }

One deliberate divergence to flag at review: `:114` currently passes `candidates: []` for its
page error, while this entity populates the real page keys. `candidates` means "did you mean",
and for a mistyped page name the mapping's own page list *is* the answer — the corpus's two live
defects are both mistyped page names, so an empty list would drop the one repair hint that
actually helps. Populating it is additive and breaks no consumer. If gz's owner prefers strict
symmetry with `:114`, downgrading to `[]` is acceptable and costs only hint quality.

This does **not** reopen Non-goal 3 (no private error-code enum) — using gz's landed channel is
the opposite of minting one, and is why the enum was deferred to a shared owner.

## Falsification

Demonstrated, not hypothetical, in three independent ways this session: (1) the scratch-migrated
`back_button` flow — reverting the patch returns it to silent zero-error resolution; (2) the
corpus-wide run — reverting any of the anchored edits reproduces the exact BEFORE numbers
(post-xn baseline: 630 errors, 360 deferred, 20 clean flows); (3) the synthetic
`tab_all`/`sidebar_dashboard`
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
  fixture infrastructure needed) — wrong-real-page rejection, shared-page/`_global` resolution
  (**AC-3's ported synthetic case — the CI-side protection for the shared-key rule**),
  page-not-found-in-mapping distinct message, the new `is visible on <page>` form, one
  `resolveMultiSite` symmetry case, and a full-suite regression run for AC-5.
- `cli.test.js`: one new AC-6 case asserting the `--json` detail shape key-by-key for both new
  error classes (tracked, CI-reproducible; the JSON-layer counterpart to AC-4's prose assertions).
- `docs/writing-tests.md` — **3 edits, now required in this PR** (xn merged as `ed15247`; edit 3
  fixes a sentence this entity makes false), plus the Caution's trailing clause;
  `agents/e2e-mapper.md:231` (1 line), `skills/e2e-test/SKILL.md:83` (1 clause).
- **`agents/e2e-test-runner.md:176,177,238` (3 line-level edits) — REQUIRED**, added after the
  cycle-1 gate. Carries the shared-page rule into the direct `/e2e-test` execution path so a
  `shared: true` mapping cannot compile clean and then fail at runtime. Prompt text only — no
  code, no tests.
- E2E-first: one real `/e2e-compile --verbose` run per the E2E-first acceptance section above.

Still ONE session and still well under the 90-minute / 3-independent-behaviors threshold —
action-side and expect-side binding share one helper and one symbol-table shape, so they are one
behavior, not two. The two gate conditions did not add a behavior either: the runner fix is 3
prompt lines, and the structured-diagnostics work is message *construction* against gz's landed
contract with **zero new fields** (see Structured diagnostics), not a new error path. gz has
merged, so its contract is now readable rather than anticipated — the earlier "re-confirm at
dispatch time" caveat is discharged. The re-size signal stands: if wiring `errorDetails` through
`resolveElementOnPage` turns out to need per-call-site restructuring beyond passing a detail
object, raise it before starting rather than absorbing it silently.

### Feedback Cycles

**Cycle 1 — ideation gate, 2026-07-26. Verdict: RETURN.**

Adjudicated independently on a different vendor (codex, mini leg
`dev-3tp0ym1m-page-binding-gate`, verdict at `origin/mini/dev-3tp0ym1m-page-binding-gate:VERDICT-3t.md`).
This gate exists because the FO approved this ideation itself, which Gate Authority does not
permit; the pass was a ratification, not a dispute.

Two layer-boundary conditions, neither touching the resolver design, which the verdict calls
coherent and adequately evidenced:

1. **`shared: true` does not carry through to `agents/e2e-test-runner.md`.** FO-verified: that
   file names `_global` as a literal fallback key at `:176`, `:177` and `:238`, and
   `grep -rl 'shared: true'` over `agents/` and `skills/` returns nothing — the semantic exists
   in no consumer. A non-`_global` page marked `shared: true` would compile, be documented as
   valid, and fail to resolve in the runner's direct execution path. Same failure shape as
   [[e2e-json-diagnostics]], caught before implementation rather than after.
2. **The structured repair field is under-specified against gz's landed contract**, which emits
   `{step_id, field, got, candidates, message}` with no `repair` field. The ACs assert behavior
   rather than formatting, so implementation could satisfy them while dropping the remedy into
   an unstructured message.

Effort: one codex leg, ~5.6K output tokens on a third quota pool, no Claude tokens consumed.

**Cycle 2 — re-gate, 2026-07-26. Verdict: PROCEED.**

Same adjudicator, resumed in-session (`codex exec resume`), verdict at
`origin/mini/dev-3tp0ym1m-page-binding-gate:VERDICT-3t.md`. Both conditions judged actually
closed, and both were closed by a better move than the one the condition implied: condition 1 by
carrying the rule into `agents/e2e-test-runner.md` rather than documenting a divergence, and
condition 2 by withdrawing a promise of a `repair` field that gz never defined, after reading
gz's contract from source.

**Escalated question ruled:** 3t populates `candidates` for page-not-found with the mapping's
real page keys. This uses gz's existing "did you mean" field for the same class of payload and
changes no contract; gz's `resolveNavigate` passing `[]` is the outlier to reconcile later, not
a reason to weaken 3t's diagnostics. Implementation must not broaden scope to retrofit every
existing page-not-found producer.

Three implementation guardrails carried from the verdict's "what would change my mind":
populating page candidates must not require changing gz's JSON schema or a broader diagnostics
refactor; the runner prompt edits must state both the explicit-location and the location-less
shared-page fallback; AC-6 must parse `--json` and check keys, never degrade to a prose or
string-only assertion.

The FO's `_global` count correction (five files, not four) was judged a reporting imprecision
rather than a scope gap — the two extra hits are compiler tests implementation already expects
to touch.

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

## Stage Report: ideation (cycle 2 — coordinator correction round)

Two scoped updates requested; no redesign. Design, ACs, and spike stand as ruled.

- DONE: xn has MERGED — doc diff is now a concrete required edit
  Fetched `origin/main` (succeeded this round — network flap cleared), read
  `## Expect Grammar Reference` verbatim via `git show origin/main:...` rather than from the
  paraphrase. Doc diff rewritten as 3 required in-PR edits with the exact landed text quoted
  (including its ASCII `--`, not an em-dash) and the exact replacement wording.
- DONE: check whether page binding changes the `text 'Created' on items-page` caution
  It does NOT — verified by running that exact string through stock vs. patched resolver:
  `deferred` before and after. The Caution's substance survives; only its trailing
  cross-reference clause ("parsed and discarded rather than verified") goes stale. Recorded with
  the 4-case evidence table.
- DONE: name the machine-local limitation in the corpus ACs
  Added a "Machine-local verification boundary" preamble plus a per-AC line on AC-1/2/3/5 stating
  they reproduce on this machine at the stated paths, not a fresh clone. ACs otherwise unweakened;
  AC-4 explicitly named as the CI-reproducible one that gates merge.
- DONE: gz sequencing recorded where it matters
  New "Sequencing — held for gz" section: the three refusal strings should be emitted through
  gz's structured channel (carrying the `shared: true` remedy as a structured repair field, its
  most machine-actionable output) rather than as prose; noted this does not reopen Non-goal 3,
  and that no AC is affected since all assert behavior, not formatting.
- DONE (not requested — self-initiated, flagged for the gate): re-baselined the spike against the
  new merge target
  xn's merge moved `main` out from under the recorded numbers. Re-ran with
  `XN_BEFORE_REF=ed15247`: deltas are **identical** (+6/−3/−3/0), only the baseline shifted by
  exactly xn's +8. Re-verified every `resolver.js` line anchor: `buildSymbolTable` and the 3
  page-bearing expect patterns unchanged; `resolveElement`/`resolveExpects`/both click-fill
  branches shifted +2 (corrected in the audit table); `resolver.test.js:456`→`455` corrected.
- DONE: state committed path-scoped and push attempted
  Stage-only commit of `e2e-page-scoped-resolution.md`; see push note below.

### Summary

Addressed both scoped updates without touching the design. Answered the coordinator's open
question with evidence rather than reasoning: page binding does **not** disturb the
`text 'Created' on items-page` caution, because this entity binds element forms only and adds no
page-scoped text form — only that paragraph's trailing cross-reference needs the same one-clause
fix already identified. Beyond the two requests, re-baselined the corpus run against the
post-merge target and re-verified every line anchor, since xn's merge invalidated the recorded
numbers' provenance; the deltas held exactly, which is independent evidence the two changes are
orthogonal. One process note worth the gate's attention: the first attempt at the text-form check
used a shell `-e` one-liner whose inner single quotes were eaten, producing a plausible but wrong
"everything defers" result — caught by noticing the quotes missing in the echoed output, and
redone via a file. The corrected result is what is recorded.

## Stage Report: ideation (cycle 3 — gate RETURN, both conditions closed)

- DONE: Condition 1 — `shared: true` carried into `agents/e2e-test-runner.md`
  Verified the gate's claim from source before acting: `:176`, `:177`, `:238` hardcode `_global`,
  and `git grep "shared: true" -- e2e-pipeline/agents/ e2e-pipeline/skills/` returns nothing.
  Chose the carry-through option (not the narrow-and-document option) with the reasoning recorded
  in the Doc diff: this entity exists to kill enforcement theatre, so shipping it with a known
  compiler/runtime divergence would recreate its own target defect one layer up, and the fix is
  3 prompt-line edits.
- DONE: Condition 2 — structured shape specified against gz's LANDED contract
  Read `tier1Detail`/`tier2Detail` from `origin/main@ccaf028:compiler/resolver.js:81-87` rather
  than trusting the summary. **Withdrew the "structured repair field" promise** — no such field
  exists. Found the remedy needs no new field: `candidates` already carries "pages this element
  is on" at `:179`, which is exactly the machine-actionable payload. Both new errors now specified
  as concrete JSON using only the landed five keys.
- DONE: AC added verifying the JSON actually emits
  AC-6, verified by a tracked `cli.test.js` case — deliberately CI-reproducible, unlike the
  machine-local corpus ACs. Its falsifier is the precise regression the gate feared: remedy in
  `message` with `candidates: []`.
- DONE: audit table corrected and the miss recorded as a method error, not a typo
  Added the `e2e-test-runner.md` row and wrote down *why* two cycles missed it — I audited "the
  test runner" as one box and opened the wrapping skill instead of the agent prompt that is the
  runner. Re-swept: exactly 4 files mention `_global`, all 4 now in scope.
- DONE: Dispatch sizing re-confirmed, not silently re-cut
  Still ONE session; both conditions add prompt text and message construction, no new behavior.
  Discharged the now-obsolete "re-confirm gz at dispatch time" caveat and kept the re-size signal.
- DONE: state committed path-scoped and pushed
- SKIPPED: re-opening resolver mechanism, action/expect unification, omitted-qualifier
  compatibility, `_global` grandfathering, `resolve()`/`resolveMultiSite()` symmetry, corpus
  evidence, machine-local disclosure, AC-1..AC-5
  Explicitly out of scope per the return: the verdict affirmed all of them. Untouched.

### Summary

Both conditions closed without reopening the design. The material one was real: `/e2e-test` is a
second, independent resolver that never calls `compiler/resolver.js`, so making `shared: true` a
mapping semantic without updating its prompt would have shipped a mapping that compiles clean,
documents as valid, and fails at runtime — this entity's own target defect, one layer up. The
second condition was an unmet guarantee in my own body: I had promised a "structured repair
field" that gz's landed contract does not have. Withdrawn and replaced with concrete JSON using
only the landed five keys, plus AC-6 to prove a consumer receives it. Worth noting for the
record that the fix turned out to need **zero** contract change — `candidates` already meant
exactly what the remedy needed — which is the outcome the reverse-recovery default predicts and
which I would have missed had I specified a new field from the summary instead of reading gz's
source. One divergence flagged for review rather than decided unilaterally: I populate
`candidates` for the page-not-found case where gz's `:114` passes `[]`.
