---
title: Cutting prose from a skill has no failure signal — build one before cutting
status: backlog
product: kc-pr-flow
sprint: S4
source: precondition for the Sprint 4 slimming track, filed 2026-07-27 on captain direction
design: required
id: 5b5gp68f2aq0bdrcf3q28jgg
started: 2026-07-28T08:10:24Z
worktree:
---

The kit is going to be cut down before it is extended. The problem with that order is that
**prose has no test**. Delete a paragraph of instruction from `SKILL.md` and every one of the 935
assertions still passes, because they exercise the shell scripts, not the skill's wording. The one
exception proves the rule: `review-shadow.test.sh:56` extracts the block between
`# typed-interactive-recipe:start/end` and sources it, so that 415-line region is genuinely
protected — and nothing else is.

This was demonstrated the expensive way. A slimming proposal in this workflow targeted "544 lines
of example output" in Step 6; 415 of those lines were that executable adapter. The proposal read
as a clean subtraction and would have broken 213 assertions.

So: before any line is cut, there has to be a way to answer "did that change what the review
produces?" other than by reading the diff and feeling confident.

## What this is

The minimum A/B capability: run the same PR through two versions of the skill and diff the
outcome — findings emitted, their severities and file:line anchors, tokens, wall-clock.

## What this is not

It is not `review-effectiveness-benchmark` (62). That entity measures **how good the kit is** in
absolute terms, against pre-registered known defects, and needs ground truth. This one measures
**whether a change moved anything**, and needs no ground truth at all — the previous version is
the reference. It is the cheaper half and it is what unblocks cutting.

## The difficulty that has to be solved first

**A review is not deterministic.** The same PR through the same skill twice will not produce a
byte-identical finding set, so a naive diff reports every run as a regression. Ideation must
decide how to separate signal from noise, and the honest options each cost something:

- **Repeat and compare distributions** rather than single runs — more expensive, and it needs a
  stated threshold for "materially different" that is chosen before the first cut, not after.
- **Compare on stable projections only** — e.g. the set of `file:line` anchors touched, or the
  count per severity, discarding wording. Cheaper, and blind to a change that alters what a
  finding *says* without moving where it points.
- **Freeze what can be frozen** — a fixed PR corpus, pinned model, temperature/seed where the
  harness allows it. Reduces variance without eliminating it.

Whichever is chosen, the threshold is pre-registered. Choosing it after seeing a cut's result is
how a slimming pass talks itself into "that difference doesn't matter".

## Scope

Two skill versions, one frozen PR corpus, one comparison report. Reuses the corpus `62` will need,
so the corpus work is shared rather than duplicated — but this entity does not wait on `62`'s
ground-truth decision, which is the expensive part.

The acceptance criteria are stated once, under `## Acceptance criteria` below.

## Problem

The sprint cuts before it extends, and **prose has no test**. Deleting instruction text from
`SKILL.md` leaves all 935 assertions green, because they exercise the shell scripts, not the
skill's wording. The captain's framing: "Subtraction needs more evidence than addition, not less.
The only protected region is the 415-line adapter that `review-shadow.test.sh:56` extracts by
sentinel (`# typed-interactive-recipe:start/end`) and sources." Everything else is unguarded.

The near-miss this exists to prevent already happened: a slimming draft proposed cutting "544 lines
of example output" from Step 6, of which 415 were that executable adapter. "It read as a clean
subtraction and would have broken 213 assertions. Classify before cutting; a fenced block is not
automatically an example."

So `5b` is item 0: "`5b` exists to fix that asymmetry, so it is item 0 and nothing else in the
sprint can be judged until it works." Downstream consumers, in order: `tm` (remove restatements of
Steps 5/6, `SKILL.md:1844+`), `fa` (~104 presentation lines → renderer), `sk` (three whole-file
reference reads → named sections). Sprint item 4 (overconstrained-rule audit) is filed only if this
harness proves able to measure that class.

This is **not** `62` (review-effectiveness-benchmark). `62` measures how good the kit is in absolute
terms against pre-registered known defects and needs ground truth. `5b` measures *whether a change
moved anything* and needs no ground truth — the previous version is the reference. `5b` does not
wait on `62`.

## Reverse-recovery audit

Layer-traced against the merge target (`origin/main` = `f4f4840`, fetched; working branch is at the
same SHA). Verdict up front: **not greenfield.** The scoring vocabulary exists and is reusable; the
driver, the corpus, and the materiality verdict are the missing seams.

| Seam | Verdict | Evidence |
|---|---|---|
| Skill-version arming (two skill trees, one ablated) | MISSING (thin) | No repo code does this. Mechanism proven available and exercised — see Spike. |
| Review driver (headless run producing an outcome) | MISSING | `review-runtime.sh:2-6` disclaims owning "review verdict, confirmation, authorization, posting, GitHub" behavior; no `claude`/`codex`/`agy`/`gh pr` invocation in it. `review-runtime-benchmark.sh:258` hardcodes `model_calls:0,remote_calls:0` and its promotion gate *requires* `.model_calls == 0 and .remote_calls == 0` (`:615-616`) — the existing benchmark is by its own schema a no-model scorer. Nothing in `kc-pr-flow/` drives a model. |
| Receipt schema (findings + usage) | WORKING_UNIT_UNPROVEN | `SKILL.md:1224-1231` already defines `kc-pr-flow.shadow-observation/v1` carrying per-lane `usage{input_tokens,output_tokens,total_tokens,...}` and `candidates[]{ordinal,path,side,anchor_sha256,category,claim_key,evidence}` — exactly the right shape. |
| Receipt *collection path* | EXISTS_BROKEN | That schema is gated behind `KC_PR_FLOW_REVIEW_SHADOW=on` (`SKILL.md:1150`) and written to an agent-chosen `0600` temp file (`SKILL.md:1223`). No stable, discoverable path a driver can collect. The break is the path, not the schema. |
| Stable-projection / fingerprint canonicalization | WORKING | `review_benchmark_fingerprint_id` (`review-runtime-benchmark.sh:451`) and `review_benchmark_candidate_id` (`:456`) canonicalize `{path,side,anchor_sha256,evidence_sha256,category,claim_key}` into stable IDs; `review_benchmark_validate_authority` (`:434-472`) recomputes them. This is the projection the seed asked for, already built. Reuse it — do not reimplement (Proof Policy #4). |
| Set comparator | WORKING, wired to the wrong verdict | `stability($pair)` (`:816-836`) already computes `common_finding_ids` / `baseline_only_finding_ids` / `shadow_only_finding_ids` via `intersection`/`difference` (`:787-790`). That *is* the A/B diff. It is currently reported, never judged. |
| Materiality verdict | EXISTS_BROKEN | The function that actually judges parity is `behavior_parity()` (`:807-815`) — exact SHA-256 equality over `body_sha256`/`event_sha256`/`payload_sha256` — and promotion gate g3 demands `matches == true` (`:654-656`). Against two nondeterministic review runs this fails every time: it is precisely the "naive diff reports every run as a regression" failure the seed predicted, already shipped. The only numeric bars present (`>=20` percent token reduction `:680`, `<=60` percent cost `:690`) are hardcoded and about cost, not finding divergence. |
| Frozen PR corpus | MISSING | Fixtures are synthetic — `repository: "acme/widgets"`, `pr_number: 42`, all-`a`/`b` hex SHAs in `test/fixtures/review-runtime/paired-runs.jsonl`. Searched for a frozen real-PR list across `kc-pr-flow/`; the only `pull/N` hits are documentation examples (`SKILL.md:100`, `reference/linear-integration.md:44`). |
| Per-run token/cost accounting | MISSING in repo, available from runtime | `claude --output-format json` returns `usage{input_tokens,output_tokens,cache_creation_input_tokens,cache_read_input_tokens}` and `total_cost_usd`. Observed directly in the spike. |
| Skill-version awareness anywhere in the stack | MISSING | No `SKILL.md` / `skill_version` / `prompt_version` reference in `review-runtime-benchmark.sh` or its test. `baseline` vs `shadow` are two *runtime code paths*, not two prompt versions. |

**Correction to an inherited claim** (Proof Policy #6, last clause — measure before adopting, and
say which). The sprint directive and the seed both cite the pre-emit quote gate as `SKILL.md:973`.
Verified: `:973` is the `### 6a. Inline Comments (CODE)` heading. The gate itself spans
**`:975-984`** (`**Pre-emit verification gate (run FIRST …)**` at `:975`, its failure-class table at
`:977-982`, its demotion rule at `:984`). More consequentially, the same rule is **restated at
`:1855`** in the Step-6 recap. An ablation that removes only `:975-984` leaves `:1855` still
instructing the gate — so AC-2 could fail for a reason unrelated to the harness. The ablation must
cut both sites, and the arm-builder must assert the removal took effect at both. This also sharpens
`tm`: those recap restatements at `:1844+` are load-bearing duplicates, not free prose.

Round 1 stopped at those two sites and that was still incomplete, and round 2's enumeration stopped
at a file boundary — the full tree-wide enumeration is under `### The AC-2 ablation` below.

### The AC-2 ablation — every site across the loaded surface, cut or keep

**The captain ruled AC-2 is a real full-site removal (option a), not an injection control.** The
deciding argument is the direction of the operation: this workflow's thesis is "subtraction needs
more evidence than addition", every Sprint 4 cut is a removal, and certifying a removal-detector
with an addition is a category mismatch. Also `sk` cuts reference-file *loading*, so an instrument
validated only against `SKILL.md` could not judge it.

**Scope: the whole `kc-pr-flow/` tree, not one file.** Round 2's defect was an enumeration that
stopped at `SKILL.md`, which left arm B cutting the gate from the collator while every dispatched
reviewer still received it verbatim from `reference/review-triage.md`. Enumerated by a tree-wide
sweep at `origin/main` = `f4f4840` (`kc-pr-flow/` is byte-identical at `1ca0ed0`, verified by
`git diff --stat f4f4840 HEAD -- kc-pr-flow/` returning empty), then every hit read in context.

The sweep ran three ways rather than one, because a keyword sweep is the instrument this section
exists to distrust: (1) the four gate keywords across every file type in the tree; (2) a bare
`quot` sweep, to catch restatements that never use the project's vocabulary; (3) a phrase sweep for
the gate's *semantics* without its name — `motivating line`, `verbatim source`, `self-refut`,
`self-check`, `confidence to 4-5`, `adversarial fan-out`, `before you report`, `zero extra agent`.

| id | Site | What it is | Disposition |
|---|---|---|---|
| S1 | `SKILL.md:975` | `**Pre-emit verification gate (run FIRST …)**` + the rule paragraph | **CUT** — the gate proper |
| S2 | `SKILL.md:977-982` | the failure-class table (what must be quoted, self-refutes when) | **CUT** — the gate's operative content; leaving it leaves the instruction |
| S3 | `SKILL.md:984` | the demotion rule (cannot quote a surviving line → confidence 4-5 → §6b) | **CUT** — the gate's consequence |
| S4 | `SKILL.md:986` | **Framework-meta nudge** — "quote the meta-construct, not the class body" | **CUT** — a sub-rule; surviving, it re-instructs quote-the-source for the largest FP subclass |
| S5 | `SKILL.md:988` | "This gate is **inline, zero extra agents**…" | **CUT** — dangling referent once S1 is gone, and it re-asserts the gate's existence |
| S6 | `SKILL.md:990` | "Apply confidence gates **after the verification gate**" | **EDIT, not cut** — delete only the substring ` after the verification gate`, keeping `**Apply confidence gates**`. Cutting confidence gates outright would ablate a second, independent mechanism and confound AC-2 |
| S7 | `SKILL.md:861-862` | §5.6a arbitration — "(reuse the **§6a quote-the-line evidence** — arbitrate on quoted code, not summaries)" | **CUT the parenthetical only** — instructs quote-the-line from the cross-model arbitration path |
| S8 | `SKILL.md:1855` | Step-6 recap — "**Pre-emit verification gate before posting** — every CODE finding must quote its motivating `file:line` + verbatim source…" | **CUT** — the recap restatement |
| S9 | `review-triage.md:221` | heading, verbatim: "**Pre-emit evidence requirement (append to every agent prompt):**" | **CUT** — names the append-to-every-prompt contract |
| S10 | `review-triage.md:223-227` | the blockquote that contract appends: the same gate, the same failure classes, the same 4-5 demotion | **CUT** — **the site that made round 2's arm B measure almost nothing.** `SKILL.md:195` loads this file on the ordinary path, so it is in the loaded context of every run |
| S11 | `learned-patterns.md:13-15` | "Pre-emit quote-the-line gate beats per-finding adversarial fan-out" — a third restatement as a named learned pattern | **CUT** — and it is the citation target of both S5 and S8 |
| K1 | `SKILL.md:143` | "Step 2.5 builds a **verification gate** from explicit concerns" | **KEEP** — a *different* mechanism (Step 2.5's user-concern gate). A naive `verification gate` grep would cut it and ablate two mechanisms at once |
| K2 | `review-triage.md:229-236` | the collator's confidence → destination table | **KEEP** — the same mechanism S6 deliberately preserves. Cutting it would ablate a second independent mechanism and confound AC-2 |
| K3 | `learned-patterns.md:9-11` | "Cross-model arbitration: reconcile by source-set, fail open, **never per-finding**" | **KEEP** — a different pattern (arbitration shape), and a naming hazard exactly like K1: a canary widened to `per-finding` or `fan-out` would cut it |

**Two things the sweep found that the round-3 dispatch's table did not name**, both recorded because
a sweep that only confirms what it was told is not a sweep:

- **K3 is a new KEEP.** `learned-patterns.md:9-11` carries "never per-finding" for the *arbitration*
  mechanism. It is the same trap as K1 one file over: the obvious widening of the canary (add
  `fan-out` or `per-finding`, since S5/S8/S11 all use those words) would silently ablate cross-model
  arbitration along with the quote gate. Enumerating it as an explicit KEEP is what stops that.
- **S11's file is not loaded on the ordinary path, and the effect model must not assume it is.**
  There is no `Read → ${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` directive anywhere in
  `SKILL.md`; `:1834` writes *to* it (D1 auto-append) and `:988`/`:1855` cite it as a "see". So S11
  is a real restatement and worth cutting — it is the citation target the two surviving pointers
  aim at — but unlike S10 it is not guaranteed to be in any given run's context. The honest
  statement is that the ablation's effect rests on S1-S10, with S11 additive when the run follows
  the pointer.

The sweep found **no additional CUT site** in `agents/`, `scripts/`, `docs/`, `hooks/`,
`reference/pr-review-loop.md`, or the other five skills. The nearest misses were read and rejected:
`SKILL.md:677` and `:714` require quoted evidence for *doc-claim* and *lint-rule* findings (Steps
4.5j / 4.5k, different mechanisms), and `break-point-probe`'s precision ladder is an evidence
discipline for a different skill entirely.

#### Arm-builder post-condition — verbatim span match, with the keyword grep demoted to a canary

Round 2's post-condition asserted "zero residual hits" for the four keyword patterns. That proof is
unsound, and unsound in this sprint's founding way — it classifies a region by pattern instead of by
reading it. **Measured, not argued:** of the 11 CUT spans, **4 are invisible to the keyword grep** —
S2, S3, S4, S10 — because none of those spans contains `pre-emit`, `quote-the-line`, `§6a quote`, or
`verification gate`. An arm that removed only the 7 keyword-bearing spans would leave the gate's
failure-class table, its demotion rule, its framework-meta sub-rule, and the entire per-agent
instruction blockquote on disk, and the keyword post-condition would report it clean.

The proof is therefore **verbatim span match, table-driven**. At build time the builder MUST:

1. **Resolve** each enumerated span from the *baseline* tree by its line range, and check the
   sha256 of the extracted text against a pinned sidecar. A drifted file fails here — this is what
   keeps the table above from going stale silently, which was the original reason for deriving at
   build time rather than reading the table.
2. Assert the baseline hit set is **non-empty**, and record the resolved span set + hashes into the
   arm manifest (this is what `arm_manifest_sha256` commits).
3. Apply the ablation. A removal whose target text is not present exactly once exits non-zero — the
   sprint's own silent-no-op failure, encoded.
4. **Assert, per span, against the enumerated spec:** every CUT span's exact text is present in the
   baseline and **absent** in arm B; every KEEP span's exact text is present and byte-identical in
   both; and S6's surviving half (`**Apply confidence gates**`) is still there.
5. Run the keyword grep as a **canary, not the proof**: a residual keyword hit outside the K1
   whitelist means the table missed a site, and fails the build. A *clean* canary proves nothing on
   its own.

**The span set checked in step 4 is the enumerated spec, never the set the builder happened to
apply.** Checking only what was applied is a check that cannot fail — it asks the builder to grade
its own homework, which is the same defect shape as proving absence by the keywords you chose to
grep for. This is not a hypothetical: the first draft of the demonstration script below made exactly
that mistake, and its own must-fail case is what caught it.

**Demonstrated, not asserted** (Proof Policy #7). `docs/dev/artifacts/skill-ablation-harness/span-match-demo.py`
builds both arms from the real tree and runs both post-conditions against both. Output:

| arm | keyword-grep post-condition | span-match post-condition |
|---|---|---|
| `arm_keyword` — only the 7 keyword-bearing spans removed | **PASS** | **FAIL** — S2, S3, S4, S10 still present |
| `arm_span` — all 11 CUT spans removed | PASS | PASS |

Plus a fourth case so the KEEP half is not vacuous: an arm that ablates correctly *and* removes K2
is rejected by span match. The script exits non-zero if any of the four claims stops holding, so it
is the regression test for this defect rather than a one-time note. It is stdlib-only Python; `jq`
and Python 3.8+ are already `kc-pr-flow` runtime dependencies (`review-runtime-safe-io.py`), so the
production `review-ablation.sh arm` inherits no new one.

## Proposed approach

Three seams to build, in order. Everything else is reuse.

**1. Arm builder.** Copy `kc-pr-flow/` to a temp tree per arm; apply the arm's ablation across every
file the spec names (`skills/kc-pr-review/SKILL.md`, `reference/review-triage.md`,
`reference/learned-patterns.md`); **assert the patch changed the files** (byte diff against
baseline, plus the verbatim span-match post-condition of `### The AC-2 ablation` — every CUT span
absent, every KEEP span byte-identical) before the arm is usable. Proof Policy #7 in its literal form: an adversarial edit must first prove it took
effect. The sprint has already paid for a spot-check edit whose target string did not exist.

Three arms are built per experiment. **A′ is a second, independently built copy of arm A** — same
baseline tree, empty ablation — so the A/A comparison exercises the whole path (build, run, collect,
compare) twice rather than comparing arm A against itself. `skill_sha256` is required to be equal
across A and A′ and required to differ between A and B; both checks are made by `compare` from the
mode it was invoked with.

**2. Driver.** One headless review per run: `claude -p <driver-prompt> --plugin-dir <arm-tree>
--model <pinned> --output-format json`, from a pristine clone at a pinned base SHA. The driver
prompt imposes constraints that override the skill: never post to GitHub, never modify the tree
except the receipt, never launch background work and defer on it, and **stop at the end of Step 6a
and serialize, as JSON, the findings the skill's own flow approved for emission.**

**The driver prompt must be ablation-neutral by construction.** Round 1's version said "the findings
that passed the pre-emit gate" — which names the very mechanism arm B has had deleted, re-instructing
arm B to run it and letting the instrument manufacture the null it is supposed to test. The design
rule that replaces it: *the driver prompt names no mechanism that any arm ablates, and no mechanism
internal to the skill at all — it names only the stopping point (end of Step 6a), the output shape,
and the safety constraints.* Enforcement: the driver prompt is a single fixed file, byte-identical
across arms, and its SHA-256 is pinned into every receipt (`driver_prompt_sha256`), so a verdict
built from receipts with two different driver hashes is rejected rather than reported.

`--output-format json` yields the run's usage and cost; the receipt yields the findings. Both go into
one per-run record. A run whose receipt is missing or unparseable is FAILED — never an empty finding
set (see Spike 2).

**3. Comparator + verdict.** Reuse `review_benchmark_fingerprint_id` / `review_benchmark_candidate_id`
to canonicalize each run's findings into a fingerprint set, then apply the pre-registered decision
rule below. This *replaces* `behavior_parity()`'s exact-hash equality for this use; it does not
change that function, which stays correct for its own runtime-parity purpose.

### Which of the seed's three options, and what each costs

- **Freeze what can be frozen** — adopted fully. Fixed PR corpus at pinned base/head SHAs, pinned
  model, pinned plugin tree except the ablation, pristine clone per run. Costs nothing and removes
  the variance that is not the model's.
- **Compare on stable projections only** — adopted as the *primary* statistic: the candidate
  fingerprint set (`path` + `side` + `anchor_sha256` + `category` + `claim_key`), discarding
  wording. This buys reuse of an already-authored canonicalization and immunity to prose churn. It
  goes blind to a cut that changes what a finding *says* while leaving where it points unmoved.
  Mitigated, not solved, by two secondary dimensions carried in the same verdict: per-severity
  counts, and total tokens per run.
- **Repeat and compare distributions** — adopted at **N=3 runs per arm**. N=1 makes the noise model
  unmeasurable and any observed diff unfalsifiable; N=2 is the smallest N that yields a within-arm
  agreement at all, but it was measured underpowered (see the power table below) and N=3 is the
  smallest N that clears the α=0.05 bar with headroom.

### Pre-registered materiality rule — fixed now, before any cut

**Sizing: N=3 runs per arm, M=3 corpus PRs, and one experiment with three arms.** Derived from the
floor and the power measurement below, not assumed.

**One experiment, three arms — A, A′, B.** A single `experiment_id` covers all 27 runs (3 arms × 3
runs × 3 PRs). Arm A′ is a byte-identical second build of arm A; arm B carries the ablation. AC-1
compares **A vs A′**, AC-2 compares **A vs B**, and both read the *same* arm-A receipts. The
comparison mode is therefore a property of the `compare` invocation (`--mode AA` / `--mode AB`), not
of a receipt: `compare --mode AA --arms A,A_prime` and `compare --mode AB --arms A,B` consume one
27-receipt set and echo the mode into their verdicts. Round 1 put `mode` inside the receipt, which
forced arm A's nine receipts to exist twice under two `experiment_id`s — 36 runs (~$91) — and the
duplicate copies are exactly what AC-3(d)'s duplicate guard is built to reject. Moving `mode` out
holds the acceptance at **27 runs / ~$68**.

Per PR *p*, arm *X*, run *i*: `F(p,X,i)` = the set of candidate fingerprint IDs from that run.

- Within-arm agreement `J_within(p,X)` = mean Jaccard over the C(N,2)=3 within-arm run pairs.
- Between-arm agreement `J_between(p)` = mean Jaccard over the N²=9 cross pairs `(A,i)×(B,j)`.
- Per-PR effect `D(p)` = mean(`J_within(p,A)`, `J_within(p,B)`) − `J_between(p)`.
- **Combined statistic `T` = mean of `|D(p)|` over the M corpus PRs.**

Jaccard of two empty sets is defined as 1.

`T` takes the absolute value **per PR, before averaging**. That is the fix for a defect this
pre-registration shipped in round 1: the round-1 statistic was the signed mean `S = mean D(p)`
tested against an upper tail only, so an ablation whose effect ran negative — between-arm agreement
*exceeding* within-arm agreement — could not be flagged however large it got. `T` is non-negative
and a change in either direction raises it.

**Decision rule.** Exact permutation test on run labels, permuted independently within each PR.
Each PR contributes 2N=6 runs; there are C(6,3)=20 relabelings per PR, so 20^M assignments in total.
`p_perm` = the fraction of assignments whose recomputed `T` is ≥ `T_observed`, at α = 0.05.

This is the rule for **one dimension**. `anchor_set` is one of three the verdict measures, and
combining three α-level tests by OR leaves the family-wise rate uncalibrated — so the verdict's
`material` bit is decided by a single **joint max-statistic** permutation over the same assignment
space, defined under `### Design determination`. Everything below in this section — the floor, the
worked cases, the sizing — is unchanged by that, because the joint rule permutes the same labels and
inherits the same floor.

**The attainable floor, and why round 1's was wrong by 8×.** `D(p)` is invariant under swapping the
A/B labels within a PR — the swap exchanges `J_within(p,A)` with `J_within(p,B)`, leaving their mean
unchanged, and leaves the cross-pair set identical. So each distinct value of `D(p)` is achieved by
2 of the C(2N,N) relabelings, and the smallest achievable `p_perm` is

    floor = (2 / C(2N,N))^M

Round 1 stated `1/6^M` = 1/216 at N=2/M=3, ignoring that invariance. The true floor there is
`(2/6)^3` = **1/27 ≈ 0.037** — one notch under α, not "resolution to spare". At the adopted
**N=3/M=3** the floor is `(2/20)^3` = **1/1000 = 0.001**.

**Worked verification — a case it must flag and a case it must not** (Proof Policy #7). Enumerated
exactly, in exact rational arithmetic, over the full assignment space:

| Case | N/M | assignments | `T_obs` | `p_perm` | verdict |
|---|---|---|---|---|---|
| Arms disjoint, perfect within-arm agreement | 2/3 | 216 | 1 | **1/27 = 0.0370** | material — and it *is* the floor, confirming the derivation |
| Same, at the adopted sizing | 3/3 | 8000 | 1 | **1/1000 = 0.0010** | material |
| Arm B a consistent superset of arm A (`A={x,y}`, `B={x,y,z}`) | 2/3 | 216 | 1/3 | **0.0370** | material |
| Arms identical (same fingerprint set every run) | 2/3 | 216 | 0 | **1.0000** | not material |

The identical row is the "it can also not fire" half; the disjoint and superset rows are the "it can
fire" half. A statistic that always fired would not reach `p_perm` = 1 on the identical row, and an
inverted one would show `p_perm` ≈ 1 on the disjoint row. Every row is exact enumeration over the
full assignment space, reproduced by the committed simulation (`sizing-simulation.py`, section
*Worked verification, anchor-set statistic*). The A/A calibration rows that stood here in round 1
moved to the joint-rule verification under `### Design determination`, because calibration is a
property of the decision rule and the decision rule is no longer this single statistic.

**Why N=3, measured rather than argued — and now reproducible.** The simulation is committed at
`docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py` (stdlib-only Python, `SEED =
20260728`, all parameters at the top of the file: stable core 6 findings/PR, noise pool 6 sampled
independently at q=0.5, AC-2-shaped effect = arm B emits 3 extra findings per run, 200 A/A trials,
60 power trials). Round 1's figures were produced by an ad-hoc script that was never committed, so
nobody else could recompute them; the table below is what the committed script prints, and it
supersedes them. Power is of **the joint decision rule** (`### Design determination`), which is what
actually decides `material`, at α=0.05:

| sizing | floor | power on the AC-2-shaped effect | acceptance runs | cost |
|---|---|---|---|---|
| N=2 / M=3 (round 1 sizing) | 0.037 | **26/60 = 0.43** (Wilson 0.32–0.56) | 18 | ~$46 |
| N=2 / M=4 | 0.012 | 43/60 = 0.72 (Wilson 0.59–0.81) | 24 | ~$61 |
| **N=3 / M=3 (adopted)** | **0.001** | **60/60** (Wilson **0.94–1.00**), median `p_joint` = 0.001 | **27** | **~$68** |

Round 1 recorded 0.40 / 0.83 / 1.00 for these three cells. The re-run gives 0.43 / 0.72 / 60-of-60;
the two middle figures differ because the simulations are not the same one, and the ordering — which
is the only thing the sizing decision rests on — is unchanged. **The adopted cell is stated as
60/60 observed with a Wilson interval of ~0.94–1.00, not as a known 1.00.** Sixty trials cannot
establish a power of exactly 1; they establish that the true power is very unlikely to be below 0.94
*under this run model*.

At N=2/M=3 AC-2 was close to a coin flip: the design would have failed more often than not for want
of power, not for want of an effect, and the harness would have been declared unable to see a gate
removal it can in fact see. N=2/M=4 clears the bar but needs a 4th corpus PR sourced and pilot-run;
N=3/M=3 reuses the corpus already scoped and costs $7 more. Adopted: **N=3 / M=3**.

**The effect the sizing was chosen against, restated for the treatment that is actually shipping.**
`EFFECT_EXTRA_FINDINGS = 3` was written when arm B was a single-file ablation. Under the captain's
option (a) the treatment spans three files and eleven spans, including `review-triage.md:223-227`,
which is appended to *every dispatched reviewer's* prompt — so the plausible effect is larger, not
smaller. Rather than assert that a larger effect is safely covered, the power curve was measured
(`sizing-simulation.py --power-curve` path, same seed, 60 trials per point, N=3/M=3, α=0.05):

| effect | power of the joint rule | median `p_joint` |
|---|---|---|
| +1 finding/run | **20/60 = 0.33** (Wilson 0.23–0.46) | 0.1125 |
| +2 findings/run | 59/60 = 0.98 (Wilson 0.91–1.00) | 0.0010 |
| +3 findings/run (the sizing model) | 60/60 (Wilson 0.94–1.00) | 0.0010 |
| +4 / +6 / +9 findings/run | 60/60 each | 0.0010 |

Two things this settles, neither of them by argument. **The sizing decision does not move**: power
is flat at the ceiling from +2 upward, so a treatment larger than the model assumed is covered by
the adopted cell — N=3/M=3 was not chosen on a fragile point estimate. And **the detection knee sits
between +1 and +2 findings per run**, which is the number the residual below needed: a cut worth one
extra finding per run is missed about two times in three. That is what "does not transfer to a small
cut" means quantitatively, under this run model.

**What the simulation is not.** The figures come from a Monte-Carlo model of the run process —
a stable core plus independently sampled noise — not from real review runs. Two consequences, both
against this design's interest:

- **The real noise is plausibly larger and more correlated than the model.** A kc-pr-review run
  dispatches multiple agents, reads tool results whose content varies, can switch strategy wholesale
  between runs, and rides a provider whose serving stack drifts. Independent per-finding Bernoulli
  noise around a fixed core is the friendly case. If the real within-arm agreement is lower or the
  run-to-run variation more structured, **AC-2's power at N=3/M=3 is lower than 60/60 suggests**,
  and N=3 may itself prove short.
- **A single AC-1 pass is a negative control, not a calibration measurement.** One A/A comparison
  returning `material: false` is one draw from a distribution that should reject about 5% of the
  time. It shows the instrument does not fire on nothing; it does **not** establish that the real
  false-positive rate is ≈ 0.05. Establishing that would need tens of A/A comparisons, which is not
  affordable and is not proposed.

The simulation sizes the design; AC-1 tests the real noise process against the rule.

This pre-registers a *decision procedure* with exactly one free parameter (α = 0.05), fixed here.
There is no magic similarity number that a later result could renegotiate — which is the specific
way "a slimming pass talks itself into 'that difference doesn't matter'".

The rule is not circular against AC-1. Under A/A there is no true effect, so `p_joint` ≤ 0.05 should
occur at about rate α. AC-1 can genuinely fail: if within-arm agreement is systematically higher
than between-arm agreement for a reason that is not the skill — sequential drift, cache warming,
time-of-day model variation — A/A reports "material" and the harness is measuring its own
scheduling. That is exactly the failure AC-1 exists to catch. Mitigation baked into the design: the
27 runs of an experiment are **interleaved across the three arms, and the arm-to-slot assignment
within each PR is randomized and recorded per run** — interleaving alone fixes an ordering, which is
a weaker guarantee than exchangeability, and the permutation test assumes exchangeability.

**Corpus precondition (guards the degenerate pass).** Each corpus PR must yield ≥1 posted-tier
finding in a pilot run, or it is replaced. Without this, an all-empty corpus makes every Jaccard 1,
`T`=0, and *both* ACs pass on a harness that measures nothing.

### Cost — the number this gate should be judged on

One verdict compares two arms = **2 arms × 3 runs × 3 PRs = 18 headless kc-pr-review runs.**

Measured, not assumed — one real headless run against a real PR was executed in the spike:
**$2.53, 7.6 minutes, 5.21M raw tokens (~141K uncached).** So one verdict is **~$46 and ~2.3 hours
of unattended compute**. The acceptance needs two verdicts, and the three-arm design is what keeps
that from doubling: one experiment builds **A, A′, B** — 3 arms × 3 runs × 3 PRs = **27 runs, ~$68**
— and arm A's 9 runs are read by both the A-vs-A′ verdict (AC-1) and the A-vs-B verdict (AC-2). Two
separate 18-run experiments would be 36 runs (~$91) and would put arm A's receipts on disk twice,
which AC-3(d) rejects as duplicates. Full reconciliation of the raw-vs-uncached token figures — and
why the workflow's earlier ~140K estimate is consistent with 5.21M — is in the Spike section.

The consequence is a scoping fact, not a footnote: **this harness is a few-times-per-sprint
instrument for load-bearing cuts, not a per-cut gate.** A cut that is obviously mechanical
(dead link, duplicated heading) does not buy a verdict; a cut to instruction text that could change
what the review flags does.

The replay alternative was considered and rejected on the merits. Replaying recorded receipts costs
near-zero and is what the existing benchmark already does — but a replay cannot observe a prose cut
changing model behavior *at all*, because no model runs. It would make the harness structurally
incapable of satisfying AC-2 for the purpose AC-2 exists to serve. The cheap option here buys
nothing.

### What this harness can and cannot detect

**Can detect** — cuts that move which code the review flags (the anchor set): the pre-emit quote
gate, triage/confidence rules, the agent dispatch list. Cuts that move cost (token totals): `fa`'s
presentation lines, `sk`'s whole-file reference reads. Cuts that move the severity distribution.
This covers the Sprint 4 majority.

**Cannot detect** — a cut that changes only a finding's *wording* while its anchor and `claim_key`
hold; this is the acknowledged price of the stable-projection choice, and it is the risk class
closest to `tm`. Behavior on PR shapes absent from a 3-PR corpus (no security-tier PR means the
`tob-*` instructions are unmeasured). Any effect too small to reach `p_joint` ≤ 0.05 at N=3/M=3 — a
cut that moves one finding on one PR will not clear the bar. The measured example of "too small":
an arm-B superset that adds one finding to each run but only in the *noisy* regime (`|D(p)|` ≈ 0.08)
does not reach the bar at either sizing; the same superset applied consistently (`|D(p)|` = 0.33)
clears it at both.

**An AC-2 pass does not transfer to `tm`, and this residual travels with the artifact.** Option (a)'s
ablation spans three files and eleven spans, so its effect is large — the measured power curve above
is at the ceiling from +2 findings/run upward. **A passing AC-2 therefore certifies that the
instrument detects a large multi-site removal; it does not establish sensitivity to a small one.**
The knee is between +1 and +2 findings per run: a cut worth one extra finding per run is missed
about two times in three. Sprint 4's first actual customer, `tm`, removes restatements that may be
both small *and* inside the fingerprint projection's known blind spot (wording changed, anchor
unmoved) — two independent reasons the transfer fails. So `tm` carries its own complementary check,
or records acceptance of this residual at its own gate; it may not cite `5b`'s AC-2 as cover. This
sentence is carried in the verdict's `certifies` field and in the `kc-pr-flow/CLAUDE.md` doc diff,
so it travels with the artifact rather than living only in this document.

**Option (b), the injection arm, is retained as a diagnostic fallback — not pre-paid.** The captain
ruled (a) for AC-2. (b)'s real strength (single-sited by construction, so the missed-site class
cannot recur) was answered at the root instead, by moving the absence proof from keyword grep to
verbatim span match. No runs are budgeted for (b). Its trigger is specific: **if AC-2 under (a)
reports `material: false`**, build an injection arm then — it is what distinguishes "the harness is
blind" from "the ablation did not take", which the (a) result alone cannot separate.

**Sprint item 4 (overconstrained-rule audit) is in-class, conditionally.** An overconstrained rule
that fires too often produces *extra* findings, which moves the anchor set — detectable, *provided*
the corpus contains a PR that trips the rule. So item 4 is supportable, and its filing should be
conditioned on corpus selection rather than on the harness alone.

## Design determination

`required`. Two interfaces are being fixed and both are contracts other work will build on.

**Receipt contract** (driver → comparator), one JSON object per run:

```json
{"schema": "kc-pr-flow.ablation-run/v3",
 "arm": "A|A_prime|B", "run_index": 1, "slot_index": 0, "nonce": "<per-experiment uuid>",
 "experiment_id": "<uuid, identical across all 27 runs of one experiment>",
 "pr": {"repository": "...", "number": 63, "base_sha": "...", "head_sha": "..."},
 "skill_sha256": "<sha256 of the arm's SKILL.md>",
 "arm_manifest_sha256": "<sha256 of the arm-builder manifest: ablation spec + baseline hit set + post-condition result>",
 "driver_prompt_sha256": "<sha256 of the fixed driver prompt file>",
 "model_id": "<pinned model id as returned by the runtime, not as requested>",
 "findings": [{"path": "...", "side": "LEFT|RIGHT|FILE", "anchor_sha256": "...", "evidence_sha256": "...",
               "category": "...", "claim_key": "...",
               "severity": "CRITICAL|HIGH|MEDIUM|LOW|NIT", "confidence": 0, "line": 0}],
 "usage": {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "total_cost_usd": 0.0},
 "wallclock_ms": 0, "written_at": "<RFC3339>"}
```

**Run manifest** (runner → comparator), one JSON object per run, written by `review-ablation.sh run`
**before** the agent is launched and never writable by it:

```json
{"schema": "kc-pr-flow.ablation-manifest/v1",
 "experiment_id": "<uuid>", "nonce": "<per-experiment uuid>",
 "arm": "A|A_prime|B", "run_index": 1, "slot_index": 0,
 "pr": {"repository": "...", "number": 63, "base_sha": "...", "head_sha": "..."},
 "run_started_at": "<RFC3339, taken by the runner before launch>",
 "expected_receipt_path": "<absolute path the runner will read>"}
```

This exists because the receipt alone cannot answer "was this written by *this* run". The receipt is
authored inside the agent's session; anything in it that claims recency is a self-report. The
manifest is the runner's own record, `compare` is given the manifest set alongside the receipt set,
and the two are joined on `(experiment_id, arm, run_index)`. Without it AC-3(c) has no run-start
authority to compare against and cannot be built.

Five things changed from round 1's `v1`, each because `v1` did not actually work.

**The findings entry now carries what the reused canonicalization consumes.** `review_benchmark_fingerprint_id`
canonicalizes `{path, side, anchor_sha256, evidence_sha256, category, claim_key}` and its validator
(`review-runtime-benchmark.sh:330-336`) demands exactly that key set — `exact_keys([...])` plus
`(.evidence_sha256 | sha256)` and `side == "LEFT" or "RIGHT" or "FILE"`. Round 1's entry carried
`line` and no hashes, so the declared reuse would not have typechecked against its own validator.
`line` is retained as **display metadata only** and is excluded from the canonical object.

**Severity uses the skill's own vocabulary.** `SKILL.md:1852` fixes it: `CRITICAL / HIGH / MEDIUM /
LOW / NIT`. Round 1 invented `blocking|important|nit`, which would have needed a mapping nobody
wrote and would have silently collapsed CRITICAL and HIGH.

**`mode` moved out of the receipt into the comparison.** Equal `skill_sha256` across the compared
pair is *required* under `AA` and *forbidden* under `AB` (AC-1 / AC-3(a)) — round 1 got that
mode-dependence right but put the field in the wrong place. A receipt records **which arm produced
it**; whether a given pair of arms is being read as an A/A or an A/B comparison is a property of the
`compare` invocation, which is why `v3` drops `mode` and adds `A_prime` to `arm`. Round 1's placement
made one arm-A receipt need to be simultaneously `"AA"` (for AC-1) and `"AB"` (for AC-2), so proving
both ACs would have meant either 36 runs or copying nine receipts with rewritten metadata — and a
copied receipt is precisely what AC-3(d) exists to reject. `compare` echoes the mode it was invoked
with into the verdict, so a verdict is still self-describing.

**Provenance is pinned.** `model_id` (as reported, not as requested — a silently-substituted model
invalidates the comparison), `pr.base_sha`/`pr.head_sha` (corpus revision), `driver_prompt_sha256`,
`arm_manifest_sha256`, plus `experiment_id`, `nonce`, `written_at`, and `slot_index`.

`skill_sha256` is what makes an arm auditable after the fact. Its limits, stated because round 1
overclaimed them: it proves two arms' `SKILL.md` **differ**, not that they differ *in the intended
way* — an arm B that changed an unrelated sentence also hashes differently and would pass. Correct
arming is established by `arm_manifest_sha256`, which commits the builder's baseline hit set and its
post-condition result (fix 5, step 4); the hash comparison is the cheap cross-check, not the proof.
`slot_index` records the randomized arm-to-slot assignment, which is what the permutation test's
exchangeability assumption actually needs.

**The freshness authority left the receipt.** Round 1 asked the receipt to prove its own freshness,
which it cannot; the run manifest above now carries `run_started_at` and the runner's `nonce`, and
`compare` reads both. The receipt keeps `written_at` and `nonce` so the two can be *compared* — a
self-report is evidence once there is an independent record to check it against.

**Verdict contract** (comparator output): `kc-pr-flow.ablation-verdict/v3` carrying `mode`
(`AA|AB`, from the invocation) and `arms` (e.g. `["A","A_prime"]`), `experiment_id`, `z_observed`
and `t_observed` per dimension, `p_joint`, `p_dim` (the max-adjusted per-dimension p-values),
`material` (bool), `flagged_dimensions` (subset of `anchor_set` / `severity_mix` / `tokens`), plus
the per-PR `D(p)`, per-arm token totals, and the provenance pins echoed from the receipts
(`model_id`, `driver_prompt_sha256`, corpus base/head SHAs).

**What `material: false` certifies — and what it does not.** It certifies **no detected difference
on the measured dimensions (anchor set, severity mix, tokens)** at α=0.05 for the corpus, sizing,
and model recorded in the verdict. It does **not** certify "no behavioral change": a cut that
rewords what a finding says while its anchor and `claim_key` hold is outside the instrument's range
by construction, and so is any effect below the power floor. The verdict JSON carries this sentence
verbatim in a `certifies` field so it travels with the artifact rather than living only here.

`certifies` is a two-element object, because the AA and AB directions certify different things and a
single sentence was letting the weaker one be read as the stronger:

```json
"certifies": {
  "null_result": "material:false certifies no detected difference on the measured dimensions (anchor set, severity mix, tokens) at alpha=0.05 for the corpus, sizing, and model recorded in this verdict. It is never a certificate of 'no behavioral change': a cut that rewords a finding while its anchor and claim_key hold is outside the instrument's range by construction, as is any effect below the power floor.",
  "detection_scope": "A material:true verdict on a multi-file, multi-span removal certifies detection of a LARGE removal only. It does not establish sensitivity to a small or wording-only cut: at N=3/M=3 the measured detection knee is between +1 and +2 findings per run, so an effect worth one extra finding per run is missed about two times in three. A downstream cut may not cite this verdict as evidence its own smaller cut would have been detected."
}
```

The second field is what makes `tm` unable to inherit AC-2's pass by reading the artifact alone.

**The decision is ONE joint permutation test, not three.** Round 1 left the entry rules undefined;
the round-1 repair defined three of them and made `material` true iff any one crossed `p_perm` ≤
0.05. That is an OR of three α=0.05 tests, so the family-wise false-positive rate is
**uncalibrated — bounded above by ~0.143 under independence** (`1 − 0.95³`), and in fact lower than
that bound because the three statistics are computed on the same runs and are positively correlated.
Neither number is the rate; the point is that nothing in the design pinned it to α. The round-1
figure of 0.045 was measured on the anchor-set statistic alone, so it never supported AC-1's
calibration claim.

The three per-dimension statistics stay as they were:

- `anchor_set` — `T` on candidate-fingerprint sets, exactly as pre-registered above.
- `severity_mix` — the same `D(p)` construction with similarity `1 − TV(H_a, H_b)`, the
  total-variation distance between two runs' normalized severity histograms over
  `CRITICAL/HIGH/MEDIUM/LOW/NIT` plus the `EMPTY` category defined below.
- `tokens` — `D(p)` = difference of arm mean per-run `usage.input_tokens + output_tokens +
  cache_creation_input_tokens` (the uncached total; cache-read is dominated by shared prefix and is
  not an arm property), and `T` = mean `|D(p)|`, i.e. mean absolute difference of arm means.

What changes is how they are combined. Over the **same** `C(2N,N)^M` label assignments, each
dimension's `T_d` is standardized by its own permutation mean and standard deviation to `z_d`, and
the joint statistic is `max_d z_d`. Then

    p_joint = fraction of assignments whose max_d z_d  >=  observed max_d z_d
    p_d     = fraction of assignments whose max_d z_d  >=  observed z_d

`material` is true iff `p_joint ≤ 0.05`; `flagged_dimensions` = `{ d : p_d ≤ 0.05 }`. Since
`p_joint = min_d p_d`, a `material: true` verdict always names at least one dimension, and a verdict
that reports `material: true` with an empty `flagged_dimensions` is a comparator bug and must exit
non-zero. All three `T_d` are invariant under the within-PR A/B label swap, so the joint rule has the
same attainable floor `(2/C(2N,N))^M` = 1/1000 at N=3/M=3.

This is single-step max-T (Westfall–Young). It is chosen over Bonferroni because it **self-calibrates
under whatever correlation the three statistics actually have**, which is unknown in advance and
which Bonferroni would have to assume away — dividing α by 3 against three heavily correlated
statistics is conservative by an amount nobody can state, and buying calibration with power is the
wrong trade for a design whose power is already the binding constraint.

**This fix costs zero additional runs.** It is arithmetic inside `compare`, over the same 27
receipts, permuting the same labels. Nothing about the experiment, the corpus, the sizing, or the
budget moves. (Recorded explicitly because the round-2 gate was told this fix might move the budget;
it does not.)

**Recalibration, re-run on the joint rule.** From the committed simulation, 200 A/A trials per
sizing at α=0.05:

| sizing | A/A false positives, joint rule | anchor-set statistic alone, same trials |
|---|---|---|
| N=2 / M=3 | 6/200 = **0.030** (Wilson 0.014–0.064) | 8/200 = 0.040 (Wilson 0.020–0.077) |
| N=2 / M=4 | 11/200 = **0.055** (Wilson 0.031–0.096) | 11/200 = 0.055 (Wilson 0.031–0.096) |
| **N=3 / M=3 (adopted)** | 10/200 = **0.050** (Wilson 0.027–0.090) | 13/200 = 0.065 (Wilson 0.038–0.108) |

At the adopted sizing the joint rule's A/A rate is 0.050 with a Wilson interval of 0.027–0.090 —
consistent with α under this run model. The bounded claim, and its enforcement point: the rule's
calibration is *asserted* only to the precision 200 trials buy, and the enforcement is the committed
script, which anyone can re-run with a different seed. The two columns are within each other's
intervals, so this table does **not** claim the joint rule is better calibrated than the single
statistic — it claims the joint rule is calibrated at all, which the OR-of-three was not.

**Worked verification of the joint rule — cases it must flag and a case it must not** (Proof Policy
#7), by exact enumeration over all 8000 assignments at N=3/M=3:

| Case | `p_joint` | `flagged_dimensions` |
|---|---|---|
| All three dimensions moved (disjoint anchors, all-HIGH vs all-NIT, 100 vs 300 tokens) | **0.0010** (the floor) | `anchor_set`, `severity_mix`, `tokens` |
| Tokens only — identical anchors and severities, 100 vs 300 tokens | **0.0010** | `tokens` only |
| Arms are the same runs | **1.0000** | none |
| Both arms all-empty runs (`findings: []`) | **1.0000** | none, and no division by zero |

The tokens-only row is the one that proves the joint rule still *discriminates*: a max-statistic that
flagged every dimension whenever any moved would name all three there. The last two rows are the
"it can also not fire" half.

**`severity_mix` on an empty run.** The histogram is over **six** categories — the five severities
plus a dedicated `EMPTY`. A run with `findings: []` gets mass 1 on `EMPTY` and 0 elsewhere; a run
with findings gets 0 on `EMPTY` and the normalized severity counts elsewhere. Without this the
normalization divides by zero, and a legitimate zero-finding receipt would crash the comparator or,
worse, be coerced to some default histogram. The corpus precondition (≥1 posted-tier finding) is a
*pilot-time* property of a PR; it does not guarantee that every one of the 27 runs is non-empty, so
this is a live path, not a hypothetical. With the `EMPTY` category the distance stays total: an empty
run and a non-empty run are at TV distance 1 (similarity 0), two empty runs at distance 0
(similarity 1). The fourth row of the table above is that case, enumerated.

**Stale and duplicate, defined so each can actually be constructed.** Round 1 stated both guards in
terms the data could not support; here is what each one computes.

- **Stale** — a receipt at `expected_receipt_path` is stale iff its `nonce` ≠ the manifest's `nonce`,
  or its `experiment_id` ≠ the manifest's, or its `written_at` is **earlier than the manifest's
  `run_started_at`**. The manifest is written by the runner before launch and is not writable by the
  agent, so this is a comparison against an authority outside the thing being checked. Constructing
  the negative case is then a two-line fixture: write a receipt, then write a manifest whose
  `run_started_at` is later.
- **Duplicate** — the projection hashed is the receipt's canonical JSON **minus
  `{run_index, slot_index, written_at}`**. Round 1 hashed the whole receipt including `run_index`,
  so two receipts differing only in `run_index` hashed differently and the guard could never fire —
  a check that cannot fail. With those three fields projected out, a receipt copied from run 1 to
  run 2 hashes identically and is caught. Two receipts colliding under this projection are rejected
  as duplicates regardless of arm; a genuine re-run differs in at least its `usage` and
  `wallclock_ms`, so a legitimate collision would itself mean the runs were not independent.

Both rules are stated as computations over fields that exist, which is the bar an AC-3 negative case
has to clear: **an AC whose negative case cannot be constructed is an AC that cannot fail.**

**CLI surface**: one script, `kc-pr-flow/scripts/review-ablation.sh`, subcommands `arm` (build an
arm tree), `run` (write the manifest, execute one headless run, collect the receipt), `compare
--mode AA|AB --arms X,Y` (manifests + receipts → verdict). Split this way so `compare` is
unit-testable against synthetic manifests and receipts with no model in the loop.

## Acceptance criteria

**AC-1 — An A/A comparison reports no material difference.**
Verified by: `review-ablation.sh compare --mode AA --arms A,A_prime` over the arm-A and arm-A′ halves of one 27-run experiment (18 receipts plus their 18 runner-written manifests, 3 runs × 3 PRs per arm, both arms built from the unablated tree on the frozen corpus), emitting `material: false` under the pre-registered joint rule (`p_joint` > 0.05) with `flagged_dimensions` empty. Under `--mode AA` the two arms' `skill_sha256` are **required to be equal** and `compare` exits non-zero if they differ — the mis-arming check is a property of the invocation, not of the receipts, which is what lets AC-1 and AC-2 share arm A's nine runs and holds the acceptance at 27 runs. What this AC does and does not establish: a single pass is a **negative control** showing the instrument does not fire on nothing; it is not a measurement of the real false-positive rate, which would need tens of A/A comparisons. Falsified by: `material: true` — the statistic is then tracking run scheduling, not the skill, and no cut can be judged with it. Falsifying edit: order the runs arm-A-then-arm-A′ instead of randomizing slot assignment; if that flips the verdict, the noise model is wrong.

**AC-2 — Removing the pre-emit quote gate is reported as a difference.**
Verified by: `review-ablation.sh compare --mode AB --arms A,B` over the arm-A and arm-B halves of the same 27-run experiment, where arm B removes the pre-emit quote gate at **every CUT span enumerated in `### The AC-2 ablation`**, across all three loaded files — `SKILL.md` (S1-S8: `:975`, `:977-982`, `:984`, `:986`, `:988`, the ` after the verification gate` substring of `:990`, the `:861-862` parenthetical, the `:1855` recap), `reference/review-triage.md` (S9 `:221`, S10 `:223-227`), and `reference/learned-patterns.md` (S11 `:13-15`) — with the arm manifest showing every CUT span **verbatim-absent** in arm B, every KEEP span (K1 `SKILL.md:143`, K2 `review-triage.md:229-236`, K3 `learned-patterns.md:9-11`) present and byte-identical, and a clean keyword canary; emitting `material: true` with at least one entry in `flagged_dimensions`. Falsified by: `material: false` for that ablation — the harness cannot catch the cuts this sprint intends. Falsifying edit: build the arm that removes only the 7 keyword-bearing spans and leaves S2/S3/S4/S10 in place; the design predicts a weaker or absent signal, and if the verdict is unchanged either way, the statistic is not reading the gate. What this AC does and does not establish: it certifies detection of a **large multi-site removal**, never sensitivity to a small or wording-only one — see the residual recorded under `### What this harness can and cannot detect`.

**AC-3 — The harness cannot report a false null.**
Verified by: five negative cases, each producing a non-zero exit and a named error rather than a `material: false` verdict — (a) a mis-armed pair under `compare --mode AB --arms A,B`, where both arms' `skill_sha256` are equal though built as A and B; (b) a failed run, where one arm's run produced no receipt at the manifest's `expected_receipt_path` (the case actually observed in spike 2); (c) a stale receipt at a reused output path, detected against the **runner-written manifest** — the receipt's `nonce` or `experiment_id` disagrees with the manifest's, or its `written_at` precedes the manifest's `run_started_at`; (d) two receipts equal under the duplicate projection (canonical receipt JSON minus `{run_index, slot_index, written_at}`), i.e. one receipt copied across runs to inflate agreement; (e) receipts whose `driver_prompt_sha256` or `model_id` disagree anywhere across the experiment's 27 receipts, not merely within the compared pair. Falsified by: `compare` emitting a normal verdict for any of them — the harness would then report "no difference" for a review that was never ablated, never finished, or never actually re-run. Falsifying edit: make the receipt loader default a missing file to `{"findings": []}`; AC-3(b) must go red.

**Residual degenerate paths, named and not closed.** Three failure shapes were raised and are *not* fully guarded by AC-3, recorded here rather than left unlisted: an early parseable `findings: []` written before the agent defers (indistinguishable from a genuine zero-finding run — the ≥1-finding corpus precondition makes it detectable at pilot time but not per-run); malformed individual findings silently dropped by the parser rather than failing the run (mitigated by failing the run on any unparseable entry, unmitigated for an entry that parses but is semantically wrong); and receipts mixed across experiments where `experiment_id` collides. These are the known residuals of the false-null guard, not oversights.

## Test plan

1. **Comparator unit tests**, no model in the loop, against synthetic receipts. Four fixtures, each pinned to a value computed by exact enumeration during ideation: identical fingerprint sets across arms → `T`=0, `p_perm`=1, `material:false`; disjoint sets with perfect within-arm agreement → `T`=1, `p_perm`=**1/1000** at N=3/M=3 (and **1/27** at N=2/M=3, asserted separately to pin the floor formula `(2/C(2N,N))^M`); a consistent superset (`A={x,y}`, `B={x,y,z}`) → `T`=1/3, `p_perm`=1/27 at N=2/M=3; and a **sign-flipped** case where between-arm agreement exceeds within-arm agreement by the same margin → identical `p_perm` as the positive case, which is the assertion that fails if anyone reverts `T` to the signed statistic. Together these are the "the check can fail" set required by Proof Policy #2 — fixture 1 fails if the statistic is inverted, fixture 2 if the permutation enumeration is wrong, fixture 2's N=2 variant if the label-swap collapse is not accounted for, and fixture 4 if the test is one-sided. Four further fixtures pin the **joint** rule to the values enumerated in `### Design determination`: all three dimensions moved → `p_joint` = 1/1000 with all three dimensions flagged; tokens moved alone → `p_joint` = 1/1000 with **only** `tokens` flagged (this one fails if the max-statistic flags every dimension whenever any moves); arms identical → `p_joint` = 1 and `flagged_dimensions` empty; and both arms all-empty (`findings: []`) → `p_joint` = 1 with no division by zero, which is the `severity_mix` `EMPTY`-category fixture. All eight expected values are printed by `docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py`, so the fixtures are pinned to a script anyone can re-run rather than to numbers quoted in prose.
2. **Arm-builder post-condition test**, the span-match assertions from `### The AC-2 ablation`. The builder must exit non-zero on each of: an ablation patch targeting a string that does not exist (the sprint's own silent-no-op failure, encoded); an empty baseline hit set; a resolved span whose sha256 disagrees with its pin (the tree moved under the table); **a CUT span still verbatim-present in arm B**; a KEEP span (K1 `SKILL.md:143`, K2 `review-triage.md:229-236`, K3 `learned-patterns.md:9-11`) missing or modified; S6's surviving `**Apply confidence gates**` lost; and a residual keyword-canary hit outside the K1 whitelist, which means the table missed a site. The load-bearing case, already demonstrated at ideation by `span-match-demo.py`: **an arm that removes only the 7 keyword-bearing spans must be REJECTED**, where the round-2 keyword post-condition accepted it — S2, S3, S4 and S10 are invisible to all four keyword patterns. Its mirror is the positive control: the fully ablated arm must be accepted, so the check is not simply always-reject.
3. **False-null guard tests** (AC-3), one per case, each built from synthetic manifest+receipt pairs: matching `skill_sha256` under `compare --mode AB --arms A,B`; a manifest whose `expected_receipt_path` holds no file; a receipt whose `nonce`/`experiment_id` disagrees with its manifest, and separately one whose `written_at` precedes the manifest's `run_started_at`; two receipts equal under the duplicate projection (identical except `run_index`/`slot_index`/`written_at`, which is constructible precisely because those three fields are projected out); and a 27-receipt set with one disagreeing `driver_prompt_sha256` / `model_id`. All must exit non-zero with a named error. A sixth, positive control: the arm-A and arm-A′ fixtures under `compare --mode AA --arms A,A_prime` with equal `skill_sha256` must be **accepted** and emit a verdict, which is what proves the mode-dependent check is not simply always-reject.
4. **Lint**: CI's pinned ShellCheck v0.9.0 via docker, per `kc-pr-flow/CLAUDE.md:117-125` — `docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt koalaman/shellcheck:v0.9.0 …`; never the local build, which has retired checks CI still enforces.
5. **Runtime/E2E** (the ACs proper): the 27 real headless runs. Unit tests prove the comparator's logic; only these prove the wiring (Proof Policy #3).
6. **CI delta**: the comparator unit tests are fast and jq-only, so no job-margin risk. The 27-run acceptance is **operator-run, never in CI** — it costs money and needs credentials. The PR carries the verdict JSON as evidence; CI runs items 1-4 only. Stated explicitly so nobody later "helpfully" wires the expensive path into a workflow.

## Doc diff

`kc-pr-flow/CLAUDE.md` — add after the ShellCheck section:

> **Judging a cut to `SKILL.md`.** Prose has no test: deleting instruction text leaves the shell
> suites green. Before a cut to instruction text that could change what the review flags, run
> `scripts/review-ablation.sh` for an A/B verdict against the frozen corpus. One verdict costs 18
> headless review runs (~$46), so it is for load-bearing cuts, not mechanical ones. The verdict compares
> candidate-fingerprint sets, so it is blind to a cut that changes a finding's wording without
> moving its anchor.
>
> Read the verdict for what it says, in both directions — the verdict's `certifies` object states
> each one. `material: false` certifies **no detected difference on the measured dimensions (anchor
> set, severity mix, tokens)** for the corpus, sizing, and model in the verdict — it is never a
> certificate of "no behavioral change". A wording-only cut is outside the instrument's range by
> construction, as is any effect below its power floor. And `material: true` on a large multi-file
> removal certifies only that a **large** removal is detected: the measured detection knee is
> between +1 and +2 findings per run, so **a passing verdict on someone else's bigger cut is not
> evidence your smaller cut would have been caught.** Each cut earns its own verdict or records its
> own accepted residual.

No `PRODUCT.md` / `ARCHITECTURE.md` change — this adds a development instrument, not a product
behavior.

## Appetite

One worker session: ~90 minutes of authoring, plus a metered compute budget for the acceptance runs.

**The compute budget: DECIDED by the captain, 2026-07-28 — N=3/M=3, envelope ≤$90.** Round 1
recorded ≤$60 on a measured basis of $2.53/run × 18 runs ≈ $45 plus re-run headroom. That sizing was
underpowered, so correcting it moved the envelope; the workflow forbids extending a budget silently,
it was escalated, and this is the ruling:

| | acceptance runs | run cost | re-run headroom | budget |
|---|---|---|---|---|
| Round 1 (recorded, underpowered) | 18 | $45 | $15 | ≤$60 |
| N=2 / M=4 (the cheaper route, refused) | 24 | $60.72 | — | — |
| **Adopted — N=3/M=3** | **27** | **$68.31** | **~$22 (~1 wave of 9)** | **≤$90** |

**The reasoning is expected cost, not absolute cost — recorded so a later reader sees why the
cheaper route was refused rather than merely that it was.** The run-cost delta between the two
routes is **$7.59** (27 × $2.53 = $68.31 against 24 × $2.53 = $60.72), not the ~$22 the FO's
escalation first stated — that figure was an envelope difference, and the correction is on the
record under Proof Policy #6. At its measured power of 0.72, the N=2/M=4 route fails AC-2 for want
of power 28% of the time and must then be re-run at N=3/M=3 anyway, so its expected spend is
`60.72 + 0.28 × 68.31 ≈ $80` — *above* the $68 of simply doing it once. It additionally needs a 4th
corpus PR sourced and pilot-run. The cheaper route is not cheaper under any accounting tried.

The delta buys measured power 0.43 → 60/60 (Wilson 0.94–1.00) on the effect AC-2 is built to detect.

The recorded overrun fallback stands unchanged and is what answers a budget objection: on overrun,
cut scope to AC-1 + AC-3 — the comparator is provably sound and the false-null guards hold — and park
AC-2 with the arm trees and receipts retained so it is re-enterable. Never extend the budget
silently, never compress the acceptance runs to fit.

## Pre-mortem

**Criteria that pass without delivering value.** If the corpus PRs produce near-empty or
near-deterministic finding sets, `T`≈0 for both A/A and A/B, and both ACs go green on a harness that
measures nothing. Guarded by the ≥1-finding corpus precondition and by AC-2 requiring a named
`flagged_dimension` whose entry rule is now computable rather than judgment, but this is the failure
to watch for at the validation gate.

## Implementation dispatch sizing

**ONE worker session.** It is one behavior — arm → receipt → verdict — with a single RED→GREEN loop,
and the expensive part is unattended compute (background launch, poll for completion), not developer
wall-clock. Splitting would pay cold-start twice, re-reading the README and this body, and buy no
parallelism the runs do not already have. Below all three split triggers.

## Out of scope

- Ground truth of any kind — that is `62`. This harness answers "did it move", never "is it good".
- Judging whether a detected difference is an *improvement*. The statistic `T` = mean `|D(p)|` is
  symmetric in the arms — swapping the A and B labels leaves every `T_d`, the joint statistic, and `p_joint` unchanged — so the
  verdict carries no notion of better or worse; a human reads `flagged_dimensions` and the per-PR
  `D(p)` and decides. (Round 1 claimed the verdict was "directional-agnostic by construction" while
  the statistic was signed and the test one-sided. That claim was false; this is the bounded version
  the corrected statistic supports, and the enforcement point is unit-test fixture 4, which asserts
  a sign-flipped case yields the same `p_perm`.)
- Changing `behavior_parity()` or the promotion gate in `review-runtime-benchmark.sh`. Those stay
  correct for runtime-parity work; this adds a sibling verdict, it does not retune theirs.
- Wiring any of this into CI or a pre-commit hook (Proof Policy #5 — behavior checks live at stage
  boundaries, never in the worker's inner loop).
- Cross-model arms (Codex/agy). One provider, pinned, for this entity.

## Spike

The riskiest unverified mechanism is "can we drive the skill twice, under two versions, and get two
comparable receipts out". It was split into the two halves that can fail independently.

### Spike 1 — version-swap reaches the model. PASSED.

`claude --plugin-dir <path>` loads a plugin from a directory for that session only (verified against
`claude --help`, not from memory). Built two arms from `kc-pr-flow/` at `f4f4840`; arm B had a unique
sentinel injected into `skills/kc-pr-review/SKILL.md`. The injection was proven non-no-op *before*
the run — sentinel count 1 in arm B, 0 in arm A — which is the check the sprint's earlier silent
no-op edit skipped.

Then a falsifiable pair, same prompt, asking the agent to invoke `kc-pr-review` and report whether
the loaded skill text contains the marker:

- Arm B, `--plugin-dir /tmp/5b-spike/arm-B` → returned the sentinel line verbatim.
- Arm A, no `--plugin-dir` (installed plugin) → returned `NO-MARKER`.

The negative control is what makes this evidence rather than a self-confirmation: if `--plugin-dir`
were ignored, arm B would also have returned `NO-MARKER`. Both runs returned full `usage` and
`total_cost_usd` under `--output-format json`, which settles the token/cost dimension too.

What this proves: the ablation reaches the model's loaded context, and per-run cost is observable.
What it does **not** prove: that a full review completes headless, or that findings come back
machine-parseable. That is spike 2.

### Spike 2 — one real headless review producing a receipt. PARTIAL — and the failure is the finding.

One real run against a real PR (`iamcxa/kc-claude-plugins#63`, 6 files / 107 lines), from a pristine
clone, with the driver prompt's no-post and receipt constraints.

**What held.** The run completed without error (`is_error: false`, 43 turns, 7.6 min). The no-post
constraint held across all 43 turns — verified independently against GitHub, not from the agent's
self-report: PR #63 has zero reviews and zero comments created today. The no-modify-tree constraint
also held; the agent put its scratch files outside the clone.

**Measured cost, and a reconciliation.** `$2.53` for the run. Tokens: 82 in, 17,780 out, 122,978
cache-creation, 5,067,023 cache-read — **5.21M total**. The workflow's prior "~140K tokens per
review pass" is not wrong, it is measuring the uncached portion: 82 + 17,780 + 122,978 ≈ 141K. Both
numbers are real and they answer different questions. Because cache reads bill at a fraction, the
number to plan on is **dollars**, not the raw total.

Restating the cost of a verdict on measured figures rather than the estimate:

| | runs | raw tokens | cost |
|---|---|---|---|
| One A/B verdict | 12 | ~62M (~1.7M uncached) | **~$30** |
| AC-1 + AC-2 acceptance (shares arm A) | 18 | ~94M (~2.5M uncached) | **~$45** |

**What did not hold, and it matters more than the cost.** *No receipt was written.* At turn 43 the
agent stopped and said it would wait for background tests to finish before producing the review and
the receipt — it had launched background work and deferred rather than completing. The run exited
`is_error: false` with no receipt on disk.

This is the receipt-collection seam (classified EXISTS_BROKEN above) failing in practice, and it
converts directly into a design requirement: **a run with no valid receipt is a FAILED run and must
never be read as an empty finding set.** If a missing receipt silently became "0 findings", both
arms would compare as identical and the harness would report "no material difference" for a review
that never finished — a false null of exactly the kind this entity exists to prevent. The driver
must therefore (a) forbid launching background work and deferring, (b) treat receipt-absent as a
hard run failure, and (c) refuse to emit a verdict when any run in either arm failed.

The spike cost one run to learn this, which is the cheapest place it could have been learned. It is
encoded as AC-3 and as test-plan item 3.

## Stage Report: ideation

- DONE: Layer-trace the EXISTING receipt/benchmark stack against origin/main and classify each seam WORKING / WORKING_UNIT_UNPROVEN / EXISTS_BROKEN / STUB / MISSING with file:line — greenfield is allowed only after multi-strategy proof of absence.
  Ten-seam table under `## Reverse-recovery audit`, traced at `origin/main` = `f4f4840` (fetched). Verdict: not greenfield. Fingerprint canonicalization and the set comparator are WORKING and reused; the materiality verdict is EXISTS_BROKEN (`behavior_parity()` at `review-runtime-benchmark.sh:807-815` is exact-hash equality, which fails every nondeterministic pair); driver and corpus are MISSING, each with the search that established it.
- DONE: Pre-register the "materially different" threshold in the entity body: which projection is compared, how many runs per arm, the numeric bar, and the noise model that justifies it — written before any cut, phrased so a later result cannot renegotiate it.
  Under `### Pre-registered materiality rule`. Projection = candidate fingerprint set (`path`+`side`+`anchor_sha256`+`category`+`claim_key`), reusing `review_benchmark_fingerprint_id` (`:451`, verified source-safe, reads the object on stdin). N=2 runs/arm, M=3 PRs. Bar = exact permutation test over 6^M label assignments, material iff `p_perm` ≤ 0.05. One free parameter, fixed now; there is no similarity number a later result could renegotiate.
- DONE: Make AC-1 (A/A reports no material difference) and AC-2 (removing the SKILL.md:973 pre-emit quote gate IS reported as a difference, flagged dimension named) each carry a runnable Verified by: command plus a named falsifying edit, with every AC resolving under `spacedock status --workflow-dir docs/dev --read 5b --ac-scan`.
  Three ACs, each with `Verified by:` / `Falsified by:` / a named falsifying edit. Scan output and its known counter discrepancy recorded below. **Correction inside this item:** the pre-emit gate is at `SKILL.md:975-984`, not `:973` (`:973` is the `### 6a` heading), and the same rule is restated at `:1855` — so AC-2 names both sites. An ablation cutting only `:975-984` would leave the gate still instructed.
- DONE: Spike the riskiest unverified mechanism end-to-end.
  Two halves. Spike 1 PASSED with a falsifiable pair — arm B under `--plugin-dir` returned the injected sentinel, arm A without it returned `NO-MARKER`; the negative control is what makes it evidence. Spike 2 PARTIAL: a real headless review of PR #63 completed (`is_error:false`, 43 turns, 7.6 min, $2.53, 5.21M raw / ~141K uncached tokens) and the no-post constraint held — verified against GitHub, not self-report — but **no receipt was written**. That failure is the stage's most useful output and became AC-3.
- DONE: Record appetite, one-sentence pre-mortem, and implementation dispatch sizing.
  Appetite ≤90 min authoring + ≤$60 metered compute, with a named cut-to-scope on overrun. Pre-mortem: criteria that pass without delivering value. Sizing: ONE worker session, below all three split triggers.

### `--ac-scan` output and the known instrument discrepancy

```
stage=ideation
ac=AC-1 line=254 unevidenced=false citations=1
ac=AC-2 line=257 unevidenced=false citations=2
ac=AC-3 line=260 unevidenced=false citations=1
```

All three resolve and none is `unevidenced`, which is what the precondition is for. The `citations`
counts are recorded, not acted on: AC-1's `Verified by:` cites the `compare` invocation, the receipt
count, the corpus and the `skill_sha256` equality check, and scores `1`; AC-3 names two distinct
negative cases and also scores `1`. That matches the known discrepancy the dispatch flagged (an AC
citing three paths scoring `0` while a single-path AC scored `2`), so a low count here is not treated
as a finding about the AC. Bold AC headings were kept to a single line so the line-based extractor
can see them — the failure that made three sprint-1 tasks ship with invisible ACs.

### Summary

Traced the existing stack rather than assuming a build: the scoring vocabulary already exists and is
reused, and the one function that actually issues a parity verdict is exact-hash equality — which is
the seed's predicted "every run reads as a regression" failure, already shipped. The design decides
all three of the seed's options (freeze everything freezable; compare on the fingerprint projection;
N=2 per arm) and pre-registers a permutation test rather than a similarity number, so no later result
can renegotiate the bar. Cost is stated plainly on measured figures: ~$30 per A/B verdict, ~$45 to
prove both ACs, which makes this a few-times-per-sprint instrument for load-bearing cuts rather than
a per-cut gate.

Two things the gate should rule on rather than accept silently. **AC-3 is mine, not the captain's** —
spike 2 produced a run that exited clean with no receipt, and a missing receipt read as "0 findings"
would make both arms compare identical and report a false null; I judged that worth an AC, but it is
an addition to a pair the captain called deliberately symmetric. And **the `:973` citation in the
directive is off**: the gate is `:975-984` and is restated at `:1855`, so AC-2 targets both sites.
Residual risks named and not solved: the fingerprint projection is blind to wording-only cuts (the
class closest to `tm`), and the receipt is authored by the agent under review — equal across arms, so
it largely cancels in a difference statistic, but a differential self-report bias would not.

### Feedback Cycles

**Round 1 — ideation gate, 2026-07-28. Verdict: RETURN (repair inside ideation, not a re-cut).**

Gate assembled by the FO, verdict by `ship-flow:science-officer-em` (fresh context, model fable).
Inputs: the FO's checklist accounting (5 done / 0 skipped / 0 failed), `--ac-scan` (AC-1/2/3 all
resolve, none `unevidenced`), one cross-vendor pass (`codex`, 12 findings, its own verdict "P1 /
block implementation until corrected"), and independent FO verification of the findings the verdict
rests on.

Findings dispositioned: **8 accepted for repair, 1 accepted as a named residual, 1 FO claim corrected
downward.** Nothing escalated to the captain — the EM ruled the call reversible (a pre-registration
not yet spent against), scope not re-cut, and no Material finding surviving repair to change what
ships.

The load-bearing ones, all confirmed rather than adopted:

- The permutation floor is misstated by 8× (`:166`). `D(p)` is invariant under swapping the A/B
  labels within a PR, so 6 relabelings collapse to 3 partitions and each value is achieved by `2^M`
  assignments. True floor at N=2/M=3 is 1/27 ≈ 0.037, not 1/216 — one notch under α=0.05, so "spare
  resolution" is false. Established by exact enumeration with a negative control (A/A → `p`=1.0,
  correctly not rejecting), and independently by the cross-vendor pass via label-swap invariance.
- The statistic is signed and the test upper-tail only, so its behavior on a change that makes one
  arm a superset of the other depends on the noise regime: `D = -0.083` in the noisy case,
  `D = +0.333` in the consistent case. The `:311-312` claim of being "directional-agnostic by
  construction" is false. **The FO's stronger framing — that AC-2 "would likely report
  `material: false`" — was overstated and the EM corrected it**; the bounded version is recorded here
  and is what the repair must write.
- AC-1 (`:255`) and AC-3(a) (`:261`) demand opposite outcomes for a pair with equal `skill_sha256`.
- The driver prompt (`:128`) names the pre-emit gate to both arms, reintroducing the ablated
  instruction through the harness's own instrument.
- The ablation misses a third live site at `SKILL.md:861` and leaves `:986`/`:988`/`:990` dangling.
- The receipt schema (`:233`) carries only `line`, so the declared reuse of the fingerprint
  canonicalization (`:145`) does not typecheck against its validator.

Accepted as a named residual: the instrument is blind to wording-only cuts — the class closest to
`tm`, which is the next entity in the sprint. Binding consequence: the verdict contract must state
that `material: false` certifies "no detected difference on the measured dimensions", never "no
behavioral change", and `tm`'s own gate inherits the residual.

Budget: the power fix moves the acceptance envelope above the recorded ≤$60 appetite (~$61 at
N=2/M=4, ~$68 at N=3/M=3). Restated explicitly rather than silently extended; the recorded overrun
fallback (cut to AC-1 + AC-3, park AC-2 re-enterably) stands.

Cost of the round: one ideation dispatch, one cross-vendor pass, one EM verdict. No compute was spent
against the pre-registration, so every fix above is a paper edit — which is the whole reason the gate
sits before the runs rather than after them.

- Cycle 3: REJECTED — validation / EM loop; surface 1 implementation worker session vs estimate 1 (100%); AC unchanged

**Cycle-3 design reset — captain approved 2026-07-28.** Reconfirm the existing ACs without narrowing
them and re-scope the missing corpus to three frozen snapshots: PR #17 at
`4489933ddf5237187c4866ab45bdecc5bdb2d0f0..f3aed43341d5fe4616d76ba02946bd4913ae260e`,
PR #19 at
`d62f2c6659d76799994482dd58be2dc2b05fb3ea..031b4908cf405724b2ed7d1b829f3c001eea7aa2`,
and PR #50 at
`536be3e7d7d8371a9e84b693804407ea1b54bc60..7c448243c0512d137a47cdf36a9b255658f096a3`
(the pre-ShellCheck-repair head). Repair V1/V3/V6; include V4/V5 because their bounded fixes are
low-cost; then pilot the three snapshots sequentially. Any pilot that yields no posted-tier finding
stops the run for captain review rather than consuming the 27-run acceptance budget. The `kj`
evidence note remains outside this single-entity route.

- Cycle 4: PARKED — captain budget stop; projected completion is at least $303.80 plus one unpriced aborted run against the $90 envelope (at least 337.6%); AC-1 and AC-2 remain acceptance-pending

**Park decision — captain, 2026-07-29.** Return this entity to backlog without claiming completion. Preserve code commit `0600f95`, state report `24d9c73`, the three corrected pilot receipts, branch `spacedock-ensign/skill-ablation-harness`, and physical worktree `.worktrees/spacedock-ensign-skill-ablation-harness` as re-entry evidence. Clear only the active worktree binding. Open findings: AC-1 has no A/A verdict; AC-2 has no ablation-detection verdict; therefore this harness does not authorize `tm`, `fa`, or `sk`. Re-entry requires an explicit new compute envelope and fresh validation; do not compress or reorder the pre-registered 27-run experiment to fit a smaller budget.

## Stage Report: ideation (correction round 1)

- DONE: The repaired pre-registration has real headroom and is two-sided: the permutation floor is stated with its derivation, N and M are chosen against it, the statistic flags a change in either direction, and the `## Appetite` compute budget is restated explicitly rather than inherited.
  Fix 1+2, at `### Pre-registered materiality rule`. Statistic is now `T` = mean `|D(p)|`, non-negative and label-symmetric. Floor derived as `(2 / C(2N,N))^M` from `D(p)`'s invariance under the within-PR A/B swap; round 1's 1/216 corrected to 1/27 at N=2/M=3. Sizing chosen against a measurement, not an argument: exact enumeration confirmed the floor (216 and 8000 assignments), 200-trial A/A calibration gave fp 0.045 at N=3/M=3 (≈α) and 0.005 at N=2/M=3, and 60-trial power on an AC-2-shaped effect gave **0.40 at N=2/M=3 vs 1.00 at N=3/M=3** — round 1 would have failed AC-2 three times in five for want of power. Adopted N=3/M=3. `## Appetite` re-proposes ≤$90 (27 runs ≈ $68) in a table against the recorded ≤$60, with the N=2/M=4 alternative (24 runs, ~$61, power 0.83) priced beside it; the recorded overrun fallback is unchanged.
- DONE: AC-1 and AC-3 no longer contradict (explicit `mode: AA|AB`), the driver prompt names no mechanism under ablation, and AC-2's arm-B spec enumerates every gate reference site — including `SKILL.md:861` — with an arm-builder post-condition that derives the list by grep at build time and asserts no residual reference survives.
  Fix 3+4+5. `mode` added to the receipt and to both AC texts: equal `skill_sha256` is *required* under `AA` (AC-1) and *forbidden* under `AB` (AC-3a). Driver prompt rewritten to "the findings the skill's own flow approved for emission" — it now names no skill-internal mechanism at all, is byte-identical across arms, and is hash-pinned as `driver_prompt_sha256`. New `### The AC-2 ablation` table enumerates nine sites cut-or-keep, grep-verified against `origin/main` = `f4f4840`: the eight cut/edited (`:975`, `:977-982`, `:984`, `:986`, `:988`, `:990` clause-only, the `:861` parenthetical, `:1855`) plus **`:143` KEEP** — Step 2.5's user-concern gate is a different mechanism a naive `verification gate` grep would have ablated too.
- DONE: The receipt schema carries the fields the reused fingerprint canonicalization actually needs plus provenance pins (model id, corpus revision, driver-prompt hash), and the verdict contract states in words what `material: false` does and does not certify.
  Fix 6+7+8. Receipt bumped to `ablation-run/v2`: findings entries now carry `anchor_sha256`, `evidence_sha256`, `side` including `FILE`, `category`, `claim_key` (matching `review-runtime-benchmark.sh:330-336`'s `exact_keys` validator, which round 1's `line`-only entry failed), severity switched to the skill's own `CRITICAL/HIGH/MEDIUM/LOW/NIT` per `SKILL.md:1852`, plus `model_id` / base+head SHAs / `driver_prompt_sha256` / `arm_manifest_sha256` / `experiment_id` / `nonce` / `slot_index`. `skill_sha256`'s overclaim is bounded in place. `flagged_dimensions` entry rules made computable (same permutation machinery on three scalars/sets), closing the vacuous-`tokens` path. AC-3 extended from 2 to 5 negative cases (stale receipt, duplicate receipt hash, provenance disagreement) plus a positive control, with three degenerate paths named as explicit residuals. Verdict contract and the `kc-pr-flow/CLAUDE.md` doc diff both carry the certification sentence, and the verdict JSON carries it in a `certifies` field.

### `--ac-scan` output (re-run after repair)

```
stage=ideation
ac=AC-1 line=412 unevidenced=false citations=1
ac=AC-2 line=415 unevidenced=false citations=2
ac=AC-3 line=418 unevidenced=false citations=1
```

All three resolve, none `unevidenced`, all three bold headings still open and close on one line.
`citations` recorded, not acted on, per the standing note that it is unreliable in this workflow —
AC-3 now names five distinct negative cases and still scores `1`.

### Summary

Eight ordered fixes applied to the existing body; the audit, spikes, cost figures, reuse decisions,
and scoping were left untouched as instructed. The two arithmetic corrections were not asserted but
demonstrated (Proof Policy #7): exact enumeration of the full assignment space reproduced the
corrected floor and confirmed a case the rule must flag and a case it must not, and a Monte-Carlo
power run is what selected N=3/M=3 over the alternatives rather than a preference.

Two things the gate should rule on rather than accept silently. **The budget genuinely moves** —
≤$60 → ≤$90 — because the round-1 sizing was underpowered, not because scope grew; the N=2/M=4 route
holds nearer the original number at power 0.83 and the cost of a 4th corpus PR, and that trade is the
gate's to make, not mine. And **the power and calibration figures are from a model of the run
process, not from real runs** — they are the right instrument for sizing a design before spending
$68, but AC-1 is still what tests the real noise process, and if the real within-arm agreement is
much noisier than the simulation assumed, N=3 may itself prove short.

**Round 2 — ideation re-gate, 2026-07-28. Verdict: RETURN (correction round 2). Two items held for a captain ruling.**

Gate assembled by the FO; verdict by `ship-flow:science-officer-em` (fresh context, model fable).
Inputs: checklist (3 done / 0 skipped / 0 failed), `--ac-scan` (all three ACs resolve), a second
cross-vendor pass against the *repaired* document (required — the schemas changed), and FO
verification of the two findings the verdict rests on.

Round-1 fix items: **4 FIXED** (two-sided statistic, AA/AB mode, neutral driver, fingerprint
fields), **2 PARTIALLY FIXED** (the floor's derivation prose overstates "exactly two relabelings";
the ablation enumeration stopped at a file boundary). The sizing change was *measured*, not argued —
round-1's N=2/M=3 has power 0.40 on the AC-2-shaped effect, so it would have failed AC-2 three times
in five for want of power rather than want of effect. The return paid for itself.

New findings, the two load-bearing ones verified against source rather than adopted:

- **F-A [P1] — the ablation never reached the loaded context.** `reference/review-triage.md:221` is
  headed "Pre-emit evidence requirement (append to every agent prompt):" and `:223-227` restates the
  same gate with the same failure classes; `SKILL.md:195` loads that file on the ordinary path, and
  `reference/learned-patterns.md:13-15` is a third site. Arm B cut the gate from the collator while
  every dispatched reviewer still received it verbatim, so the power model's "+3 findings per run"
  premise was invalid and AC-2 could have returned `material: false` for a reason unrelated to the
  harness. The EM confirmed and extended it (`review-triage.md:229-234` carries collator gates too)
  and classed it an **incomplete round-1 fix — the enumeration boundary, not any single missed
  line**.
- **F-B [P1] — AC-1's calibration claim is unsupported.** `material` is true iff
  `flagged_dimensions` is non-empty, and three dimensions each enter at `p_perm ≤ 0.05`, so the
  family-wise rate is uncalibrated — bounded above by ~0.143 under independence, lower given the
  statistics share runs. The reported 0.045 was measured on the anchor-set statistic alone. Fix is a
  joint max-statistic permutation, which **costs zero additional runs**.

Also carried into the fix list: the arm-builder's grep post-condition would report "zero residual
hits" while `SKILL.md:984` and `:986` still instruct the gate, because neither line matches the
keyword patterns — the sprint's founding error (classify a region by pattern rather than by reading)
reproduced inside the instrument built to prevent it. Plus four spec-level defects: two AC-3 negative
cases that cannot be constructed as written, `severity_mix` undefined on an empty run, and power
figures that are not reproducible and probably optimistic.

**Three FO assembly errors the EM corrected, recorded because the FO made them.** F-B's fix moves no
budget (same receipts, comparator arithmetic only) — the FO wrote that it might. The 36-run/$91
figure is avoidable: a single three-arm experiment (A, A′, B) holds 27 runs and ~$68, so the captain
sees one stable number rather than a creeping one. And 0.143 is an independence *upper bound*, not a
measured rate — the bounded claim is "uncalibrated, ≤ ~0.143" (Proof Policy #6).

Seat split, ruled per pressure rather than collectively: opening round 2 is the EM's (every finding
is new — the two-rejection rule bites on the same finding twice, and no compute has been spent).
The budget extension and the F-A instrument-scope choice are the captain's. Recorded deviation:
ideation has now consumed roughly twice its ~90-minute authoring appetite across three passes; the
EM judged the round worth funding anyway because a paper round is the cheapest place these defects
can die.

Fix items 2-6 dispatched immediately; items 1 and 7 held pending the captain.

## Stage Report: ideation (correction round 2)

- DONE: The acceptance is one three-arm experiment (A, A', B) at 27 runs with `mode` moved out of the receipt into the `compare` invocation, so AC-1 and AC-2 share arm A without a receipt needing two modes, and the budget table stays 27 runs / ~$68 / <=$90.
  Fix item 2. `### Pre-registered materiality rule` opens with the three-arm paragraph (one `experiment_id`, A' a second unablated build, `compare --mode AA --arms A,A_prime` vs `--mode AB --arms A,B`); receipt bumped to `ablation-run/v3` — `mode` deleted, `arm` widened to `A|A_prime|B`; the schema notes explain why the round-1 placement forced 36 runs and collided with AC-3(d); `### Cost` restated as 3 arms x 3 runs x 3 PRs = 27; the exchangeability paragraph now says 27 runs interleaved across three arms; verdict contract carries `mode` + `arms`. `## Appetite` numbers untouched, as instructed.
- DONE: `material` is decided by ONE joint max-statistic permutation rather than three independent alpha=0.05 entries, the A/A Monte-Carlo is re-run on the joint rule with the new false-positive figure recorded, and the text states explicitly that this fix costs zero additional runs.
  Fix item 3. `### Design determination` replaces the three-way OR with single-step max-T (Westfall-Young): standardize each `T_d` against its own permutation distribution, `p_joint` = P(max_d z_d >= observed max), `p_d` = P(max_d z_d >= observed z_d), `material` iff `p_joint <= 0.05`, `flagged_dimensions` = {d : p_d <= 0.05}. The old rate is written as the bounded claim — "uncalibrated, bounded above by ~0.143 under independence" — never as a measured 0.143, and the note that round 1's 0.045 was measured on the anchor statistic alone is on the record. Re-run at 200 A/A trials: joint rule 10/200 = 0.050 (Wilson 0.027-0.090) at N=3/M=3, tabled beside the anchor-only column (13/200) with an explicit refusal to claim the joint rule is better calibrated — only that it is calibrated at all. The zero-additional-runs sentence is in the body verbatim: same 27 receipts, comparator arithmetic only.
- DONE: The remaining spec defects are closed so every AC-3 negative case is constructible: a runner-authored run manifest gives `compare` a run-start authority outside the agent's control, the duplicate projection is defined, `severity_mix` is defined on an empty run, and the simulation is committed with seed and parameters with power restated as 60/60 (Wilson ~0.94-1.00) rather than a known 1.00.
  Fix items 4, 5, 6-reproducibility. New `kc-pr-flow.ablation-manifest/v1` contract written by `review-ablation.sh run` before launch (`run_started_at`, nonce, `expected_receipt_path`), joined to receipts on `(experiment_id, arm, run_index)`; stale and duplicate each restated as a computation over fields that exist, with the duplicate projection = canonical receipt JSON minus `{run_index, slot_index, written_at}` (round 1 hashed `run_index` in, so that guard could never fire). `severity_mix` histogram widened to six categories with a dedicated `EMPTY` carrying mass 1. AC-3(a)/(c)/(d)/(e) and test-plan item 3 rewritten so each negative case is buildable; test-plan item 1 gains four joint-rule fixtures. Simulation committed at `docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py` (stdlib-only, `SEED = 20260728`, all parameters at the top), power restated as **60/60 observed, Wilson 0.94-1.00**, and the caveat strengthened on both halves the EM named.
- SKIPPED: Item 1 — the shape of AC-2's ablation, its scope, and the arm-builder span-level post-condition.
  Held for the captain per the dispatch. `### The AC-2 ablation`, AC-2's text, and the arm-builder's post-condition steps are byte-unchanged; the span-level verbatim-match redesign is recorded as pending, not implemented.
- SKIPPED: Item 7 — the compute budget.
  Held for the captain per the dispatch. `## Appetite` is presented exactly as it stood: 27 runs, ~$68, <=$90, with the N=2/M=4 alternative priced beside it.

### Coupling between the held items and the work done

One concrete coupling, and it is a notation collision rather than a design one. **AC-2's `Verified by:`
still reads `an A/B run (mode: "AB")`, which is the receipt field fix item 2 deleted.** The correct
phrasing is `compare --mode AB --arms A,B`. I did not make that edit because the dispatch forbids
touching AC-2's text and the captain's ruling rewrites that AC either way; whoever applies the ruling
should fold the notation change into the same edit. Everything else in item 1's scope is independent
of items 2-6: the three-arm restructure changes which receipts a comparison reads, not what arm B
ablates, and the joint statistic changes how `material` is decided, not what the ablation removes.

The second coupling is one-directional and already satisfied: item 2's arithmetic (27 runs, ~$68) is
what item 7's budget table already assumes, so a captain ruling on the budget does not disturb the
three-arm restructure, and the restructure is what keeps the number from creeping to 36/$91.

The N=2/M=4 alternative's power figure moved on re-measurement (0.83 -> 43/60 = 0.72, Wilson
0.59-0.81). That is inside item 7's decision surface, so it is flagged here rather than acted on: if
the captain takes the cheaper route to hold nearer the original budget, the power it buys is lower
than the round-1 table advertised.

### `--ac-scan` output (re-run after correction round 2)

```
stage=ideation
ac=AC-1 line=585 unevidenced=false citations=1
ac=AC-2 line=588 unevidenced=false citations=4
ac=AC-3 line=591 unevidenced=false citations=3
```

All three resolve, none `unevidenced`, all three bold headings still open and close on one line.
`citations` recorded and not acted on. New evidence for why: the identical AC text scanned
`AC-1 citations=2 / AC-3 citations=2` before this stage report was appended and
`AC-1 citations=1 / AC-3 citations=3` after, with no AC line edited in between. The scan is
deterministic on a fixed file (three consecutive runs agree); the counter is simply sensitive to
document content outside the AC it reports on, so it cannot be read as a property of the AC.

### Summary

Five of the seven fix items applied; items 1 and 7 held for the captain and left byte-unchanged. The
two structural fixes are the ones that mattered: moving `mode` out of the receipt turns two
overlapping 18-run experiments into one three-arm 27-run experiment, which is what stops the budget
creeping to 36 runs and stops arm A's receipts being duplicated into the teeth of their own
duplicate guard; and replacing the OR-of-three-alpha-tests with a single max-T permutation gives the
`material` bit a calibration it did not have, for zero additional runs.

Nothing here was asserted without being run. The sizing simulation is now a committed, stdlib-only,
seeded script rather than a lost ad-hoc one, and it prints every number the body quotes — the exact
floor (1/27, 1/1000), the anchor-statistic worked cases, four joint-rule worked cases including one
the rule must flag on a single dimension and two it must not fire on, and the A/A and power rates
with Wilson intervals. Two of its figures disagree with round 1's (power 0.43 and 0.72 where round 1
recorded 0.40 and 0.83); the disagreement is recorded in the body rather than smoothed over, the
ordering that the sizing decision rests on is unchanged, and the adopted cell is now stated as 60/60
with an interval rather than as a known 1.00.

One thing the gate should rule on rather than accept silently: **the joint rule's calibration is
established at 200 trials against a run model, not against real runs.** 0.050 with a Wilson interval
of 0.027-0.090 is consistent with alpha and is the honest precision available before spending $68;
it is not a measurement of the harness's real false-positive rate, and AC-1 — a single A/A
comparison — is a negative control, not that measurement either. The body now says so in both
places.

**Captain rulings, 2026-07-28 — both held items decided as recommended.**

**Decision 1 — compute budget: N=3/M=3 adopted, envelope ≤$90.** The FO's escalation initially framed
the delta as ~$22; that was an envelope difference, and the corrected run-cost delta is **$7.59**
(27 × $2.53 = $68.31 against 24 × $2.53 = $60.72). The argument that decided it is expected cost, not
absolute cost: at power 0.72 the cheaper N=2/M=4 route fails AC-2 for want of power 28% of the time
and then has to be re-run at N=3/M=3 anyway, so its expected spend is 60.72 + 0.28 × 68.31 ≈ **$80**,
*above* the $68 of simply doing it once. N=2/M=4 additionally needs a 4th corpus PR sourced and
pilot-run. The cheaper route is not cheaper under any accounting tried.

**Decision 2 — AC-2 is a real full-site removal (option a), not an injection control.** The deciding
argument is the direction of the operation. This workflow's own thesis is "subtraction needs more
evidence than addition"; every Sprint 4 cut is a removal; certifying a removal-detector with an
addition is a category mismatch that would leave the dispatch → reviewer → collate path — the exact
path F-A showed everyone had mis-modelled — unexercised. Second: Sprint 4 item 3 (`sk`) cuts
reference-file *loading*, so an instrument validated only against `SKILL.md` could not judge it, and
`5b` is item 0 precisely so that everything downstream is judgeable.

Option (b)'s real strength — single-sited by construction, so the F-A class cannot recur — was
answered at the root instead: the arm-builder's absence proof moves from keyword grep to verbatim
span match. (b) is retained as a **diagnostic fallback, not pre-paid**: if AC-2 under (a) reports
`material: false`, an injection arm then distinguishes "the harness is blind" from "the ablation did
not take".

**Residual recorded before the money is spent, not after.** Option (a)'s ablation spans three files,
so its effect is large. AC-2 passing therefore certifies that the instrument detects a *large
multi-site removal* — it does **not** establish sensitivity to a small one. Sprint 4's first actual
customer, `tm`, removes restatements that may be both small and inside the fingerprint projection's
known blind spot (wording changed, anchor unmoved). **An AC-2 pass does not transfer to `tm`**: `tm`
carries its own complementary check or records acceptance of the residual at its own gate. This
sentence travels in the verdict artifact's `certifies` field rather than living only here.

## Stage Report: ideation (correction round 3)

- DONE: AC-2's ablation covers the whole loaded surface, not one file: every gate site across `kc-pr-flow/` is enumerated cut-or-keep — `reference/review-triage.md:221-227` CUT, `reference/review-triage.md:229-234` KEEP, `reference/learned-patterns.md:13-15` CUT — and the arm builder derives the site set by a tree-wide sweep at build time rather than reading the table.
  `### The AC-2 ablation` rewritten tree-wide: 11 CUT spans (S1-S11) + 3 KEEP spans (K1-K3) across three files, swept three ways (four gate keywords tree-wide; a bare `quot` sweep; a phrase sweep for the gate's semantics without its name). K2 is `review-triage.md:229-236`, wider than the dispatch's `:229-234`, because `:229-234` truncates the table it names: `:229` is the intro sentence, `:231-232` the header and separator, and the four destination rows run `:233-236`, so stopping at `:234` leaves the 3-4 and 1-2 rows outside the KEEP span and unprotected. The default-to-6 rule at `:238` is deliberately left outside it. No additional CUT site exists in `agents/`, `scripts/`, `docs/`, `hooks/`, `pr-review-loop.md`, or the other five skills; the nearest misses (`SKILL.md:677`, `:714`, `break-point-probe`) were read and rejected as different mechanisms. `kc-pr-flow/` is byte-identical between the audit SHA `f4f4840` and `HEAD`, verified by `git diff --stat f4f4840 HEAD -- kc-pr-flow/` returning empty.
- DONE: The arm builder proves absence by verbatim span match (each span present in baseline, absent in arm B) with keyword grep demoted to a canary, so an arm that still instructs the gate at `SKILL.md:984` or `:986` cannot pass its post-condition.
  Five-step build-time post-condition: resolve each span by line range and check its sha256 against a pinned sidecar (stale-table detection); assert the hit set non-empty; apply; assert per span against the **spec** — every CUT absent, every KEEP byte-identical; run the keyword grep as a canary that can only fail the build, never pass it. Demonstrated, not asserted: `docs/dev/artifacts/skill-ablation-harness/span-match-demo.py` (exit 0) builds `arm_keyword` (only the 7 keyword-bearing spans removed) and shows keyword-grep **PASS** / span-match **FAIL** with S2, S3, S4, S10 named; `arm_span` passes both. The measured scope of the old defect is worse than the dispatch stated: **4 of 11 CUT spans are invisible to all four keyword patterns** — not only `:984`/`:986` but the entire failure-class table at `:977-982` and the whole per-agent instruction blockquote at `review-triage.md:223-227`. Two must-fail cases keep the check falsifiable: removing K2 is rejected, and the fully ablated arm is accepted (not always-reject).
- DONE: The captain's two rulings are propagated everywhere they bind: Appetite fixed at N=3/M=3 with the <=$90 envelope and the expected-cost reasoning recorded, AC-2's stale `mode: "AB"` notation replaced by `compare --mode AB --arms A,B`, and the verdict's `certifies` field stating that an AC-2 pass does not transfer to small or wording-only cuts.
  `## Appetite` records the ruling with the corrected $7.59 run-cost delta (not the FO's ~$22, which was an envelope difference) and the expected-cost argument that decided it: N=2/M=4 at power 0.72 spends `60.72 + 0.28 × 68.31 ≈ $80`, above doing it once at $68. AC-2 now reads `compare --mode AB --arms A,B`; the only surviving `mode: "AB"` string is the round-2 report's record of the collision, correctly historical. `certifies` split into `null_result` + `detection_scope`, the second stating the non-transfer with its measured number; the same two-directional reading is in the `kc-pr-flow/CLAUDE.md` doc diff. Option (b) recorded as a diagnostic fallback with a specific trigger (`material: false` under (a)), explicitly not pre-paid.

### The effect model was restated against a measurement, not an argument

`EFFECT_EXTRA_FINDINGS = 3` was written for a single-file ablation, so leaving it attached to an
eleven-span three-file treatment would have been a stale rationale on a changed treatment. Rather
than argue that a larger effect is safely covered, `sizing-simulation.py` gained a `power_curve()`
sweep (same `SEED = 20260728`, 60 trials/point, N=3/M=3, α=0.05) and the curve was run:

```
effect=+ 1 findings/run: power=20/60=0.33 (Wilson 0.23-0.46)  median p_joint=0.1125
effect=+ 2 findings/run: power=59/60=0.98 (Wilson 0.91-1.00)  median p_joint=0.0010
effect=+ 3 findings/run: power=60/60=1.00 (Wilson 0.94-1.00)  median p_joint=0.0010
effect=+ 4/+6/+9        : power=60/60 each                     median p_joint=0.0010
```

Power is flat at the ceiling from +2 upward, so **the sizing decision does not move** under a larger
treatment. The new number this buys is the detection knee, between +1 and +2 findings per run, which
is what turns the `tm` non-transfer residual from prose into a quantity. The full re-run reproduced
every previously recorded figure exactly (A/A 0.030 / 0.055 / 0.050, power 0.43 / 0.72 / 60-of-60),
so the curve is an addition to the committed script, not a re-baselining of it.

### `--ac-scan` output (re-run after correction round 3)

```
stage=ideation
ac=AC-1 line=712 unevidenced=false citations=1
ac=AC-2 line=715 unevidenced=false citations=4
ac=AC-3 line=718 unevidenced=false citations=3
```

All three resolve, none `unevidenced`, all three bold headings still open and close on one line.
`citations` recorded and not acted on, per the standing evidence that the counter is sensitive to
document content outside the AC it reports on.

### Summary

Both captain-held items are applied and their consequences propagated. The ablation is now a
tree-wide, span-level spec — 11 CUT and 3 KEEP spans across `SKILL.md`, `review-triage.md`, and
`learned-patterns.md` — and the proof of removal is verbatim span match with the keyword grep
demoted to a canary that can only fail a build, never pass one.

Nothing here rests on an argument where a measurement was available. The keyword post-condition's
unsoundness is not asserted but shown against the real tree: 4 of 11 CUT spans carry none of the
four keywords, and the arm that removes only the keyword-bearing ones passes the old check while
still shipping the gate's failure-class table and its append-to-every-agent-prompt blockquote. The
restated effect model is likewise a curve that was run, and it answers both open directions at once
— larger treatments are covered, and the knee at +1-to-+2 findings/run is the number the `tm`
non-transfer residual needed.

Two things the gate should rule on rather than accept silently. **The sweep found a KEEP the
dispatch did not name**: `learned-patterns.md:9-11` ("never per-finding", for cross-model
arbitration) is the same naming trap as `SKILL.md:143` one file over — the obvious widening of the
canary to `fan-out` or `per-finding` would ablate arbitration alongside the quote gate. And **S11's
file is not loaded on the ordinary path**: there is no `Read → …/learned-patterns.md` directive in
`SKILL.md`, only a D1 auto-append target and two "see" pointers, so the ablation's effect properly
rests on S1-S10 with S11 additive when a run follows the pointer. Both are corrections to premises
this round was handed, recorded rather than quietly absorbed.

## Stage Report: implementation

- DONE: `review-ablation.sh` exists with `arm` / `run` / `compare`, built RED-before-GREEN with the RED output recorded, and every assertion added appears as a failure in that RED run.
  Commit `41d9573`. RED digest, taken with no implementation on disk: **`0 passed, 55 failed`**. The first RED run read `1 passed, 54 failed`; that single green assertion (`C2b`, which compared an empty verdict against an empty string) held in the pre-fix world too, so it was rewritten to pin the literal `runs_compared` = 18 and the digest re-taken. The `run` group (6 assertions) was added after GREEN and falsified separately — see the last checklist item. Final: `61 passed, 0 failed`.
- DONE: Test-plan items 1-4 pass: the four comparator fixtures pinned to the exact enumerated values, the arm-builder span-match post-condition tests (including the arm that keyword-grep accepts and span-match must reject), the five false-null guards plus their must-accept positive control, and ShellCheck v0.9.0 via docker.
  Item 1 (28 assertions): all eight fixtures pinned to `sizing-simulation.py`'s exact enumeration — floor `(2/20)^3`=0.001 and `(2/6)^3`=0.037037, superset `T`=1/3, joint must-flag/tokens-only/identical/all-empty. Item 2 (16): the keyword-only arm is rejected naming S2, S3, S4, S10. Item 3 (11). Item 4: `shellcheck v0.9.0` via docker exits 0 — it exited **1** on first run (two SC2015 at `review-ablation.sh:89,214`), which is the check the local build would not have caught. Full pre-existing suite unaffected: 305 / 139 / 213 / 135, 0 failed.
- DONE: Every check written carries its two-line provenance record — the independent authority it reads and the defective artifact that must fail it — with that artifact constructed and the check observed RED on it before any GREEN is trusted.
  Table below. Every negative case is a constructed defective artifact whose rejection is the assertion; each group also carries a positive control, so no check is merely always-reject.
- DONE: Re-verify `kc-pr-flow/` against the audit SHA `f4f4840` before building arms.
  `git diff --stat f4f4840 HEAD -- kc-pr-flow/` empty; `span-match-demo.py` re-run against the worktree tree — all 14 spans match their pins, no drift, no line number hand-adjusted.
- DONE: Keep receipts and manifests durable as they land.
  `run` writes the manifest before launch and collects to `<out-dir>/{manifests,receipts}/<arm>-<pr>-<run>.json`; `compare` reads a directory, so a part-finished experiment is re-enterable.
- SKIPPED: Test-plan item 5 — the 27 real headless runs (~$68).
  Out of scope for this stage by dispatch; it belongs to validation. No model was run, so nothing was drawn against the ≤$90 envelope.

### Provenance record — what each check reads, and what must fail it

| Check | Independent authority it reads | Defective artifact that must fail it |
|---|---|---|
| 8 comparator fixtures | `sizing-simulation.py` exact enumeration, a different implementation written at ideation | an inverted, one-sided, or mis-enumerated statistic — F1 fails if inverted, F2/F2b if the assignment space or label-swap collapse is wrong, F4 if `T` reverts to signed, F6 if max-T flags every dimension when one moves |
| span pins | the generated `review-ablation-spans.tsv` sidecar, cross-checked against ideation's `span-pins.txt` | a tree reworded inside S10's range (B3) |
| CUT-span absence | the **enumerated** span table, not the applied patch set | the arm removing only the 7 keyword-bearing spans (B4) |
| KEEP-span survival | the enumerated K1/K2/K3 rows | an arm that also cuts K2, the collator table (B5) |
| S6 surviving half | the literal `**Apply confidence gates**` in the spec | a span table whose S6 row is mistyped `cut` (B6) |
| removal uniqueness | the baseline text's own occurrence count | a tree with S1's line duplicated (B1) |
| keyword canary | the K1 whitelist | a gate sentence appended to a file the table does not enumerate (B7) |
| receipt freshness / arm / experiment | the **runner-written manifest**, not writable by the receipt's author | receipts with a rewritten `nonce` (C3a) and with `written_at` before `run_started_at` (C3b) |
| missing receipt | the manifest's `expected_receipt_path` | a deleted receipt (C2) and a stub agent that exits 0 writing nothing (R2) |
| duplicate | canonical receipt JSON minus `{run_index, slot_index, written_at}` | a receipt copied across runs (C4) |
| provenance | the whole experiment's receipt set, not the compared pair | one substituted `model_id` (C5), one rewritten `driver_prompt_sha256` (C5b) |
| mis-arming | the `--mode` on the invocation | equal `skill_sha256` under AB (C1) and differing under AA (C1b) |

**Falsification actually run, not asserted.** AC-3's own named falsifying edit — make the receipt loader default a missing file to `{"findings": []}` — was applied to `review-ablation.sh` and the suite re-run: C2 and both R2 assertions went **red**. The edit was then reverted. This is the evidence that the false-null guards are not passing by construction.

### Two things to flag rather than quietly absorb

- **The entity body misquotes K1.** It renders `SKILL.md:143` as "Step 2.5 builds a **verification gate** from explicit concerns"; the file has no bold — "Step 2.5 builds a verification gate from explicit concerns". The implementation matches the file, not the body, and the canary whitelist depends on that exact string. Verified: arm B has exactly one residual keyword hit, and it is this whitelisted line. The body's quotation should be corrected; nothing in the build is wrong.
- **Two helper files, one CLI.** The design fixes "one script, `review-ablation.sh`". The CLI surface is one script; the numerics live in `review-ablation-core.py` (span builder + permutation test) because both need computation shell does not do, matching the existing `review-runtime-benchmark.sh` / `review-runtime-safe-io.py` pairing. This adds no dependency — the body already records Python 3.8+ and `jq` as current kc-pr-flow runtime dependencies. Flagged because it is a visible departure from a literal reading of the design.

### Summary

Built the harness the settled design specifies: `arm` proves its ablation by verbatim span match against the enumerated table (the keyword grep demoted to a canary that fails the build on a residual hit but proves nothing when clean), `run` writes the runner's manifest before launch and treats a receipt-absent run as FAILED rather than empty, and `compare` decides with one joint max-T permutation test over the full assignment space. The comparator's expected values come from ideation's enumeration script rather than from this harness's own output, and the span pins were regenerated independently and agree with ideation's sidecar on all 14. Test-plan items 1-4 pass (61 assertions), CI now runs that model-free half, and the 27-run acceptance is left to validation with the budget untouched.

**Round 3 — validation gate, 2026-07-28. Verdict: REJECTED, routes back to implementation.**

Cheap gates all passed: 61/61 unit assertions, ShellCheck v0.9.0 via docker exit 0, the sizing
simulation reproducing all eight pinned fixture values exactly, the span-match demo holding, and the
shipped span pins agreeing with ideation's independently generated `span-pins.txt` on all 14 spans.
The required adversarial spot-check was done correctly — the validator degraded `span_postcondition`
to grade only the applied patch set instead of the enumerated spec, **proved the edit landed** with a
unified diff plus a uniqueness assertion before running, and the suite went red on exactly the
load-bearing case (B4, the arm removing only the seven keyword-visible spans). **The span
post-condition is therefore not the fourth instance of the recurring defect.**

**V1 [Material] — instance four is in the diff, one layer above where everyone was looking.**
`cmd_arm` independently computes the true `skill_sha256` and writes it to `arm-manifest.json` before
any agent runs — and neither `run` nor `compare` ever opens that file. The mis-arming guard therefore
compares `receipt.skill_sha256` against `receipt.skill_sha256`: a value **self-reported by the agent
under measurement**. Demonstrated, not argued — `compare --mode AB` emitted a clean verdict over 18
receipts whose skill hashes were `000…0` and `111…1`, matching no arm tree ever built. AC-3(a)'s
guard is vacuous as shipped. The runner-written manifest carries nine fields; the four that decide a
verdict's validity — `skill_sha256`, `driver_prompt_sha256`, `model_id`, `arm_manifest_sha256` — are
not among them, although the runner holds all four at launch.

This is the fourth instance of the entity's structural attractor, and it landed **despite** a standing
constraint written specifically to prevent it. The constraint asked each check to name the independent
authority it reads; this check names a manifest that exists, is correct, and is never opened. The
lesson to carry: naming an authority is not reading one, and only an executed negative case
distinguishes them.

**V2 [Blocker] — the frozen 3-PR corpus does not exist, so AC-1 and AC-2 cannot be run.** The
reverse-recovery audit classified the corpus MISSING at ideation; the implementation commit ships no
corpus; `run` never checks out the PR it names; and only one PR was ever identified, whose single real
run wrote no receipt (the case that became AC-3(b)).

**This gap is the FO's, not the worker's.** The implementation dispatch scoped the stage to "build and
prove the machinery, do not run the 27-run acceptance" and never assigned the corpus to anyone;
validation then inherited an acceptance it had no corpus to run. Ideation listed the corpus in
`## Scope`, so the omission was in the dispatch, not the design. Recorded here because the failure
mode — a deliverable named in scope falling between two stage dispatches — is invisible to both the
checklist accounting and the AC cross-check, which each verify their own stage.

Spend against the ≤$90 envelope: **one pilot run** (~$2.53), bought deliberately to establish whether
the runner works at all rather than assert it either way. The 27-run acceptance was never started, so
~$87 of the envelope remains. A probe was still executing when the stage reported.

**Validation, reviewer panel — four further findings on `41d9573`.** Citations spot-checked against
the on-disk files; the reviewer verified the `claude` CLI flags against `claude --help` rather than
trusting the script's own comments.

- **V3 [Important] — `run` never checks the headless invocation's exit code**
  (`review-ablation.sh:181-196`). `rc` is captured only to decorate an error message when the receipt
  is empty; it is never itself a failure condition. Because the receipt path is deterministic and is
  not cleared before invocation, a retry whose `claude` call crashes while a prior attempt's non-empty
  receipt is still on disk makes `run` **report success and print the stale path**. `compare`'s
  staleness guard catches it at the end — which is the point: an operator can burn most of an 18- or
  27-run budget believing each slot succeeded, then have the whole batch rejected. Operationally the
  sharpest of the four, given the ≤$90 envelope.
- **V4 [Important] — `remove_span`'s precondition validates a different string than it mutates**
  (`review-ablation-core.py:166-176`). It asserts `body.count(text) == 1` but replaces `text + "\n"`.
  A span that occurs once without a trailing newline (a span at true end-of-file) makes `.replace()`
  match zero times and write the file back unchanged, with no exception. `span_postcondition` does
  catch it, so no wrong verdict is produced — but it surfaces as "CUT span still present" and points
  the diagnosis at the resolver rather than at a newline mismatch. Not reachable today (`SKILL.md`
  ends with a newline and S8 is at `:1855`, well short of EOF); latent for any future EOF span.
- **V5 [Important] — the S6 removal text is a module constant, not read from its span row**
  (`review-ablation-core.py:50`, applied at `:278`). `S6_REMOVE` is applied to whatever row has
  `kind == "cut_sub"`. One such row exists today, so it is harmless now; a second would silently
  attempt to remove SKILL.md's text from the wrong file. It undercuts the design's own insistence that
  the enumeration table is the single source of truth.
- **V6 [Proof Policy #6] — an unenforced absolute in a code comment** (`review-ablation.sh:108-111`):
  the manifest is "never writable by it". Nothing enforces that — the invocation at `:181-183` passes
  no `--disallowedTools`, no `--add-dir` restriction, no sandbox flag. The only thing keeping the agent
  out of the manifest is a **prose instruction in the driver prompt**. In an entity whose founding
  premise is that prose has no test, the freshness authority is guarded by prose. Either name a real
  enforcement point or write the bounded claim. Rule 6 binds code comments precisely because no gate
  reads them, and this is the fifth instance in this entity of a check resting on something it does
  not actually control.

Statistics core reviewed end to end with no logic bug found: assignment 0 is genuinely the observed
labelling, `agreement_D`/`scalar_D` are symmetric under label swap, and `p_dim` compares each
dimension's observed z against the null of the **max** over dimensions — the correct single-step
Westfall-Young max-T construction, which is what actually delivers FWER control. The reviewer declined
to certify it beyond that and recommended a second statistician's read before the cost claims are
relied on operationally.

## Stage report: implementation correction cycle 3 — 2026-07-28

**Code commit:** `0600f95` (`fix(kc-pr-flow): bind ablation runs to independent evidence`).
This cycle repairs V1/V3/V4/V5/V6, supplies V2's exact frozen corpus, and stops before the
27-run acceptance because the corrected pilot cost invalidates the captain's ≤$90 envelope.

### Corrections made

- **V1 / runner-owned provenance:** `run` validates `arm-manifest.json`, independently reads the
  actual arm skill, hashes the fixed driver prompt, records the runtime-reported model, and writes
  all four pins into `kc-pr-flow.ablation-manifest/v2`. The receipt must match the manifest on
  `skill_sha256`, `arm_manifest_sha256`, `driver_prompt_sha256`, and `model_id`; `compare` reads
  provenance and arm hashes from manifests, not receipts. Fabricating every receipt's four pins
  consistently now fails.
- **V2 / exact corpus and checkout:** `review-ablation-corpus.tsv` freezes exactly:
  PR #17 `4489933ddf5237187c4866ab45bdecc5bdb2d0f0..f3aed43341d5fe4616d76ba02946bd4913ae260e`;
  PR #19 `d62f2c6659d76799994482dd58be2dc2b05fb3ea..031b4908cf405724b2ed7d1b829f3c001eea7aa2`;
  PR #50 `536be3e7d7d8371a9e84b693804407ea1b54bc60..7c448243c0512d137a47cdf36a9b255658f096a3`.
  `run` rejects any other tuple before launch, creates a clean detached shared clone at the pinned
  head, proves the base and head commits, hashes `base...head`, and fails if the agent changes HEAD
  or the checkout.
- **V3 / stale retry:** deterministic receipt and runner-output paths are cleared before launch;
  every non-zero headless exit fails immediately; `is_error:true`, absent/unparseable receipts,
  incomplete runtime usage, and missing/ambiguous runtime model IDs also fail.
- **Runtime-owned accounting:** usage, cost, wall clock, and actual model are normalized from the
  terminal Claude JSON into the receipt. Agent-authored values are not accepted as accounting.
- **V4 / EOF removal:** `remove_span` validates and removes the same exact bytes, with an optional
  trailing newline rather than assuming one exists.
- **V5 / table-owned substring:** the span table now carries each `cut_sub` removal string. The
  module constant is gone, and a second `cut_sub` in another file proves row-local behavior.
- **V6 / bounded claim:** comments now say the manifest is a separate runner-authored path but not
  an OS-enforced trust boundary. The receipt directory is explicitly added for the headless run;
  no comment claims the manifest is "never writable".
- Both workflow path filters include the new corpus file. `kc-pr-flow/CLAUDE.md` records the exact
  corpus and checkout/provenance contract. Every changed file serves V1-V6 or V2's CI/documentation
  surface; there is no unrelated implementation diff and no version bump.

### RED → GREEN evidence

- V1 provenance guard: **RED 10 passed / 4 failed**, then **GREEN 14 / 0** after receipts were checked
  against runner-owned skill, arm-manifest, prompt, and model pins.
- V4/V5 arm builder: **RED 16 / 2** on true-EOF removal and a second `cut_sub`, then
  **GREEN 18 / 0**.
- V3 and V6 runner group first exposed the missing arguments, accepted stale crashed receipt, and
  unenforced absolute; runtime-accounting tests then went **RED 18 / 2**; changing into the pristine
  checkout exposed relative arm/output paths at **RED 15 / 5**. Absolute runner paths, hard exit
  checks, and terminal-JSON normalization finish at **GREEN 20 / 0**.
- The complete model-free harness suite is now **80 passed / 0 failed** (up from 61 assertions).

### Sequential corrected pilot gate

All corrected pilots use one experiment (`50af1d49-dbe1-4e2f-9132-2a799e1a11e9`), one nonce
(`b20928db-edc3-475c-b2d0-b2ee8470bb9b`), arm A skill
`24aafc1f97b5c86704ce70ea94c0bc62ca4bfac7f29c6159c54a4f656bf1990d`, arm manifest
`34788f7f25ff0ddab75974f3233559ba745b6527a3e8196f546de5ddf56793da`, driver prompt
`4ca65d793b973d921b8956ea12ea6576d0e7b2c8a31ee8601192f2e11494d1fa`, and runtime model
`claude-sonnet-5`. They ran sequentially and each produced at least one posted-tier finding:

| frozen PR | findings | runner cost | wall clock | receipt sha256 | manifest sha256 | diff sha256 |
|---|---:|---:|---:|---|---|---|
| #17 | 9 (2 CRITICAL, 5 HIGH, 2 MEDIUM) | $9.016940700000003 | 1,514,908 ms | `9559ddd5a8e1802990930147a1b2678d30cd8e56d893184d3dea8de0162ff97a` | `e1500267c8c3c2211aca6da6c15bcc317d35d7812b34aad866058035c351e4eb` | `fdc80f1e7df0fe220f32b6cb89f403548acf6b791bfff044ef3e8b084d61b2a6` |
| #19 | 1 MEDIUM | $4.329564000000001 | 580,736 ms | `d1b6380283a2c290c59147dd52a3698723b0c9374b8d0f3ac838585afb6f8e38` | `8959c41dc1ce2711a4a3321a26c213f20199e430de058f04d7f31fc3218655a4` | `1b8dd1659efb31ff496063dcd0655eddc070a1eeb372e23d922b1b2492a1d0f6` |
| #50 | 4 (1 HIGH, 2 MEDIUM, 1 LOW) | $15.93819315000001 | 2,154,438 ms | `cf84f4547ffe8d55015b04dc4444b4b31584db793c82fa8c1d0b8d548dfd5c42` | `b3ea51d30d42b6eb0336d4dbd3cb1a6b9e86c6e1895b1eabcd480533afda414b` | `f70ffdb16f8cb0a79cba04e3c65123035afd66bc69559b9b0e6f31a975c34176` |

The first attempted pilot series is **invalidated and retained only as failure evidence**. `run`
changed into the frozen checkout while `--plugin-dir` was still relative, so Claude could load the
installed skill (`ca15c6ec02dc965922e531da0a3371eaa985eea0193b803fc24b9c7cf8d0a1ed`)
instead of arm A (`24aafc…`). PR #17 and #19 nevertheless cost $5.622738300000001 and
$2.8017971999999993 according to terminal runner JSON. The invalid PR #50 attempt was interrupted;
its runner file is zero bytes and its cost is therefore unknown. A later zero-finding receipt is
untrusted residue, not a completed run. The corrected absolute-path test went RED before the fix and
all three valid manifests record the intended arm hash after it.

### Budget gate — acceptance not started

- Corrected three-pilot total: **$29.284697850000015**; mean: **$9.761565950000005/run**.
- Straight 27-run projection at that observed mean: **$263.56228065000016**. Even crediting these
  three pilots toward the matrix leaves 24 projected runs at **$234.27758280000012**.
- Known spend is at least **$40.239233350000015**: validation's earlier ~$2.53 pilot, the two
  invalid completed attempts ($8.4245355), and the corrected pilots ($29.284697850000015), plus the
  unpriced interrupted PR #50 attempt. Against ≤$90, remaining authority is no more than
  **$49.760766649999985**, and is lower by that unknown charge.

Therefore the 27-run AC-1/AC-2 acceptance was **not launched**. The pilot corpus gate passed, but
the price gate did not. Validation must obtain an explicit captain budget reauthorization or apply
the recorded cut-to-scope fallback; implementation does not silently extend the envelope.

### Fresh exit verification

- `review-ablation.test.sh`: **80 passed, 0 failed** after the final workflow correction.
- `review-runtime.test.sh`: **305 passed, 0 failed**.
- `review-post.test.sh`: exit **0** (the harness's expected reconcile diagnostics are on stderr).
- `review-shadow.test.sh`: **213 passed, 0 failed**.
- `review-runtime-benchmark.test.sh`: **135 passed, 0 failed**.
- Docker `koalaman/shellcheck:v0.9.0` over the documented runtime files plus
  `review-ablation.sh` and `review-ablation.test.sh`: exit **0**.
- No-bytecode Python compile and native `git diff --check`: exit **0**.

AC-3's corrected false-null machinery and the frozen pilot precondition are implementation-proven.
AC-1 and AC-2 remain acceptance-pending because their required 27-run verdicts were intentionally
not purchased outside the approved budget.

## Note: harness code integrated to main while parked — 2026-07-30

The entity stays `backlog` and stays parked. What changed is where its code lives: the two product
commits that were only ever on `spacedock-ensign/skill-ablation-harness`, plus the AC-3 sizing and
span-match artifacts that were only ever on `iamcxa/ac3-split-pr-review-agent-native`, were
restacked onto `ec9502c` as one integration branch, `iamcxa/review-kit-ablation-integration`, and
landed as PR #111, squash-merged by the captain at `7bdb8c4`. Nothing about the acceptance changed:
AC-1 has no A/A verdict and AC-2 has no ablation-detection verdict, so this harness still does not
authorize `tm`, `fa`, or `sk`, and re-entry still requires an explicit new compute envelope.

Verified on the landed merge commit, not only on the branch: `review-ablation.test.sh` 82/82 and
pinned ShellCheck v0.9.0 clean at `7bdb8c4`, and the merged tree is byte-identical to the reviewed
head `e2ebda9` on every path the PR touched.

Restacking surfaced one repair the park had hidden. The span table was enumerated at `f4f4840`;
merged PR #82 (`85959dc`) then deleted `S8`, the `SKILL.md` tail restatement of the pre-emit gate,
as one of its 31 clause-complete duplicates. Against the current tree the table failed closed on
`S8` and 30 of the 80 harness assertions failed with it. The table was re-derived rather than
hand-adjusted: every surviving span matched its `f4f4840` text byte-for-byte at unchanged
coordinates, so every pin is unchanged; `S8` is retired and its id is not reused; the cut set is 10
and still names every statement of the gate in `kc-pr-flow/`. Harness assertions are back to 80/80
at the integration head.

Two prose claims were corrected in the same pass. `kc-pr-flow/CLAUDE.md` priced one verdict at 18
runs / ~$46, both figures derived from the discredited `$2.53` spike; it now states the
pre-registered 27 runs at the measured `$9.76/run` mean, names the spike as not a cost sample, and
says that this harness has no acceptance verdict yet. The `span-match-demo.py` artifact now records
that its table is pinned to `f4f4840`, gives the `git archive` command to reproduce it there, and
states that it is not re-pinned forward.

Exact-head review found one further defect, fixed in `e2ebda9` before the merge. `--arms` was read
as first-name-and-last-name, so on the pre-registered directory that holds `A`, `A'` and `B`
together, `--arms A,A_prime,B` dropped the middle arm and returned a real, plausible A-vs-B verdict
for a comparison nobody asked for — which would have been a wrong acceptance verdict, silently. The
arity is now checked before the names are read; reverting the guard fails exactly the two new
assertions and nothing else. This is the class of defect the park's delay made cheap to find: the
harness had never been exercised through a merge gate before.

The `product` and `sprint` frontmatter was added under the product-local sprint contract
(`701c664`), as the captain-designated owner annotating a released parked entity.
