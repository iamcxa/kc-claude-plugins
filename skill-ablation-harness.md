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
except the receipt, never launch background work and defer on it, and stop at the end of Step 6a to
serialize the findings that passed the pre-emit gate as JSON. `--output-format json` yields the
run's usage and cost; the receipt yields the findings. Both go into one per-run record. A run whose
receipt is missing or unparseable is FAILED — never an empty finding set (see Spike 2).

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
- **Repeat and compare distributions** — adopted minimally, N=2 runs per arm. N=1 makes the noise
  model unmeasurable and any observed diff unfalsifiable; N=2 is the smallest N that yields a
  within-arm agreement to compare the between-arm agreement against.

### Pre-registered materiality rule — fixed now, before any cut

Per PR *p*, arm *X*, run *i*: `F(p,X,i)` = the set of candidate fingerprint IDs from that run.

- Within-arm agreement `J_within(p,X)` = Jaccard(`F(p,X,1)`, `F(p,X,2)`).
- Between-arm agreement `J_between(p)` = mean Jaccard over the 4 cross pairs `(A,i)×(B,j)`.
- Per-PR effect `D(p)` = mean(`J_within(p,A)`, `J_within(p,B)`) − `J_between(p)`.
- Combined statistic `S` = mean of `D(p)` over the M corpus PRs.

Jaccard of two empty sets is defined as 1.

**Decision rule.** Exact permutation test on run labels. Each PR contributes 4 runs labelled
(A,A,B,B); there are C(4,2)=6 relabelings per PR, so 6^M assignments in total. `p_perm` = the
fraction of assignments whose recomputed `S` is ≥ `S_observed`. **A change is material iff
`p_perm` ≤ 0.05.** With M=3 the minimum attainable `p_perm` is 1/216 ≈ 0.005, so the rule has
resolution to spare.

This pre-registers a *decision procedure* with exactly one free parameter (α = 0.05), fixed here.
There is no magic similarity number that a later result could renegotiate — which is the specific
way "a slimming pass talks itself into 'that difference doesn't matter'".

The rule is not circular against AC-1. Under A/A there is no true effect, so `p_perm` ≤ 0.05 should
occur at about rate α. AC-1 can genuinely fail: if within-arm agreement is systematically higher
than between-arm agreement for a reason that is not the skill — sequential drift, cache warming,
time-of-day model variation — A/A reports "material" and the harness is measuring its own
scheduling. That is exactly the failure AC-1 exists to catch. Mitigation baked into the design: the
12 runs of a verdict are interleaved by arm, not run arm-A-then-arm-B.

**Corpus precondition (guards the degenerate pass).** Each corpus PR must yield ≥1 posted-tier
finding in a pilot run, or it is replaced. Without this, an all-empty corpus makes every Jaccard 1,
`S`=0, and *both* ACs pass on a harness that measures nothing.

### Cost — the number this gate should be judged on

One A/B verdict = **2 arms × 2 runs × 3 PRs = 12 headless kc-pr-review runs.**

Measured, not assumed — one real headless run against a real PR was executed in the spike:
**$2.53, 7.6 minutes, 5.21M raw tokens (~141K uncached).** So one verdict is **~$30 and ~1.5 hours
of unattended compute**; the AC-1 and AC-2 acceptance runs share arm A's 6 runs, so proving both
costs **18 runs, ~$45**, not 24 runs. Full reconciliation of the raw-vs-uncached token figures — and
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
`tob-*` instructions are unmeasured). Any effect too small to reach `p_perm` ≤ 0.05 at N=2/M=3 — a
cut that moves one finding on one PR will not clear the bar.

**Sprint item 4 (overconstrained-rule audit) is in-class, conditionally.** An overconstrained rule
that fires too often produces *extra* findings, which moves the anchor set — detectable, *provided*
the corpus contains a PR that trips the rule. So item 4 is supportable, and its filing should be
conditioned on corpus selection rather than on the harness alone.

## Design determination

`required`. Two interfaces are being fixed and both are contracts other work will build on.

**Receipt contract** (driver → comparator), one JSON object per run:

```json
{"schema": "kc-pr-flow.ablation-run/v1",
 "arm": "A|B", "run_index": 1, "pr": {"repository": "...", "number": 63, "base_sha": "...", "head_sha": "..."},
 "skill_sha256": "<sha256 of the arm's SKILL.md>",
 "findings": [{"path": "...", "line": 0, "side": "LEFT|RIGHT", "category": "...", "claim_key": "...", "severity": "blocking|important|nit", "confidence": 0}],
 "usage": {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "total_cost_usd": 0.0},
 "wallclock_ms": 0}
```

`skill_sha256` is what makes an arm auditable after the fact — a receipt whose `skill_sha256`
matches the other arm's is a mis-armed run, and the comparator rejects the verdict rather than
reporting "no difference".

**Verdict contract** (comparator output): `kc-pr-flow.ablation-verdict/v1` carrying `s_observed`,
`p_perm`, `material` (bool), `flagged_dimensions` (subset of `anchor_set` / `severity_mix` /
`tokens`), plus the per-PR `D(p)` and per-arm token totals. `flagged_dimensions` is not decorative:
AC-2 requires the flagged dimension to be *named*, so a verdict that says "material" without
naming a dimension does not satisfy it.

**CLI surface**: one script, `kc-pr-flow/scripts/review-ablation.sh`, subcommands `arm` (build an
arm tree), `run` (one headless run → receipt), `compare` (receipts → verdict). Split this way so
`compare` is unit-testable against synthetic receipts with no model in the loop.

## Acceptance criteria

**AC-1 — An A/A run reports no material difference.**
Verified by: `review-ablation.sh compare` over 12 receipts from two identically-armed trees on the frozen 3-PR corpus, emitting `material: false` under the pre-registered rule (`p_perm` > 0.05), with both arms' `skill_sha256` recorded as equal. Falsified by: an A/A run emitting `material: true` — the statistic is then tracking run scheduling, not the skill, and no cut can be judged with it. Falsifying edit: interleave the runs arm-A-then-arm-B instead of alternating; if that flips the verdict, the noise model is wrong.

**AC-2 — Removing the pre-emit quote gate is reported as a difference.**
Verified by: an A/B run whose arm B deletes the pre-emit verification gate at `SKILL.md:975-984` **and its restatement at `:1855`**, emitting `material: true` with at least one entry in `flagged_dimensions`. Falsified by: `material: false` for that ablation — the harness cannot catch the cuts this sprint intends. Falsifying edit: ablate only `:975-984` and leave `:1855` in place; the design predicts a weaker or absent signal, and if the verdict is unchanged either way, the statistic is not reading the gate.

**AC-3 — The harness cannot report a false null.**
Verified by: two negative cases, each producing a non-zero exit and a named error rather than a `material: false` verdict — (a) a mis-armed pair, where both arms' `skill_sha256` are equal though labelled A and B; (b) a failed run, where one arm's run produced no receipt (the case actually observed in spike 2). Falsified by: `compare` emitting a normal verdict for either — the harness would then report "no difference" for a review that was never ablated, or never finished. Falsifying edit: make the receipt loader default a missing file to `{"findings": []}`; AC-3(b) must go red.

## Test plan

1. **Comparator unit tests**, no model in the loop, against synthetic receipts: identical fingerprint sets across arms → `S`=0, `p_perm`=1, `material:false`; disjoint sets across arms with perfect within-arm agreement → `S`=1, `p_perm`=1/216, `material:true`. These two are the "the check can fail" pair required by Proof Policy #2 — the first fails if the statistic is inverted, the second if the permutation enumeration is wrong.
2. **Arm-builder post-condition test**: build an arm whose ablation patch targets a string that does not exist; the builder must exit non-zero. This is the sprint's own silent-no-op failure, encoded as a test.
3. **False-null guard tests** (AC-3): synthetic receipts with matching `skill_sha256`; and a run record whose receipt file is absent. Both must exit non-zero with a named error. The second encodes the failure spike 2 actually produced, so it is a regression test for an observed defect, not a hypothetical.
4. **Lint**: CI's pinned ShellCheck v0.9.0 via docker, per `kc-pr-flow/CLAUDE.md:117-125` — `docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt koalaman/shellcheck:v0.9.0 …`; never the local build, which has retired checks CI still enforces.
5. **Runtime/E2E** (the ACs proper): the 18 real headless runs. Unit tests prove the comparator's logic; only these prove the wiring (Proof Policy #3).
6. **CI delta**: the comparator unit tests are fast and jq-only, so no job-margin risk. The 18-run acceptance is **operator-run, never in CI** — it costs money and needs credentials. The PR carries the verdict JSON as evidence; CI runs items 1-4 only. Stated explicitly so nobody later "helpfully" wires the expensive path into a workflow.

## Doc diff

`kc-pr-flow/CLAUDE.md` — add after the ShellCheck section:

> **Judging a cut to `SKILL.md`.** Prose has no test: deleting instruction text leaves the shell
> suites green. Before a cut to instruction text that could change what the review flags, run
> `scripts/review-ablation.sh` for an A/B verdict against the frozen corpus. One verdict costs 12
> headless review runs, so it is for load-bearing cuts, not mechanical ones. The verdict compares
> candidate-fingerprint sets, so it is blind to a cut that changes a finding's wording without
> moving its anchor.

No `PRODUCT.md` / `ARCHITECTURE.md` change — this adds a development instrument, not a product
behavior.

## Appetite

One worker session: ~90 minutes of authoring, plus a metered compute budget of **≤$60** for the
acceptance runs (measured basis: $2.53/run × 18 runs ≈ $45, with headroom for one re-run wave). On
overrun, cut scope to AC-1 + AC-3 — the comparator is provably sound and the false-null guards hold
— and park AC-2 with the arm trees and receipts retained so it is re-enterable. Never extend the
budget silently, never compress the acceptance runs to fit.

## Pre-mortem

**Criteria that pass without delivering value.** If the corpus PRs produce near-empty or
near-deterministic finding sets, `S`≈0 for both A/A and A/B, and both ACs go green on a harness that
measures nothing. Guarded by the ≥1-finding corpus precondition and by AC-2 requiring a named
`flagged_dimension`, but this is the failure to watch for at the validation gate.

## Implementation dispatch sizing

**ONE worker session.** It is one behavior — arm → receipt → verdict — with a single RED→GREEN loop,
and the expensive part is unattended compute (background launch, poll for completion), not developer
wall-clock. Splitting would pay cold-start twice, re-reading the README and this body, and buy no
parallelism the runs do not already have. Below all three split triggers.

## Out of scope

- Ground truth of any kind — that is `62`. This harness answers "did it move", never "is it good".
- Judging whether a detected difference is an *improvement*. The verdict is directional-agnostic by
  construction; a human reads `flagged_dimensions` and decides.
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

### One thing the FO must set

The body records `## Design determination` = `required` (receipt contract, verdict contract, CLI
surface), but the frontmatter `design:` field is still empty and ensigns do not write frontmatter.
The FO needs `spacedock status --workflow-dir docs/dev --read 5b --set design=required` before the
gate, or the stage definition returns the gate unread.

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
