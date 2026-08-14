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

S1 shipped all three: #110 (`58d6969`), #88 (`8634d89`), #91 (`3cbdb48`).

### Sprint S2 — a green artifact means what it says

End value: no artifact this pipeline emits asserts something the pipeline did
not observe. Today three separate outputs do — a recorder reports
`first_navigation.status=verified` about a profile it never read back, a run
reports `Executed flow EXACTLY as written` after improvising past a step, and an
issue records a capability ceiling the instrument does not actually have.

The sprint is ordered by **the direction of the lie**, weighted by cost. An
output that claims more than it observed is worse than one that fails, because a
reviewer citing it cannot tell it apart from an output that was earned. That
ordering puts the two false-`verified` defects ahead of the false-negative one,
and puts the flaky test first only because it is the cheapest item and every
later item's green depends on it.

Two of these are captain rulings taken as assumptions rather than open
questions; both are recorded here so they can be bounced rather than discovered
in a diff. **(1)** `--no-compile` forfeits the right to any fidelity claim — the
compiled script is the fidelity authority, and a run that disables it reports
`unverified`, not `EXACTLY`. **(2)** the `>> nth=N` ban **stays whole**, and the
migration for the 39 corpus occurrences is `css_selector:` rather than a
`:nth-of-type(N)` rewrite.

Ruling (2) reverses the direction this sprint was first drafted with. The draft
said narrow the ban to the interaction path, on #124's reasoning that the
visibility path already translated the chord correctly so banning it there was
over-broad. That reasoning was true of the pre-#91 tree and is not true of this
one: after #91 mapped visibility does not translate selectors at all — it
requires `css_selector:` and fails at resolve without one. So no path handles the
chord correctly anymore, the asymmetry that made a single rule unable to speak is
gone, and there is nothing left to narrow toward.

The same change makes #124's hard question moot. It worried that
`:nth-of-type(N)` is not semantically equivalent — different index base, siblings
under a parent versus the matched set — and that a codemod getting it wrong
silently retargets elements. None of that has to be decided: 37 of the 39
occurrences carry no `css_selector:` today, so any of them used for mapped
visibility already fails to compile under #91 independently of the chord. Adding
`css_selector:` discharges both requirements at once, after which deleting the
chord is a text edit with no semantic content.

| # | issue | scope |
|---|-------|-------|
| 1 | `#122` | Make the TERM-ignoring-descendant case wait on an observable condition, and assert the timeout contract separately from its arrangement, so a loaded machine cannot fail the precondition and read as a regression. |
| 2 | `#150` | Retract the capability-limitation framing against a live probe, document the `network` subcommands the instrument already has, and state per-step what it can and cannot evidence. |
| 3 | `#149` | Make `first_navigation.status=verified` contingent on a positive observation taken after navigation, not on the init script having attached. Attachment is evidence about the recorder, not about the profile. |
| 4 | `#148` | Give a run a step-level deviation ledger, make the closing assertion conditional on it, and retire the `EXACTLY` vocabulary from the path that cannot check it. |
| 5 | `#121` | Prove or disprove that the sole `selectorToA11yPattern` emission site is unreachable post-#91; delete the branch if so, otherwise land one snapshot-pattern authority both branches call. |
| 6 | `#124` | Rule on the ban's scope now that #88 supplies the migration path, and give the surviving rule an enforcement point that a consumer repo actually runs. |

Sequencing notes. #150 is second rather than fifth because the live probe already
refuted its premise, so most of it is a retraction and a reference page — it does
not compete with #149 for the same files. #149 precedes #148 because it
establishes the pattern #148 reuses: a status word is earned by a post-hoc
positive observation, never by a precondition having been arranged. #121 dropped
in severity when #91 landed — its defect now sits behind a branch comment
claiming unreachability, so the first deliverable is the proof, not the fix.

Exit: every `verified`/`EXACTLY`-class assertion in a shipped artifact names the
observation that earned it; the suite's verdict is attributable to behavior under
load; and the per-step evidence the instrument can guarantee is written down
where a downstream contract author will read it before writing the contract.

Out of scope: SQL and server-stderr evidence (outside the browser boundary by
construction — S2 documents the boundary rather than crossing it), an
`agent-browser` version bump, the multi-match visibility contract itself (shipped
in #91), and consumer-repo mapping migrations beyond what the #124 ruling
requires.

#### Outcome — five shipped, one part-shipped and still open

S2 shipped #122, #150, #148, #121 and #124 in `fe3c9f4`. Two of those turned out
not to be the issue as filed: #150's premise was refuted by a live probe (the
instrument does capture full HTTP bodies and retains them across navigation, it
was simply undocumented), and #122 carried an unnamed sibling in the same file
that fails the same way under load.

**#149 is the exception and stays open.** It asked for `verified` to become
contingent on a positive post-navigation observation. What shipped instead is the
receipt saying, in `first_navigation.profile_state`, that `verified` covers
navigation continuity and not the profile's contents — the false claim is gone,
the measurement was not built.

A caller-declared detector was built and reverted. Seven cross-model gate rounds
returned findings against it in every round that contained it — the predicate, the
polling, the page binding, the failure recording, the wiring — and none against
the disclosure. Round three found the documentation's own example appending to a
variable that existed nowhere but that document, so a caller following it would
have installed nothing while believing otherwise: the sprint's own defect class,
inside the fix for it. A later attempt to retrofit the disclosure onto legacy
receipts turned read-only command paths into writing ones and made a `snapshot`
able to erase a peer's `last_navigation`, so that was withdrawn too and the claim
bounded instead.

The rule that kept applying is the kernel's: an absolute either names its
enforcement point or becomes the bounded claim the artifact supports. Three times
in one issue the correct move was to shrink the claim rather than grow the
mechanism.

**What the exit criterion did and did not get.** "Every `verified`/`EXACTLY`-class
assertion names the observation that earned it" is met for `EXACTLY` (#148) and
for the trace suite's verdict under load (#122). For `verified` it is met only in
the weaker sense that the assertion now names what it does *not* cover. Anyone
reading this sprint as having closed the false-`verified` class should read #149
first.

## `kc-dev-flow`

### Sprint S1 — prove the runtime, then shorten the route

Captain-approved order for the next single-release batch:

1. `kc-dev-flow-published-tag-smoke-review`
2. `halve-dev-flow-cycle-time`
3. `subtractive-first-bounded-irreducibility`

Exit: all three items have exact-revision validation, implementation opens no
EM review loop, the published-tag smoke has a keep-or-remove disposition backed
by installed-runtime evidence, and the subtractive pilot rejects green or
`UNKNOWN` proposed additions. Hold the kc-dev-flow Release PR until the dependent
`repo-platform/S1` item below also exits.

### Sprint S2 — make evidence proportional without weakening delivery

Dependency: begin product delivery after the kc-dev-flow 2.4.0 Release PR and
the S1 release closeout finish.

Captain-approved order:

1. `issue213`
2. `kc-dev-flow-path-and-necessity`
3. `proportional-work-profile`
4. `roborev-implementation-exit`

Exit: external PR feedback is reconciled before completion, each proposed
control names the criterion and failed simpler route that earn it, and normal
ideation records one Captain-selected POC, Pilot, or Production receipt before
acceptance criteria expand. A declared RoboRev implementation exit records one
exact-revision observation or an honest non-green fallback without becoming
validation or delivery authority. All four items have exact-revision validation
and delivery evidence, and the product diff retains no generalized evaluation
platform. Hold the S2 Release PR until all four items exit.

### Sprint S3 — GitHub projection dogfood

Captain direction: begin immediately alongside the remaining `kc-dev-flow/S2`
validation work. S3 does not change S2 scope, ordering, or release hold.

Captain-approved sequence:

1. `spacedock-github-project-projection` (`qa`)
2. `spacedock-project-status-updates` (`16`), after the projection snapshot contract is stable

End value: a repository can install a one-way, idempotent projection of one
selected Spacedock workflow into one selected GitHub Project without making
GitHub lifecycle authority or requiring LLM-generated runtime facts. The first
dogfood maps `kc-claude-plugins/docs/dev` into user Project #1.

Projection exit: a disposable proof establishes the selected trigger and
authentication topology; a ten-entity Project #1 dry-run is reviewed before an
approved bounded subset is applied; an identical rerun performs zero mutations;
a view grouped by exact SD stage is usable; and every successful reconcile emits
a versioned deterministic status snapshot.

Status-update exit: the sibling classifies delivery, scope, and definition deltas
from that snapshot, produces deterministic reviewable drafts, refuses stale or
foreign baselines, and publishes only after explicit human confirmation.

Out of scope: GitHub-to-SD writeback, Relay or CarLove rollout, automatic Project
Status Update publication, and LLM-authored unattended payloads.

## `repo-platform`

### Sprint S1 — reduce the runtime reading surface

Dependency: run after `kc-dev-flow/S1` settles the review contract.

1. `workflow-readme-runtime-budget`

Exit: the runtime README is at most 700 lines, every retained mandatory clause
has an enforcement/owner mapping, recovery and stage-specific details are loaded
only when their trigger fires, and the contract suite plus fresh EM validation
pass. Only then may the pending kc-dev-flow Release PR be merged.

### Hazard carried forward

`spacedock status --ac-scan`'s citation counter is not trustworthy — an AC citing three paths
scored `0` while one citing a single path scored `2`. The README makes that scan a hard
precondition for the ideation gate, so the first entity through it will hit this. Record the scan
output and the discrepancy in the stage report rather than treating a `0` as a finding about the AC.
