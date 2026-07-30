# Roadmap — `docs/dev`

Sprint boundaries and sequencing only. This file never tracks task state; that is
`spacedock status --workflow-dir docs/dev`. Owner: captain, or the sprint commander
writing on the captain's direction.

Sprint numbers are product-local ordinals with no cross-product chronology or
rank. Use the qualified identity `<product>/S<number>` outside a product section;
for example, `kc-pr-flow/S5` and `e2e-pipeline/S1` may run concurrently without
sharing a sprint boundary.

A number is allocated only by a product sprint heading in this file, written by
the ROADMAP owner named above and accepted into `main`. Mentions and proposals
elsewhere do not reserve it; the first accepted heading for a product/number pair
wins. Bare `Sprint N` or `SN` references written before this contract's
2026-07-30 adoption resolve to `kc-pr-flow/SN`, because `kc-pr-flow` was the only
scheduled product. After adoption, a bare reference outside a product section is
a defect.

## `kc-pr-flow`

### Unscheduled prerequisites

Two work items belong to neither scheduled sprint and should not wait for one.
The third entry records a prerequisite that has already landed.

- **`zn` item 1** — `SKILL.md:405-413` prescribes a `codex exec` mode whose output file is 0 bytes
  for the whole run, so an in-flight dispatch reads as failed. One live occurrence bought a
  duplicate ~140K-token review. Measured here: `--json` grows within 4s, plain writes 59 bytes at
  the end. Pure bug fix, unrelated to slimming or strengthening.
- **`kj`** — `SKILL.md:1870` appends learned patterns to the public `learned-patterns.md`;
  `knowledge-capture.md:7` says LOCAL only and not the public file. Decide this before `v5` is
  scheduled: if LOCAL-then-promote was the intent, the 1193-line corpus is an accident and `v5`
  and `3w` are treating a symptom.
- **PR #75** — the tier estimate now says what it does not count. Merged.

### Sprint S4 — slim the kit

Opened 2026-07-27 on captain direction: **make the kit smaller before adding to it**, so that the
strengthening work lands on a smaller surface rather than being layered onto a 1884-line skill.

Two inputs support the order. Anthropic's context-engineering guidance for this model generation
favours progressive disclosure, fewer worked examples, and expressive interfaces over instruction
volume. And this workflow has already recorded that the kit's failure mode is accretion — it keeps
adding mechanisms to prove its prose workflow ran.

**Subtraction needs more evidence than addition, not less.** Adding a wrong mechanism wastes
tokens; removing a load-bearing one breaks the review, and prose has no test to catch it. That
asymmetry sets the sequence below: the harness comes first, and the cuts are ordered by how loudly
they would fail.

#### Sequence

| # | id | slug | risk | why here |
|---|----|------|------|----------|
| 0 | `5b` | skill-ablation-harness | — | Nothing else in this sprint can be judged without it. Deleting prose leaves all 935 assertions green; the only protected region is the 415-line adapter `review-shadow.test.sh:56` extracts. |
| 1 | `tm` | redundant-rule-removal | low | `SKILL.md:1844` onward restates Steps 5 and 6. Removing a restatement removes no information — and it is the natural first exercise of the harness: if A/A parity cannot be shown on a pure restatement cut, the harness is not ready. |
| 2 | `fa` | presentation-renderer | medium | ~104 lines of fenced presentation examples become a renderer with a closed input schema. Follows the guidance's "design the interface" over "show an example", and makes the output shape enforceable rather than imitated. |
| 3 | `sk` | reference-progressive-load | medium | Three references load whole on an ordinary path (246 + 162 + 1193 lines). `gh-api-patterns.md` already demonstrates named-section reads inside this same skill. First cut whose failure mode is a *quieter* review rather than a broken one. |
| 4 | — | overconstrained-rule audit | **high** | Not filed yet, on purpose. The guidance says replace rigid rules with judgment — but this kit's prose partly constrains five dispatched subagents that cannot recover an omitted constraint from the parent context. File it only if the harness proves able to measure this class. |

#### What is not cut, and why

An earlier draft of this sprint proposed removing "544 lines of example output" from Step 6. **415
of those lines are an executable Bash adapter** that `review-shadow.test.sh:56` extracts by
sentinel and sources; cutting it would have broken 213 assertions. The real presentation-example
total is ~104 lines.

Also staying, all of them load-bearing rather than decorative:

- the dispatched-agent output/coverage contract (`SKILL.md:341`)
- the baseline instruction given to every reviewer (`review-triage.md:181`)
- the pre-emit quote-the-source gate (`SKILL.md:973`)
- the PR-summary evidence requirements (`SKILL.md:941`)
- the confirmation menu and preview-before-post authorization boundary (`SKILL.md:1723`) — if this
  is ever rendered, the rendering becomes part of the contract and needs its own test
- the typed/shadow schemas

### Sprint S5 — strengthen, on the smaller surface

The entities that were Sprint 3's core, deferred deliberately so they land after the cuts rather
than before them.

| # | id | slug | note |
|---|----|------|------|
| 1 | `2t` | prescan-coverage-honesty | Builds the runtime refusal that makes a check unskippable; owns the coverage representation `1c` fills. |
| 2 | `1c` | prescan-script-evidence | Three mechanically decidable pre-scans stop needing a model; their evidence can contradict the agent's prose. |
| 3 | `q0` | reviewer-return-contract | The only mechanism that can retire the duplicated baseline verification — agents assert it in prose today (`review-triage.md:181`) and Step 5c re-reads every file with a finding (`compliance-audit.md:65`). |
| 4 | `v5` | learned-pattern-selection | After `kj` decides where D1 writes go. Pure subtraction, so it is the one item where fewer tokens genuinely fights finding defects. |

Then the measurement track — `qe` (token denominator) and `62` (quality numerator, pre-registered
known defects). They are **not** dropped, and the deferral has a cost stated below.

Following that: `x0r` as a bounded fixture spike, `dk` after `q0`, `3w` after `v5`.

### The cost of this ordering, stated plainly

`5b` answers "did this change move anything". It does **not** answer "how good is the kit". Only
`qe` + `62` answer that, and they now come after the cuts. So Sprint 4 can prove it broke nothing
measurable while remaining unable to prove the kit is any good — including unable to notice if it
was already worse than believed.

That is an acceptable trade for a slimming pass, because the reference is the previous version
rather than an absolute standard. It would **not** be acceptable for the strengthening work, which
is why `qe` and `62` sit before the point where anyone claims the kit improved.

### Superseded: Sprint S3

Sprint 3 (`zn item 1 → qe → 62 → 2t → 1c`) was committed 2026-07-27 and superseded the same day
by captain direction. Its thesis was measure-then-mechanize; the captain's is slim-then-strengthen,
on the reasoning that strengthening a 1884-line skill builds on the wrong base. No entity is lost
— `2t` and `1c` move to Sprint 5, `zn item 1` moves to the pre-sprint clear, and `qe`/`62` move
behind the cuts with the cost recorded above.

A cross-model review argued against recutting twice in one day, and it was right about the
evidence available at the time: the draft that prompted it contained two misclassifications,
including the 415-line adapter. This recut rests on a captain scope decision rather than on that
draft's analysis.

**Sprint 2** (`qh` → `11` → `n9` → `2t`) shipped `qh` only (#67, `f7dd1a0`): python3 spawns per
`post` 65 → 9, CI job 488s at 139 assertions against main's 512–598s at 137. Its remaining items
were resequenced when the captain named the four goals the kit is graded on.

### Runtime closeout before Sprint S6

`n9` then `11`, in that order. Real posting-correctness repairs that serve none of the review-kit
goals; `n9` breaks the shipped `gh` adapter on any ordinary busy PR, `11` needs a custom transport
or a future adapter.

### Sprint S6 — EM merge-readiness (interrupt, bounded)

End value: for one exact PR head, EM synthesizes existing CI, test, and review
evidence into `READY`, `NOT_READY`, or `UNKNOWN` with explicit confidence.
Humans remain sole merge authority; S6 adds no merge operation. The existing
§6c confirmation gate remains the interactive review-post authority.

S6 recovers `kc-pr-review`'s exact-head evidence, confidence, and human-confirmation
seams. It fills only the missing landing synthesis and daemon authority boundary.

| # | id | scope |
|---|----|-------|
| 1 | `4a` | Re-cut at ideation as the core EM merge-readiness gate. |
| 2 | `vf` | Reconcile daemon review-post authority with merge judgment; record no-change evidence if they are already disjoint. |
| 3 | `x0f` | Feed existing head-freshness and coverage-refusal evidence into the decision; add no daemon or repair framework. |

Exit: an exact green head can yield high-confidence `READY`; a moved head or
incomplete or unknown required evidence cannot yield `READY`. The gate never
auto-merges.

Out of scope: auto-merge, title/body auto-authoring, daemon redesign, ACP, a
general repair loop, mandatory agy routing, and cross-repo adoption.

## `e2e-pipeline`

### Sprint S1 — trustworthy browser diagnostics and selectors

End value: application E2E diagnostics retain owned Chrome for Testing lifecycle
proof from before the first navigation, while selector defects fail before an
expensive browser run and visibility verdicts cannot silently use first-match
semantics.

This sprint is independent of `kc-pr-flow/S4`–`S6`. Issue #110 is first because
it currently blocks a bounded CarLove diagnostic that cannot safely bypass the
shared browser runtime.

| # | issue | scope |
|---|-------|-------|
| 1 | `#110` | Add a fail-closed, runtime-owned pre-navigation recorder hook with hashed provenance, an allowlisted sanitized projection, first-navigation continuity proof, and scoped cleanup. |
| 2 | `#88` | Make compiler/dry-run enforce the same strict selector grammar as mapping lint, including a scoped legacy migration path. |
| 3 | `#91` | Define and enforce deterministic multi-match visibility semantics with evidence that distinguishes no match, all hidden, visible, and invalid selector states. |

Exit: every recorder stays inside the owned runtime and survives the first
application navigation; invalid selectors fail before browser startup; every
browser consumer shares one explicit multi-match visibility contract.

Out of scope: application-specific auth or tenant logic, raw browser-state/HAR
upload, browser-runtime ownership redesign, and the broader generated-output
hardening in #39.

## `repo-platform`

No sprint is scheduled in this roadmap yet. Shared workflow, CI, marketplace,
and root-configuration work uses this product's own sequence beginning at
`repo-platform/S1`.

### Hazard carried forward

`spacedock status --ac-scan`'s citation counter is not trustworthy — an AC citing three paths
scored `0` while one citing a single path scored `2`. The README makes that scan a hard
precondition for the ideation gate, so the first entity through it will hit this. Record the scan
output and the discrepancy in the stage report rather than treating a `0` as a finding about the AC.
