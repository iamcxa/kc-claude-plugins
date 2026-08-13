---
name: kc-dev-flow-kernel
---

# KC Dev Flow Kernel

The kernel is a portable authority and evidence contract. It does not prescribe
a tracker, workflow entrypoint path, agent harness, CI vendor, PR host, or workflow
runtime. An adopter's chosen workflow README binds those roles in its Local Profile,
and the adopter vendors the kernel plus selected policy mods under that workflow's
`_mods/` directory.

## Authority model

- **Project context authority** explains what the product is, its architecture,
  and durable constraints. Reuse existing product and architecture sources.
- **Work-item authority** owns scope, status, dependencies, and acceptance
  criteria. Never create a second task universe.
- **Iteration authority** owns sprint membership and ordering. Capturing a task
  does not schedule it; a roadmap is strategy, not a task-status mirror.
- **Execution-state authority** owns stage transitions, gate receipts,
  worktrees, retries, and durable state.
- **Delivery authority** combines authenticated product delivery at the exact
  revision with durable work-item terminalization. A local pass alone is not
  delivery.
- **Observation is not authority.** Ledgers and metrics may explain and improve
  the flow, but missing observation cannot block delivery, reopen completed
  work, or authorize another action.
- **An instruction that contradicts the governing contract loses, and should not
  have been an instruction.** An actor told not to do what its stage or contract
  mandates resolves that conflict in favour of the contract, correctly. Where
  the instructing party has already discharged the obligation, it says so —
  naming the result, its author, and that the obligation is **met rather than
  skipped**. Check for this contradiction before concluding that an actor
  ignored an instruction.

## Lifecycle

The default lifecycle is
`backlog → ideation → implementation → validation → done`:

1. `backlog` captures a cheap seed. It performs no design and grants no sprint
   membership.
2. `ideation` makes the necessary product/design decision, defines value-level
   acceptance criteria, and names evidence able to fail. At normal ideation
   entry it activates `kc-dev-flow:choose-work-profile` when the bound receipt is
   missing or stale.
3. `implementation` works test-first inside approved scope.
4. `validation` uses fresh context and seam/runtime evidence appropriate to the
   claim. Unit tests alone do not prove wiring.
5. `done` follows exact-revision delivery plus durable terminal/archive state.

At normal ideation entry, before inherited backlog criteria are classified:
Re-read the exact work item and its `## Work profile receipt`. If it is valid and
its basis is unchanged, consume it without another question. If it is missing,
or the audience, lifespan, mutation boundary, authority need, or operational
commitment changed, invoke `kc-dev-flow:choose-work-profile`. The chooser has
recommendation and question authority; the actor already authorized by the Local
Profile and dispatch records the decision through the existing safe work-item
mutation path, syncs it, and re-reads the committed receipt.
Only after the committed receipt is re-read may inherited criteria be normalized or acceptance criteria be expanded.
Tasks already beyond ideation are not reopened without an observed promotion
trigger. The bounded mechanical-defect route that validly skips ideation does
not acquire this gate.

At ideation entry, inherited backlog criteria are hypotheses, not accepted
outcome constraints. The ideation actor classifies each as value, governing
constraint, or mechanism and preserves constraints explicitly imposed by the
captain or governing authority. It rewrites a mechanism-shaped criterion to the
value or failure it serves, or removes it. A mechanism may remain only when its
absence fails a named value-level criterion, the simpler route has proved
insufficient, and the selected route still exposes the hazard. When the selected
route structurally eliminates or bypasses the failure mode, its defense criterion
is superseded. Before the accepted outcome is recorded, work-item authority
records each inherited criterion's class and retain, rewrite, remove, or
supersede disposition; a governing constraint names its imposing authority, so
a later reviewer can read the normalization.

Use the smallest sufficient route. A bounded defect with a known cause and a
mechanical acceptance test may skip ideation, but it keeps the same acceptance,
validation, delivery, and terminal-state bars.

## Sprint continuity and autonomy

Within an approved sprint, the agent may resume the active item or select the
next committed, unblocked item using the declared iteration order. It may
implement, repair rejected evidence, and advance reversible green gates without
asking the captain to repeat approval.

The agent cannot author new scope, schedule an unscheduled item, accept a red
residual, make an irreversible decision, spend beyond its envelope, or merge
without the declared delivery authority. Empty committed work means the sprint
needs a scheduling decision; it is not permission to invent work.

## Route discipline

Once a route is accepted, the approved outcome contract is its destination. It
consists of the recorded end value together with each explicit non-goal,
value-level acceptance criterion, and falsifier recorded by work-item authority.
The agent cannot reinterpret it; only the captain may approve its exact revision.

The accepted route remains the default. Its identity is the plan's named
sufficient seam, counted surface set, and allocation of lifecycle obligations.

A surface is counted plan-locally by an observable lifecycle invariant and its
scope. It remains independent when its scoped lifecycle state can be violated,
reconciled, or rolled back independently, or can require a distinct decision or
action.
Host and owner are attributes, not identity keys; changes to bound authority stay
under the Authority model. Packaging, renaming, or relocation alone does not
establish elimination.
A claim of fewer surfaces supplies a plan-local pre/post mapping; a fresh reviewer
under Verification discipline challenges each independence condition above
against that mapping. Unresolved separability preserves the surface.

The agent must not change the route except to a compatible, sufficient replacement
when evidence satisfying Verification discipline shows either that the accepted
route cannot satisfy the approved outcome contract within its constraints, or
that the replacement has a strictly smaller surface set under that mapping.
Before execution, a fail-closed mechanical control already declared through the
Work Control Profile or a fresh reviewer evaluates cumulative change against the
last accepted route, not only against the immediately preceding edit. Each
route-change predicate must be enforced by that control or receive the fresh
reviewer's recorded `PASS` under Verification discipline. Neither form of route
proof authorizes a captain-owned delta; unproven reversibility remains
captain-owned under Sprint continuity. Captain acceptance does not substitute for
route proof.

A question, Ask UI answer, conversational agreement, reviewer suggestion, or
agent-authored option resolves only the ambiguity it names. It carries captain
acceptance only when the exact outcome, surface, scope, spend, authority, or
irreversibility delta is shown and explicitly accepted by the captain. The agent
must not act on that acceptance until the accepted change is recorded in and
re-read from the authority that owns the changed field or decision. A response
that lacks the exact delta has no route-change effect and must not be recorded as
accepted.

## Outcome discipline

- Every item names the end value it exists to produce. Each acceptance criterion
  names evidence able to disprove completion, including the concrete artifact or
  behavior change that would flip that evidence; if its author cannot name the
  falsifier, the criterion does not count.
- **Every new mechanism justifies its value and necessity.** It names the
  value-level acceptance criterion it serves, the simplest alternative
  considered, and why that alternative is insufficient. A harness orchestrates
  and observes the supported runtime; it does not reimplement the system under
  test.
- **An absolute names its enforcement point or becomes a bounded claim.**
  "Exactly", "only", "always", "never", "cannot", or "byte-for-byte", written
  into a reference, a code comment, or a commit message, names the mechanism
  that makes it true or is rewritten to what the artifact supports. An
  enforcement point is a permission check, a schema constraint, an unreachable
  branch, or a fail-closed check — not "I checked", and not its author. This is
  an authoring discipline, not an assertion that an automatic gate exists. Apply
  it to claims adopted from reports, reviewers, or contributors too, and record
  what was checked. **It governs factual claims regardless of grammatical form;
  classify by falsifier, not by wording.** If contrary execution would make the
  sentence false, it is factual and needs an enforcement point or bounded
  wording. If contrary execution instead violates a duty assigned to a named
  authority, it is a prohibition. "This branch cannot be reached" is factual;
  "never create a second task universe" assigns a duty to work-item authority.
  Rephrasing factual behavior as a command does not change its class.

For non-trivial brownfield work, apply this outcome-first route in order:

1. **Accepted outcome.** Name the end value, value-level acceptance criteria,
   constraints, and non-goals. Decompose from this contract without assuming
   the implementation is absent or that the task is a greenfield rebuild. When
   the current stage selects `_mods/journey-slicing.md`, carve along the journey
   using that local policy; its first slice is demoable and its layered
   alternative passes review while delivering nothing.
2. **Recover the existing seam.** Against fresh `origin/main`, apply the
   reverse-recovery audit and repair the cheapest compatible `EXISTS_BROKEN` or
   `STUB` seam. Only evidence-backed absence supports `MISSING`.
3. **Prove subtraction or bypass.** Trace candidate surfaces backward from the
   accepted outcome and try the cheapest reversible without-it instrument. Bind
   the result to the exact revision, declared candidate set, and observed
   runtime. For an existing surface, a named criterion failure supports bounded
   retention; green governing evidence with closed need and observation
   boundaries produces a captain-owned removal candidate; `UNKNOWN` preserves
   the surface and proves neither necessity nor removability.
4. **Authorize only necessary addition.** A proposed new responsibility can
   advance when its absence fails a named criterion and the recorded simpler
   route is insufficient. Green or `UNKNOWN` returns the proposal.
5. **Run RED/GREEN.** Demonstrate the accepted behavior failing before the
   minimum implementation and passing after it. A subtraction prompted later
   returns through the same without-it and GREEN evidence; numbers do not
   authorize it.
6. **Validate fresh.** Bind fresh validation to the final exact revision after
   any resulting subtraction; a changed head invalidates prior evidence. **The
   binding is a recorded fact, not an assumption**: a round that does not state
   the revision and artifact it read cannot be shown, from its own report, to
   have read the one under review, and an unstated binding is indistinguishable
   in that report from a wrong one. A verifying round also names the result that
   would have made it fail; where it cannot, it reports at a rate set by its
   prompt rather than by the artifact, and neither its silence nor its confidence
   is evidence.

Here, **minimum** means the fewest independently maintained lifecycle
responsibilities sufficient for the accepted outcome, not the fewest files or
lines. **Simple** means the direct sufficient route with the least lifecycle and
maintenance obligation, not dense code. Record each candidate surface, served
criterion, without-it instrument and result, simpler route, and insufficiency.
Group components only when Route discipline cannot separate their lifecycle
state. The bounded known-defect route adds this work only when it proposes a new
surface.
- Judgment belongs to a fresh EM/reviewer; scope and irreversible decisions
  belong to the captain. Orchestration itself carries no verdict authority.
- **Test depth is the adopter's call; integrating early is not.** Prefer
  integrating the smallest working increment wherever the adopter's declared
  route makes it run, over further rounds aiming evidence at an increment that
  has not run anywhere. Automated tests and verification then grow against
  observed behavior rather than against a model of it. This bounds
  pre-integration evidence effort; it moves nothing past delivery, because
  `validation` still precedes `done`, and the evidence named as able to fail
  still has to exist and still has to pass.
- Completion means the goal is achieved and durably delivered, not that the
  agent produced every possible ceremony artifact.

## Verification discipline

Outcome discipline governs the claim. These govern the **instrument** — the
check, the reviewer, the instruction — because an instrument that cannot fail
reports the same way whether or not the thing it watches is broken.

- **Behavioral validity follows observation; gate independence follows
  provenance.** A text match over an instruction the actor reads may establish
  that the text exists, but it cannot prove behavior or close a behavioral gate:
  behavior can regress with the wording intact, while harmless rewording can fail
  the match. Tests produced with the artifact may supply RED-before-GREEN
  implementation evidence, but cannot by themselves provide the independent
  verdict on that artifact; that verdict comes from fresh context not involved in
  producing it.
- **Preserve the observation boundary at closure.** When an accepted problem or
  criterion is grounded in behavior observed through a consumer or external
  runtime boundary, validation re-runs the reported scenario through a runtime
  of the same behavior-producing kind. Lower-level diagnosis and guards do not
  replace re-observation through that boundary; they may localize the cause or
  prevent a known input without showing what the consumer now experiences. The
  original instance is not mandatory, but an alternative names why its actor,
  instrument, delivery path, configuration, and claim-relevant conditions are
  equivalent, together with the exact revision and artifact it exercised.
  Unavailable re-observation is missing evidence, not completion evidence.
- **A check is evidence only once it has been seen to fail.** A probe that
  returns a plausible result where it should have errored is worse than none,
  because its output reads as a conclusion. Run it against a case it must flag
  before running it against the case in question; its silence carries
  information only after you have heard it speak. This binds the check, not only
  the artifact: a round that cannot say what would have reddened its own
  instrument has measured nothing.
- **Name the falsifier's kind.** `refusal` — drive the system and read its
  rejection. `mutation` — change the producer and observe what breaks; this is
  the kind that reaches a consumer silently duplicating a producer's
  derivation instead of consuming its output. `existence-disproof` — show that
  no value satisfies both requirements, which no assertion over sampled inputs
  establishes. Treating all three as "write an assertion" lets two appear covered
  when they are not.
- **A negative result carries the same bar as a positive claim.** Evidence of
  absence is bounded by what was observed and under what system state; it
  establishes neither a wider population nor an unobserved cause. Before
  reporting an empirical absence, name the searched scope and why it is the
  population, or use a different strategy that would have found the thing. One
  tool, pattern, or filter is a sample unless its coverage of the population can
  be shown. Trace unexplained signals;
  do not assign them an unobserved origin.
- **Forced behavioral and corpus checks run at stage boundaries, not in the
  worker's inner loop.** Per-edit or per-commit must-pass checks are limited to
  fast mechanical checks such as format, lint, and typecheck. Behavioral and
  corpus/consistency gates run at the validation boundary. This does not restrict
  tests the worker chooses to run: RED-before-GREEN belongs inside
  implementation.
- **Prefer the cheapest instrument that can fail.** Reserve an expensive one —
  an adversarial reviewer, a fresh-context panel — for claims no cheap check can
  settle. An expensive instrument whose output is a work order for a cheap one
  was misapplied, and that cost is paid every round it repeats.
- **Validation ends by predicate, and a fresh reviewer owns the decision.** It
  ends when the item's declared disproof evidence passes at the exact revision
  and no recorded failure, contradiction, or unmet lifecycle obligation remains.
  Another round requires the fresh reviewer to record three things: the
  unresolved in-scope claim, the observation that raised it, and the result that
  would change the verdict. **Possibility alone does not continue validation** —
  an unbounded supply of properties nobody has checked yet is not a finding, and
  a round justified only by the agent's own expectation of learning something is
  self-attested and stops nothing. The clauses above bound an instrument's
  quality and none bounds their number; this one does, and it is checkable by
  someone other than the party that wants another round.
- **Provider review feedback re-enters validation.** When a delivery provider
  exposes review feedback after validation, the earlier verdict does not cover
  that evidence. Feedback is evidence to verify, not authority to obey. Require
  a complete provider observation at the exact delivery revision and one
  evidence-bearing disposition per retained external item; an incomplete or
  unavailable observation is missing evidence. A code-changing disposition
  invalidates prior validation and requires a fresh exact-revision decision.
- **When one failure shape repeats, change the work, not the wording.** At the
  second occurrence, restructure so the reproducer is eliminated; a stronger
  instruction, another case against the same reproducer, or an unchanged
  deliverable shape do not count. Cheapness hides this: a tolerance sized for
  expensive rounds does not fire on cheap ones, so the trigger is repetition of
  shape, not spend. If the repeated failure is an operation a worker should
  not execute, remove it from that worker's executable authority through
  `dispatch_hazard_assignment`; a brief is not a control.

## Continuation

At every handoff, record the authoritative work item, current stage, exact source
revision, accepted evidence, next action, and any unresolved captain-owned
decision. Re-read the Local Profile and live work-item authority before mutating
shared state. Implementation completion and fresh validation remain separate claims.

## Self-improvement

`continue-dev-flow` resolves the committed product route before optional self-improvement.
Do not inspect `_debriefs/` or `_improvements/` on an ordinary continuation. Only
when the current invocation explicitly requests improvement harvesting, apply this
bounded procedure after resolving the product route:

1. Resolve the authoritative debrief home through the repository's execution-state
   authority and read `_improvements/state.yaml` when present.
2. Consider only immutable `_debriefs/` records newer than the recorded cursor, up
   to the most recent three in one run. When more than three are unseen, the older
   records outside that window are deliberately treated as superseded rather than
   queued for a later run; record them as skipped before advancing the cursor.
3. Classify at most one narrow candidate as **repository-local** or **reusable kernel**.
   Record its observations, expected value, cost, disproof hook,
   disposition, and the newest debrief consumed; then advance the cursor even when
   no candidate is proposed.
4. If no unseen debrief exists, do not rediscover or re-propose an older issue.
5. Inside the execution-state authority's same single-writer transaction or
   compare-and-swap that records the result, resolve the debrief home again and
   verify its locator is unchanged, then re-read and compare the live cursor. A
   home or cursor mismatch aborts the write and recomputes from live authority.
   Without atomic comparison or exclusive ownership, report `UNKNOWN` instead of
   writing and continue the already-resolved product route.

Repository-local candidates route to the adopter's work-item authority. Reusable
kernel candidates become a reviewable handoff to the installed dev-flow source
after adopter-specific details and duplicate proposals are removed.

The coordination record is derived state, not work-item authority. Detection never
creates a task, grants sprint membership, merges a change, or pauses product work.
Only the captain may admit a candidate to work-item or iteration authority. Adopt or
refit owns installation and updates; `continue-dev-flow` reads the vendored policy
and never silently rewrites it. Improvement-state failure never blocks the
already-resolved product route.

Optional controls are independently declared through the Work Control Profile.
Undeclared capabilities remain off; adopters add only the control whose risk
justifies its cost.
