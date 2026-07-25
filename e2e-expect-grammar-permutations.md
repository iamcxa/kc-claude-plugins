---
title: Close the expect-grammar permutation holes
status: ideation
source: sprint-1 (compiler boundary) entity 1 of 5; measured this session, corroborated by the cross-model reviewer as the highest-ROI lowest-risk item in the codebase
started: 2026-07-25T12:41:25Z
completed:
verdict:
worktree:
issue:
pr:
design:
id: xnj27a2qnjtb61mqegdasm00
---

## Problem

`resolver.js:119-151` holds **14** ordered regexes (corrected — the previous draft said 12;
verified by direct read against `origin/main @ 7521546`, byte-identical in this checkout). An
`expect:` string matching none of them is silently dropped (see
[[e2e-assertion-honesty-gate]]). Two of the misses are not expressiveness limits — they are
permutations the table simply forgot:

- **Element asymmetry (verified, one hole).** The negated form has
  `^(\w+) is not visible on [\w-]+$` (line 130), but the positive form has only
  `^(\w+) is visible$` (121) and `^(\w+) visible on [\w-]+$` (124) — there is no
  `^(\w+) is visible on [\w-]+$`. A negation that supports a form its positive does not is an
  oversight, not a design.
- **Text quoting (verified, one hole — narrower than it first looked, see below).** The table
  accepts `text "v" visible` (147) and `text 'v' on page` (146) but not `text 'v' is visible`.

**What this entity actually delivers.** Captain's framing of the pain — "可能是作者反覆寫了不會跑
的斷言卻沒回饋" (his own hedge, kept verbatim, not hardened into certainty) — describes a
feedback loop. xn cannot deliver that: it emits no signal to anybody, it only widens which
strings resolve. The feedback mechanism is [[e2e-assertion-honesty-gate]] (fail loud) and
[[e2e-json-diagnostics]] (structured repair candidates). xn's honest value is **blast-radius
reduction**: every assertion it recovers here is one fewer assertion that
e2e-assertion-honesty-gate turns into a hard failure later, and recovering it now (widening)
is cheaper than discovering it via a compile failure later (narrowing). Lane order
xn → gz → 3t → 5v stays as sequenced; reordering 5v first would flip the whole deferred corpus
to hard failures in one step, which is strictly worse for a 1-session appetite.

This is a pure widening: it can reject nothing that compiles today, adds no new `type`, and
touches no other compiler layer (see Reverse-recovery audit below).

## Corpus evidence — what's verified this session vs. inherited

**Attempted reproduction of the entity's own baseline figures (368/794 deferred, 46.3%/~25%,
8%/10% class split) — blocked, and here's why, concretely:** those numbers and the classifying
script live at `.context/spike-*.js`, cited by [[e2e-typed-operands]] and
[[e2e-page-scoped-resolution]]. `.context/` does not exist in this checkout
(`/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1`) and a filesystem-wide
`find` for it and for `spike-page-binding.js` from `/` returned nothing reachable on this
machine. The 100-flow corpus is external (likely the downstream project referenced in
`CHANGELOG.md:36`, `DataRecce/recce-cloud-infra#1383`), not checked into this repo. I am
carrying the existing spike-recorded numbers forward **with this caveat** rather than
re-deriving or asserting them as independently confirmed — the gate/FO/captain has access to
that corpus location; this ensign's sandbox does not. AC1 below is written so its pass/fail
depends on a re-run against wherever that corpus actually lives, not on the literal "66"
estimate holding.

**What I could and did verify directly (not inherited, exercised this session):** I copied
`resolver.js` to a scratch path outside the repo (no tracked file touched) and ran the real
`resolve()` function against the two corpus-sourced example strings that *are* recorded
verbatim elsewhere in this sprint's entities:

| Input string | Source | Before patch | After adding the 2 new patterns |
|---|---|---|---|
| `email_input is visible on login` | [[e2e-typed-operands]] 8%-class example | `deferred` | `element-visible`, active |
| `text '請先選擇廠牌' is visible` | [[e2e-typed-operands]] 10%-class example | `deferred` | `text-visible`, active |

All 14 pre-existing forms (one per category: `active`, `element-visible` ×3, `element-not-visible`
×4, `url-contains`, `url-not-contains`, `text-visible` ×2, `text-not-visible` ×2, `or-visible`)
were re-checked against the patched table and **all resolve unchanged** — confirming FO evidence
item (c) empirically (no shadowing) rather than by anchored-regex argument alone.

## Design — the grammar table, before/after

Insert exactly 2 lines into `EXPECT_PATTERNS` (`resolver.js:119-151`); add nothing else.

| # | Form | Resolves to | Status |
|---|---|---|---|
| 1 | `<element> is visible` | `active` | existing |
| 2 | `<element> visible on <page>` | `element-visible` | existing |
| **NEW** | `<element> is visible on <page>` | `element-visible` | **add** — insert after line 124 |
| 3 | `<element> visible` | `element-visible` | existing |
| 4 | `<element> is not visible on <page>` | `element-not-visible` | existing |
| 5 | `<element> not visible on <page>` | `element-not-visible` | existing |
| 6 | `<element> is not visible` | `element-not-visible` | existing |
| 7 | `<element> not visible` | `element-not-visible` | existing |
| 8 | `url does not contain <value>` | `url-not-contains` | existing |
| 9 | `url contains <value>` | `url-contains` | existing |
| 10 | `text '<value>' not on page` | `text-not-visible` | existing |
| 11 | `text "<value>" not visible` | `text-not-visible` | existing |
| 12 | `text '<value>' on page` | `text-visible` | existing |
| **NEW** | `text '<value>' is visible` | `text-visible` | **add** — insert after line 146 |
| 13 | `text "<value>" visible` | `text-visible` | existing |
| 14 | `<elemA> visible or <elemB> visible` | `or-visible` | existing |

Both new patterns route to a **type that already exists** — no new `type`, no new codegen branch,
no new rejection path. `on <page>` in every row (existing and new) is parse-and-discard, not
page-scoped verification (see Reverse-recovery audit) — the new element form inherits exactly
the same (non-)semantics as row 2, not new debt.

## Deviation from the FO's text-class hypothesis — flagged for the gate

The FO's dispatch note (section 3d) modeled the text-quoting gap as a coupled 2×2×2 axis (quote
style × predicate word × polarity) with 4 missing "diagonal" forms: `text "<v>" on page`,
`text '<v>' visible`, `text "<v>" not on page`, `text '<v>' not visible`. I searched every entity
file in `.spacedock-state` for concrete corpus strings and found exactly **one**:
`text '請先選擇廠牌' is visible` (from e2e-typed-operands' own classification of the 10% class) —
which matches **none** of the FO's four hypothesized forms literally (it has `is`, none of the
four do). This task's own completion checklist says: *"enumerate from the corpus, never from the
cross-product... a pattern with no recovered real string is cut, not kept for symmetry."* Applying
that rule, I'm recommending **only** `^text '(.+)' is visible$` and cutting the FO's other 3
hypothesized forms (plus a negated `is not visible` text variant, which also has no corpus
string) as unverified this session. The FO's symmetry argument may still be right — but building
it now would be speculation, not corpus-driven widening. **Gate: accept the narrower cut, or
overrule with your own corpus check for the other 3 forms before implementation.**

One practical consequence: since both surviving fixes are now ~1 line each, the FO's Q3
"what to cut if forced" question (recommending cut-the-element-form, keep-the-text-class) is
close to moot at this scope — there's no real budget pressure left to force a cut between them.

## Acceptance Criteria

- **AC1 (value).** Deferred-expect count strictly decreases on a re-run of the corpus
  measurement, and every recovered assertion is enumerated from the corpus (not asserted from
  the cross-product). Explicitly disclaims two things this entity does NOT deliver: (a) author
  feedback — that mechanism is [[e2e-assertion-honesty-gate]]; xn only shrinks the queue it will
  fail on; (b) page-scoped verification — `on <page>` remains parse-and-discard (see
  [[e2e-page-scoped-resolution]]). **Verified by:** re-run the corpus deferred-count (see
  "Corpus baseline mechanism" below) before and after the resolver.js patch, against whatever
  location the FO/captain designates as the corpus (not reproducible from this ensign's
  sandbox — flagged above).
- **AC2 (element permutation).** `<element> is visible on <page>` resolves to type
  `element-visible`. **Verified by:** `resolver.test.js` case + the live `email_input is visible
  on login` transition already demonstrated this session (deferred → element-visible).
- **AC3 (text permutation).** `text '<value>' is visible` resolves to type `text-visible`.
  **Verified by:** `resolver.test.js` case + the live `text '請先選擇廠牌' is visible` transition
  already demonstrated this session (deferred → text-visible).
- **AC4 (no regression, order-safety).** All 14 pre-existing forms resolve to their original
  types after insertion, regardless of where the 2 new lines land in the table. **Verified by:**
  full `resolver.test.js` suite green + a dedicated shadowing-regression test (insert the new
  lines at the *end* of the table in one test run and confirm identical results — proves
  independence from position, not just the chosen position).
- **AC5 (no semantics change).** No new `type`, no new rejection, `codegen.js` and `parser.js`
  diffs are empty. **Verified by:** the change is scoped to `resolver.js` only; existing
  `codegen.test.js` / `parser.test.js` pass unmodified.

## Corpus baseline mechanism (for AC1)

Reverse-recovery finding: the primitive already exists. `compile()` (`compiler.js:189-191`)
always returns `stats.{activeExpects, deferredExpects}` and already prints
`"Compiled: N steps, M expects active, K expects deferred (Phase 2)"` per flow, every run,
`--coverage` or not. What's missing is aggregation across `--all`:
`bin/e2e-compile.js`'s batch loop (lines ~82-113) sums coverage% but never sums
`activeExpects`/`deferredExpects` across the directory. That's a 2-counter addition to an
existing loop — not new infrastructure — and it IS the re-runnable baseline AC1 needs. Classify
this seam **EXISTS_BROKEN** (primitive present, aggregation unwired), not MISSING.

## Reverse-recovery audit (layer trace, against `origin/main @ 7521546`)

| Layer | File:line | Verdict | Note |
|---|---|---|---|
| Parser | `compiler/parser.js` | WORKING, out of blast radius | `expect:` strings pass through as raw strings; parser's `expect.*` handling (lines 351-368) is for `finally`-step JSON fields, unrelated to this grammar |
| Resolver | `resolver.js:119-151`, `175-272` | WORKING — the seam being widened | 14 patterns confirmed by direct read; dispatch loop at 185-269 |
| Codegen | `codegen.js:1570` (`active`/`element-visible`), `:1640` (`text-visible`) | WORKING, reused as-is | Confirmed by direct read — both new patterns route to existing branches; **zero codegen changes** |
| Compiler tests | `compiler/test/resolver.test.js:441-637` ("Phase 2" tests) | WORKING harness | Needs ~3 new cases (2 new-form + 1 shadowing-regression), not new infra |
| Batch corpus counter | `bin/e2e-compile.js:82-113` | EXISTS_BROKEN | See "Corpus baseline mechanism" above |
| Docs | see Doc diff below | MISSING (canonical reference) | No file currently claims to enumerate the grammar; resolver.js source is the only true reference today |

Boundary with sibling entities, stated explicitly: xn changes no resolution semantics, adds no
new rejection, and leaves the page-qualifier question (parse-and-discard) exactly as found —
that's [[e2e-page-scoped-resolution]]'s question. Author-visible feedback on the assertions xn
does *not* recover is [[e2e-assertion-honesty-gate]]'s job. Operand typing
([[e2e-typed-operands]]) is unaffected — this entity works entirely within the existing
prose-string `expect:` grammar.

## Doc diff

No file today enumerates the expect grammar canonically — `CLAUDE.md`, `docs/writing-tests.md`,
`references/common-patterns.md`, and `skills/e2e-map/SKILL.md:201` each show 1-3 example strings
in passing (verified by grep); resolver.js's source is the only complete reference that exists.

**Proposed:** add a new `## Expect Grammar Reference` section to `docs/writing-tests.md`,
inserted before the existing `## Element Coverage` section (currently at line 340), containing
the 16-row before/after table above (with the 2 new rows marked, matching the table format
already used in that file's `## Element Coverage` section for consistency) plus one line:
*"`on <page>` is accepted but not verified — element/text resolution is mapping-wide, not
page-scoped (tracked separately)."* Also update `skills/e2e-compile/SKILL.md:111`'s
"unrecognized format" warning line to link to the new reference section.

## E2E-first acceptance

Real-flow exercise, not unit-test-only: compile a flow YAML whose `expect:` list contains both
`<element> is visible on <page>` and `text '<value>' is visible`, run it through
`/e2e-compile --verbose <flow>`, and observe both resolve to active (not deferred) in the
printed summary. This session's spike already performed the equivalent check directly against
`resolve()` (see Corpus evidence table above) using a scratch copy of resolver.js outside the
repo — that does not itself count as the shipped proof; implementation must repeat it as an
actual `.claude/e2e/flows/*.yaml` compile, since the ideation-time spike was deliberately kept
off the tracked codebase (design-only stage).

## Spike (result recorded)

Performed 2026-07-25, see Corpus evidence table above for the artifact. RED: both corpus-sourced
strings measured `deferred` against unpatched resolver.js. GREEN: inserting exactly the 2 lines
in the Design table above made both resolve to their target existing types. No regression: all
14 pre-existing forms unaffected. No further spike needed for the page-qualifier mechanism —
item (f)/(3f) already established it's parse-and-discard; not re-run here.

## Falsification

Demonstrated directly, not hypothetical: reverting either added line returns its corpus string
to `deferred` (this is exactly what "before patch" vs. "after patch" showed in the Corpus
evidence table — the RED state *is* the falsification baseline for the GREEN state).

## Design determination

`design: required` (not `trivial-pass`) — the expect grammar is the flow-authoring interface;
the concrete design decision is the before/after grammar table above (2 new rows + exact
insertion points + the explicit call not to build the FO's other 3 hypothesized text forms).
Frontmatter `design:` field left blank per ensign rules (no frontmatter edits) — gate to set it.

## Non-goals (Q4 — FO recommendation, not captain-authored; captain delegated this question)

1. No cross-product completion. `or-visible` is/page/negation variants are out — same omission
   family, zero corpus evidence, explicitly deferred.
2. The FO's other 3 hypothesized text-diagonal forms are out this round (see "Deviation" above)
   — no corpus string, cut per this task's own checklist rule.
3. No grammar redesign — `on page` stays a literal word for text; whether text should take a
   page name like elements do is [[e2e-page-scoped-resolution]] / [[e2e-typed-operands]]'s
   question, not this entity's.
4. No semantics change, no new rejection — every string that compiles today still compiles to
   the same type.
5. No page-binding fix smuggled in, and no claim anywhere in this body/ACs/doc-diff of
   page-scoped verification.

## Appetite, cut priority, pre-mortem (Q3/Q5 — FO recommendations, not captain-authored)

- **Q3 (keep if forced to cut):** FO recommended keep-text/cut-element (3t absorbs the element
  form for free since it already edits page-qualified patterns). Recorded, but see "Deviation"
  above — with the text fix narrowed to 1 line, there is no real budget pressure forcing a
  choice between two ~1-line changes at a 1-session appetite.
- **Q5 (pre-mortem), class: criteria that pass without delivering value:** *"If this ships
  exactly per spec and still fails, the most likely cause is the deferred-count AC going green
  while authors still get zero feedback — because the feedback mechanism is
  [[e2e-assertion-honesty-gate]]'s, and xn only shortened the queue it will fail on."* Recorded
  verbatim from the FO dispatch.

## Dispatch sizing

**ONE implementation worker session.** Scope: 2 regex lines in `resolver.js` (insertion points
fixed above) + 3 new `resolver.test.js` cases + the `writing-tests.md` doc-diff section +
(for AC1's re-runnable baseline) a ~5-line aggregation addition to `bin/e2e-compile.js`'s
existing `--all` loop, summing an already-computed field. All independently confirmed cheap by
the ideation-time spike (2-line patch, zero codegen/parser diff, no shadowing). Well under the
90-minute / 3-independent-behaviors split threshold — this is 2 independent 1-line behaviors,
not 3.

## Stage Report: ideation

- DONE: Correct the entity body's pattern count and re-verify against origin/main
  Read `resolver.js:119-151` at `origin/main @ 7521546` (byte-identical in this checkout) —
  confirmed 14 entries, not 12; body corrected.
- DONE: Every proposed pattern justified by a corpus string, enumerated not cross-producted
  2 patterns proposed total (element `is visible on <page>`, text `'<v>' is visible`), each
  tied to a named corpus example from e2e-typed-operands' own classification; FO's 3 other
  hypothesized text forms explicitly cut for lacking corpus evidence (see "Deviation" section).
- DONE: Value AC measures deferred-reduction against a re-runnable baseline, disclaims feedback + page-scoping
  AC1 in the body; disclaims author-feedback (e2e-assertion-honesty-gate's job) and page-scoped
  verification (e2e-page-scoped-resolution's job) by name.
- DONE: Reverse-recovery audit and design determination recorded against origin/main
  Layer table in body: parser/resolver/codegen/tests/batch-counter/docs, each WORKING /
  EXISTS_BROKEN / MISSING with file:line; boundary vs. 3t/g5/5v stated explicitly.
- DONE: Reproduce the baseline the entity body leans on
  Attempted — `.context/` (corpus + spike scripts) not present in this checkout or reachable
  anywhere on this machine (`find` from `/` came up empty); documented as a caveat rather than
  silently trusting or silently dropping the inherited 368/794 figures. Directly verified
  instead: patched a scratch copy of resolver.js outside the repo, confirmed both corpus-cited
  example strings go deferred→active after the 2-line patch, and all 14 pre-existing forms
  resolve unchanged (no shadowing) — this is real `resolve()` execution, not a re-read of prose.
- DONE: E2E-first acceptance — do NOT skip it
  Body specifies the real-flow check implementation must run (`/e2e-compile --verbose` on a
  flow containing both new forms); ideation's own spike used an untracked scratch copy of
  resolver.js precisely so no code changes landed in this design-only stage, and the body says
  explicitly that spike does not substitute for the shipped E2E proof.
- DONE: Spike recorded
  RED/GREEN spike results in body's "Spike" and "Corpus evidence" sections; page-qualifier
  mechanism spike from e2e-page-scoped-resolution cited, not re-run.
- DONE: Falsification hook
  Direct — reverting either line returns its corpus string to `deferred`, already demonstrated
  as the RED state before patch.
- DONE: Dispatch sizing recorded
  ONE session; 2 independent 1-line behaviors, both well under the 90-minute/3-behavior split
  threshold.

### Summary

Corrected the entity's own pattern-count claim (14, not 12) and reframed the Problem section
around the FO's Q1 correction (blast-radius reduction, not author feedback). Verified both
proposed regex additions empirically by patching a scratch copy of resolver.js and running the
real resolve() function — both corpus-cited example strings flip deferred→active, and all 14
existing forms are unaffected (no shadowing). Materially narrowed the FO's text-class proposal
from 4 hypothesized diagonal forms to the 1 form actually backed by a corpus string, per this
task's own "enumerate from the corpus" rule — flagged explicitly for the gate to accept or
overrule. Could not reproduce the entity's inherited 368/794 corpus figures because `.context/`
is not present in this checkout or reachable on this machine; recorded that limitation rather
than asserting the numbers as re-verified, and wrote AC1 so it depends on a fresh re-run against
wherever the corpus actually lives, not on the specific "66" estimate.
