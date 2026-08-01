---
title: "Make the compiler refuse the selector grammar the linter bans — one policy, one gate"
status: ideation
source: GitHub #88, sprint e2e-pipeline/S1 item 2; re-shaped after PR #123 retired two of the five ban classes
product: e2e-pipeline
sprint: S1
started: 2026-08-01
completed:
verdict:
worktree:
issue: "88"
pr:
design: required
lane: main
id: pjjs91zrbrcm2we467a3vvp4
---

## Problem

`scripts/lint-mapping.sh` is the plugin's selector-grammar authority and **nothing on
the compiled path invokes it**. Proven by two independent strategies, both over the
tracked tree at `origin/main` (`1119387`):

- `git grep -n -I -- 'lint-mapping'` — every hit outside the script itself is prose
  (CLAUDE.md, agents/*.md, docs/*.md, references/*.md) or `test/integration-smoke.sh`.
  No `.github/workflows/` hit, no `bin/`, no `compiler/` hit.
- `git grep -n 'selector-translate' -- e2e-pipeline` — the compiler's only selector
  code path is the *translator*, which converts forms; it never refuses one.

So the ban is enforced by restating it in fourteen markdown files and by nothing that
can say no. A mapping carrying `>> nth=`, `:has-text(`, or a `find role …` subcommand
chain compiles green, dry-runs green, and fails only after browser startup — which is
exactly the expensive-late-detection the issue was filed for.

The premise the issue was *originally* written against is retired: PR #123 (`7108495`)
deleted lint CLASS 1 (`role=X[name=…]`) and CLASS 3 (bare `text=`) on the captain's
2026-07-25 ruling. Three classes survive and are what this entity gates:

| class | pattern | why it still breaks |
|---|---|---|
| CLASS 2 | `>> nth=N` | Playwright chord; on the `click`/`fill` path the raw value goes to `agent-browser` and does not resolve |
| CLASS 4 | `:has-text(` | broken in agent-browser, no equivalent, times out |
| CLASS 5 | `find role\|text\|label\|testid …` as a `selector:` value | a CLI subcommand chain, not selector grammar |

## Scope (captain / EM authored, not inferred)

Scope for this entity is not composed here. It is the EM `proceed` determination
recorded on issue #88 (2026-08-01,
[#88 comment](https://github.com/iamcxa/kc-claude-plugins/issues/88#issuecomment-5145878666)),
which the captain explicitly delegated ("D2 EM 已裁 proceed，不用你管"). Its five
conditions are carried into the ACs below verbatim in substance:

1. One shared policy module, not two implementations plus parity tests.
2. Hard-fail at compile/dry-run, **plus** the scoped/delta mode `docs/dev/ROADMAP.md`
   already writes into this sprint item ("including a scoped legacy migration path").
3. The baseline must not be regenerable by the thing it gates.
4. CLASS 3 enforcement must not return — it is retired, not deferred.
5. At least one AC is E2E-first: a fixture carrying each surviving banned class exits
   **before browser startup**, observed on the real CLI rather than a unit test
   asserting a validator returned false.

**Baseline file location — one decision taken rather than re-escalated.** The delta
baseline records real grandfathered violations, and the only real corpus lives in a
private consumer repo. Presented to the captain last session with a recommendation; the
reply was to proceed. Taken: **the baseline file lives in the consumer repo**
(`.claude/e2e/selector-baseline.tsv` by default, `--selector-baseline` to override); the
plugin defines the format and ships **synthetic** fixtures only. No consumer app's
violation inventory enters this public marketplace repo.

**Gate granularity — captain decision, pending.** See the next section; the ACs are
written against the recommended answer.

## Gate granularity — measured, and the alternative named on record

The ideation clause requires the simplest alternative be named and refused (Proof Policy
rule 4). The alternative to gating **every** `selector:` value in a loaded mapping is
gating **only the selectors a flow actually resolves**. It matters because whole-file
granularity is what forces the baseline contract into existence at all.

Measured against the real consumer corpus at `/Users/kent/Project/carlove/.claude/e2e`
(45 flows, 5 mappings), by running this plugin's own `parser.js` + `resolver.js` over
every flow and classifying every `selector` value in the resolved output
(`/tmp/measure-resolved-scope.js`, reproducible):

| scope | banned findings | unique records | blast radius on day one |
|---|---|---|---|
| mapping-file | **39** | 36 | 2 of 5 mappings — which reds *every* flow that loads them |
| flow-resolved | **≥3** | 3 | 2 of 45 flows |

The resolved number is a **floor, not an exact count**: 43 of 45 flows already carry
pre-existing resolve errors (`vehicle-brand-select.yaml` alone has 32), so element
references that never resolve were never classified. Those errors are corpus rot that
predates this entity; the floor is still the right decision input, because it can only
move up and the mapping-file number is fixed at 39.

Independently corroborating: the 4 compiled artifacts in that repo contain **zero**
`>> nth=` tokens, because `compiler/lib/selector-translate.js:93-95` silently strips the
chord on the visibility path. So the class survives by being invisible, and the flows it
actually reaches are few.

**Recommended: two severities, one policy table.**
- **Blocking — flow-resolved scope.** A banned selector on an element the flow resolves
  fails compile and dry-run. This is the defect the issue reports.
- **Warning — mapping-file scope.** Every other banned selector in a loaded mapping is
  printed with `path:line:class` on stderr, non-blocking. Latent rot stays visible
  instead of silently accumulating.
- The baseline applies to the **blocking** set only, so the corpus adopts 3 records
  rather than 36.

Refusal of the pure alternatives, on record: pure file-scope contradicts the issue's own
acceptance idea ("without requiring an unrelated whole-file migration") and multiplies
the migration by 12×; pure resolved-scope with no warning channel loses the visibility of
the other 36 findings entirely, which is the only reason file-scope was attractive.

## Appetite

**Estimate: 4 hours** implementation (one dispatch), plus validation. Revised up from 3
after the EM priced the unpriced part: threading `--selector-baseline` through
`bin → compile() → parse()`, whose signature is `parse(flowPath, mappingDir)` and which
has a separate cross-site multi-mapping branch.
**Tolerance: +50% (6 hours).** Past that the work stops and gets re-cut rather than
continuing — the re-cut is to land the blocking gate alone and defer the baseline to its
own entity.

## Fastest path / smallest cut, and which one is taken

- **Fastest path**: have the compiler shell out to `scripts/lint-mapping.sh` per mapping
  file. One process boundary, zero new policy code.
- **Smallest cut**: hard-fail only, no delta mode.
- **Simplest alternative to the whole baseline contract**: gate only resolved selectors —
  named, measured, and partially adopted above rather than refused.
- **Taken**: the policy moves **into** a Node module (`compiler/lib/selector-policy.js`)
  and `lint-mapping.sh` becomes a thin wrapper that execs it, preserving its exit codes
  and stderr shape. Shelling out to bash was refused because it makes the policy
  unavailable to the `--json` structured-error channel, puts a bash dependency on the Node
  compiler, and leaves the bash regexes as the sole implementation — a second consumer
  would still have to reimplement them to get structured findings.
- Delta mode is **not** cut: ROADMAP:169 scopes it into this sprint item, and even at the
  narrower resolved granularity the corpus still needs 3 grandfathered records, so
  hard-fail alone still reds a real repo on day one.

## Design determination — `design: required`

This decides a contract, not just behavior: a new CLI flag, a new on-disk file format
that consuming repos will commit, and a new module boundary two consumers read.

**Module.** `compiler/lib/selector-policy.js`, **core-Node only, zero dependencies**
(the linter must stay wireable into a consumer `.githooks` without `npm install`).
Exports:
- `BANNED_CLASSES` — **the single policy table**: `{id, label, pattern, guidance}` per class.
- `classifySelector(value)` → class id or `null`. Every consumer's decision about whether
  a string is banned goes through this one function.
- `scanMappingText(text, filePath)` → findings with **line numbers**, for the linter and
  the file-scope warning channel.
- `scanResolvedElements(elements)` → findings with **element identity**, for the blocking
  gate.
- `parseBaseline(text)` / `isGrandfathered(finding, baseline)`.

**Two traversals, one policy — stated plainly rather than claimed away.** The text scan
and the element scan are different code, because line numbers and element identity are
different facts and neither traversal can produce the other's. What is single-sited is
the *policy*: both call `classifySelector`, and `BANNED_CLASSES` appears once in the repo.
The bounded claim is therefore "one banned-class table, two traversals", not "one
implementation".

**Baseline format.** One record per line, tab-separated:

```
<mapping-file>\t<page>.<element>\t<class-id>\t<selector-value>
```

`#` comments and blank lines allowed; matching is exact on all four fields. Keyed by
**element identity**, not line number and not count — a line number churns the baseline on
every unrelated edit above it, while an element name is stable across formatting. This
closes the residual an earlier draft accepted: pasting the same banned selector onto a
*different* element is a new record and still fails. Measured relevance: the corpus
contains `role=switch >> nth=1` three times and one other banned string twice, so a
format keyed only by `(file, class, selector)` would have granted those strings a
permanent licence in files that `e2e-mapper` authors by pattern repetition.

**No regeneration by the gate.** The compile path contains **no write call** to the
baseline path — that is the enforcement point, and AC-4 tests it by byte-comparison. The
only producer is `scripts/lint-mapping.sh --format=baseline`, which prints records to
**stdout** and accepts no output path. To be explicit about what that does and does not
buy: an agent can redirect stdout in an inner loop exactly as easily as a person can, so
stdout-only does not enforce human authorship. What it buys is that adopting or widening a
baseline lands as a reviewable diff rather than as a side effect of a gate run.

## Reverse-recovery audit (against `origin/main` `1119387`, fetched 2026-08-01)

| layer | verdict | evidence |
|---|---|---|
| Policy definition | **WORKING** | `scripts/lint-mapping.sh:135-158` — three surviving classes, post-#123 |
| Policy as a reusable unit | **EXISTS_BROKEN** | it exists only as inline bash regexes inside the CLI script; no module, no export. Re-run over the corpus: 2 files exit 2, 39 findings, all `>>nth` — the regexes run, they are just not reusable |
| Compiler invocation of policy | **MISSING** | two-strategy grep above; `compiler/parser.js:388-401 validateMapping()` validates `version` and `pages` only |
| Chord handling in the compiler | **EXISTS_BROKEN** | `compiler/lib/selector-translate.js:93-95` silently strips `>> nth=N` on the visibility path, which is why CLASS 2 has been survivable and invisible — and why the compiled artifacts show zero chords. Narrowing that behavior is #124, not this entity |
| Diagnostics channel | **WORKING** | `compiler/compiler.js:54-64` already surfaces parse errors as `errorDetails` for `--json` |
| Delta / baseline mode | **MISSING** | `git grep -e selector-baseline -e selector-policy` — zero hits |
| Test fixtures for banned forms | **WORKING** | `test/fixtures/legacy-playwright-mapping.yaml` (must exit 2), `test/fixtures/native-css-mapping.yaml` (must exit 0) |

Single broken seam → repair scoped to that seam. The policy is not rebuilt; it is
**extracted** from the bash script and then wired to a second consumer.

**Enforcement facts read live**, not from `.github/`: required contexts come from
`gh api repos/iamcxa/kc-claude-plugins/branches/main/protection` at implementation time.
No job is renamed by this task.

## Spike

**No spike needed.** The three mechanisms relied on are all already proven in this repo:
`parser.js` accumulates and returns blocking errors before `resolve()` and `generate()`
run (`compiler.js:53-64`); `compiler/lib/` already hosts a shared module two call sites
read (`selector-translate.js`); and the banned-class regexes are the exact ones running in
`lint-mapping.sh` today with fixtures that pin both directions. The one previously
unpriced mechanism — resolved-scope classification — was not spiked but **measured**, by
running the real parser and resolver over the whole corpus (table above).

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is
**criteria that pass without delivering value**: the gate fires at compile, so a repo
whose findings are fully grandfathered gets a green compile forever, while the actual
generator of violations — `e2e-mapper` — keeps emitting them and nothing tells it.
Mitigation inside this scope: grandfathered findings and file-scope findings both print
on stderr every run, so a growing baseline is visible rather than absorbed. Closing the
generator side is #124's and the mapper's business.

**A second failure mode the EM found and this entity now owns naming:** the sprint's exit
condition is "invalid selectors fail before browser startup", and the *compiled* path is
not the only path to a browser. `e2e-test-runner`, `e2e-flow-verifier`, and the
walkthrough path are LLM-driven and read the mapping directly. This entity does not reach
them, and no existing entity owns them — #124 is the chord-narrowing question and #91 is
multi-match semantics. A backlog entity is filed for the runner-path remainder as part of
this stage rather than left as a bare out-of-scope line; **#88 alone does not close the
sprint exit condition**, and saying so here is the point.

## Acceptance criteria

**AC-1 — A mapping carrying a surviving banned class fails compile and dry-run**

The compiled artifact is not written, and the failure names mapping path, line, selector
key, banned class, and replacement guidance.
Verified by: `node bin/e2e-compile.js <flow> --mappings-dir <fixture-dir>` exits 1 with
those five fields on stderr and no `.sh` in the output dir; same for `--dry-run`; and the
`--json` document carries the class id in `errors[]`. RED evidence recorded first.
Falsifier: delete the policy call from `parser.js` `validateMapping()` and the case goes
green.

**AC-2 — The bash linter's verdicts are produced by the shared table, not its own copy**

Changing `BANNED_CLASSES` changes what `scripts/lint-mapping.sh` reports.
Verified by: a drift test that runs the linter against a fixture, then re-runs it against
a scratch copy of the plugin whose `BANNED_CLASSES` has one class removed, and asserts the
linter's findings changed accordingly — proving the bash consumer reads the module rather
than a private pattern.
Falsifier: reintroduce an inline regex for that class in `lint-mapping.sh` and the second
run still reports it, so the test goes red.
Bounded claim recorded in the docs: "one banned-class table, two traversals" — not "one
implementation" and not "no second table can exist", neither of which has an enforcement
point.

**AC-3 — A baseline grandfathers existing findings without hiding new ones**

An otherwise-blocking mapping compiles when every blocking finding is listed in the
baseline; a newly introduced violation still fails, and the failure names only the new
finding.
Verified by: fixture with 2 blocking findings + a baseline listing both → exit 0 with both
reported as grandfathered warnings on stderr; add a third violating selector → exit 1
naming only the third; and re-point an existing baselined selector string onto a second
element → exit 1, proving the record is keyed by element identity.
Falsifier: make `isGrandfathered` return true unconditionally and both negative cases go
green.

**AC-4 — The gate cannot regenerate its own baseline**

No compile-path invocation writes the baseline file, and the CLI exposes no flag that does.
Verified by: byte-compare the baseline file before and after a compile run over a
violating mapping; `e2e-compile --help` output contains no baseline-writing option; the
only producer is `lint-mapping.sh --format=baseline` writing to stdout with no output-path
argument.
Falsifier: add an `--update-baseline` flag that writes the file and the byte-compare test
goes red.

**AC-5 — A flow that compiles green today is refused, and the artifact a browser would have run is never produced**

Baseline that can move the wrong way: today `gate-smoke-all-pages.yaml` and
`vehicle-brand-select.yaml` resolve banned selectors (`role=combobox >> nth=0`,
`role=row >> nth=1 >> …`) and `bin/e2e-compile.js` writes their scripts with exit 0 —
0 of ≥3 resolved findings refused. End state: both are refused with exit 1 and no `.sh`
written; with the baseline adopted both compile again, and a hand-added violation on a
new element is refused.
Verified by (E2E, real runtime, not a unit test): a **differential** run of the real CLI —
the same flow and mapping bytes compiled at `origin/main` (exit 0, `.sh` written,
resolved element present in it) and at the branch head (exit 1, no `.sh`). Both runs'
exit codes and directory listings recorded as command output. The differential is what
makes this able to fail: an implementation that does not actually block produces two
identical runs.

## Test plan

1. `compiler/test/selector-policy.test.js` — per class: one violating and one clean
   selector; comment/description lines carrying a banned token are ignored (the PR #8 C2
   narrowing); quoted and unquoted YAML scalars; baseline parse/match; `#` comments;
   duplicate-string-on-a-different-element must not match a baseline record.
2. `compiler/test/selector-gate.test.js` — compile and dry-run against fixture mappings;
   asserts exit status, the five diagnostic fields, no output file, `--json` `errors[]`
   carrying the class id, and that a file-scope-only finding warns without blocking.
3. Drift test (AC-2) — bash consumer against a perturbed copy of the policy module.
4. `test/integration-smoke.sh` — unchanged expectations must still hold (it calls the
   linter directly; the wrapper preserves exit codes 0/1/2 and the `path:line: class:`
   stderr shape).
5. Full suite at stage exit. No version, marketplace, or SKILL.md frontmatter surface is
   touched, so `version-parity-check.sh` / `marketplace-verify.sh` /
   `skill-frontmatter-lint.sh` are not earned by this diff — stated so validation can
   check the classification rather than the checklist.

## Measurement

- Resolved-scope refusal rate on the real corpus: 0 of ≥3 today → ≥3 of ≥3 with no
  baseline; 0 of ≥3 with the baseline adopted, all reported as warnings.
- File-scope findings surfaced: 0 of 39 today → 39 of 39 as warnings.
- Policy definition sites: 2 (bash regexes + prose) → 1 table + prose that points at it.
- Diff coverage on the executable surface: bar 85%, measured on added/changed executable
  lines only. Prior gates in this repo have twice mis-derived this number by counting
  comment lines lcov emits `DA` records for — the denominator is executable lines, and
  numerator and denominator are reported separately.

## Doc diff (proposed here, applied in implementation, verified at validation)

- `e2e-pipeline/CLAUDE.md` § Selector Priority — "Enforcement lives in
  `scripts/lint-mapping.sh` (what's banned)" becomes "Enforcement lives in
  `compiler/lib/selector-policy.js` (the single banned-class table), invoked by
  `scripts/lint-mapping.sh` and by the compiler at parse time"; items 7/8/9's
  "BANNED — see `scripts/lint-mapping.sh`" pointers retarget to the module; the bounded
  claim "one banned-class table, two traversals" is stated where the absolute would be.
- `e2e-pipeline/docs/ci-integration.md` § Mapping Linter — compile and dry-run now enforce
  the same table; `--selector-baseline` and the baseline record format; the baseline is
  produced by `lint-mapping.sh --format=baseline` on stdout; and the linter's new
  prerequisite — it now requires `node` on PATH, where it was previously pure bash with
  zero dependencies and wireable into a `.githooks` without `npm install`.
- `e2e-pipeline/skills/e2e-compile/SKILL.md` — the new failure mode and its remedy.
- `e2e-pipeline/agents/e2e-mapper.md` — producer-side: emitting a banned form now fails
  the consumer's compile, not just its lint.
- `e2e-pipeline/CHANGELOG.md` is release-please-owned; not hand-edited.

## Implementation dispatch sizing

**One dispatch.** Three behaviors (policy module + linter delegation; compiler wiring;
baseline/delta mode) but they are sequentially dependent, not independent — 2 and 3 both
consume 1 — so splitting buys no parallel wall-clock and pays three cold starts.

**Implementation re-verifies before building** (README ideation clause): re-fetch
`origin/main`, re-run the corpus measurement, and report if 39 / ≥3 have moved. A premise
that has collapsed is escalated, not built around.

## Out of scope, with owners

- Narrowing the `>> nth=` chord ban to the interaction path — **#124**.
- Multi-match visibility semantics — **#91**.
- Migrating the grandfathered findings — the consumer repo, tracked by its own baseline diff.
- Any change to `selector-translate.js` translation behavior — **#124**.
- Enforcing the policy on the LLM-driven paths (`e2e-test-runner`, `e2e-flow-verifier`,
  walkthrough) — **no owner today; a backlog entity is filed by this stage.** Without it
  the sprint exit condition is not met by #88 alone.
- An element that declares `css_selector:` is still refused when its `selector:` carries a
  banned class. The mitigation applies to the click path only, while `selector:` still
  feeds the visibility path, so refusing is correct — recorded because it is surprising.

## Stage Report: ideation

**TL;DR** — #88's filed premise was retired by PR #123; three ban classes survive and
none is enforced anywhere the compiler can reach. This entity extracts the bash regexes
into a dependency-free `compiler/lib/selector-policy.js`, has `scripts/lint-mapping.sh`
exec that module instead of carrying its own patterns, calls it from `parser.js` so
compile and dry-run hard-fail before any artifact is written, and adds a delta baseline
(consumer-repo-owned, stdout-only producer, keyed by element identity) so real
grandfathered findings do not red a working repo on day one. Five ACs; AC-5 is the
E2E/value one and is a differential against `origin/main`, so an implementation that does
not actually block produces two identical runs and the AC fails. One dispatch, 4h
appetite, +50% tolerance. `design: required` — it decides a CLI flag, an on-disk format
consumers commit, and a module boundary two consumers read.

**Scope authorship** — not composed by the agent. Carried from the EM `proceed`
determination on issue #88 (2026-08-01), which the captain delegated explicitly. One
sub-decision (gate granularity) is escalated to the captain rather than taken here.

**Reverse-recovery** — one broken seam (policy exists but only as inline bash), repair
scoped to it. No greenfield.

**Pre-mortem** — criteria that pass without delivering value; plus the named gap that
#88 alone does not close the sprint exit condition, because the LLM-driven browser paths
are unreached.

**`--ac-scan`** — `spacedock status --read e2e-selector-compile-gate --ac-scan`: all five
ACs resolve; each reports `unevidenced=true` (expected at ideation) and `citations=0`,
which is the known-untrustworthy counter recorded in ROADMAP's "Hazard carried forward",
not a finding about the ACs.

**`dev-flow-work-context-check.py validate`** — re-run after this revision, since an edit
invalidates the prior receipt.

### Gate cycle 1 — EM verdict `narrow`, four conditions, all addressed

| # | EM finding | disposition |
|---|---|---|
| 1 | AC-2's parity test is tautological — both sides are one code path, so no edit can redden it | **Fixed.** AC-2 is now a *drift* test against a perturbed copy of the module; the "no second table exists" absolute is replaced by the bounded "one table, two traversals" |
| 2 | AC-5 measures refusal rate but is titled as value; the "no browser spawned" probe cannot fail because `e2e-compile` never spawns one | **Fixed.** AC-5 is now a differential against `origin/main` on two named real flows, with the written artifact as the observable |
| 3 | The baseline's no-count residual is ~13% of the real corpus (`role=switch >> nth=1` ×3) | **Fixed, and stronger than the proposed count-pinning.** Records are keyed by element identity, which is stable across formatting *and* refuses a re-paste onto a different element |
| 4 | The resolved-scope alternative was never named; it is what forces the baseline into existence | **Named, measured, partially adopted** — and the granularity change is escalated to the captain, per the EM's own routing |
| 5 (cond.) | Module must stay dependency-free; the linter's new Node prerequisite is undocumented | Adopted into the design and into the `ci-integration.md` doc diff |
| 6 (cond.) | AC-4's "human redirect" wording overclaims | Rewritten: the enforcement point is the absent write call; stdout-only buys a reviewable diff, not human authorship |
| 7 (cond.) | Implementation re-verifies corpus numbers against fresh `origin/main` | Written into the dispatch sizing section |
| NM | The translator's silent chord strip is missing from the audit | Added as a fifth audit row |
| NM | `css_selector:`-mitigated elements are still refused | Recorded in Out of scope with its reason |
| NM | Sprint exit is not met by #88 alone; the runner path has no owner | Recorded in the pre-mortem and Out of scope; a backlog entity is filed by this stage |
