---
id: gzh8xe17fgnjpc03qk19n3xx
title: Structured compiler diagnostics an agent can repair from
status: validation
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started: 2026-07-25T16:12:08Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-e2e-json-diagnostics
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

**Scope ruling, captain, 2026-07-26: NO `code` field in this entity.** The channel ships
structured fields only; the error-code vocabulary belongs to [[e2e-schema-contract]] (1d) and a
follow-up adds `code` once 1d lands. See "Escalation — RESOLVED" for the rationale and the
follow-up's definition. Every shape below is `code`-less by ruling, not by oversight.

**Shape (single-flow mode):**
```json
{
  "ok": false,
  "flow": "list-data-completeness",
  "stats": { "total": 12, "activeExpects": 9, "deferredExpects": 0, "resolveErrors": 3 },
  "errors": [
    {
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
1 (failure) exactly as today. Class distinction is not carried by the exit code, and (per the
ruling) not yet by a `code` field either; until 1d lands, a consumer that must dispatch by class
matches on `message`. That interim cost is named honestly in "Escalation — RESOLVED" rather than
hidden — it is the accepted price of not improvising a vocabulary in 1d's territory.

**Two-tier error structure, and why the split falls where it does.** Every error the compiler
raises today falls into one of two families:

- **Tier 1 — resolution errors about a named symbol that has a home in the symbol table**
  (`resolveNavigate`'s page lookup, `resolveElement`'s expect-side lookup, and the click/fill
  inline lookups in both `resolve()` and `resolveMultiSite()`). These are repairable FROM DATA
  THE COMPILER ALREADY HAS — the whole point of this entity. Full shape: `step_id`, `field`,
  `got`, `candidates`, `message`.
- **Tier 2 — structural/type errors** (`parser.js`'s ~56 validation errors, plus
  `resolver.js`'s no-type-field, unknown-step-type / action-format-mismatch
  (`parseActionString`), unknown-runtime-ref, and `resolveMultiSite`'s
  missing-site-qualifier / unknown-site). None of these name a symbol with a "did you mean"
  answer sitting in a table. `{message}` only.

The tier split survives the `code` ruling intact, because the split was never about codes — it
is about **whether `candidates` has real data behind it**. Tier 1 carries five fields; tier 2
carries one. When 1d lands, `code` is added to both tiers without re-shaping either.

This is a semantic split, not a size-driven cut: **`candidates` only exists where the compiler
already computed the closest-thing** (the collision table for ambiguous elements; nothing new is
computed for anything else). This directly answers whether fuzzy matching belongs here: **no** —
`candidates` for the element-not-found and page-not-found branches is `[]` today and stays `[]`
until (if ever) a fuzzy-match feature is separately scoped; Levenshtein-style suggestion is new
detection logic, explicitly cut (Non-goals).

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
`{message}` only). `errors: string[]` is not edited at any existing call site, so all six
consumers above need zero changes and are safe by construction, not by care. `parser.js` stays
untouched entirely: `compile()` already returns early on a parse failure before `resolve()`/
`resolveMultiSite()` ever runs (`compiler.js:52-56`), so parse errors and resolve errors are
never in the same array at the same time — the `--json` boundary wraps `parseResult.errors`
generically as `errorDetails: parseResult.errors.map(m => ({message: m}))` only at the point of
building the JSON response, never touching `parser.js` itself.

**Where `candidates` come from for the ambiguity branch (today, no fuzzy match needed):**
`resolveElement` (`resolver.js:157-173`) already has `collisionsTable.get(elemName)` — the exact
list of pages the ambiguous element is defined on. Today that list is interpolated into the
message string ("found on: X, Y") and thrown away as structured data; `candidates` for this
class is that same array, exposed as JSON instead of English — zero new computation.

**How `3t` and `5v` are born structured without a `code` field.** This is what the reorder
actually needs, and it does not depend on a vocabulary. `[[e2e-page-scoped-resolution]]`'s two
new message shapes populate the same five fields the moment they are raised: `page 'P' not found
in mapping` → `{step_id, field: 'page', got: 'P', candidates: [], message}`; `element 'X' not
found on page 'P' (found on: Y)` → `{step_id, field: 'element', got: 'X', candidates: [Y ∪
collisions.get('X')], message}` (the union per 3t's own point 7). `[[e2e-assertion-honesty-gate]]`'s
deferred-expect refusals arrive the same way, with `field: 'expect'` and `got` = the unmatched
string. No re-shape is needed when `code` is added later — the field set is stable, and `code`
is purely additive on top of it.

**Follow-up entity, to be filed so it is not lost: add `code` to `--json` errors once
[[e2e-schema-contract]] (1d) lands.** Scope: one `code` field on each `errorDetails` object,
drawn from 1d's published validation vocabulary, at the ~10 `errors.push` sites this entity
already touches plus whatever 3t/5v have added by then. It is a small, mechanical follow-up
precisely because this entity establishes the field-population plumbing and the tier split
first — the expensive half is done here, the naming half waits for its owner. The captain's
ruling records this dependency direction explicitly (see "Escalation — RESOLVED").

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

**The `CODE` column above is the harness's own analysis label, NOT a field the compiler emits.**
Per the captain's ruling this entity ships no `code` field (see "Escalation — RESOLVED"); the
labels exist so the measurement can name what it counted. Do not read this table as evidence for
a code vocabulary — it is evidence for the tier split and for the population size, which is what
the ruling actually turned on.

**Reproducibility scope — machine-local, stated plainly.** `flow-corpus.txt` is 3286 absolute
paths into other repos on this machine (`/Users/kent/Project/...`, `/Users/kent/conductor/...`),
so this measurement and its harness are reproducible **on this machine at the stated paths**, not
on a fresh clone and not in CI. This is why the harnesses stay `.context/`-excluded rather than
committed: committing them would make the corpus ACs *look* CI-reproducible when they cannot be,
which is a worse failure than an honest gap. The numbers themselves were independently
reproduced by the FO from the persisted harness at the pinned ref.

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

## Measurement correction — the repair-cost premise is false for the ambiguity class (captain, 2026-07-26)

**Implementation measured AC-4's original cost claim and it did not hold.** Recorded here rather
than folded silently into the re-scoped AC, because the correction is worth more than the AC it
replaced: it falsifies a sentence in this entity's own Problem statement.

Repairing the 3-error anchor flow, prose baseline vs `--json`, both at `632f04c`:

```
prose (deduped ERROR lines) bytes:  472
json errors[] compact bytes:        974
json full document bytes:          1133
```

Reproduce verbatim from `e2e-pipeline/` (both commands print the byte counts above):
```bash
node bin/e2e-compile.js --dry-run list-data-completeness \
  --flows-dir compiler/test/fixtures --mappings-dir compiler/test/fixtures --output-dir /tmp/gz-a \
  2>&1 1>/dev/null | grep '^ERROR' | sort -u | wc -c

node bin/e2e-compile.js --json --dry-run list-data-completeness \
  --flows-dir compiler/test/fixtures --mappings-dir compiler/test/fixtures --output-dir /tmp/gz-b \
  2>/dev/null \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const e=JSON.parse(s).errors;console.log(JSON.stringify(e).length,s.trim().length)})'
```
(Byte counts include the newline each `wc -c` line carries; the comparison is like-for-like since
both modes are counted as the bytes an agent actually receives.)

**The structured channel is ~2x LARGER in bytes, not smaller** — `message` already carries the
full "found on:" text, and the structured fields restate it rather than replacing it.

**The premise that fails.** The Problem statement says *"the information needed to repair is
sitting in the symbol table the resolver just built, and is thrown away with the error."* For the
**ambiguity class that is false** — `resolveElement` already interpolates the exact collision list
into the message string (`found on: X, Y, ...`), so the information was never thrown away; it was
thrown away *as structure*, not as content. 5 of the 9 tier-1 corpus cases are that class.

**Which class actually gains what** — this is the axis the re-scoped AC-4 rests on, and it is the
inverse of the intuitive reading:

| Class | Corpus cases | `candidates` | Repairable from the error alone? | What `--json` adds |
|---|---|---|---|---|
| Ambiguous element | 5 | Real page list | **Yes** — pick the right page from the list | The list as an array instead of a comma-list embedded in English |
| Element/page not found | 4 | `[]` by design (Non-goal 5) | **No** — the real name is not in the error, in either mode | Structured `got`/`step_id`/`field` without regexing the message |

So "repair without re-reading the mapping" holds for the **ambiguity** class (where a candidate
list exists), and cannot hold for **not-found** (where `candidates: []` is correct, not a channel
failure — this section's own counter-example above). Both classes gain parseability; only the
ambiguity class gains repairability, and it gains it in *form* rather than in *content*.

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

**AC-3 — Tier-1 `candidates` are real data, never invented.** Errors raised from the ambiguity
branch (`resolver.js:157-173`, where `collisionsTable.has(elemName)`) carry `candidates` = the
exact pages already in `collisionsTable`; errors raised from the not-found branches (element or
page absent entirely) carry `candidates: []` — no fuzzy-match/distance algorithm is added.
Stated by call site rather than by class name, since this entity emits no `code` field (ruling).
Verified by: `--json` against the snapshotted `list-data-completeness` fixture — the `tab_all`
(2-way) and `data_table` (9-way) ambiguous errors show `candidates` matching today's "found on:"
lists; the existing `missing-element-flow.yaml`'s `nonexistent_button` shows `candidates: []`.
Both fixtures live in `compiler/test/fixtures/`, so this AC is CI-reproducible on a fresh clone.
Falsified by: `candidates` non-empty for a not-found error (proof of undisclosed fuzzy-matching),
or an ambiguous error's `candidates` not matching `collisionsTable`'s pages.

**AC-4 — the channel is consumed without regexing prose, and the skill text it replaces is a measured recurring saving (value AC, re-scoped by the captain 2026-07-26).**
Re-scoped off byte cost: implementation measured the original cost claim and it was false — the
structured channel is ~2x LARGER in bytes (974 vs 472), because the ambiguity class's prose
already embeds its candidate list. See "Measurement correction" for the numbers and the premise
they falsify. The two properties below are what is true, measured, and still worth having.
Scoped to the tier-1 resolution class only, as before: NOT the no-type-field class (this entity
doesn't touch migration status) and NOT deferred-expect (still a silent-pass hole per
[[e2e-typed-operands]]/[[e2e-assertion-honesty-gate]], which would let a "before" case succeed by
not failing).

**(a) The skill-prose reduction is a recurring saving.** `skills/e2e-compile/SKILL.md` drops from
202 to 144 lines (−58, −29%). That file is loaded on every compile invocation, so the reduction
recurs per-invocation rather than being a one-off. This is also the pre-mortem's own guardrail:
the channel is load-bearing precisely because the prose it replaced is gone (AC-5).
Verified by: `git show ac33dab:e2e-pipeline/skills/e2e-compile/SKILL.md | wc -l` → 202, versus
`wc -l` on the merged file → 144. CI-reproducible on a fresh clone. Falsified by: the merged file
at or above 202 lines, or Phase 3's prose surviving alongside the JSON path.
(The figure was 135 / −67 / −33% through cycle 2; the gate's doc-honesty conditions added 9 lines
of bounded-claim and missing-vs-empty-directory correctness. Restated rather than left stale —
the saving is smaller than first claimed and still real.)

**(b) A tier-1 error is consumed structurally, not by regex — and the ambiguity class is
repairable from the error alone.** Every tier-1 error exposes `step_id`/`field`/`got` as fields,
so no consumer parses them out of English. For the ambiguity class specifically, `candidates` is
a JSON array of the exact pages, so the repair (disambiguate to the right page) needs nothing but
the error. Note the direction: this holds for **ambiguity**, and cannot hold for **not-found**,
where `candidates: []` is correct by design (Non-goal 5) and the real name is absent from the
error in either mode — see "Measurement correction"'s table.
Verified by: `cli.test.js` CLI-08 asserts `tab_all`'s 2-way and `data_table`'s 9-way `candidates`
arrays match today's "found on:" lists verbatim, and `missing-element-flow`'s `candidates: []`;
each assertion reads parsed JSON fields, never a regex over `message`. CI-reproducible (repo
fixtures only). Falsified by: a consumer needing to regex `message` to recover `got`/`candidates`,
`candidates` non-empty for a not-found error, or an ambiguity error whose `candidates` does not
match `collisionsTable`.

**Population claim (unchanged, still load-bearing for the scope above).** That this class is 9
corpus-live cases and that `list-data-completeness.yaml` carries exactly 3 is reproduced by
`node .context/spike-gz-error-classify.js .context/flow-corpus.txt --detail` (pinned to
`GZ_BEFORE_REF=529296d`; expect `tier-1 ... 9` and `3  list-data-completeness.yaml`). Falsified
by: a tier-1 count that no longer matches the 3-error anchor the fixtures are built on.
**Reproducibility scope:** this population step is verifiable **on this machine at the stated
paths only** — `flow-corpus.txt` is 3286 absolute paths into other repos under
`/Users/kent/Project` and `/Users/kent/conductor`, so neither it nor the harness can run on a
fresh clone or in CI. Properties (a) and (b) are both CI-reproducible. The numbers are real and
were independently reproduced by the FO from the persisted harness at the pinned ref; the
limitation is on where they can be re-derived, not on whether they hold.

**AC-5 — the SKILL.md prose is deleted, not supplemented (the pre-mortem's own guardrail).**
`skills/e2e-compile/SKILL.md`'s Phase 3 "Present Results" (currently lines 94-189, 96 of 202
lines — teaching the agent to regex-parse 6 distinct human-prose shapes) is replaced by a
`--json`-first flow. Target: under 40 lines.
Verified by: line-count diff of the merged SKILL.md at the gate/implementation review. Falsified
by: the ~96-line prose block still present alongside a new JSON path (an unconsumed channel —
exactly the pre-mortem's failure mode), or the replacement exceeding ~40 lines by re-deriving the
same per-mode prose recipes against JSON fields instead of collapsing them.

**AC-6 — exit-code semantics unchanged.** `--json` introduces no new exit codes; 0 on success /
1 on failure exactly as today. Error class is not encoded in the exit status (nor, per the
ruling, in a `code` field) — the exit code answers only "did compilation succeed".
Verified by: a CLI test asserting `result.status` for a success case (0) and a resolve-error case
(1) under `--json`, matching the non-`--json` exit codes for the same fixtures. CI-reproducible
on a fresh clone (repo fixtures only). Falsified by: any exit code other than 0/1, or an exit
code varying by error class.

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
single JSON document from stdout; map `ok`/`stats`/`errors[].message`/`.got`/`.candidates` to
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
feature is real, not a no-op); a deliberately-introduced fuzzy-match "helpful guess" on the
not-found branch would show a non-empty `candidates` for the corpus's `'the'`/`'customer'`
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
1. Not emitting a `code` field at all — settled by the captain's ruling, not merely "not
   inventing an enum unilaterally". [[e2e-schema-contract]] (1d) owns the vocabulary and a named
   follow-up adds `code` once 1d lands (Design; "Escalation — RESOLVED").
2. Not changing any error's *detection* — every classification wraps an EXISTING
   `errors.push(string)` call; no error newly raised, none stops being raised, no message text
   changes.
3. Not touching exit-code semantics — 0/1 only, unchanged.
4. Not building a repair loop or auto-fixer — this entity emits repairable information;
   consuming it is the agent's (or a future entity's) job.
5. Not adding fuzzy/nearest-match suggestion logic on the element-not-found / page-not-found
   branches — `candidates` there is `[]` by design, not a placeholder oversight (Design's Tier
   split).
6. Not touching `parser.js` — its ~56 error strings are wrapped generically only at the
   JSON-boundary in `compiler.js`, never edited at the source.
7. Not migrating `carlove`'s 565 un-migrated v1-format flows (the no-type-field majority of the
   630) — a corpus-owner action in another repo, same non-goal class as
   [[e2e-page-scoped-resolution]]'s Non-goal 4.
8. Not deciding whether the skill surfaces `--json` as a user-facing flag versus always using it
   internally — flagged in Doc diff for the gate.

## Escalation — RESOLVED by the captain, 2026-07-26

**The conflict as escalated.** This dispatch's section 5 said codes should come from
[[e2e-schema-contract]] (1d)'s vocabulary, not a private enum. Ideation then found that **1d's
own body asserts the opposite sequencing** (`e2e-schema-contract.md:41-42`): *"this must land
before [[e2e-json-diagnostics]], because the structured error codes should be derived from the
schema's validation vocabulary rather than invented ad hoc and then migrated"* — a cross-model
reviewer's argument already adopted into 1d. That collided with the FO's reorder putting this
entity first, and with 1d's own dependency on [[e2e-typed-operands]] (g5, backlog). Three-way,
and not self-adjudicable by the working agent per the README's Judgment Escalation clause.

**The ruling: split the entity. Ship the structured channel WITHOUT a `code` enum.** Emit
`{step_id, field, got, candidates, message}`. `code` is dropped from this entity's scope
entirely; 1d owns the vocabulary; a named follow-up (defined in Design) adds `code` once 1d
lands.

**Why this dissolves the conflict instead of picking a winner:**
- **The reorder is satisfied.** `3t` and `5v` refusals are born structured, because what they
  actually need is the *fields*, not the names — see "How `3t` and `5v` are born structured
  without a `code` field" in Design.
- **No schema is improvised in 1d's territory.** The "invented ad hoc and then migrated" cost
  1d's note warns about is not paid at all, rather than merely mitigated.
- **g5 is not needed.** The value measurement stays on the resolution class, which hard-fails
  today, so nothing waits on the silent-pass hole being closed.

**The justification is this entity's own measurement, not taste:** tier-1 is **9 of 630**;
tier-2 is **621**. The `candidates` machinery — the part that needs a vocabulary to be useful
for dispatch — serves 9 cases. The channel itself serves **two downstream entities**. Channel
first, vocabulary later, is the better trade, and the numbers that establish it are the ones
this ideation corrected and the FO independently reproduced (Corpus evidence).

**Known interim cost, recorded rather than hidden.** Until 1d lands, a consumer that must
dispatch by error class matches on `message` text — the cost this ideation originally raised
against its own option 3. The ruling accepts it knowingly: it is bounded (one follow-up removes
it), it affects only class-dispatch (not repair, which uses `got`/`candidates`/`field`), and
there is no consumer keying on class today because this entity is the first consumer. Recorded
so the follow-up's value is legible and does not get quietly dropped as "nice to have".

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

**The captain's `code` ruling shrinks this, and the estimate stands unchanged rather than being
re-padded to fit.** Dropping `code` removes the vocabulary-assignment decision from every one of
the ~10 `errors.push` sites (each addition is now purely mechanical field population) and removes
the `docs/commands.md` vocabulary documentation entirely. The sizing above already described the
plumbing as the expensive half; the ruling removes part of the cheap half. Appetite stays 1
session with more headroom, not a smaller stated budget — per the stage-def's forcing-budget
clause, a variance is a signal to investigate, not a number to hit.

### Feedback Cycles

- Cycle 1: REJECTED — validation reviewer panel (`code-reviewer` + `silent-failure-hunter`, converged unprompted on the same three sites; `agy` cross-model confirmed after `codex` failed on quota); surface ~1.64M subagent tokens vs estimate 1 session (~769K, [[e2e-expect-grammar-permutations]] being the only comparable that shipped) (213%); AC narrowed: AC-4 re-scoped mid-implementation from repair-loop token cost to the SKILL.md reduction plus structural consumption, after the byte measurement inverted (472 prose vs 974 compact JSON).

Both design-reset triggers fired on this cycle — past the 2x tolerance and a narrowed AC — so
the reset decision is recorded before any further round rather than after it. Where the budget
went is the load-bearing fact: ~793K of the ~1.64M (48%) was spent in ideation across four
correction rounds, against 363K to actually build it. This entity did not overrun on
construction; it overran on deciding, and two of those four rounds existed only to correct
first-officer errors (a wrong root-cause diagnosis of the AC-scan break, and a swapped
attribution of which error class gains repairability).

**Design-reset decision, captain, 2026-07-26: RECONFIRM.** Scope stands; finish it. The sunk
1.64M does not enter the decision — what enters is the cost to complete, and that is three
located sites in one file. The channel is load-bearing for [[e2e-page-scoped-resolution]] and
[[e2e-assertion-honesty-gate]], both of which are sequenced behind it precisely so their
refusals are born structured; parking would strand that. Two constraints ride with the
reconfirm: the correction round is scoped to the three sites with no redesign and no new AC,
and any further FO-initiated correction round on this entity goes to the captain first rather
than being dispatched on first-officer judgment.

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
  Escalated with 3 costed options and the NEW conflict finding ([[e2e-schema-contract]]:41-42
  asserts the opposite sequencing). **Captain ruled 2026-07-26** — split the entity, ship the
  channel `code`-less, 1d owns the vocabulary, follow-up adds `code`. Recorded as
  "Escalation — RESOLVED"; see Correction round 2.
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
surfacing a new sequencing conflict against `e2e-schema-contract`'s own notes; **the captain
ruled the entity split — the channel ships `code`-less, 1d owns the vocabulary, a named follow-up
adds `code`** (applied in Correction round 2, justified by this entity's own 9-vs-621 tier
split). Six ACs, a full reverse-recovery audit, and a doc diff recorded; `design: required` for
the gate to set.

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

### Correction round 2 — captain's ruling applied: no `code` field (scoped)

The captain ruled on the escalation: **split the entity, ship the structured channel without a
code enum.** `code` is dropped from this entity's scope entirely; [[e2e-schema-contract]] (1d)
owns the vocabulary; a named follow-up adds `code` once 1d lands. Applied:

- **Escalation section rewritten as RESOLVED** with the ruling's rationale — the conflict is
  dissolved rather than won: the reorder is satisfied (3t/5v need the *fields*, not the names),
  no schema is improvised in 1d's territory, and g5 is not needed because the value measurement
  stays on the resolution class. Justification recorded as an argument from this entity's own
  data — tier-1 is 9 of 630, tier-2 is 621, so `candidates` serves 9 cases while the channel
  serves two downstream entities.
- **`code` removed from every shape**: the JSON example, tier-1 (`{step_id, field, got,
  candidates, message}`), tier-2 (`{message}`), the `parser.js` boundary wrap, the SKILL.md
  field mapping, AC-6's exit-code clause, and Non-goal 1. The tier split survives intact — it
  was always about whether `candidates` has real data, never about codes.
- **Class names replaced by call-site descriptions** in AC-3, AC-4, Non-goals, and Falsification,
  so nothing reads as an emitted vocabulary. The Corpus-evidence table's `CODE` column now
  carries an explicit note that it is the harness's analysis label, not a compiler field — that
  table must not be misread as evidence for a code enum.
- **Follow-up recorded in Design** so it is not lost: add `code` from 1d's published vocabulary
  at the ~10 sites this entity already touches, plus whatever 3t/5v have added by then.
- **Interim cost named, not hidden**: until 1d lands, class-dispatch means matching on `message`
  — the exact cost this ideation raised against its own option 3. The ruling accepts it
  knowingly; recording it keeps the follow-up's value legible.
- **Machine-local reproducibility stated** on the corpus-measured AC (AC-4) and in Corpus
  evidence: `flow-corpus.txt` is 3286 absolute paths into other repos on this machine, so step
  (a) is verifiable on this machine at the stated paths only, never on a fresh clone or in CI.
  This is also why the harnesses stay `.context/`-excluded — committing them would make the ACs
  look CI-reproducible when they cannot be. AC-3 and AC-6, which use repo fixtures, are marked
  CI-reproducible so the distinction is visible rather than blanket-hedged.

Unchanged per the FO: the two-tier structure (now `code`-less at tier 1), the additive
`errorDetails` strategy protecting the five identified consumers, the SKILL.md lines 94-189
deletion, the reverse-recovery audit, sizing, and the persisted classifier.

## Stage Report: implementation

- DONE: RED before GREEN, and the additive `errorDetails` strategy is proven not to disturb the
  five identified prose consumers
  15 new tests (10 `resolver.test.js`, 5 `cli.test.js`) confirmed RED by `git stash`-reverting
  `resolver.js`/`compiler.js`/`bin/e2e-compile.js` and re-running `node --test` before restoring;
  GREEN after. `resolver.test.js` re-asserts the pre-existing `.includes()` check (line 127 before
  this branch) verbatim, zero edits, alongside the new channel. Commit `632f04c`.
- DONE: No `code` field ships anywhere in the emitted contract
  tier1Detail = `{step_id, field, got, candidates, message}`, tier2Detail = `{message}`; every new
  test asserts `!('code' in detail)`. `e2e-schema-contract` still owns the vocabulary.
- DONE: AC-5 — the SKILL.md deletion happens in this branch, verified by line count not eyeballed
  Phase 3 was lines 94-189 (96 lines); is now lines 97-122 (26 lines) — `grep -n '^## Phase 3\|^##
  Common Mistakes'` before/after, not assertion. Under the AC-5 target of ~40 lines.
- DONE: AC-1 (single JSON document, all three cases) + a real gap found and fixed
  `cli.test.js` CLI-08: success/resolve-error/parse-error each assert stdout is exactly one
  parseable line. Found (RED-confirmed) and fixed: `--all --json` on an empty flows directory
  still printed plain prose to stdout before this session's own second pass — same stdout-purity
  bug class AC-1 exists to close, caught by writing the edge-case test rather than trusting the
  happy-path ones.
- DONE: AC-2 (default behavior byte-identical) / AC-6 (exit codes unchanged)
  Full suite green (647 tests, zero edits to any `errors.push` site or the six string-array
  consumers); CLI-08 asserts 0/1 exit codes under `--json` matching non-`--json` for the same
  fixtures.
- DONE: AC-3 (tier-1 candidates real, never invented) + E2E-first acceptance
  Snapshotted `list-data-completeness`/`secha-office` fixtures reproduce the real corpus's 3 live
  ambiguous errors byte-for-byte: `tab_all`'s 2-way and `data_table`'s 9-way "found on:" lists
  match verbatim; `missing-element-flow`'s not-found case shows `candidates: []`. Cross-checked
  `--json --dry-run` against the same flow compiled without `--json` (same `resolve()` call, not
  independent parsing) — surfaced a pre-existing, unrelated bug in doing so: `compile()` prints
  each resolve error to stderr AND `bin/e2e-compile.js`'s non-json failure branch prints the same
  `errors` array again, so every prose ERROR line appears twice today. Out of this entity's scope
  (Non-goal 2 — no change to existing prose/detection); noted here rather than fixed.
- FAILED: AC-4 value measurement, step (b) — "costs fewer tokens... does not require re-reading
  the mapping"
  Measured, not assumed, and it does not hold as stated for this fixture: deduped prose for the
  3-error case is 472 bytes; compact JSON `errors[]` is 974 bytes (full document 1133) — *larger*,
  not smaller, because `message` already carries the full "found on:" text and the structured
  fields mostly restate it. Neither mode requires a mapping re-read for this class either — the
  ambiguous branch's collision list was already interpolated into prose before this entity existed
  (Design's own point). Step (a) reproduces cleanly (9 tier-1 corpus-wide, 3 in this flow, exact
  messages — CLI-08's third test). Recommend the gate re-scope AC-4 off raw byte count toward
  what's actually load-bearing: no-regex parseability/reliability, and serving `3t`/`5v`'s new
  message shapes, which won't have pre-existing prose candidates the way this one already did.
  **Superseded — the captain accepted this and re-scoped AC-4 (2026-07-26). Both re-scoped
  properties now pass; see "Correction round 3" below.**
- DONE: Doc diff applied in this branch
  SKILL.md Phase 2 (`--json` always-on internally, not user-facing per Non-goal 8) + Phase 3
  rewrite (above); one `docs/commands.md` flags-table row.

### Summary

The structured `--json` channel is built, tested, and additive: `errorDetails` threads through
`resolveExpects`/`resolve`/`resolveMultiSite`/`compiler.js`/`bin/e2e-compile.js` without editing a
single existing `errors.push` call site or its six consumers, ships no `code` field, and the
SKILL.md prose-reformatting path is deleted and measured (96 → 26 lines). AC-1/2/3/5/6 and the
E2E-first acceptance are verified against a real, snapshotted production flow with exact-match
corpus numbers. AC-4's value claim, measured honestly rather than asserted, does not hold on a raw
byte-count reading for this specific ambiguous-only fixture — flagged for the gate to re-scope
rather than silently passed (the captain accepted and re-scoped it; Correction round 3). One
pre-existing, out-of-scope stderr double-print bug was found during cross-checking and is
recorded, not fixed.

### Correction round 3 — AC-4 re-scoped by captain ruling (scoped; no code change)

The captain accepted the byte-measurement finding and ruled AC-4 re-scoped off cost onto the two
properties that are true and measured. Applied, entity-only — **no source file was touched in this
round**; the implementation commit stands unchanged at `632f04c`.

- **New body section "Measurement correction"** records the numbers (472 prose vs 974 compact
  JSON `errors[]`, 1133 full document) with two copy-pasteable commands that reproduce them, plus
  the premise it falsifies: the Problem statement's "the information needed to repair is... thrown
  away with the error" is false for the ambiguity class, where `resolveElement` already
  interpolated the collision list into the message. It was thrown away as *structure*, not as
  *content*. Recorded as its own section rather than folded into the AC, per the ruling.
- **AC-4 rewritten** to (a) the recurring skill-prose saving — `SKILL.md` 202 → 135 lines (−67,
  −33%) against `ac33dab`, verified by `git show ac33dab:... | wc -l` vs `wc -l`, CI-reproducible
  — and (b) structural consumption without regex, with the ambiguity class repairable from the
  error alone. Both pass. The population claim and its machine-local reproducibility caveat are
  retained verbatim. Bold span opens/closes on one line; `--ac-scan` re-run, all six ACs resolve
  unevidenced=false.
- Unchanged per the ruling: the design, the other five ACs, the tier split, the absence of `code`,
  and the SKILL.md range.

**One deviation from the ruling's literal wording, flagged rather than silently applied.** The
ruling says the "repair without re-reading the mapping" property "holds specifically for the
not-found class." The evidence says the inverse, so AC-4 (b) attributes it to the **ambiguity**
class instead:

- Ambiguous (5 corpus cases): `candidates` = the real page list → the repair is available from the
  error alone.
- Not-found (4 corpus cases): `candidates: []` by design (Non-goal 5) → the real element name is
  absent from the error in **both** prose and JSON, so a mapping read is still required. This
  entity's own Corpus-evidence section already says exactly this: "`candidates: []` there is
  correct, not a channel failure."

What the not-found class *does* gain is structured `got`/`step_id`/`field` — parseability, not
repairability. If the captain intended "gains new information relative to prose" (arguably true
for not-found, since its prose carries no list to begin with) rather than "is repairable from the
error alone", the wording is reconcilable and AC-4 (b) should be re-read accordingly — but as
literally stated the two classes are swapped, and writing the AC to match the ruling verbatim
would have shipped an AC that its own verification would falsify.

## Stage Report: validation

- FAILED: Reproduce every AC's `Verified by:` clause yourself with actual command output
  AC-2/3/4/5/6 PASS, independently reproduced (not the implementer's self-report):
  `--json`/non-`--json` exit codes match at 0/1 for the same fixtures; the click-path ambiguous
  push at `resolver.js:369` re-asserts `resolver.test.js`'s pre-existing `.includes()` check
  unedited (confirmed by blame — line untouched in this commit's diff); `git show ac33dab:.../SKILL.md
  | wc -l` → 202 vs current `wc -l` → 135 (AC-4a, AC-5, exact match); the 472/974/1133-byte
  measurement correction reproduces verbatim via the two `node bin/e2e-compile.js` commands in
  "Measurement correction"; the population harness (`spike-gz-error-classify.js`, `GZ_BEFORE_REF=529296d`)
  reproduces `tier-1 9`/`tier-2 621`/`list-data-completeness.yaml: 3` exactly; `grep` confirms zero
  `code` field anywhere in the emitted contract.
  AC-1 FAILS its own falsification clause ("any non-JSON text present on stdout" / implicitly,
  `JSON.parse(stdout)` succeeding at all). Three reproducible invocation shapes under `--json` do
  NOT emit a JSON document, contradicting the Design section's unconditional claim ("stdout carries
  exactly one JSON document and nothing else") that `skills/e2e-compile/SKILL.md` (rewritten in
  this same commit) now depends on unconditionally:
  1. `node bin/e2e-compile.js --all --json --flows-dir <nonexistent-dir>` → stdout is **empty**
     (0 bytes), prose only on stderr. `bin/e2e-compile.js:76-81`'s `fs.readdirSync` catch never
     checks `options.json`.
  2. `node bin/e2e-compile.js --json <flow> --output-dir <unwritable-dir>` (EACCES on `mkdirSync`)
     → stdout **empty**. `bin/e2e-compile.js:310-312`'s outer catch (the safety net around
     `compile()`) never checks `options.json`.
  3. `node bin/e2e-compile.js --json` (no flow name, no `--all`) → stdout is 23 lines of Commander
     help prose, not JSON. `bin/e2e-compile.js:315-318`'s `program.help()` fallthrough never checks
     `options.json`.
  All three repro'd directly (not inferred from reading) with real exit codes/stdout/stderr
  captured. Two independent Sonnet reviewer-lens subagents (`code-reviewer`, `silent-failure-hunter`)
  converged on the same three sites unprompted with matching file:line citations, verified accurate
  against the actual file; `agy` (cross-model gate, see below) independently confirmed the same
  three on a targeted retry. This is this entity's own scope, not pre-existing: the catch bodies
  predate this diff, but the `--json` contract they now violate does not, and the implementer added
  `options.json` branches to every other exit path (empty-dir case, success/failure/coverage) except
  these three.
- DONE: Adversarial spot-check on the additive `errorDetails` strategy
  Edited the click-path ambiguous push (`resolver.js:369`, `errors.push(ambigMsg)` →
  `errors.push({message: ambigMsg})`) in the worktree, ran full suite: 5/647 failed, including
  `resolver.test.js`'s exact pre-existing `.includes()` consumer test
  (`TypeError: e.includes is not a function`) and `cli.test.js`'s CLI-08 prose/JSON cross-check
  (caught `'[object Object]'` on stderr) — proves the five-consumer no-regression claim is
  load-bearing, not vacuously green. Reverted via backup copy; full suite re-confirmed 647/647 green.
- DONE: Confirm no `code` field ships anywhere, and the SKILL.md prose deletion actually happened
  `grep -rn "code:" compiler/*.js bin/*.js` → zero matches (also zero for `'code'`/`"code"` string
  literals). `skills/e2e-compile/SKILL.md` Phase 3's old six-shape regex-prose recipe is gone,
  replaced by a single field→line table; no dual path (JSON table + surviving old prose) exists.
- Cross-model gate: `codex exec review --commit 632f04c` failed on first attempt (usage-limit quota
  error, recorded in `/tmp/codex-review-gz.log`) — fell back to `agy` per preference order. First
  `agy` attempt also failed (`Error: timeout waiting for response`, ~500-word prompt); second,
  narrower-scoped attempt succeeded and independently reproduced the AC-1 finding above with
  matching file:line citations.

### Summary

AC-2/3/4/5/6 and the E2E-first acceptance all independently reproduce clean — real command output,
not self-report, including AC-4's byte-cost re-scoping and the corpus population numbers. AC-1
fails its own falsification clause: three real, cheaply-reachable invocation shapes (unreadable
`--flows-dir`, an unwritable `--output-dir`, and bare `--json` with no flow argument) leave stdout
empty or full of Commander help prose instead of the promised single JSON document, directly
undermining the guarantee `skills/e2e-compile/SKILL.md`'s own rewrite (this same commit) now
depends on unconditionally. Three independent reviewers (two Sonnet lens agents, one cross-vendor
model) converged on the identical three file:line sites without prompting each other; all citations
verified against the real file and all three failure modes reproduced live. Recommend: route back
to implementation — the fix is small and mechanical (extend the existing `options.json` branching
pattern, already used at the empty-flows-dir case, to these three exit paths), not a design change.

## Stage Report: implementation (cycle 2)

Scoped fix round for validation's AC-1 finding. Only `bin/e2e-compile.js` and
`compiler/test/cli.test.js` were touched — no redesign, no new AC, no change to the tier split,
the `code`-less shapes, or the SKILL.md range. Commit `1c3977d`; cycle-1 commit `632f04c` stands.

- DONE: AC-1 — all three sites reproduced live before any fix
  Confirmed independently rather than trusted: site 1 (unreadable flows dir) exit 1 / 0-byte
  stdout; site 2 (EACCES output dir) exit 1 / 0-byte stdout; site 3 (`--json`, no flow, no
  `--all`) **exit 0** with 1192 bytes of Commander help prose on stdout. Site 3 was worse than
  reported — exit 0 tells a consumer the run succeeded.
- DONE: AC-1 — RED before GREEN, per site
  Three tests added to `cli.test.js` CLI-08, each asserting stdout parses as exactly one JSON
  document via the existing `parseOnlyStdout` helper. Confirmed RED (3 fail / 32) against the
  cycle-1 binary, then GREEN (32/32) after the fix. The falsifying change for each: revert its
  `options.json` branch and stdout goes empty (sites 1-2) or prose (site 3). This closes AC-1's
  own falsification clause ("any non-JSON text present on stdout"), which is what caught them.
- DONE: Each condition got its own document shape, not one collapsed shape
  **Site 1** — `{ok: false, flows: [], summary: {0,0}, errors: [{message}]}`, exit 1. Deliberately
  NOT the empty-directory shape: an empty dir stays `ok: true` / exit 0 (nothing to compile), an
  unreadable one is a failure (could not look). A regression test asserts both shapes side by side
  so a future collapse fails. `errors` is additive at batch level — without it the enumeration
  failure is literally unrepresentable in the document.
  **Site 2** — the documented single-flow shape with the thrown text as a tier-2 error, mirroring
  how batch mode already wraps a thrown `compile()` error.
  **Site 3** — chose to emit a document (`ok: false`, `flow: null`), move the usage text to
  **stderr**, and change exit 0 → 1. Rationale: this is a usage error, not a compile error, but
  SKILL.md's Phase 3 now parses stdout unconditionally with no prose fallback left, so making the
  guarantee conditional on argument validity reopens the exact hole being fixed. A human running
  `--json` by hand still gets the usage text; exit 1 because nothing was compiled.
- DONE: Swept for remaining unguarded stdout paths rather than assuming three was the whole set
  Audited every `console.log` / `process.exit` / `program.help` in the file: all prose writes sit
  behind `!options.json` or after a `--json` early-return. No further holes in the action handler.
- FAILED (out of scope, flagged not fixed): AC-1 has a FOURTH class — Commander's own arg-parse errors
  `--json --bogus-flag` and `--json --flows-dir` (missing value) both exit 1 with **0-byte stdout**,
  error on stderr. Not fixed: it needs `program.exitOverride()` plus a try/catch around
  `parseAsync`, which changes CLI-wide error handling for non-`--json` callers too — the scope
  widening the captain's reconfirm explicitly forbade. Materially lower risk than the three fixed:
  those are reachable from a *correct* skill invocation against a bad environment, whereas a
  malformed command line means the skill's own fixed invocation template is broken. Gate's call.
- DONE: AC-2, AC-3, AC-6 re-verified unchanged by the full suite at stage exit
  650/650 pass (was 647; +3 new). This round edited no resolver/compiler source and no
  `errors.push` call site, so AC-2's byte-identical default behavior holds by construction; AC-3's
  ambiguous/not-found `candidates` assertions and AC-6's 0/1 exit-code assertions both re-ran
  green. Lint on the two touched files shows only pre-existing findings (`allCoverageTotal`,
  `execFileSync`, unused `var result`) — none introduced this round, verified by grepping the
  added lines.
- DONE: AC-4 and AC-5 re-verified unchanged — SKILL.md was not touched this round
  `git diff --name-only 632f04c 1c3977d` returns only `bin/e2e-compile.js` and
  `compiler/test/cli.test.js`; `git show HEAD:...SKILL.md | wc -l` is still 135, so AC-5's
  deletion and AC-4(a)'s 202 → 135 recurring-saving measurement both stand. AC-4(b)'s
  no-regex/candidates assertions re-ran green in the same suite.

### Summary

Validation's finding was correct and reproduced on all three sites; one was worse than reported
(exit 0, not just empty stdout). Each site now emits a shape chosen for its condition rather than a
uniform stub — the empty-vs-unreadable directory distinction is itself regression-tested, since
collapsing them would make "nothing to compile" indistinguishable from "could not look". A fourth
class (Commander arg-parse errors) was found during the sweep and deliberately left unfixed as
out-of-scope, with its cost and risk stated for the gate. Diff is two files; everything that passed
cycle-1 validation is untouched.

### Gate conditions C1–C4 applied (doc-only; no code, no new tests)

Approved narrow on four doc conditions. Each premise was re-measured before editing rather than
taken on report — two of the four were stated slightly wrong upstream, and one of those was C4,
which exists precisely to correct a wrong premise.

- DONE: C1 — AC-1's batch shapes are now documented as built, and the distinction survives to the user
  `SKILL.md` Phase 3 claimed a *missing* flows directory returns `{ok:true, …}` exit 0. Measured:
  `ok:false`, exit 1, with `errors[]`. Phase 3 now documents empty (`ok:true`/exit 0) and
  missing-or-unreadable (`ok:false`/exit 1/`errors[]`) as separate results, tells the consumer to
  present `errors[].message`, and warns against reporting it as "no flows found" — which would hide
  a mistyped `--flows-dir` as an empty project. Optional top-level batch `errors` added to Phase
  3's batch rule and to `docs/commands.md:170`. This closes the P2 finding that the bespoke shape's
  distinction died at the consumer.
- DONE: C2 — AC-1's absolute is bounded and a fallback exists
  Phase 3 now scopes the one-document guarantee to the two supported invocations and adds: if
  stdout does not parse, fall back to stderr and the exit code rather than assuming success.
  **Phase 3 is 35 lines against AC-5's ~40-line ceiling** — 5 lines of headroom, so this does not
  and cannot be refused on AC-5 grounds. (C2 quoted 26; that was the pre-condition count. C1+C2
  added 9 lines. Stating the post-condition number, since the stale one is what a later reader
  would check against.)
- DONE: C3 — the coverage rows no longer promise what the skill's `--json` path does not do
  `SKILL.md:22-23` only, descriptive, no flag removed and no capability decided. Reproduced the
  EM's finding first: `--all --coverage` writes `coverage.json` + `coverage-history.json`; adding
  `--json` leaves the directory non-existent, exit unchanged. Sharpened by measurement — batch and
  single-flow differ, and the rows now say so: the **batch** document has no `coverage` key at all
  (verified: `JSON.stringify(doc).includes("coverage")` is `false`), while **single-flow** `--json
  --coverage` *does* carry populated `coverage` in the document but still writes no files.
- DONE: AC-4 — the (a) measurement restated after these edits changed it
  C1–C3 moved `SKILL.md` 135 → 144 lines, so AC-4(a)'s "202 → 135 (−67, −33%)" would have gone
  stale the moment these conditions landed. Restated in AC-4 to **202 → 144 (−58, −29%)** with the
  prior figure and the reason recorded. The saving is smaller than first claimed and still real;
  leaving the old number would have made this the entity's fourth wrong premise.
- DONE: C4 — the `--json --help` premise corrected, and the follow-up inference marked as one
  Recorded in the validation (cycle 2) section where the wrong premise lives. Measured at
  `1c3977d`: exit 0, **stdout 1192 bytes, stderr 0** — help on the contract channel, not an absent
  document, which is AC-1's falsification clause verbatim and widens the follow-up's worst case
  from "consumer sees nothing" to "consumer parses help text as a compile result". The
  `exitOverride`-is-insufficient claim is filed as an **inference at ~75%, explicitly unverified**,
  with a one-command disproof hook, because it is reasoned from Commander's write-then-exit
  ordering rather than observed.
- SKIPPED: `docs/commands.md:40` and `docs/writing-tests.md:386`
  Named in C3 as out of scope for this round; they belong to follow-up (b). Left untouched.

## Stage Report: validation (cycle 2)

Re-review of someone else's fix at `1c3977d`. Recommendation: **APPROVE with one recorded
condition** (a one-line doc/skill fix, below) — not a rejection cycle.

- DONE: Reproduce every AC's `Verified by:` clause with actual command output
  Re-run against the NEW commit, not cycle-1 evidence. AC-1's three fixed sites each emit exactly
  one parseable document (`parseOnlyStdout`, 32/32). AC-2/3/6 re-ran green in the 650/650 suite;
  this round edited no `errors.push` site, so AC-2 holds by construction. AC-4(a)/AC-5:
  `git show HEAD:...SKILL.md | wc -l` → 135 vs `ac33dab`'s 202, and `git diff --name-only
  632f04c 1c3977d` returns only the two files, so SKILL.md is provably untouched this round.
- DONE: Adversarial spot-check
  Ran the three NEW tests against the cycle-1 binary (`git show 632f04c:...bin/e2e-compile.js`
  into a scratch copy): exactly **3 fail / 32**, matching the report's RED claim precisely. The
  cycle-1 `errorDetails` spot-check is unaffected — no resolver source changed.
- DONE: Confirm no `code` field ships, and the SKILL.md prose deletion stands
  Both unchanged this round; SKILL.md not in the diff.
- DONE: JUDGED — the fourth class (Commander arg-parse) residual acceptance is **sound, but its
  recorded justification is empirically wrong**
  Reproduced: `--json --bogus-flag` and `--json --flows-dir` (no value) → exit 1, 0-byte stdout.
  Two corrections to the record. (1) "A malformed command line means the skill's own template is
  broken" is not quite right — the template is intact; only the substituted value need be hostile.
  `node bin/e2e-compile.js --json --my-weird-flow` (a dash-leading *flow name* in the skill's own
  fixed `--json <flow-name>` slot) reproduces the 0-byte stdout. Pathological, but reachable.
  (2) "Needs `exitOverride()` … changing CLI-wide error handling for non-`--json` callers" is
  disproved: a `--json`-gated `exitOverride` is ~14 lines, leaves non-`--json` byte-identical
  (verified: `--bogus-flag` without `--json` still exits 1 with 0-byte stdout and prose on
  stderr), and passes **650/650** in a scratch copy.
  Accepting anyway, for a reason the report does not give: the class has an **irreducible tail** —
  even with that fix, `--json --help` is not covered, so closing the class requires deciding what
  `--json --help` *means*. That is a design question, not a mechanical patch, and AC-1's letter
  covers only the two named invocation forms (`--json <flow>`, `--json --all`). Recommend filing
  the follow-up with the gated-prototype evidence attached so the next owner does not re-derive it.
  **CORRECTION (gate condition C4, measured 2026-07-26).** The line above previously read
  "`--json --help` still emits no document (exit 0, help to stderr)". That is wrong in the way that
  matters. Measured at `1c3977d`: **exit 0, stdout 1192 bytes, stderr 0 bytes** — the help text
  goes to **stdout**, and `JSON.parse` on it throws. So this is not an absent document; it is prose
  on the contract channel, which is AC-1's falsification clause verbatim ("any non-JSON text
  present on stdout"). It also changes the follow-up's scope rather than just its wording: the
  worst case is a consumer parsing help text as a compile result, not a consumer seeing nothing.
  Reproduce: `node bin/e2e-compile.js --json --help >/tmp/o 2>/tmp/e; wc -c </tmp/o </tmp/e`.
  **INFERENCE, not a finding — confidence ~75%, unverified.** A `--json`-gated `exitOverride`
  alone is likely insufficient for this tail, because Commander writes help through its output
  writer *before* the exit path fires, so intercepting the exit does not unwrite what is already on
  stdout; closing the class probably also needs `configureOutput`/`writeOut` redirection. Flagged
  as an inference because it is reasoned from Commander's documented write-then-exit ordering, not
  observed — and this record has now had three premises turn out wrong when a plausible-sounding
  claim went unmarked. **Disproof hook (one command):** add `--json`-gated `exitOverride` to the
  existing scratch prototype, run `--json --help`, and check stdout — if it is 0 bytes or valid
  JSON, this inference is wrong and `exitOverride` alone suffices.
- FAILED: The new top-level batch `errors` key is undocumented and **unconsumed** (P2, new this round)
  `bin/e2e-compile.js:86-91` puts the enumeration failure in a top-level `errors` array. The normal
  batch document (`:170-175`) has no such key, and **both** consumers document the batch shape as
  `{ok, flows, summary}` — `skills/e2e-compile/SKILL.md` Phase 3 and `docs/commands.md:170`.
  Exercised rather than read: feeding the real unreadable-directory output through SKILL.md's
  documented batch rule verbatim renders `Batch compilation complete: 0 OK, 0 failed` and lists
  nothing — the directory error is never shown. So at the user-visible layer "could not look" still
  collapses into "nothing to compile", which is the exact distinction the bespoke shape was built to
  preserve; the distinction exists in JSON but dies at the consumer. This is the entity's own
  pre-mortem (an unconsumed channel) in miniature. Fix is one line in each of SKILL.md and
  `docs/commands.md`; no code change. Independently surfaced by both reviewers this round.
- DONE: Verified the cycle-2 report's citations are true, not merely present
  Checked the load-bearing one myself: the "swept every `console.log`/`process.exit`/`program.help`"
  claim holds — every prose write sits behind `!options.json`, an `else`, or a `--json`
  early-return with `process.exit` + `return`. It is also correctly *bounded*: it says "in the
  action handler", and the fourth class lives outside it at `parseAsync`. 650/650, 32/32, 3-fail
  RED, SKILL.md 135, and the two-file diff all reproduce.
- SKIPPED: Treating the four dead bindings as a defect of this diff
  All four are **pre-existing at `ac33dab`** (`execFileSync` plus the same three unread `var result`
  at `cli.test.js:101,128,201`) — verified against the base file, not inferred. And the concern
  behind the question does not hold: all three tests do assert, on filesystem side effects
  (`fs.readdirSync(tmpDir)` length), so they are weak-but-real, not intended-and-never-written.
  Context for a future cleanup, not this entity's.
- Cross-model gate: `codex exec review --commit 1c3977d` attempted, failed again (exit 1, usage
  limit until Jul 29) — recorded, not assumed. Fell back to `agy`, which ran and independently
  reached the same top-level-`errors` inconsistency. Caveat on that round: `agy` rendered its
  citations under a stale absolute path that resolves to a different 254-line checkout, but its
  line numbers (350-360, 324-338, 83-91) only exist in the real 370-line worktree file and each
  claim checks out there, so the substance is anchored correctly. Two of its five line cites were
  near-miss region pointers. Reviewer-agent citations were verified individually and all four held.

### Summary

The fix is real and the rejection is discharged: all three sites now emit exactly one JSON
document, RED-before-GREEN reproduced independently at exactly 3 fail/32, and nothing that passed
cycle-1 validation moved. Two judgment calls go back to the gate rather than being inherited. The
fourth-class deferral is the right call but for the wrong recorded reason — the widening it cites
is disproved by a 14-line gated prototype that passes 650/650, while the real reason to defer is an
irreducible `--json --help` tail that needs a design decision. And site 1's bespoke shape preserves
the "could not look" vs "nothing to compile" distinction in JSON but not at the consumer: the
documented skill mapping renders it as `0 OK, 0 failed` and drops the error, so that channel ships
unconsumed unless one line is added to SKILL.md and `docs/commands.md`. Recommend approving on
that condition, with the fourth class filed as a named residual carrying the prototype evidence.
