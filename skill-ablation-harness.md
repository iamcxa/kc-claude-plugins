---
title: Cutting prose from a skill has no failure signal — build one before cutting
status: ideation
source: precondition for the Sprint 4 slimming track, filed 2026-07-27 on captain direction
design: required
id: 5b5gp68f2aq0bdrcf3q28jgg
started: 2026-07-28T08:10:24Z
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

Round 1 stopped at those two sites and that was still incomplete — the full enumeration is under
`### The AC-2 ablation` below.

### The AC-2 ablation — every site, cut or keep

Enumerated by grep over `kc-pr-flow/skills/kc-pr-review/SKILL.md` (1884 lines) at `origin/main` =
`f4f4840`, for `pre-emit` / `verification gate` / `quote-the-line` / `§6a quote`, then each hit read
in context. Round 1's arm-B spec named two of these seven.

| Site | Text | Cut or keep |
|---|---|---|
| `:975` | `**Pre-emit verification gate (run FIRST — kills the "claim about code that isn't there" FP class).**` + the rule paragraph | **CUT** — the gate proper |
| `:977-982` | the failure-class table (what must be quoted, self-refutes when) | **CUT** — the gate's operative content; leaving it leaves the instruction |
| `:984` | the demotion rule ("cannot quote a motivating line that survives the quote → confidence 4-5 → §6b") | **CUT** — the gate's consequence |
| `:986` | **Framework-meta nudge** — "quote the meta-construct, not the class body… the check is 'I read the source that creates this symbol'" | **CUT** — a sub-rule of the gate; surviving, it re-instructs quote-the-source for the largest FP subclass |
| `:988` | "**This gate** is inline, zero extra agents…" | **CUT** — dangling referent once `:975` is gone, and it re-asserts the gate's existence |
| `:990` | "Apply confidence gates **after the verification gate**" | **EDIT, not cut** — delete only the trailing clause, keeping "Apply confidence gates". Cutting the confidence gates entirely would ablate a second, independent mechanism and confound AC-2 |
| `:861` | §5.6a arbitration dispatch — "(reuse the **§6a quote-the-line evidence** — arbitrate on quoted code, not summaries)" | **CUT the parenthetical only** — an independent third site that instructs quote-the-line from the cross-model arbitration path; round 1 missed it entirely |
| `:1855` | Step-6 recap — "**Pre-emit verification gate before posting** — every CODE finding must quote its motivating `file:line` + verbatim source…" | **CUT** — the recap restatement |
| `:143` | "Step 2.5 builds a **verification gate** from explicit concerns" | **KEEP** — a *different* mechanism (Step 2.5's user-concern gate), not the pre-emit quote gate. A naive `verification gate` grep would cut it and ablate two mechanisms at once |

**Arm-builder post-condition — derived at build time, never read off this table.** This table is
provenance for the gate reviewer; it is not the arm spec's runtime input, because it goes stale the
moment `SKILL.md` moves a line. The builder MUST, at build time:

1. Grep the *baseline* tree for the site patterns (`pre-emit`, `quote-the-line`, `§6a quote`, and
   `verification gate` minus the explicitly whitelisted Step-2.5 sentence, matched by its full text
   rather than by line number) and record the hit set into the arm manifest.
2. Apply the ablation.
3. Assert the arm-B tree has **zero** residual hits for those patterns outside the whitelist, and
   that the whitelisted Step-2.5 sentence is still present and unmodified.
4. Assert the baseline hit set was non-empty and that every hit is accounted for as cut-or-edited —
   an ablation that silently matched nothing must exit non-zero (test-plan item 2).

## Proposed approach

Three seams to build, in order. Everything else is reuse.

**1. Arm builder.** Copy `kc-pr-flow/` to a temp tree per arm; apply the arm's ablation patch to
`skills/kc-pr-review/SKILL.md`; **assert the patch changed the file** (byte diff against baseline,
plus a post-condition that the removed span is absent at every site named in the arm spec) before
the arm is usable. Proof Policy #7 in its literal form: an adversarial edit must first prove it took
effect. The sprint has already paid for a spot-check edit whose target string did not exist.

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

**Sizing: N=3 runs per arm, M=3 corpus PRs.** Derived from the floor and the power measurement
below, not assumed.

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
`p_perm` = the fraction of assignments whose recomputed `T` is ≥ `T_observed`. **A change is
material iff `p_perm` ≤ 0.05.**

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
| A/A drawn from one noisy process, 200 independent trials | 3/3 | 8000 | — | fp rate **0.045** | not material — calibrated at α |
| A/A, same, at N=2/M=3 | 2/3 | 216 | — | fp rate **0.005** | not material |

The A/A rows are the "it can also not fire" half; the disjoint and superset rows are the "it can
fire" half. A statistic that always fired would show fp ≈ 1 on the A/A rows, and an inverted one
would show `p_perm` ≈ 1 on the disjoint row.

**Why N=3, measured rather than argued.** Simulating the AC-2-shaped effect (arm B systematically
emits 3 extra findings per PR on top of the same noise process), power at α=0.05:

| sizing | floor | power on the AC-2-shaped effect | acceptance runs | cost |
|---|---|---|---|---|
| N=2 / M=3 (round 1) | 0.037 | **0.40** | 18 | ~$46 |
| N=2 / M=4 | 0.012 | 0.83 | 24 | ~$61 |
| **N=3 / M=3 (adopted)** | **0.001** | **1.00** (median `p_perm` = 0.001) | **27** | **~$68** |

At N=2/M=3 AC-2 was a coin flip: the design would have failed roughly three times in five for want
of power, not for want of an effect, and the harness would have been declared unable to see a gate
removal it can in fact see. N=2/M=4 clears the bar but needs a 4th corpus PR sourced and pilot-run;
N=3/M=3 reuses the corpus already scoped and costs $7 more. Adopted: **N=3 / M=3**.

The power and calibration figures come from a Monte-Carlo model of the run process (stable core
findings plus sampled noise), not from real review runs — they size the design, they do not
substitute for AC-1. AC-1 is what tests the real noise process against this rule.

This pre-registers a *decision procedure* with exactly one free parameter (α = 0.05), fixed here.
There is no magic similarity number that a later result could renegotiate — which is the specific
way "a slimming pass talks itself into 'that difference doesn't matter'".

The rule is not circular against AC-1. Under A/A there is no true effect, so `p_perm` ≤ 0.05 should
occur at about rate α. AC-1 can genuinely fail: if within-arm agreement is systematically higher
than between-arm agreement for a reason that is not the skill — sequential drift, cache warming,
time-of-day model variation — A/A reports "material" and the harness is measuring its own
scheduling. That is exactly the failure AC-1 exists to catch. Mitigation baked into the design: the
18 runs of a verdict are **interleaved by arm, and the arm-to-slot assignment within each PR is
randomized and recorded per run** — interleaving alone fixes an ordering, which is a weaker
guarantee than exchangeability, and the permutation test assumes exchangeability.

**Corpus precondition (guards the degenerate pass).** Each corpus PR must yield ≥1 posted-tier
finding in a pilot run, or it is replaced. Without this, an all-empty corpus makes every Jaccard 1,
`T`=0, and *both* ACs pass on a harness that measures nothing.

### Cost — the number this gate should be judged on

One A/B verdict = **2 arms × 3 runs × 3 PRs = 18 headless kc-pr-review runs.**

Measured, not assumed — one real headless run against a real PR was executed in the spike:
**$2.53, 7.6 minutes, 5.21M raw tokens (~141K uncached).** So one verdict is **~$46 and ~2.3 hours
of unattended compute**; the AC-1 and AC-2 acceptance runs share arm A's 9 runs, so proving both
costs **27 runs, ~$68**, not 36 runs. Full reconciliation of the raw-vs-uncached token figures — and
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
`tob-*` instructions are unmeasured). Any effect too small to reach `p_perm` ≤ 0.05 at N=3/M=3 — a
cut that moves one finding on one PR will not clear the bar. The measured example of "too small":
an arm-B superset that adds one finding to each run but only in the *noisy* regime (`|D(p)|` ≈ 0.08)
does not reach the bar at either sizing; the same superset applied consistently (`|D(p)|` = 0.33)
clears it at both.

**Sprint item 4 (overconstrained-rule audit) is in-class, conditionally.** An overconstrained rule
that fires too often produces *extra* findings, which moves the anchor set — detectable, *provided*
the corpus contains a PR that trips the rule. So item 4 is supportable, and its filing should be
conditioned on corpus selection rather than on the harness alone.

## Design determination

`required`. Two interfaces are being fixed and both are contracts other work will build on.

**Receipt contract** (driver → comparator), one JSON object per run:

```json
{"schema": "kc-pr-flow.ablation-run/v2",
 "mode": "AA|AB", "arm": "A|B", "run_index": 1, "slot_index": 0, "nonce": "<per-experiment uuid>",
 "experiment_id": "<uuid, identical across all runs of one verdict>",
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

Four things changed from round 1's `v1`, each because `v1` did not actually work.

**The findings entry now carries what the reused canonicalization consumes.** `review_benchmark_fingerprint_id`
canonicalizes `{path, side, anchor_sha256, evidence_sha256, category, claim_key}` and its validator
(`review-runtime-benchmark.sh:330-336`) demands exactly that key set — `exact_keys([...])` plus
`(.evidence_sha256 | sha256)` and `side == "LEFT" or "RIGHT" or "FILE"`. Round 1's entry carried
`line` and no hashes, so the declared reuse would not have typechecked against its own validator.
`line` is retained as **display metadata only** and is excluded from the canonical object.

**Severity uses the skill's own vocabulary.** `SKILL.md:1852` fixes it: `CRITICAL / HIGH / MEDIUM /
LOW / NIT`. Round 1 invented `blocking|important|nit`, which would have needed a mapping nobody
wrote and would have silently collapsed CRITICAL and HIGH.

**`mode` is explicit.** See AC-1/AC-3 below — equal `skill_sha256` across arms is *required* under
`mode: "AA"` and *forbidden* under `mode: "AB"`. Without this field the two ACs contradict.

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

**Verdict contract** (comparator output): `kc-pr-flow.ablation-verdict/v2` carrying `mode`,
`t_observed`, `p_perm`, `material` (bool), `flagged_dimensions` (subset of `anchor_set` /
`severity_mix` / `tokens`), plus the per-PR `D(p)`, per-arm token totals, and the provenance pins
echoed from the receipts (`model_id`, `driver_prompt_sha256`, corpus base/head SHAs).

**What `material: false` certifies — and what it does not.** It certifies **no detected difference
on the measured dimensions (anchor set, severity mix, tokens)** at α=0.05 for the corpus, sizing,
and model recorded in the verdict. It does **not** certify "no behavioral change": a cut that
rewords what a finding says while its anchor and `claim_key` hold is outside the instrument's range
by construction, and so is any effect below the power floor. The verdict JSON carries this sentence
verbatim in a `certifies` field so it travels with the artifact rather than living only here.

**`flagged_dimensions` entry rules are computable, pre-registered here, not judgment.** Round 1 left
them undefined, which let AC-2's "named dimension" condition be satisfied vacuously. A dimension is
entered iff:

- `anchor_set` — the primary test on fingerprint sets returns `p_perm` ≤ 0.05. (This is the same
  statistic as the verdict; it is listed when it is what fired.)
- `severity_mix` — the same permutation procedure, run on a per-PR distance between arms' severity
  histograms over `CRITICAL/HIGH/MEDIUM/LOW/NIT` (total-variation distance on the normalized
  histogram, averaged over runs), returns `p_perm` ≤ 0.05.
- `tokens` — the same permutation procedure on per-run `usage.input_tokens + output_tokens +
  cache_creation_input_tokens` (the uncached total; cache-read is dominated by shared prefix and is
  not an arm property), using mean absolute difference of arm means, returns `p_perm` ≤ 0.05.

All three are the identical permutation machinery on a different per-run scalar or set, so one
implementation serves all three and one test covers all three. `material` is true iff
`flagged_dimensions` is non-empty; a verdict reporting `material: true` with an empty
`flagged_dimensions` is a comparator bug and must exit non-zero.

**CLI surface**: one script, `kc-pr-flow/scripts/review-ablation.sh`, subcommands `arm` (build an
arm tree), `run` (one headless run → receipt), `compare` (receipts → verdict). Split this way so
`compare` is unit-testable against synthetic receipts with no model in the loop.

## Acceptance criteria

**AC-1 — An A/A run reports no material difference.**
Verified by: `review-ablation.sh compare` over 18 receipts (2 arms × 3 runs × 3 PRs) from two identically-armed trees on the frozen corpus, every receipt carrying `mode: "AA"`, emitting `material: false` under the pre-registered rule (`p_perm` > 0.05) with `flagged_dimensions` empty. Under `mode: "AA"` the two arms' `skill_sha256` are **required to be equal** and `compare` exits non-zero if they differ — the mis-arming check is mode-dependent, which is what removes round 1's contradiction with AC-3(a). Falsified by: an A/A run emitting `material: true` — the statistic is then tracking run scheduling, not the skill, and no cut can be judged with it. Falsifying edit: order the runs arm-A-then-arm-B instead of randomizing slot assignment; if that flips the verdict, the noise model is wrong.

**AC-2 — Removing the pre-emit quote gate is reported as a difference.**
Verified by: an A/B run (`mode: "AB"`) whose arm B removes the pre-emit quote gate at **every site enumerated in `### The AC-2 ablation`** — `SKILL.md:975`, `:977-982`, `:984`, `:986`, `:988`, the trailing clause of `:990`, the `:861` parenthetical, and the `:1855` recap — with the arm manifest showing zero residual hits and the Step-2.5 sentence at `:143` intact; emitting `material: true` with at least one entry in `flagged_dimensions`. Falsified by: `material: false` for that ablation — the harness cannot catch the cuts this sprint intends. Falsifying edit: ablate only `:975-984` and leave `:861` and `:1855` in place; the design predicts a weaker or absent signal, and if the verdict is unchanged either way, the statistic is not reading the gate.

**AC-3 — The harness cannot report a false null.**
Verified by: five negative cases, each producing a non-zero exit and a named error rather than a `material: false` verdict — (a) a mis-armed pair under `mode: "AB"`, where both arms' `skill_sha256` are equal though labelled A and B; (b) a failed run, where one arm's run produced no receipt (the case actually observed in spike 2); (c) a stale receipt at a reused output path, detected because its `nonce`/`experiment_id` does not match the current experiment or its `written_at`/mtime predates the run's start; (d) one receipt content-hash appearing under two `run_index` values, i.e. a duplicated receipt inflating agreement; (e) receipts whose `driver_prompt_sha256` or `model_id` disagree across the set. Falsified by: `compare` emitting a normal verdict for any of them — the harness would then report "no difference" for a review that was never ablated, never finished, or never actually re-run. Falsifying edit: make the receipt loader default a missing file to `{"findings": []}`; AC-3(b) must go red.

**Residual degenerate paths, named and not closed.** Three failure shapes were raised and are *not* fully guarded by AC-3, recorded here rather than left unlisted: an early parseable `findings: []` written before the agent defers (indistinguishable from a genuine zero-finding run — the ≥1-finding corpus precondition makes it detectable at pilot time but not per-run); malformed individual findings silently dropped by the parser rather than failing the run (mitigated by failing the run on any unparseable entry, unmitigated for an entry that parses but is semantically wrong); and receipts mixed across experiments where `experiment_id` collides. These are the known residuals of the false-null guard, not oversights.

## Test plan

1. **Comparator unit tests**, no model in the loop, against synthetic receipts. Four fixtures, each pinned to a value computed by exact enumeration during ideation: identical fingerprint sets across arms → `T`=0, `p_perm`=1, `material:false`; disjoint sets with perfect within-arm agreement → `T`=1, `p_perm`=**1/1000** at N=3/M=3 (and **1/27** at N=2/M=3, asserted separately to pin the floor formula `(2/C(2N,N))^M`); a consistent superset (`A={x,y}`, `B={x,y,z}`) → `T`=1/3, `p_perm`=1/27 at N=2/M=3; and a **sign-flipped** case where between-arm agreement exceeds within-arm agreement by the same margin → identical `p_perm` as the positive case, which is the assertion that fails if anyone reverts `T` to the signed statistic. Together these are the "the check can fail" set required by Proof Policy #2 — fixture 1 fails if the statistic is inverted, fixture 2 if the permutation enumeration is wrong, fixture 2's N=2 variant if the label-swap collapse is not accounted for, and fixture 4 if the test is one-sided.
2. **Arm-builder post-condition test**: build an arm whose ablation patch targets a string that does not exist; the builder must exit non-zero. Plus the grep-derivation assertions from `### The AC-2 ablation` — the builder must exit non-zero when the baseline hit set is empty, when a residual hit survives in arm B, and when the whitelisted Step-2.5 sentence at `:143` was removed. This is the sprint's own silent-no-op failure, encoded as a test.
3. **False-null guard tests** (AC-3), one per case: synthetic receipts with matching `skill_sha256` under `mode: "AB"`; a run record whose receipt file is absent; a receipt whose `nonce`/`experiment_id` is stale or whose `written_at` predates the run start; one receipt content-hash under two `run_index` values; and a receipt set with disagreeing `driver_prompt_sha256` / `model_id`. All must exit non-zero with a named error. A sixth, positive control: the same fixtures with `mode: "AA"` and equal `skill_sha256` must be **accepted**, which is what proves the mode-dependent check is not simply always-reject.
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
> Read the verdict for what it says. `material: false` certifies **no detected difference on the
> measured dimensions (anchor set, severity mix, tokens)** for the corpus, sizing, and model in the
> verdict — it is never a certificate of "no behavioral change". A wording-only cut is outside the
> instrument's range by construction, as is any effect below its power floor.

No `PRODUCT.md` / `ARCHITECTURE.md` change — this adds a development instrument, not a product
behavior.

## Appetite

One worker session: ~90 minutes of authoring, plus a metered compute budget for the acceptance runs.

**The compute budget is restated here, not inherited.** Round 1 recorded **≤$60** on a measured
basis of $2.53/run × 18 runs ≈ $45 plus re-run headroom. That sizing was underpowered — measured
power 0.40 on the AC-2-shaped effect — so correcting it moves the envelope. At the adopted N=3/M=3
the acceptance is 27 runs ≈ **$68**, which does not fit under $60. The workflow forbids extending a
budget silently, so the budget is re-proposed explicitly for the gate to accept or refuse:

| | acceptance runs | run cost | re-run headroom | budget |
|---|---|---|---|---|
| Round 1 (recorded, underpowered) | 18 | $45 | $15 | ≤$60 |
| **Round 2 (proposed, N=3/M=3)** | **27** | **$68** | **$22 (~1 wave of 9)** | **≤$90** |

The delta buys power 0.40 → 1.00 on the effect AC-2 is built to detect; the cheaper N=2/M=4 route
(24 runs, ~$61, power 0.83) is available if the gate prefers to hold near the original number, at the
cost of sourcing and pilot-running a 4th corpus PR.

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
  symmetric in the arms — swapping the A and B labels leaves `T` and `p_perm` unchanged — so the
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
