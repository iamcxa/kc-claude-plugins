---
name: kc-dev-flow-kernel
---

# KC Dev Flow Kernel

The kernel is a portable authority and evidence contract. It does not prescribe
a tracker, Markdown filename, agent harness, CI vendor, PR host, or workflow
runtime. Adopters bind those locally.

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
   acceptance criteria, and names evidence able to fail.
3. `implementation` works test-first inside approved scope.
4. `validation` uses fresh context and seam/runtime evidence appropriate to the
   claim. Unit tests alone do not prove wiring.
5. `done` follows exact-revision delivery plus durable terminal/archive state.

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
- Before planning new capability, apply the reverse-recovery audit and repair
  the cheapest compatible seam. Only confirmed `MISSING` work is greenfield.
- Fresh validation is bound to the exact revision. A changed head invalidates
  prior evidence. **The binding is a recorded fact, not an assumption**: a round
  that does not state the revision and artifact it read cannot be shown to have
  read the one under review, and an unstated binding is indistinguishable from a
  wrong one. A verifying round also names the result that would have made it
  fail; where it cannot, it reports at a rate set by its prompt rather than by
  the artifact, and neither its silence nor its confidence is evidence.
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
  tool, pattern, or filter is a sample, not a census. Trace unexplained signals;
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
- **When one failure shape repeats, change the work, not the wording.** At the
  second occurrence, restructure so the reproducer is eliminated; a stronger
  instruction, another case against the same reproducer, or an unchanged
  deliverable shape do not count. Cheapness hides this: a tolerance sized for
  expensive rounds does not fire on cheap ones, so the trigger is repetition of
  shape, not spend. If the repeated failure is an operation a worker should
  not execute, remove it from that worker's executable authority through
  `dispatch_hazard_assignment`; a brief is not a control.

## Self-improvement

At each sprint boundary, if repeated friction was observed, remind the captain
once and classify at most one narrow proposal:

- **repository-local** — the defect depends on the adopter's product,
  architecture, provider, or policy. Route it to the adopter's work-item
  authority.
- **reusable kernel** — the defect is portable across adopters. Route it to the
  kernel source named by the local binding after removing adopter-specific
  details and checking for an existing issue or change.

The proposal cites observations, expected value, cost, and a disproof hook. No
observed repeated friction means no reminder ritual. Detection never schedules
or advances improvement work.

For a reusable kernel proposal, read `upstream_contribution.mode` from the local
binding. Missing or `propose_only` produces a reviewable proposal or patch
handoff. `pull_request` permits an isolated, test-first patch and pull request
to the declared upstream repository after the ownership and duplicate checks.
It does not grant merge authority, local sprint membership, or permission to
pause product work unless the defect makes safe delivery impossible.

Optional controls are independently declared through the Work Control Profile.
Undeclared capabilities remain off; adopters add only the control whose risk
justifies its cost.
