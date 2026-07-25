---
title: Close the expect-grammar permutation holes
status: validation
source: sprint-1 (compiler boundary) entity 1 of 5; measured this session, corroborated by the cross-model reviewer as the highest-ROI lowest-risk item in the codebase
started: 2026-07-25T12:41:25Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-e2e-expect-grammar-permutations
issue:
pr:
design: required
id: xnj27a2qnjtb61mqegdasm00
---

## Problem

`resolver.js:119-151` holds **14** ordered regexes (corrected — the previous draft said 12;
verified by direct read against `origin/main @ 7521546`, byte-identical in this checkout). An
`expect:` string matching none of them is silently dropped (see
[[e2e-assertion-honesty-gate]]). The corpus (measured, below) shows the recoverable misses are
**two text-quoting permutations**, both single-quote `is`-predicate forms the table simply
forgot: it accepts `text 'v' on page` (146) and `text "v" visible` (147) but neither
`text 'v' is visible` nor `text 'v' is not visible`.

The element-side asymmetry is real — the negated form has `^(\w+) is not visible on [\w-]+$`
(130) while the positive has only `^(\w+) is visible$` (121) and `^(\w+) visible on [\w-]+$`
(124), with no `^(\w+) is visible on [\w-]+$` — but **closing it here is measurably harmful and
is deferred to [[e2e-page-scoped-resolution]]**. See "Element form: why it is deferred, with
numbers" below. This is the single biggest change from the first ideation draft, and it is
driven by data rather than by symmetry argument in either direction.

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

As scoped (text forms only), this is a pure widening: **measured** to reject nothing that
compiles today (0 flows flip clean→error, below), add no new `type`, and touch no other
compiler layer (see Reverse-recovery audit below).

## Corpus evidence — measured this session

**Baseline reproduced exactly.** `.context/spike-deferred-rate.js` run against
`.context/flow-corpus.txt` (3286 paths → 100 unique flows by content hash, 87 scored):

    total_expects 794 · active 426 · deferred 368 · deferred_rate 46.3%
    flows_with_any_deferred 17 (19.5%) · flows_asserting_nothing 1

The inherited figures hold — no drift. Corpus flows live under
`/Users/kent/Project/carlove/.claude/e2e/flows/` (plus carlove worktrees).

**Candidate patterns scored against the real deferred set** (151 unique strings / 368
occurrences). A candidate earns a place only by recovering a real deferred string:

| Candidate | uniq | occ | Verdict |
|---|---|---|---|
| `text '<v>' is visible` | **4** | 4 | **ADD** |
| `text '<v>' is not visible` | **4** | 4 | **ADD** |
| `<elem> is visible on <page>` | 3 | 3 | defer — harmful today, see below |
| element name with hyphen (`\w+`→`[\w-]+`) | 2 | 4 | defer — different class, see below |
| `text "<v>" on page` (FO-hypothesized) | 0 | 0 | CUT |
| `text '<v>' visible` (FO-hypothesized) | 0 | 0 | CUT |
| `text "<v>" not on page` (FO-hypothesized) | 0 | 0 | CUT |
| `text '<v>' not visible` (FO-hypothesized) | 0 | 0 | CUT |
| `text "<v>" is visible` / `is not visible` | 0 | 0 | CUT |
| `<a> is visible or <b> is visible` | 0 | 0 | CUT |

The 8 strings the two ADD rows recover, verbatim from the corpus:
`text '請先選擇廠牌' is visible`, `text '請選擇車主' is visible`, `text '新增「hino」' is visible`,
`text '廠牌' is visible`, `text '工單記錄' is not visible`, `text '建立提醒' is not visible`,
`text '安排預約' is not visible`, `text '排程通知' is not visible`.

**Before/after over the whole corpus, with the 2 ADD patterns applied** (scratch copy of
resolver.js outside the repo — no tracked file touched):

| | before | after | delta |
|---|---|---|---|
| active expects | 426 | 434 | **+8** |
| deferred expects | 368 | 360 | **−8** |
| deferred rate | 46.3% | 45.3% | −1.0pt |
| resolve errors | 630 | 630 | **0** |
| flows compiling clean (0 errors) | 20 | 20 | **0 flipped** |

**Order-independence proved, not argued.** All 14 pre-existing forms plus the 2 new ones were
re-checked with the new patterns inserted at their intended position AND appended at the very
end of the table (worst case). 16/16 correct in both arrangements — the new patterns cannot
shadow and cannot be shadowed.

### Element form: why it is deferred, with numbers

Adding `^(\w+) is visible on [\w-]+$` recovers 3 strings but **breaks 2 flows that compile
cleanly today** (20 clean → 18):

    Step 'open_customer_profiles': expect element 'data_table' is ambiguous --
      found on: service-schedule, customer-profiles, branches, employee-profiles, …
    Step 'operations-overview': expect element 'heading' is ambiguous --
      found on: resources-completeness, operations-overview

The cause is exactly the parse-and-discard defect [[e2e-page-scoped-resolution]] owns: the
strings are `data_table is visible on customer-profiles` and
`heading is visible on operations-overview` — **the page name that would disambiguate is
present in the string and thrown away** (`[\w-]+` is not a capture group at 124/130/131;
handlers at 206-231 read only `match[1]`; `resolveElement` at 157-173 raises the collision
error at 158-162 against a mapping-wide table). So the element permutation is not
"cheap and rides along" — it is **blocked on 3t**, and lands for free the moment the qualifier
binds. This strengthens rather than contradicts the FO's Q3 instinct to let 3t absorb it, and
replaces the symmetry rationale with a measurement.

### Hyphenated element names: a distinct defect, also deferred

Not a permutation hole — a character-class limitation. `(\w+)` excludes `-`, so
`vehicles-create-button is visible` (3 occ) and `wr-shell visible on war-room` (1 occ) defer.
Widening to `([\w-]+)` recovers them but **also breaks 2 clean flows** (`vehicles-create-button`
is genuinely absent from its mapping — an authoring gap, not a grammar gap). Surfacing that
class is [[e2e-assertion-honesty-gate]]'s job, not a silent widening's. Recorded here so it is
not rediscovered; **out of scope for xn**.

## Design — the grammar table, before/after

Insert exactly 2 lines into `EXPECT_PATTERNS` (`resolver.js:119-151`); add nothing else.

| # | Form | Resolves to | Status |
|---|---|---|---|
| 1 | `<element> is visible` | `active` | existing |
| 2 | `<element> visible on <page>` | `element-visible` | existing |
| 3 | `<element> visible` | `element-visible` | existing |
| 4 | `<element> is not visible on <page>` | `element-not-visible` | existing |
| 5 | `<element> not visible on <page>` | `element-not-visible` | existing |
| 6 | `<element> is not visible` | `element-not-visible` | existing |
| 7 | `<element> not visible` | `element-not-visible` | existing |
| 8 | `url does not contain <value>` | `url-not-contains` | existing |
| 9 | `url contains <value>` | `url-contains` | existing |
| 10 | `text '<value>' not on page` | `text-not-visible` | existing |
| 11 | `text "<value>" not visible` | `text-not-visible` | existing |
| **NEW** | `text '<value>' is not visible` | `text-not-visible` | **add** — after line 143, with the other negatives |
| 12 | `text '<value>' on page` | `text-visible` | existing |
| **NEW** | `text '<value>' is visible` | `text-visible` | **add** — after line 146 |
| 13 | `text "<value>" visible` | `text-visible` | existing |
| 14 | `<elemA> visible or <elemB> visible` | `or-visible` | existing |

Both new patterns route to a **type that already exists** — no new `type`, no new codegen branch,
no new rejection path. Placement follows the table's negatives-before-positives convention, but
the arrangement is not load-bearing: order-independence was proved empirically (see Corpus
evidence). No element-side row changes; `on <page>` stays parse-and-discard everywhere.

## Deviation from BOTH prior hypotheses — the corpus overruled each of us

Recorded explicitly because the first ideation draft got this wrong and the gate should see why.

- **The FO's 4 hypothesized "diagonal" text forms** (`text "<v>" on page`, `text '<v>' visible`,
  `text "<v>" not on page`, `text '<v>' not visible`) score **0 occurrences each** in the
  corpus. The 2×2×2 coupled-axis model is elegant and empirically empty. CUT.
- **My own first-draft cut of the negated text form was wrong.** I searched `.spacedock-state`
  — design documents — found one example string, and concluded the class was one form wide.
  That is not the corpus. The corpus has **4 occurrences of `text '<v>' is not visible`**,
  exactly as many as the positive form. Restored. The FO's diagnosis was correct: right
  discipline, wrong evidence base.
- **`e2e-typed-operands.md:70` was misread by me.** "10% text-assertion quoting **variants**
  (`text '請先選擇廠牌' is visible`)" names a plural class and gives one illustration; it does not
  bound the class to that string.

Method correction now applied: patterns are scored by running the real resolver over the real
corpus, never by reading prose or reasoning about symmetry. Harnesses left in `.context/`
alongside the sibling spikes (git-excluded, same convention as `spike-deferred-rate.js`):

    node .context/spike-xn-pattern-candidates.js .context/flow-corpus.txt
    node .context/spike-xn-before-after.js       .context/flow-corpus.txt [text|element|hyphen]

`spike-xn-before-after.js` builds its own patched resolver from the real `resolver.js` at run
time, so every number in this body is re-derivable without a scratch copy having to survive.

The FO's Q3 "what to cut if forced" recommendation (cut the element form, keep the text class)
is **confirmed by measurement rather than by symmetry** — the element form is not merely
absorbable by 3t, it is actively harmful before 3t lands.

## Acceptance Criteria

**AC-1 (value) — the corpus deferred-expect count drops from 368/794 (46.3%) to 360/794 (45.3%), recovering exactly the 8 enumerated corpus strings, with clean-compiling flows and resolve errors unchanged.**
Explicitly disclaims two things this entity does NOT deliver: (a) author feedback — that
mechanism is [[e2e-assertion-honesty-gate]]; xn only shrinks the queue it will fail on;
(b) page-scoped verification — `on <page>` remains parse-and-discard (see
[[e2e-page-scoped-resolution]]).
Verified by: `node .context/spike-xn-before-after.js .context/flow-corpus.txt text` from the
`montpellier-v1` checkout, which reports all four numbers (active, deferred, resolve errors,
clean-flow count) in one run. Falsified by: reverting either of the 2 added lines returns its
corpus strings to `deferred` (368/794 again); a pattern that over-matches would raise the
resolve-error count above 630 or drop the clean-flow count below 20 — exactly what disqualified
the element and hyphen variants.

**AC-2 (text positive) — `text '<value>' is visible` resolves to type `text-visible`.**
Verified by: `resolver.test.js` case (xn AC2). Falsified by: the pattern being dropped, or
shadowed by `^text '(.+)' on page$` matching first — either leaves the string `deferred`
instead of `text-visible`.

**AC-3 (text negative) — `text '<value>' is not visible` resolves to type `text-not-visible`, NOT `text-visible`.**
Verified by: `resolver.test.js` case (xn AC3). Falsified by: the negative pattern being placed
where a positive pattern captures it first, which is the specific regression this table's
negatives-before-positives convention exists to prevent — the type would flip to `text-visible`
(or the string would stay `deferred`).

**AC-4 (no regression, order-safety) — all 14 pre-existing forms resolve to their original types after insertion, regardless of where the 2 new lines land in the table.**
Verified by: full `resolver.test.js` suite green + a dedicated ordering test (xn AC4) that
exercises all 8 recovered corpus strings alongside 2 pre-existing sibling-shaped forms in one
step. Falsified by: any of the 14 pre-existing forms changing type after insertion, or any new
pattern unanchored enough to shadow a neighbour — already demonstrated 16/16 correct in both
the designed position and appended-at-end arrangements during ideation.

**AC-5 (no semantics change, no new rejection) — no new `type`; `codegen.js` and `parser.js` diffs are empty; corpus resolve-error count is unchanged at 630.**
Verified by: the before/after corpus run (`spike-xn-before-after.js`) asserts the error count
explicitly. Falsified by: the error count moving away from 630 — exactly what caught the
element-form regression, and why the element form is not in this scope.

## Corpus baseline mechanism (for AC1)

**The re-runnable baseline already exists and was used for AC1's numbers:**
`.context/spike-deferred-rate.js <flow-list>` requires the real `resolver.js` (not a
reimplementation), dedups the flow list by content hash, and prints the headline block. This is
the harness AC1 cites. Two pointer corrections so it is not re-searched: `.context/` is a
dotfile (an `ls` without `-a` misses it, which is how the first ideation draft wrongly concluded
it was absent), and `e2e-pipeline/scripts/measure-fallback-baseline.sh` is **not** related — it
measures `eval_fallback_hits`, a different metric.

Separately, and still worth doing but no longer load-bearing for AC1: `compile()`
(`compiler.js:189-191`) already returns and prints per-flow
`stats.{activeExpects, deferredExpects}`, but `bin/e2e-compile.js`'s `--all` batch loop
(lines ~82-113) sums coverage% and never sums those two counters across the directory. A
2-counter addition to an existing loop would give the plugin a first-party corpus baseline
instead of relying on an untracked spike script. Classify **EXISTS_BROKEN** (primitive present,
aggregation unwired), not MISSING. Optional in this scope — see Dispatch sizing.

## Reverse-recovery audit (layer trace, against `origin/main @ 7521546`)

| Layer | File:line | Verdict | Note |
|---|---|---|---|
| Parser | `compiler/parser.js` | WORKING, out of blast radius | `expect:` strings pass through as raw strings; parser's `expect.*` handling (lines 351-368) is for `finally`-step JSON fields, unrelated to this grammar |
| Resolver | `resolver.js:119-151`, `175-272` | WORKING — the seam being widened | 14 patterns confirmed by direct read; dispatch loop at 185-269 |
| Codegen | `codegen.js:1640` (`text-visible`), `:1640+` (`text-not-visible`) | WORKING, reused as-is | Both new patterns route to existing branches; **zero codegen changes** |
| Element→page binding | `resolver.js:157-173` (`resolveElement`), collision error at 158-162 | EXISTS_BROKEN — **and now measured** | Mapping-wide symbol table ignores the page qualifier. Not repaired here (3t owns it), but it is the reason the element permutation is out of scope: adding it breaks 2 clean flows |
| Compiler tests | `compiler/test/resolver.test.js:441-637` ("Phase 2" tests) | WORKING harness | Needs 3 new cases (2 new-form + 1 ordering), not new infra |
| Corpus baseline | `.context/spike-deferred-rate.js` (+ `spike-xn-*.js` added this session) | WORKING (git-excluded) | Ran clean; reproduces 368/794 exactly |
| Batch corpus counter | `bin/e2e-compile.js:82-113` | EXISTS_BROKEN | Optional first-party replacement for the above |
| Docs | see Doc diff below | MISSING (canonical reference) | No file enumerates the grammar; resolver.js source is the only true reference today |

Boundary with sibling entities, stated explicitly: xn changes no resolution semantics, adds no
new rejection (**asserted numerically** — errors 630→630, clean flows 20→20), and leaves the
page-qualifier question exactly as found. The measurement above hands
[[e2e-page-scoped-resolution]] a concrete inheritance: closing the element permutation is
blocked on page binding, and the 2 flows it would break are named. Author-visible feedback on
the assertions xn does *not* recover — including the hyphenated-element class — is
[[e2e-assertion-honesty-gate]]'s job. Operand typing ([[e2e-typed-operands]]) is unaffected.

## Doc diff

No file today enumerates the expect grammar canonically — `CLAUDE.md`, `docs/writing-tests.md`,
`references/common-patterns.md`, and `skills/e2e-map/SKILL.md:201` each show 1-3 example strings
in passing (verified by grep); resolver.js's source is the only complete reference that exists.

**Proposed:** add a new `## Expect Grammar Reference` section to `docs/writing-tests.md`,
inserted before the existing `## Element Coverage` section (currently at line 340), containing
the 16-row table above (with the 2 new rows marked, matching the table format already used in
that file's `## Element Coverage` section for consistency) plus one line:
*"`on <page>` is accepted but not verified — element resolution is mapping-wide, not
page-scoped (tracked separately)."* Also update `skills/e2e-compile/SKILL.md:111`'s
"unrecognized format" warning line to link to the new reference section.

Note for the doc author: `docs/writing-tests.md:238` already uses `text 'Created' on items-page`
— a form that reads as page-qualified but where `on page` is a literal keyword and
`items-page` is being swallowed by `(.+)` as part of the text value. Worth an explicit caution
in the new section so authors do not infer a page-name slot that does not exist.

## E2E-first acceptance

Real-flow exercise, not unit-test-only: compile a flow YAML whose `expect:` list contains both
`text '<value>' is visible` and `text '<value>' is not visible`, run it through
`/e2e-compile --verbose <flow>`, and observe both resolve to active (not deferred) in the
printed per-step output and the `expects active / expects deferred` summary line. This session's
spike exercised `resolve()` directly across the whole corpus, which is stronger evidence for the
*counts* but does not prove the CLI path end to end; implementation must do the real
`.claude/e2e/flows/*.yaml` compile, since ideation deliberately kept every patch off the tracked
codebase (design-only stage — the spike harnesses build their patched resolver into a temp dir
at run time and never write to `e2e-pipeline/`).

## Spike (result recorded)

Performed 2026-07-25 against the real corpus, not a fixture. RED: the 8 corpus strings measured
`deferred` against unpatched `resolver.js` (368/794, 46.3%). GREEN: inserting exactly the 2
lines in the Design table recovered all 8 (360/794, 45.3%) with resolve errors unchanged at 630
and clean-compiling flows unchanged at 20. Three rejected variants were spiked the same way and
their damage measured (element form: 2 clean flows broken; hyphen widening: 2 clean flows
broken; FO's 4 diagonal forms: 0 strings recovered). The page-qualifier mechanism did not need
re-spiking — but the element-form measurement independently re-confirms it, since the failure
mode is precisely the discarded qualifier.

## Falsification

Demonstrated, not hypothetical: reverting either added line returns its corpus strings to
`deferred` — the "before" column of the Corpus evidence table *is* the falsification baseline,
produced by running both resolver versions over the same corpus in one process. Sharper still:
the AC set is falsifiable in the *harmful* direction too — AC5's error-count assertion (630) and
AC1's clean-flow assertion (20) are exactly what failed for the element and hyphen variants, so
a wrong pattern cannot pass this AC set by only moving the deferred number.

## Design determination

`design: required` (not `trivial-pass`) — the expect grammar is the flow-authoring interface;
the concrete design decision is the grammar table above (2 new rows, their insertion points,
and the evidence-backed exclusion of the element form, the hyphen widening, and all 6
zero-corpus symmetric completions). Frontmatter `design:` left blank per ensign rules (no
frontmatter edits) — gate to set it.

## Non-goals (Q4 — FO-recommended, captain delegated; now corpus-backed)

1. **No cross-product completion.** All 6 symmetric candidates tested — the FO's 4 hypothesized
   diagonal text forms, the 2 double-quote `is` forms, and the `or-visible` `is` variant — score
   **0 corpus occurrences**. Cut on evidence, not taste.
2. **No element permutation this round.** `<elem> is visible on <page>` is deferred to
   [[e2e-page-scoped-resolution]]: it recovers 3 strings but breaks 2 clean flows today.
3. **No hyphenated-element widening.** Distinct defect class (character class, not permutation);
   recovers 2 strings but breaks 2 clean flows; belongs with [[e2e-assertion-honesty-gate]].
4. **No grammar redesign** — `on page` stays a literal word for text.
5. **No semantics change and no new rejection** — asserted numerically (errors 630→630, clean
   flows 20→20), not merely intended.
6. **No page-binding fix smuggled in**, and no claim of page-scoped verification anywhere.

## Appetite, cut priority, pre-mortem (Q3/Q5 — FO recommendations, not captain-authored)

- **Q3 (keep if forced to cut):** FO recommended keep-text / cut-element. **Confirmed by
  measurement, and the scope cut it implies is now mandatory rather than optional** — the
  element form is not merely absorbable by 3t at zero marginal cost, it is net-negative before
  3t lands. The surviving scope is the text class alone.
- **Q5 (pre-mortem), class: criteria that pass without delivering value:** *"If this ships
  exactly per spec and still fails, the most likely cause is the deferred-count AC going green
  while authors still get zero feedback — because the feedback mechanism is
  [[e2e-assertion-honesty-gate]]'s, and xn only shortened the queue it will fail on."* Recorded
  verbatim from the FO dispatch. Partly mitigated in the AC set: AC1 and AC5 also assert the
  error count and clean-flow count, so the deferred number cannot go green alone. Fully
  unmitigated for the feedback half — by design, that is 5v's.

## Dispatch sizing

**ONE implementation worker session.** Scope: 2 regex lines in `resolver.js` (insertion points
fixed above) + 3 new `resolver.test.js` cases (positive, negative, ordering) + the
`writing-tests.md` doc-diff section. Every piece is measured, not estimated: the patch is
2 lines, codegen/parser diffs are empty, ordering is position-independent, and the corpus
before/after already ran clean. Well under the 90-minute / 3-independent-behaviors threshold.

The `bin/e2e-compile.js` corpus aggregation is **optional** and explicitly cuttable — AC1 is
satisfied by the existing `.context/spike-deferred-rate.js` harness. Include it only if the
session has room; it buys a first-party baseline instead of an untracked script.

## Stage Report: ideation (cycle 1 — superseded)

Retained for audit. Its scope decisions were rebuilt in cycle 2 below; where the two disagree,
cycle 2 governs. Moved ahead of cycle 2 in file order (implementation carried item c) so
`status --read xn --checklist` — which reads the LAST `## Stage Report: ideation` section —
selects the current cycle 2 round instead of this superseded one.

- DONE: Correct the entity body's pattern count and re-verify against origin/main
  Read `resolver.js:119-151` at `origin/main @ 7521546` (byte-identical in this checkout) —
  confirmed 14 entries, not 12; body corrected. (Still valid.)
- DONE: Reverse-recovery audit and design determination recorded against origin/main
  Layer table produced. (Extended in cycle 2.)
- FAILED: Reproduce the baseline the entity body leans on
  Concluded `.context/` was absent from the checkout and the machine, on the strength of a
  single `find` whose output I misread and never cross-checked with `ls -a`. The directory was
  present at the exact path claimed. Every downstream conclusion that rested on "corpus
  unreachable" was wrong, including the text-class narrowing.
- FAILED: Enumerate proposed patterns from the corpus
  Enumerated from `.spacedock-state` design documents instead, and misread
  `e2e-typed-operands.md:70` ("quoting **variants**", plural, with one illustration) as bounding
  the class to a single string. Correct discipline, wrong evidence base.
- DONE: Empirical resolver spike (scratch copy, real `resolve()`, 14 forms unchanged)
  Sound method and correct results; carried forward and extended in cycle 2.

## Stage Report: ideation (cycle 2 — repair round)

Supersedes cycle 1 above on every point where they disagree. Cycle 1's load-bearing premise
(the corpus is unreachable) was false; everything it concluded from that premise was rebuilt
against the real corpus.

- DONE: Every proposed pattern is justified by a corpus string that is deferred today and resolves after the change; enumerate from the corpus, never from the cross-product. A pattern with no recovered real string is cut, not kept "for symmetry".
  12 candidates scored by running the real resolver over the real 368-string deferred set.
  2 survive (`text '<v>' is visible` 4 occ, `text '<v>' is not visible` 4 occ). 10 cut on zero
  evidence or measured harm — including all 4 FO-hypothesized diagonal forms (0 occ each) and
  the element permutation (3 occ but breaks 2 clean flows).
- DONE: The value AC measures deferred-expect reduction against a re-runnable baseline, and explicitly disclaims two things it does NOT deliver: author feedback (that mechanism is 5v) and page-scoped verification (`on <page>` is parse-and-discard today - see scope notes).
  AC1 now carries real numbers (368→360 of 794; 46.3%→45.3%) from
  `.context/spike-deferred-rate.js`, plus error count (630→630) and clean-flow count (20→20)
  so the baseline can move the wrong way. Both disclaimers retained verbatim in substance.
- DONE: Reverse-recovery audit and design determination are recorded against origin/main, and the entity states its boundary with 3t / g5 / 5v: xn changes no resolution semantics, adds no new rejection, and leaves the page-qualifier question untouched.
  Audit extended with a new EXISTS_BROKEN row (`resolveElement` page binding) now backed by
  measurement rather than inference. "Adds no new rejection" is now a measured claim, and it is
  what forced the element form out of scope — the strongest possible statement of the 3t
  boundary.
- DONE: Reproduce the baseline (cycle-1 failure, now corrected)
  `node .context/spike-deferred-rate.js .context/flow-corpus.txt` reproduces 368/794 · 46.3% ·
  17 flows · 1 asserting-nothing — exactly the inherited figures, no drift.
- DONE: E2E-first acceptance
  Unchanged in intent, updated to the surviving forms; still requires a real
  `/e2e-compile --verbose` run, since the corpus spike proves counts but not the CLI path.
- DONE: Spike recorded
  Four variants spiked and measured (text-only; +element; +hyphen; end-of-table ordering).
- DONE: Falsification hook
  Retained and strengthened — the AC set is now falsifiable in the harmful direction too
  (error/clean-flow counts), which is what caught the element-form regression.
- DONE: Dispatch sizing recorded
  ONE session, narrowed: 2 regex lines + 3 tests + doc section; the CLI aggregation is now
  explicitly optional because AC1 no longer depends on it.

### Summary

The repair round overturned this ideation's central scope decision. Running the real corpus
(reachable all along — `.context/` is a dotfile my cycle-1 `find` missed, and I trusted a single
mangled negative instead of confirming with `ls -a`) reversed three conclusions: the negated
text form I had cut has exactly as much corpus support as the positive one (4 occurrences each)
and is restored; the FO's 4 hypothesized diagonal forms have zero support and are cut; and the
element permutation — which both prior drafts wanted to ship — recovers 3 strings but breaks 2
flows that compile cleanly today, because the page name that would disambiguate is parsed and
discarded. It is now deferred to 3t on evidence. Final scope is 2 text patterns recovering 8
corpus assertions with zero new errors and zero flows harmed. A hyphenated-element-name defect
was found along the way, measured (recovers 2, breaks 2), and handed to 5v rather than smuggled
in. Method lesson recorded in the body: proof-of-absence needs a second strategy, and pattern
proposals get scored against the corpus, never against prose.

## Stage Report: implementation

- DONE: RED before GREEN with recorded evidence for each of the 2 patterns, including an ordering test that would fail if `text '<v>' is not visible` were captured by a positive pattern first
  Added tests for AC-2/AC-3/AC-4 to `resolver.test.js`; ran scoped file first: 3 fail / 47 pass
  (RED — `deferred` instead of `text-visible`/`text-not-visible`). Added the 2 lines to
  `EXPECT_PATTERNS`; re-ran: 50/50 (GREEN). AC-4 asserts the negative type is explicitly
  NOT `text-visible` alongside 8 corpus strings + 2 pre-existing sibling forms in one step.
  RED+GREEN+2-line patch committed together, worktree commit `444e846`.
- DONE: AC-1's `Verified by:` command still reproduces AFTER the patch lands
  Rewrote `.context/spike-xn-before-after.js` (gitignored harness) to source BEFORE via
  `git show <ref>:e2e-pipeline/compiler/resolver.js` instead of requiring the live file.
  Verified the fix directly: ran it with `XN_REPO_DIR` pointed at this worktree *after* the
  2-line patch was already on disk — still reproduced 368→360/426→434/630→630/20→20, proving
  the harness no longer collapses once the patch is merged.
- DONE: The real `/e2e-compile --verbose` run happened against an actual `.claude/e2e/flows/*.yaml` (not a fixture)
  Used the real corpus flow `carlove/.claude/e2e/flows/vehicle-brand-select.yaml` (copied
  read-only into a scratch `flows/`+`mappings/` dir; carlove itself untouched). `--verbose`
  dry-run shows 5 of the 8 corpus strings as `text-visible`/`text-not-visible` (active) where
  the pristine 7521546 build shows all 5 `deferred` (3→8 active, 37→32 deferred for this one
  flow). A real (non-dry-run) compile emitted correct `grep -qF`/`grep -qF ... elif` codegen for
  both new types via the existing branches — confirms AC-5's "codegen.js diff empty" claim by
  execution, not inspection. Doc diff landed in the same commit: `## Expect Grammar Reference`
  (16-row table) in `docs/writing-tests.md` before `## Element Coverage`, and the
  `skills/e2e-compile/SKILL.md:111` warning line now points to it.
- DONE: Carried item (b) — reformat ACs to the README template
  `## Acceptance Criteria` rewritten to `**AC-N — <property>.**` + `Verified by: ... Falsified
  by: ...`, substance unchanged (Falsified-by clauses extracted from the existing Falsification
  section, not invented). Confirmed: `--ac-scan` now returns AC-1..AC-5 (previously nothing).
- DONE: Carried item (c) — move the superseded cycle-1 report
  Swapped physical order: cycle 1 now precedes cycle 2. Confirmed:
  `--stage ideation --checklist` now reads cycle 2's 8 DONE items, not cycle 1's 2 FAILED ones.
- DONE: Scope discipline — only the 2 approved patterns shipped
  Element form, hyphen widening, and all 6 zero-corpus symmetric completions were not added.

### Summary

Landed exactly the approved 2-line `resolver.js` patch (worktree commit `444e846`, doc
cross-reference fixup `05e3d79`) plus 3 new `resolver.test.js` cases, the
`docs/writing-tests.md` doc diff, and the `SKILL.md` link, with RED recorded before GREEN and
the full suite green once (630/630) at exit. All 3 carried items
closed: the AC1 harness survives the patch landing, the ACs are in the scannable template, and
the stage-report ordering bug is fixed. One discrepancy surfaced and corrected rather than
silently propagated: the entity's doc-diff note says `docs/writing-tests.md:238`'s
`text 'Created' on items-page` example is "swallowed by `(.+)` as part of the text value" —
empirically it isn't captured by any pattern at all (verified against both the pristine and
patched resolver) and resolves as `deferred`; the shipped caution states the verified behavior
instead. Flagging for the gate in case the doc author wants the example itself fixed (out of
scope here — only the caution was requested).
