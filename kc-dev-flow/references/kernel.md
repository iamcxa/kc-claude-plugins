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
  prior evidence.
- Judgment belongs to a fresh EM/reviewer; scope and irreversible decisions
  belong to the captain. Orchestration itself carries no verdict authority.
- Completion means the goal is achieved and durably delivered, not that the
  agent produced every possible ceremony artifact.

## Self-improvement

Repeated friction may yield at most one narrow improvement proposal at a sprint
boundary. The proposal cites observations, expected value, cost, and a disproof
hook. It does not create, schedule, advance, or merge its own task. Improvement
work competes for iteration authority like any other work.

Optional controls are independently declared through the Work Control Profile.
Undeclared capabilities remain off; adopters add only the control whose risk
justifies its cost.
