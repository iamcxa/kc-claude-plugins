---
id: gzh8xe17fgnjpc03qk19n3xx
title: Structured compiler diagnostics an agent can repair from
status: ideation
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started: 2026-07-25T16:12:08Z
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

The compiler emits nothing a program can consume. There is no `--json`; errors are prose on
stderr (`ERROR: Step 'x': element 'submit_btn' not found in mapping`) and the exit code is
0 or 1 with no per-class distinction. There is also no fuzzy matching anywhere — grepping
`compiler/` for levenshtein, "did you mean", closest, or suggest returns zero hits. So an
agent that hits an unknown-element error has no path to the fix except reading the entire
mapping YAML back into context to discover the real name was `submit_button`. The
information needed to repair is sitting in the symbol table the resolver just built, and is
thrown away with the error.

The cost of that missing structure is visible in the skill layer: roughly 100 of the 202
lines of `skills/e2e-compile/SKILL.md` are prose instructions teaching the agent how to
re-format the compiler's human prose into different human prose — a presentation layer for
a machine talking to a machine.

Shape to decide at ideation: `--json` emitting `{ok, output, stats, errors: [{code,
step_id, field, got, candidates[], message}]}`, with nearest-match candidates drawn from
the symbol table for unknown element/page, and for a rejected expect the list of supported
expect shapes. Then delete the reformatting prose from the compile skill.

## Notes for ideation

- The value AC should be measured, not asserted: repair a flow carrying three seeded errors
  with and without `--json`, and record both the token cost of the repair loop and whether
  the agent had to re-read the mapping file at all. That is a baseline that can move the
  wrong way.
- That measurement is only meaningful after [[e2e-typed-operands]] closes the silent-pass
  hole — otherwise the "before" case can succeed by not failing.
- Error codes should come from [[e2e-schema-contract]]'s vocabulary rather than a private
  enum invented here.

## Sequencing note from the FO, 2026-07-25

**Implement this before [[e2e-page-scoped-resolution]] and
[[e2e-assertion-honesty-gate]], even though `3t` reached ideation first.**

Both of those entities introduce new compile-time refusals. If the structured error
channel exists first, each new refusal is born structured; if it does not, they emit
prose that has to be converted afterwards — the same work, done twice, plus a window
where the compiler speaks two error dialects.

This does **not** ask anyone to discard `3t`'s ideation. Ideation produces a design
and acceptance criteria, and neither is invalidated by landing `gz` first. The reorder
is only at the implementation boundary, so nothing already done is wasted.

If `3t` has already reached implementation by the time this is read, ignore this note
and let it finish — the conversion cost is small and is not worth an interrupt.

## FO-authored scope (recorded verbatim per dispatch — captain delegated the conn for this sprint)

**Appetite: 1 session.** Larger than `xn` ([[e2e-expect-grammar-permutations]]) and `3t`
([[e2e-page-scoped-resolution]]) — a new output surface plus a skill-prose deletion, not a
resolver-internal fix.

**What to keep if forced to cut: the structured error channel itself.** That is what `3t` and
`5v` ([[e2e-assertion-honesty-gate]]) need in order to be born structured, and it is the
reorder's entire justification. Nearest-match candidates are the agent-ergonomics win and are
the cut — valuable, but they do not block anything downstream. Cutting the channel to keep the
candidates would invert the sprint's dependency.

**Happily NOT doing:**
1. Not inventing an error-code enum unilaterally.
2. Not changing any error's *detection*; this entity changes how errors are *emitted*, not what
   is rejected. No new refusals here — those belong to `3t` and `5v`.
3. Not touching exit-code semantics beyond what a structured channel needs, and not adding
   per-class exit codes without saying why prose-to-JSON alone is insufficient.
4. Not building a repair loop or an auto-fixer. This entity emits repairable information;
   consuming it is the agent's job.

**One-sentence pre-mortem — class: hidden assumption.**
> If this ships exactly per spec and still fails, the most likely cause is that the JSON channel
> landed while `skills/e2e-compile/SKILL.md` kept its prose-reformatting path, so agents went on
> reading the human text and the structured channel became dead weight nobody consumed.

## Design — `--json` output shape, tiered structure, additive compatibility

**Shape (single-flow mode):**
```json
{
  "ok": false,
  "flow": "list-data-completeness",
  "stats": { "total": 12, "activeExpects": 9, "deferredExpects": 0, "resolveErrors": 3 },
  "errors": [
    {
      "code": "element_ambiguous",
      "step_id": "select-all-tab",
      "field": "element",
      "got": "tab_all",
      "candidates": ["service-schedule", "employee-profiles"],
      "message": "Step 'select-all-tab': element 'tab_all' is ambiguous -- found on: service-schedule, employee-profiles"
    }
  ],
  "coverage": null
}
```
Batch mode (`--all --json`): `{ "ok": bool, "flows": [ {flow, ok, stats, errors}, ... ], "summary": {passed, failed} }` — same per-flow shape nested.

**`--json` is a stdout contract, not an addition to one.** When `--json` is set, stdout carries
exactly one JSON document and nothing else — no `Compiled: N steps...` line, no `OK: <flow>`
line. Today's prose moves to stderr or is dropped; `--verbose`'s existing stderr step-dump is
untouched and orthogonal (a debugging aid, not part of the machine contract). Interleaving JSON
with prose on stdout is worse than either alone — an agent parsing stdout would have to strip
prose lines out of the very channel this entity exists to make trustworthy.

**Exit codes are unchanged.** No per-class exit codes (Non-goal 3) — process exits 0 (success) /
1 (failure) exactly as today; class distinction lives in `errors[].code`, not the exit code.

**Two-tier error structure, and why the split falls where it does.** Every error the compiler
raises today falls into one of two families:

- **Tier 1 — resolution errors about a named symbol that has a home in the symbol table**
  (`resolveNavigate`'s page lookup, `resolveElement`'s expect-side lookup, and the click/fill
  inline lookups in both `resolve()` and `resolveMultiSite()`). These are repairable FROM DATA
  THE COMPILER ALREADY HAS — the whole point of this entity. Full shape: `code`, `step_id`,
  `field`, `got`, `candidates`, `message`.
- **Tier 2 — structural/type errors** (`parser.js`'s ~56 validation errors, plus
  `resolver.js`'s `no_type_field`, `unknown_step_type`/`action_format_mismatch`
  (`parseActionString`), `unknown_runtime_ref`, and `resolveMultiSite`'s
  `missing_site_qualifier`/`unknown_site`). None of these name a symbol with a "did you mean"
  answer sitting in a table. `{code, message}` only.

This is a semantic split, not a size-driven cut: **`candidates` only exists where the compiler
already computed the closest-thing** (the collision table for ambiguous elements; nothing new is
computed for anything else). This directly answers whether fuzzy matching belongs here: **no** —
`candidates` for `element_not_found`/`page_not_found` is `[]` today and stays `[]` until (if
ever) a fuzzy-match feature is separately scoped; Levenshtein-style suggestion is new detection
logic, explicitly cut (Non-goals).

**Additive compatibility strategy — the load-bearing implementation risk, flagged now.**
`resolver.js`'s `errors` return field is an array of PLAIN STRINGS today, depended on
exactly-as-shaped in five existing call sites that a naive "make errors objects" implementation
would silently break:
- `compiler.js:54` — `parseResult.errors.forEach(e => console.error('ERROR: ' + e))` (shared,
  parse errors, both single- and cross-site paths).
- `compiler.js:67` — same pattern, cross-site `resolveResult.errors`.
- `compiler.js:103` — same pattern, single-site `resolveResult.errors`.
- `bin/e2e-compile.js:104` — `result.errors.join(', ')` in the `--all` batch FAIL log.
- `bin/e2e-compile.js:237` — `result.errors.forEach(e => console.error('ERROR: ' + e))`,
  single-flow error branch.
- `compiler/test/resolver.test.js:127` — `result.errors.find(e => e.includes('...'))`.

An object at any of these sites prints `ERROR: [object Object]` or throws
`TypeError: e.includes is not a function`. The fix is **additive, not a type change**:
`resolve()`/`resolveMultiSite()` gain a NEW parallel return field, `errorDetails` (same length
and order as `errors` — Tier-1 sites populate the full shape, Tier-2 sites populate
`{code, message}` only). `errors: string[]` is not edited at any existing call site, so all six
consumers above need zero changes and are safe by construction, not by care. `parser.js` stays
untouched entirely: `compile()` already returns early on a parse failure before `resolve()`/
`resolveMultiSite()` ever runs (`compiler.js:52-56`), so parse errors and resolve errors are
never in the same array at the same time — the `--json` boundary wraps `parseResult.errors`
generically as `errorDetails: parseResult.errors.map(m => ({code: 'compile_error', message: m}))`
only at the point of building the JSON response, never touching `parser.js` itself.

**Where `candidates` come from for `element_ambiguous` (today, no fuzzy match needed):**
`resolveElement` (`resolver.js:157-173`) already has `collisionsTable.get(elemName)` — the exact
list of pages the ambiguous element is defined on. Today that list is interpolated into the
message string ("found on: X, Y") and thrown away as structured data; `candidates` for this
class is that same array, exposed as JSON instead of English — zero new computation.

**Provisional code vocabulary (recommendation, not a decision — see Escalation).** Named
descriptively after what the compiler already emits, not invented as a taxonomy:
`page_not_found`, `no_url_pattern`, `element_ambiguous`, `element_not_found`,
`unknown_runtime_ref`, `no_type_field`, `unknown_step_type`, `action_format_mismatch`,
`missing_site_qualifier`, `unknown_site`, and a generic `compile_error` fallback for anything
from `parser.js`. `[[e2e-page-scoped-resolution]]`'s two new message shapes (`page 'P' not found
in mapping` for a stated-but-undefined page — reuses `page_not_found`; `element 'X' not found on
page 'P' (found on: Y)` — a new `element_not_found_on_page` code, `candidates` = the union of the
"found on" page(s) and any `collisions.get(elemName)` entries per 3t's own point 7) slot into
this vocabulary without a re-shape — the whole reason this entity is sequenced first.

## Corpus evidence — measured this session (and a correction to this dispatch's own framing)

Reused the sprint's shared corpus baseline (`.context/flow-corpus.txt`, 100 unique flows by
content hash) and the real `resolve()` function (not a reimplementation), classifying all 630
resolve-error strings by shape. Harness persisted at `.context/spike-gz-error-classify.js`,
following the sibling convention (`spike-xn-before-after.js`): it sources `resolver.js` from
`git show <ref>:...` rather than the on-disk checkout, so the baseline stays valid after gz's own
patch — and, more importantly, after [[e2e-page-scoped-resolution]] lands, since 3t adds two new
error message shapes and collapses 3 of the ambiguity errors counted below. Ref override
`GZ_BEFORE_REF`, checkout override `GZ_REPO_DIR`.

```
node .context/spike-gz-error-classify.js .context/flow-corpus.txt

ref: 529296d   corpus: 100 unique flows by content, 87 scored

CODE                          TIER   COUNT
no_type_field                 2      565
action_format_mismatch        2      22
unknown_step_type             2      19
unknown_runtime_ref           2      15
element_ambiguous             1      5
element_or_page_not_found     1      4

total resolve errors           630
tier-1 (repairable: candidates already computed)  9
tier-2 (structural: no candidate data exists)     621

TIER-1 cases by flow (5 flows, 9 errors):
  3  list-data-completeness.yaml
  2  073-26-complaint-activity.yaml
  2  smoke-war-room.yaml
  1  billing-settlement.yaml
  1  073-28-service-follow-up.yaml
```

The harness's tier split is the same one the Design section uses, so the AC-3 boundary
("`candidates` only where the compiler already computed them") is measured, not asserted:
9 tier-1 vs 621 tier-2. `--detail` prints each tier-1 case with its full flow path.

**Correction to this dispatch's own framing — measured, not assumed.** Section 3 cites "630
resolve errors... These hard-fail today. Seed those" as the basis for choosing resolution-class
errors for the value AC. That call is still right — resolution-class errors DO hard-fail
(unlike the deferred-expect class section 2 correctly excludes) — but reading "630" as "630
repairable-via-candidates cases" would be wrong: **565 of the 630 (90%) are `no_type_field`** —
un-migrated v1-format flows (a `carlove`-side migration debt this entity does nothing about),
not the "agent hits an unknown-element error" scenario the Problem statement motivates. The
actual population this entity's value AC is about — a name that has a real answer sitting in
the symbol table — is **9 corpus-live cases** (5 ambiguous, 4 not-found), not 630. This doesn't
change section 2's core call; it changes how the value AC's evidence should be described, so a
future reader doesn't inherit an inflated sense of how common this specific defect is.

**Real corpus example selected for the value AC — `list-data-completeness.yaml`**, full path
`/Users/kent/Project/carlove/.claude/e2e/flows/list-data-completeness.yaml`, mapping
`secha-office` (project `carlove`). It is the highest-density tier-1 flow in the corpus and
already carries exactly 3 live ambiguous-element errors today, matching this entity's own
"repair a flow carrying three seeded errors" measurement design without seeding anything
synthetically. Reproduce the three verbatim with
`node .context/spike-gz-error-classify.js .context/flow-corpus.txt --detail`:
```
Step 'navigate-to-service-schedule': expect element 'tab_all' is ambiguous -- found on: service-schedule, employee-profiles
Step 'ensure-list-view': expect element 'data_table' is ambiguous -- found on: service-schedule, customer-profiles, branches, employee-profiles, workspaces, services, self-check-lists, audit-templates, report-step-templates
Step 'select-all-tab': element 'tab_all' is ambiguous -- found on: service-schedule, employee-profiles
```
`data_table`'s 9-way collision is exactly the case where today's prose forces an agent to either
parse a 9-item comma list out of English text or re-open the mapping YAML to enumerate pages —
`candidates: [...]` as a JSON array removes both. The existing `element_or_page_not_found` cases
(`'the'`, `'customer'` — natural-language parsing artifacts, not typos of real names) are the
honest counter-example: `candidates: []` there is correct, not a channel failure.

Because `list-data-completeness.yaml` lives in another project's tree (the sprint's shared
cross-repo corpus convention, `.context/`-excluded), **implementation should snapshot it (flow +
the relevant slice of `secha-office.yaml`) into `compiler/test/fixtures/`** rather than depend on
the external path at test time — matching this repo's existing fixture convention
(`duplicate-elements-mapping.yaml` already covers the ambiguous case, `resolver.test.js:119-128`;
`missing-element-flow.yaml` already covers not-found) and keeping the proof runnable on a machine
that has never seen `carlove`.

## Acceptance Criteria

**AC-1 — a single `--json` document, not prose plus JSON.** `e2e-compile --json <flow>` and
`e2e-compile --json --all` each emit exactly one JSON document on stdout with fields
`{ok, flow, stats, errors, coverage?}` (batch: `{ok, flows: [...], summary}`), for success,
resolve-error, and parse-error cases alike.
Verified by: a `compiler/test/cli.test.js` case that spawns the real CLI with `--json` and
asserts `JSON.parse(stdout)` succeeds with the required keys present, for a success case
(`simple-flow`), a resolve-error case (`missing-element-flow` or the new ambiguous fixture), and
a parse-error case. Falsified by: `JSON.parse(stdout)` throwing, a required key missing in any
of the three cases, or any non-JSON text present on stdout.

**AC-2 — default (non-`--json`) behavior is byte-identical, by construction.** Existing prose
stdout/stderr shape, exit codes, and file-write side effects are unchanged when `--json` is
omitted, because no existing `errors.push(string)` call site is edited (Design's additive
strategy).
Verified by: the full existing suite (`npm test`) passing with zero source edits to
`compiler/test/resolver.test.js:127`'s `.includes()` check or `bin/e2e-compile.js:104`'s
`.join(', ')` — both depend on `errors` staying `string[]`. Falsified by: either test requiring
an edit to keep passing, or a diff touching an existing `errors.push` call site's string
argument.

**AC-3 — Tier-1 `candidates` are real data, never invented.** `element_ambiguous` errors carry
`candidates` = the exact pages already in `collisionsTable` (`resolver.js:157-173`);
`element_not_found`/`page_not_found` carry `candidates: []` — no fuzzy-match/distance algorithm
is added.
Verified by: `--json` against the snapshotted `list-data-completeness` fixture — the `tab_all`
(2-way) and `data_table` (9-way) ambiguous errors show `candidates` matching today's "found on:"
lists; the existing `missing-element-flow.yaml`'s `nonexistent_button` shows `candidates: []`.
Falsified by: `candidates` non-empty for a not-found error (proof of undisclosed fuzzy-matching),
or an ambiguous error's `candidates` not matching `collisionsTable`'s pages.

**AC-4 (value AC) — the repair loop costs less, measured against a baseline that can move the
wrong way, scoped to the class that genuinely fails today.** Repairing the 3 live
ambiguous-element errors in `list-data-completeness.yaml` costs fewer tokens and does not
require re-reading the full mapping YAML into context via `--json`'s `candidates`, versus
today's prose-only stderr. Scoped to `element_ambiguous`/`element_not_found` only — corrected
scope, see Corpus evidence: NOT `no_type_field` (this entity doesn't touch migration status) and
NOT deferred-expect (still a silent-pass hole per [[e2e-typed-operands]]/[[e2e-assertion-honesty-gate]],
which would let the "before" case succeed by not failing).
Verified by: two steps, both re-runnable verbatim. (a) The population claim — that this class is
9 corpus-live cases and that `list-data-completeness.yaml` carries exactly 3 of them — is
reproduced by `node .context/spike-gz-error-classify.js .context/flow-corpus.txt --detail`
(pinned to `GZ_BEFORE_REF=529296d`; expect `tier-1 ... 9` and `3  list-data-completeness.yaml`).
(b) The cost claim is measured by running the repair task twice (prose baseline vs `--json`) on
the fixture snapshotted from that flow, recording token count + whether the mapping YAML was read
in full. Falsified by: the harness in (a) reporting a tier-1 count that no longer matches the
3-error anchor the measurement is built on, or, in (b), the `--json` condition using
equal-or-more tokens or still needing a full mapping re-read.

**AC-5 — the SKILL.md prose is deleted, not supplemented (the pre-mortem's own guardrail).**
`skills/e2e-compile/SKILL.md`'s Phase 3 "Present Results" (currently lines 94-189, 96 of 202
lines — teaching the agent to regex-parse 6 distinct human-prose shapes) is replaced by a
`--json`-first flow. Target: under 40 lines.
Verified by: line-count diff of the merged SKILL.md at the gate/implementation review. Falsified
by: the ~96-line prose block still present alongside a new JSON path (an unconsumed channel —
exactly the pre-mortem's failure mode), or the replacement exceeding ~40 lines by re-deriving the
same per-mode prose recipes against JSON fields instead of collapsing them.

**AC-6 — exit-code semantics unchanged.** `--json` introduces no new exit codes; 0 on success /
1 on failure exactly as today, class distinction living only in `errors[].code`.
Verified by: a CLI test asserting `result.status` for a success case (0) and a resolve-error case
(1) under `--json`, matching the non-`--json` exit codes for the same fixtures. Falsified by: any
exit code other than 0/1, or a code varying by error class.

## Reverse-recovery audit (against `origin/main @ 529296d`)

| Layer | File:line | Verdict | Note |
|---|---|---|---|
| CLI flag surface | `bin/e2e-compile.js` (Commander `.option(...)`, lines 33-40) | MISSING | No `--json`; `--coverage`/`--dry-run`/`--verbose` are the precedent to extend |
| Compiler core | `compiler/compiler.js` (`compile()`, lines 47-198) | WORKING for prose, MISSING for structure | Aggregates plain-string errors into `console.error`/`console.log`; no structured return shape exists |
| Resolver — Tier-1 candidate source | `resolver.js:157-173` (`resolveElement`), `86-106` (`resolveNavigate`) | EXISTS_BROKEN | `collisionsTable.get(elemName)` (the real "found on" list) is already computed and then discarded into a string — verified live against the real corpus |
| Resolver — Tier-2 sites | `resolver.js:75,80` (`parseActionString`), `293` (no type field), `360` (runtime_ref), `518,525` (`resolveMultiSite` site errors) | WORKING (prose), MISSING (structure) | No candidate data exists or is needed; minimal `{code,message}` wrap only |
| Parser | `compiler/parser.js` (~56 `errors.push` sites) | WORKING, out of blast radius | Pre-empted by `compiler.js:52-56`'s early return — parse errors never coexist with resolve errors; wrapped generically at the JSON boundary, zero source edits |
| Test harness | `compiler/test/cli.test.js`, `resolver.test.js` (`duplicate-elements-mapping.yaml`, `missing-element-flow.yaml` already exist) | WORKING harness, MISSING `--json` coverage | Both Tier-1 fixture shapes already exist — no new fixture infra needed for Tier-1, same finding pattern as [[e2e-page-scoped-resolution]]'s audit |
| Skill consumer | `skills/e2e-compile/SKILL.md` Phase 3 (lines 94-189) | EXISTS_BROKEN | Works today by teaching regex-parsing of 6 prose shapes — the presentation-layer defect this entity exists to retire, not a hole to fill |
| Docs | `docs/commands.md:150-172` (e2e-compile flags table) | WORKING, needs one row | No `--json` row yet |

No fresh `git fetch` was needed this session — `origin/main` is already `529296d` in this shared
checkout (per this dispatch's section 3), matching the tip cited throughout.

## Doc diff

**`skills/e2e-compile/SKILL.md`** — Phase 3 (lines 94-189, 96 lines) deleted and replaced with a
`--json`-first flow, target under 40 lines: Phase 2 always adds `--json` to the CLI invocation
(the skill is the agent-facing consumer this entity is about; human-prose mode stays available
directly via CLI for anyone invoking the compiler outside the skill). Phase 3 becomes: parse the
single JSON document from stdout; map `ok`/`stats`/`errors[].code`/`.message`/`.candidates` to
the existing presentation shapes — one field->line table replaces six prose-shape recipes.
Whether to also surface `--json` as a user-facing flag in the Invocation table, versus the skill
always using it internally without exposing it, is left open for the gate (Non-goals).

**`docs/commands.md:150-172`** — add a `--json` row to the e2e-compile flags table (mechanical,
matches the existing `--coverage-output`/`--dry-run` row format).

**`docs/writing-tests.md`** — no changes; this entity does not touch grammar or resolution
semantics (Non-goal 2), only emission format.

## E2E-first acceptance

A real CLI invocation on a real flow, not an isolated fixture assertion:
`node bin/e2e-compile.js --json --dry-run <flow>` against the snapshotted
`list-data-completeness` fixture must show `JSON.parse(stdout)` succeeding, `ok: false`, exactly
3 entries in `errors`, and `errors[].candidates` matching today's "found on:" lists verbatim —
cross-checked against the same flow compiled without `--json` (prose mode), to prove the two
paths agree on the same underlying `resolve()` call rather than merely each parsing
independently. A second real invocation against the existing `simple-flow.yaml` fixture (passes
clean today) must show `ok: true`, `errors: []`, and the compiled `.sh` file still written to
disk exactly as in non-`--json` mode — proving `--json` changes reporting, not compilation.

## Falsification

Falsifiable in the harmful direction, matching the sprint's established bar (`xn`/`3t`):
reverting the `errorDetails` addition returns `--json` output to a parse failure (proves the
feature is real, not a no-op); a deliberately-introduced fuzzy-match "helpful guess" for
`element_not_found` would show a non-empty `candidates` on the corpus's `'the'`/`'customer'`
cases — AC-3's test catches it, the intended guardrail against silent scope creep into new
detection logic. AC-4 (value) is falsified in the direction that matters: if the `--json`
condition needs equal-or-more tokens or still needs a full mapping re-read, the channel has NOT
bought anything and the AC fails honestly rather than passing by construction.

## Design determination

`design: required` — a machine-readable `--json` output is a contract for programmatic
consumers (any agent invoking the compiler, and downstream [[e2e-page-scoped-resolution]] /
[[e2e-assertion-honesty-gate]]). The concrete decision is the shape in "Design" above:
`{ok, flow, stats, errors[], coverage?}` single-flow / `{ok, flows[], summary}` batch, with the
two-tier `errorDetails` structure and the additive (non-breaking) implementation strategy.
Frontmatter `design:` left blank per ensign rules — gate to set it.

## Non-goals ("Happily NOT doing")

Transcribed from the FO-authored scope above, plus what emerged during design:
1. Not inventing an error-code enum unilaterally — the provisional vocabulary is a
   recommendation for the gate; [[e2e-schema-contract]] (1d) owns the final word (Escalation).
2. Not changing any error's *detection* — every classification wraps an EXISTING
   `errors.push(string)` call; no error newly raised, none stops being raised, no message text
   changes.
3. Not touching exit-code semantics — 0/1 only, unchanged.
4. Not building a repair loop or auto-fixer — this entity emits repairable information;
   consuming it is the agent's (or a future entity's) job.
5. Not adding fuzzy/nearest-match suggestion logic for `element_not_found`/`page_not_found` —
   `candidates` there is `[]` by design, not a placeholder oversight (Design's Tier split).
6. Not touching `parser.js` — its ~56 error strings are wrapped generically only at the
   JSON-boundary in `compiler.js`, never edited at the source.
7. Not migrating `carlove`'s 565 un-migrated v1-format flows (the `no_type_field` majority of the
   630) — a corpus-owner action in another repo, same non-goal class as
   [[e2e-page-scoped-resolution]]'s Non-goal 4.
8. Not deciding whether the skill surfaces `--json` as a user-facing flag versus always using it
   internally — flagged in Doc diff for the gate.

## Escalation — the error-code vocabulary, and a sequencing conflict this dispatch didn't have

Per this dispatch's section 5: codes should come from [[e2e-schema-contract]] (1d)'s vocabulary,
not a private enum invented here. **New finding this session: 1d's own "Notes for ideation"
states the opposite sequencing** — *"this must land before [[e2e-json-diagnostics]], because the
structured error codes should be derived from the schema's validation vocabulary rather than
invented ad hoc and then migrated"* (a cross-model reviewer's recommendation, already adopted
into 1d's body). That conflicts with the FO's sequencing note in this entity's own body (this
entity before `3t`/`5v` at the implementation boundary) — 1d-vs-gz ordering was never explicitly
re-litigated by the FO's reorder, and 1d asserts it should come first specifically for the reason
this section escalates.

**The options, with costs (not settled here):**

1. **Wait for 1d.** Correct per 1d's own note; no private enum ever exists. Cost: 1d itself
   depends on [[e2e-typed-operands]] (g5, backlog, itself deferred behind
   [[e2e-assertion-honesty-gate]] per g5's own body) settling whether operands move to typed
   fields — a multi-entity dependency chain, entirely in backlog. Waiting blocks the entire
   reason this entity was reordered to go first (3t/5v keep emitting unstructured prose
   meanwhile, recreating the "two error dialects" problem the reorder exists to prevent).
2. **Define a minimal provisional vocabulary now, that 1d adopts and/or renames.** The
   recommendation in Design: descriptive names for what already exists, explicitly marked
   provisional in code and in `docs/commands.md`. Cost: a rename when 1d lands is a compatible
   migration for any `--json` consumer keying on `code` (nobody depends on it yet — this entity
   is the first consumer) — bounded, not free, but small relative to the alternative.
3. **Ship structured fields with no `code` at all** (`step_id`/`field`/`got`/`candidates`/
   `message` only), deferring code assignment entirely. Cost: a consumer has to pattern-match on
   `message` text to dispatch by error class — reintroducing the "read prose to find the class"
   problem this entity exists to remove, just relocated onto a JSON field instead of stderr.

**Recommendation: option 2.** It unblocks the reorder's stated purpose; the "invented ad hoc"
risk 1d's note warns about is mitigated by naming codes after what already exists rather than a
speculative taxonomy; the migration cost when 1d lands is bounded and compatible. This is a
recommendation for the gate, not a decision made here — if the gate prefers option 1 or 3, say
so; option 1 effectively re-reverses the sprint order back to a captain-level call.

## Appetite, cut priority, pre-mortem

**Appetite: 1 session** (FO-authored) — larger than `xn`/`3t`: a new output surface plus a
skill-prose deletion plus a value measurement. The additive `errorDetails` strategy (Design)
keeps the `resolver.js` diff small (~8-10 one-line additions, existing lines untouched) despite
touching more of the pipeline (`compiler.js`, `bin/e2e-compile.js`, `SKILL.md`) than 3t's
single-file patch.

**What to keep if forced to cut: the structured error channel itself** (FO-authored) — `--json`
emitting `{ok, stats, errors[]}` with Tier-2 minimal structure everywhere, even if Tier-1's
`candidates` enrichment or the value-AC measurement don't fit in the session. `3t`/`5v` need the
channel to exist, not the enrichment, to be "born structured."

**Cut priority, in order:** (1) fuzzy/nearest-match candidates — never in scope (Non-goal 5);
(2) the value-AC measurement (AC-4) — defer to a follow-up if the session runs long, since it
measures the channel rather than building it; (3) SKILL.md's full Phase 3 rewrite — could ship a
smaller interim (try `--json`, fall back to prose parsing on failure) rather than the full
replacement, though this directly risks the pre-mortem below and should be a last resort.

**One-sentence pre-mortem (FO-authored, evidence-checked this session):** *If this ships exactly
per spec and still fails, the most likely cause is that the JSON channel landed while
`skills/e2e-compile/SKILL.md` kept its prose-reformatting path, so agents went on reading the
human text and the structured channel became dead weight nobody consumed.* This session's
Design section makes the SKILL.md deletion mechanically checkable (a line-count target, AC-5)
rather than a vibe. The gate should treat AC-5 failing (prose block still present) as equivalent
to the whole entity failing its value proposition, even if AC-1/AC-3 (the channel itself) pass
clean.

## Dispatch sizing

**ONE implementation worker session**, scoped by this session's design work, not a guess:
- `resolver.js`: add `errorDetails` parallel array; ~8-10 one-line additions beside EXISTING
  (untouched) `errors.push(...)` calls in `resolveNavigate`, `resolveElement`, and the click/fill
  inline blocks in both `resolve()` and `resolveMultiSite()`. No existing line is edited.
- `compiler.js`: thread `errorDetails` through `compile()`'s return value (both early-return
  branches + success path); build the JSON-boundary wrap for `parser.js`'s plain strings at this
  point only (no `parser.js` edit).
- `bin/e2e-compile.js`: new `--json` Commander option; a JSON-emission branch for single-flow and
  `--all` modes replacing the console.log/console.error prose calls with one
  `console.log(JSON.stringify(...))`, gated on the flag.
- `compiler/test/cli.test.js` / `resolver.test.js`: new `--json` cases against the
  ALREADY-EXISTING `missing-element-flow.yaml` and `duplicate-elements-mapping.yaml` fixtures —
  no new fixture infra for Tier-1 coverage; one NEW fixture (snapshotted `list-data-completeness`
  slice) for the value-AC measurement specifically.
- `skills/e2e-compile/SKILL.md`: Phase 2 (`--json` always-on) + Phase 3 rewrite (96 → <40 lines).
- `docs/commands.md`: one row addition.
- E2E-first: two real CLI invocations per the E2E-first acceptance section.

Under the 90-minute/3-independent-behaviors split threshold **as one behavior** (structured
emission is one seam, threaded through four files) but flagged as the larger end of "one
session" given the file count — if it runs long, the cut priority above gives the order, not an
extended budget.

## Stage Report: ideation

- DONE: Reverse-recovery audit against merge target
  `origin/main @ 529296d`, layer trace table in "Reverse-recovery audit" (resolver/codegen/
  compiler/parser, file:line per layer).
- DONE: Design determination
  `design: required`, shape + additive `errorDetails` compatibility strategy in "Design".
- DONE: Spike the riskiest unverified mechanism first
  `.context/spike-gz-error-classify.js` (real `resolve()` sourced from `git show 529296d:`, not
  the on-disk checkout — sibling convention, survives 3t's error-string changes) classified all
  630 resolve errors: 565 `no_type_field`, 5 `element_ambiguous`, 4 `element_or_page_not_found`,
  rest structural — corrected the dispatch's "630 hard-fail" framing to the true 9-case
  repairable population, in "Corpus evidence".
- DONE: AC are end-state properties with falsifiable proof
  AC-1..AC-6, each with Verified-by/Falsified-by; AC-4 named as the value AC, re-scoped to the
  corrected 9-case population.
- DONE: E2E-first acceptance
  Two real `--json`/non-`--json` CLI invocations (snapshotted corpus fixture + `simple-flow.yaml`)
  recorded as an implementation obligation.
- DONE: Doc diff proposed here
  `skills/e2e-compile/SKILL.md` Phase 3 deletion (96 -> <40 lines) + one `docs/commands.md` row.
- DONE: Size the implementation dispatch here
  ONE session, scope enumerated in "Dispatch sizing" against the additive `errorDetails` design.
- DONE: Appetite is a forcing budget / one-sentence pre-mortem / captain scope discipline
  FO-authored scope transcribed verbatim; cut priority and the pre-mortem (with its AC-5
  enforcement hook) in "Appetite, cut priority, pre-mortem".
- DONE: The value measurement seeds only error classes that genuinely fail today
  AC-4 scoped to `element_ambiguous`/`element_not_found` only (excludes the 565-case
  `no_type_field` noise and the still-silent deferred-expect class); real corpus flow
  `list-data-completeness.yaml` has exactly 3 live ambiguous errors, no synthetic seeding needed.
- DONE: The error-code vocabulary is brought to the gate as a decision, not settled
  "Escalation" lays out 3 costed options, recommends provisional-vocabulary, and surfaces a NEW
  conflict: [[e2e-schema-contract]]'s own notes assert the opposite sequencing (1d before this
  entity) that the FO's reorder never addressed.
- DONE: The prose deleted from `skills/e2e-compile/SKILL.md` is counted and named
  Phase 3 "Present Results" is exactly lines 94-189 (96 of 202 lines), not "roughly 100";
  replacement target <40 lines, in "Doc diff" and AC-5.

### Summary

Designed a `--json` output contract (`{ok, stats, errors[], coverage?}`, batch `{ok, flows[],
summary}`) with a two-tier error structure and an additive `errorDetails` strategy that never
edits an existing `errors.push(string)` call site, protecting five identified existing consumers
from silent breakage. Corrected the dispatch's "630 hard-fail" framing via a real corpus spike:
only 9 cases are the repairable class the value AC is about, and a real un-seeded corpus flow
covers exactly that measurement. Escalated the error-code vocabulary with 3 costed options,
surfacing a new sequencing conflict against `e2e-schema-contract`'s own notes. Six ACs, a full
reverse-recovery audit, and a doc diff recorded; `design: required` for the gate to set.

### Correction round 1 — spike durability (FO-requested, scoped)

The first pass ran the classifier from `/tmp` and deleted it, leaving AC-4's load-bearing number
as an unverifiable assertion — the same durability gap `xn`'s implementation was returned for.
Repaired, design untouched:

- Persisted to `.context/spike-gz-error-classify.js` on the sibling convention: sources
  `resolver.js` via `git show <ref>:e2e-pipeline/compiler/resolver.js` rather than the on-disk
  checkout, with `GZ_BEFORE_REF` / `GZ_REPO_DIR` overrides. Pinning is load-bearing here beyond
  the usual patch-survival argument — [[e2e-page-scoped-resolution]] adds two new error message
  shapes and collapses 3 of the ambiguity errors counted here, so a live-file harness would
  silently re-baseline AC-4 against a different resolver after 3t lands.
- Re-ran from the persisted path: **numbers unchanged** — 630 total (565 `no_type_field`, 22, 19,
  15, 5 `element_ambiguous`, 4 `element_or_page_not_found`), 9 tier-1, and
  `list-data-completeness.yaml` carrying exactly 3. The harness now also prints the tier-1/tier-2
  split (9 vs 621) that AC-3's boundary rests on, and `--detail` prints each case with its full
  flow path.
- AC-4's `Verified by:` now cites the runnable command line and its expected output; the
  Corpus-evidence section names the anchor flow's full path and the `--detail` reproduction.

Design, ACs, the additive `errorDetails` strategy, the SKILL.md line range, and the escalation
section are unchanged — per the FO, the escalation stays open and costed for the captain's ruling
on the `e2e-schema-contract` sequencing conflict.
