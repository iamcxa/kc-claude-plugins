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

- Every item names the end value it exists to produce and evidence that would
  disprove completion.
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

- **A check is evidence only once it has been seen to fail.** A probe that
  returns a plausible result where it should have errored is worse than none,
  because its output reads as a conclusion. Run it against a case it must flag
  before running it against the case in question; its silence carries
  information only after you have heard it speak. This binds the check, not only
  the artifact: a round that cannot say what would have reddened its own
  instrument has measured nothing.
- **Name the falsifier's kind.** `refusal` — drive the system and read its
  rejection. `mutation` — change the producer and observe what breaks; this is
  the only kind that finds a consumer silently duplicating a producer's
  derivation instead of consuming its output. `existence-disproof` — show that
  no value satisfies both requirements, which cannot be written as an assertion
  at all. Treating all three as "write an assertion" lets two appear covered
  when they are not.
- **Prefer the cheapest instrument that can fail.** Reserve an expensive one —
  an adversarial reviewer, a fresh-context panel — for claims no cheap check can
  settle. An expensive instrument whose output is a work order for a cheap one
  was misapplied, and that cost is paid every round it repeats.
- **A round names what it expects to learn that the last one did not.** A round
  that cannot is a repeat. This is where verification stops: not when every
  defensible check has been run, but when no round can state new information it
  would produce. The clauses above bound the *quality* of an instrument and
  none of them bounds the *number* — cheap, falsifiable, correctly bound checks
  can be produced without limit, and an agent that satisfies every other clause
  while never converging has complied locally and failed globally. This clause
  is the one that ends it.
- **When one failure shape repeats, change the work, not the wording.** A second
  occurrence of a single failure class is the signal to restructure — never to
  restate the instruction more firmly, and never to add another case against the
  same reproducer. Cheapness hides this: rounds that are individually fast never
  breach a cost tolerance, so the trigger is repetition of shape, not spend.
  **The options always include reshaping the deliverable**, and a round that
  leaves that off the list has narrowed the decision rather than taken it —
  a wrong shape is exactly the case the other options cannot repair.
- **A hazard that has defeated an instruction is removed from the path, not
  described more carefully.** Where a worker can reach an operation that has
  repeatedly gone wrong — a command slow enough to invite deferring it, a
  destructive step, a credential — the repair is that the operation is *absent
  from the worker's path and carries another named owner*, not that the brief
  warns about it more firmly. A brief is not a control: it is read by the party
  the control exists to bound. "The worker still needs to do the slow thing" is
  the signal to split the work, not to rewrite the warning.
- **An instruction that contradicts the governing contract loses, and should not
  have been an instruction.** A worker told not to do what its stage mandates
  resolves that conflict in favour of the stage, correctly. Where the dispatcher
  has already discharged the obligation, it says so — naming the result, its
  author, and that the obligation is **met rather than skipped**. Check for this
  contradiction before concluding that a worker ignored an instruction.

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
