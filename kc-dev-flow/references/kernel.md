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

## Brief admission and planning

A Development Brief is required for Pilot and Production. New admission uses
one `## Acceptance criteria` section whose concrete bullets have unique,
ascending `AC-N` identifiers; it also fixes the problem, accepted outcome,
complete non-goal list, and route-back conditions. The explicit admission
loader mode rejects a missing, duplicate, placeholder, evidence-only, or
dual-section brief. Default loading leaves already-admitted headings unchanged.
The v3 POC decision, falsifier, budget, and stop condition form the Exploration
Brief. New POCs also record artifact class, any repository safety boundary, and
a positive decision-ready minute limit. The limit defaults to 15; an override
requires its reason.

A Planning Receipt is optional and must be complete or absent. Explicit
admission mode validates it before provider access. It is exactly the
`source`, `planning-window`, and `planning-outcome` tuple. A partial Planning
Receipt is invalid. When all three fields are present, the planning item owns
discussion, the accepted goal, priority, and human-facing status; the planning
window owns time and the planning outcome owns the accepted result. At
admission, each execution record stores the tuple and a runtime may also record
a local execution group. The admitted execution set is the admission snapshot;
its group is not a planning authority. Its accepted goal and non-goals are a
snapshot, not another accepted-goal authority. The runtime owns execution and
evidence.

For a complete Planning Receipt, use the repository-local read-only planning
reader at every engage to re-read the current Ready set for the snapshot's
planning window/outcome plus every currently Ready snapshot source outside those
bounds. The First Officer passes its source identities, window, outcome,
accepted goal, and non-goals with the committed execution snapshot and the exact
engaged source, window, and outcome read from that work item to the read-only
engage comparator. The supplied expected source, window, and outcome must match,
and the comparator refuses a snapshot whose items do not all share that planning
scope. Classify every difference as added, removed, changed, or moved. The First
Officer may continue only when the comparator exits `0` and stdout is one parsed
`status: clean` result. The First Officer must refuse new dispatch or state
mutation on exit `1`, exit `2`, or any other output; invalid input reports
reconcile unavailable. The Captain admits the delta before an authorized actor
commits a replacement snapshot. Do not cancel a running worker.

Without a Planning Receipt, the Captain-approved committed work item is the
planning authority. It does not invoke the planning reader or comparator and it
does not invent a provider, planning window, or planning outcome.

Before dispatch and on any execution-time scope proposal, compare the accepted
goal and complete non-goal list exactly with the admission snapshot. If either
differs or implementation needs either to change, stop without rewriting the
snapshot or candidate and return a structured planning delta naming the changed
premise, affected acceptance evidence, and recommended `change` or `stop`.

Runtime adapters own task and execution-context cardinality. Do not add an
execution-to-planning-provider projector, importer, polling loop, or
bidirectional sync. No reconcile result writes either side automatically.

## Select before routing

Before entering a working stage, re-read the committed receipt. New choices use
`kc-dev-flow-work-profile/v3`; active v2 Pilot and Production remain loadable,
while active v2 POC fails closed. If it is absent or stale, use
`kc-dev-flow:choose-work-profile`; the Captain chooses and the locally authorized
actor records the decision. A recommendation is not a selection.

The profile loader accepts the exact committed work-item file. It validates and
hash-binds that item's supported receipt and current status, then loads this core, that
profile's base contract, and that profile's current stage contract. A stage
outside the selected route fails closed. Profiles are per work item, never
project-global; different items may use different routes concurrently.

| Profile | Working route |
|---|---|
| `poc-exploration` | `build -> prove` |
| `pilot-product-slice` | `shape -> build -> verify-deliver` |
| `production` | `shape -> build -> verify`; eligible recovery `build -> verify` |

A v3 POC fixes one `poc_decision`, `poc_falsifier`, `poc_budget`, and
`poc_stop_when` before implementation. A `no-code` or `disposable` POC with no
safety boundary uses direct proof: build records the durable outcome and skips
review plus fresh validation. Retained work or any named safety boundary keeps
fresh proof. Older admitted v3 receipts keep that fresh path. Decision-ready
time runs from admission to the durable outcome; Captain wait and terminal
cleanup are separate. Over budget or after a Captain intervention, only a
complete `change` outcome may continue to the terminal authorization gate.
A short Production route requires only
concrete `recovery_failure`, `recovery_falsifier`, `recovery_rollback`, and a
closed non-empty `review_risks`; other Pilot and Production receipts omit them.

`backlog` is queue state and `done` is terminal state; neither is a working
stage. A workflow runtime may expose the union of stage names and skip stages
outside the selected route. Skipping an inactive stage requires no synthetic
review or receipt — but only when the skipped stage carries no authorization
checkpoint a later stage does not also carry. A stage whose skip would remove
the route's sole terminal-authorization checkpoint is not a candidate for this
clause; fold that checkpoint into an adjacent working stage's contract
instead, the way `production`'s route above folds release authorization into
`verify` rather than skipping a dedicated `release` stage.

An eligible Production recovery at `ideation` emits an implementation skip and
loads no shape contract. Changed or uncertain premises stop with
`RECOVERY_FULL_ROUTE_REQUIRED`; only the Captain or the recorded rollback may
restore the full route.

Queue state still has an exit bar. An item leaves `backlog` only after its
required brief is admitted. Pilot and Production require the canonical
Development Brief above for new admission; continuation does not revalidate or
rewrite admitted prose. POC requires the complete Exploration Brief recorded
by its v3 receipt. A complete Planning Receipt adds provider reconciliation; its
absence selects the standalone authority path instead of blocking the work.

A runtime may separately require a local execution group and readiness field.
That local execution grouping does not prove a Planning Receipt and must not
invent provider scheduling metadata. The Captain checks the brief admission bar
on every `backlog` exit at profile selection. A reused profile receipt answers
which route the item takes, never whether the bar is met, so reuse does not skip
the check. `kc-dev-flow:choose-work-profile` asks for a missing part and reports
the item as not ready to leave `backlog` when it cannot ask.

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
