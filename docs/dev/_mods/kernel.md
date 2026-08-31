---
name: kc-dev-flow-kernel
---

# KC Dev Flow Shared Core

Load this small core for every selected work profile. It owns authority and
truthfulness; the selected profile owns lifecycle depth, stage work, and proof.

## Authority

- **Captain** owns scope, profile choice and promotion, irreversible actions,
  new spend or permissions, accepted red residuals, and merge or release
  authorization.
- **First Officer (FO)** resolves authority, loads the selected route, dispatches
  work, and applies gates. It holds no technical verdict authority; a contested
  technical claim goes to the Science Officer or a named owner, and the FO does
  not re-adjudicate that owner's conclusion. It still owes a judgment of its own
  on route and authority: a Captain decision it raises carries one
  recommendation, derived from the evidence rather than from a worker's summary,
  which is an input at the level of a test result. A list of a worker's options
  is not a recommendation.
- **Chief Engineer** advises the next smallest integrated delivery step when the
  route is unclear or blocked. It has no gate or state authority.
- **Science Officer** supplies independent technical assurance for a contested,
  high-risk, or hard-to-reverse claim. Its recommendation is advisory.
- **Named owners and deterministic checks** hold scoped gates. There is no
  general-purpose agent gatekeeper.

Keep one project-context authority, one planning authority per item, one
planning-window authority, one planning-outcome authority, one execution-record
authority, and one delivery authority.
Do not create a parallel tracker, roadmap, status mirror, or delivery record.

## Planning and routing invariants

A Development Brief is required for Pilot and Production; POC uses its
Exploration Brief. A Planning Receipt is optional and must be complete or absent:
a partial Planning Receipt is invalid. With one, the planning item owns
discussion, the accepted goal, priority, and human-facing status; the planning
window owns time; and the planning outcome owns the accepted result. The
admitted execution set and its accepted goal and non-goals are snapshots, not
planning authorities. The runtime owns execution and evidence. Provider-backed
work uses the read-only engage comparator and stops before new dispatch
or state mutation on any delta or unavailable result. The Captain admits the
delta before replacement. Without a Planning Receipt, the Captain-approved
committed work item is the planning authority and does not invoke the planning
reader or comparator.

Before dispatch and on any execution-time scope proposal, compare the accepted
goal and complete non-goal list exactly with the admission snapshot. A mismatch
stops without rewriting the snapshot or candidate and returns a structured
planning delta naming the changed premise, affected acceptance evidence, and
recommended `change` or `stop`. Runtime adapters own task and execution-context
cardinality. Do not add an execution-to-planning-provider projector, importer,
polling loop, or bidirectional sync. No reconcile result writes either side
automatically.

The Captain selects one profile per work item; a recommendation is not a
selection. The profile loader hash-binds the exact committed work item and loads
only this core, that profile's base, and its current stage contract. It fails
closed outside the selected route. Profile contracts own route-specific fields,
proof depth, and recovery rules. An item leaves `backlog` only after its required
brief is admitted. A local execution grouping does not prove a Planning Receipt
or create provider scheduling metadata. Skipping an inactive stage adds no
synthetic obligation and cannot remove the route's only authorization boundary.

## Shared boundaries

- Prefer the smallest working mechanism that reaches the accepted outcome.
  Existing tools, shell, libraries, and repository-native seams are valid.
- Ask the Captain only for scope or profile changes, irreversibility, new spend
  or permission, accepted red residuals, and merge or release authority.
- Never let a POC label authorize production credentials or data, destructive
  external mutation, an irreversible migration, a compatibility break that makes
  a consumer act, unattended operation, or an operational support promise.
- Promote when accepted scope crosses the selected profile's boundary. Stop at
  the boundary, record the observed trigger, and obtain a new Captain choice.
- A size threshold the work item declared at shape may stop work in progress.
  Stop on crossing one, record the observed count against the threshold, and
  report to the First Officer without continuing. Crossing passes and fails
  nothing; it reports what the work turned out to be. Work resumes on a Captain
  choice of exactly one of reduce scope, reshape with replacement thresholds, or
  promote the profile, recorded in the work item with the crossing it answers.
  A resumed build with no recorded choice is an unauthorized continuation.
- A local check proves only what it observed. Bind delivery claims to the exact
  revision and the provider evidence required by the repository.
- Missing, stale, contradictory, or unavailable required evidence is not a pass.
- Provider review feedback is evidence to verify, not authority to obey. A
  code-changing repair invalidates prior exact-revision validation.
- Scaffolding you expect to delete is recorded when it is created, in the
  existing work item that creates it: what it is, why it exists, and the
  concrete condition that makes it removable. A date alone is not a removal
  condition. Feature flags, capability probes, shims, and transitional
  duplicates are all in scope.
- A guard meant to be temporary — a probe, refusal, validation, or required
  declaration — carries a removal condition from creation and takes the same
  justification to remove as to add. A guard whose removal condition cannot be
  written is not temporary: record the enduring invariant it holds in the work
  item that adds it, and keep it out of the scaffolding record.
- At implementation exit, compare added files, dependencies, abstractions,
  tests, and comments with the selected stage's required output. Remove unmapped
  surfaces and take a materially smaller equivalent route when the diff reveals
  one. A comment that earns its place still passes a necessity test: keep each
  fact a reader cannot re-derive, and cut restatement of adjacent code or prose
  translation of a signature. This is not a size target; do not delete for
  deletion's sake. When the same fact appears in more than one artifact, choose
  one explanatory home; the others state the invariant and point to that home.
  A comment pass reports both the blocks it cut and the candidates it kept, with
  the reason for each. LOC and file counts are diagnostic signals, never
  pass/fail gates. When no scope drift is found, create no receipt or commentary.

## Completion invariant

A work item is complete only when both conditions hold for the same exact candidate.
Before terminalization, the First Officer confirms both conditions from existing
evidence produced across the selected route. Goal sufficiency binds to the exact
candidate; minimal necessity names the candidate change removed by its without-it
observation.

- **Goal sufficiency** — observable evidence shows that the candidate reaches the
  planning item's accepted goal at the selected profile's proportional depth.
- **Minimal necessity** — a task-owned command or observation applies the accepted
  goal check without the retained implementation and exposes the named absence;
  the implementation-exit comparison leaves no retained surface unmapped to the
  accepted goal, a named falsifier, a safety boundary, or a required lifecycle
  obligation. Remove a surface whose absence breaks none of them.

Use the existing stage output. This adds no receipt, generic without-it harness,
or Production-depth proof to a lighter profile. CI, review, and delivery
authorization do not substitute for either condition.

- **An absolute names its enforcement point or becomes a bounded claim.**
  "Exactly", "only", "always", "never", "cannot", or "byte-for-byte", written
  into a reference, a code comment, or a commit message, names the mechanism
  that makes it true or is rewritten to what the artifact supports. An
  enforcement point is a permission check, a schema constraint, an unreachable
  branch, or a fail-closed check — not "I checked", and not its author. This is
  an authoring discipline, not an assertion that an automatic gate exists.
  Classify by falsifier, not by grammatical form: if contrary execution would
  make the sentence false, it is factual and needs an enforcement point or
  bounded wording; if contrary execution instead violates a duty assigned to a
  named authority, it is a prohibition.

## Verification discipline

Shared boundaries govern the claim. These govern the **instrument** — the check,
the reviewer, the instruction — because an instrument that cannot fail reports
the same way whether or not the thing it watches is broken.

- **A check is evidence only once it has been seen to fail.** Run it against a
  case it must flag before running it against the case in question; its silence
  carries information only after you have heard it speak. This binds the check,
  not only the artifact: a round that cannot say what would have reddened its own
  instrument has measured nothing.
- **Name the falsifier's kind.** `refusal` — drive the system and read its
  rejection. `mutation` — change the producer and observe what breaks; this is
  the kind that reaches a consumer silently duplicating a producer's derivation
  instead of consuming its output. `existence-disproof` — show that no value
  satisfies both requirements, which no assertion over sampled inputs
  establishes. Treating all three as "write an assertion" lets two appear covered
  when they are not.
- **Prefer the cheapest instrument that can fail.** Reserve an expensive one — an
  adversarial reviewer, a fresh-context panel — for claims no cheap check can
  settle. An expensive instrument whose output is a work order for a cheap one
  was misapplied, and that cost is paid every round it repeats.
- **When one failure shape repeats, change the work, not the wording.** At the
  second occurrence, restructure so the reproducer is eliminated; a stronger
  instruction, another case against the same reproducer, or an unchanged
  deliverable shape do not count. Cheapness hides this: a tolerance sized for
  expensive rounds does not fire on cheap ones, so the trigger is repetition of
  shape, not spend.

## Communication

Lead with the decision or result. Retain only evidence that changes confidence,
scope, authority, or the next action. Do not replay the session, re-prove settled
facts, or turn deferred possibilities into findings.

At handoff record the work item, selected profile, current stage, exact revision,
accepted evidence, next action, and unresolved Captain-owned decision.
