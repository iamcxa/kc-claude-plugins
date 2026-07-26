---
commissioned-by: spacedock@0.25.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 2
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
      worktree: true
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
    - name: done
      terminal: true
---

<!--
  Instantiated from the lean SD workflow canonical template
  (spacedock-workflows muscat/docs/lean-sd-workflow/README-template.md @ 82e8b541).
  Methodology only - runtime concerns belong to the spacedock binary.
  Litmus: crash/concurrency/duplicate-delivery correctness -> binary;
  agent reasoning / evidence discipline -> this README.
-->


# kc-claude-plugins — Development Workflow

kc-claude-plugins is Kent's Claude Code plugin monorepo — home of kc-team-ops, kc-pr-flow, kc-hyperfocus, e2e-pipeline, kc-nightwatch, kc-plugin-forge and friends, published through the personal marketplace. The workload is prose-heavy (markdown skills + agents) with a thin executable layer (scripts, hooks). Repo-level conventions live in CLAUDE.md; PRODUCT.md / ARCHITECTURE.md baselines are seeded by this workflow's first tasks.

Tasks move `backlog → ideation → implementation → validation → done`. One
gated design stage (ideation), one worktree build stage (implementation), one
fresh-context verification stage (validation) with `feedback-to`
implementation, and a terminal merge. The spacedock binary owns all runtime
semantics: stage transitions, gate records, worktree lifecycle, state
durability, exactly-once approval. This README owns judgment discipline only.

## File Naming

Each task is `{slug}.md` (default) or a folder `{slug}/index.md` when
per-stage artifacts accumulate. Slugs: lowercase, hyphens, no spaces. Task
state lives in the split-root state checkout (`state:` above) so stage
transitions never churn the code branch.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | SD-B32 stored ID from `status --next-id --id-seed <slug>` |
| `title` | string | Human-readable task name |
| `status` | enum | backlog, ideation, implementation, validation, done |
| `source` | string | Where the task came from (captain note, defect, audit) |
| `started` / `completed` | ISO 8601 | Boundary timestamps |
| `verdict` | enum | PASSED or REJECTED — set at final stage |
| `worktree` | string | Set on first worktree dispatch, cleared at terminal merge |
| `issue` / `pr` | string | External references |
| `design` | enum | `required` or `trivial-pass` — set during ideation, never empty at the ideation gate |

## Proof Policy

Inherited from the spacedock proof discipline; the four rules below are
binding in every stage report and every gate review.

1. **No prose-grep, and provenance decides independence.** A string match
   over an instruction file the model reads never proves a behavioral claim.
   A grep may serve as one-off evidence for an existence fact in a validation
   report; the same grep committed as a test is banned — it cannot fail. And
   a check counts as independent evidence only when what it inspects was not
   authored by the agent under review — a script over a self-written artifact
   is a self-issued stamp, not a gate.
2. **Evidence must be able to fail.** Each AC's cited evidence names the
   concrete change that would flip it. If the author cannot name the
   falsifying edit, the criterion does not count.
3. **Prove behavior by exercising it.** Output bytes, exit codes, resulting
   on-disk state, a browser actually driving the flow. Unit tests prove logic;
   they do not prove wiring. Seam-level claims need runtime or E2E evidence.
4. **Trace every mechanism to value.** Any new mechanism names the value AC it
   serves, the simplest alternative considered, and why that alternative is
   insufficient. A test harness orchestrates and observes the supported
   runtime; it never becomes a second implementation of the system under test.
5. **Behavior checks live at stage boundaries, never in the worker's inner
   loop.** Hooks that fire on every commit/edit inside a work session are
   limited to fast mechanical checks (format, lint, typecheck). Behavioral or
   corpus/consistency checks belong to the validation gate and CI: a
   must-pass check inside the inner loop turns "implement the behavior" into
   "make the check shut up", and the worker will drift the implementation —
   or the check's inputs — to satisfy it.

## Stages

Every stage report opens with a one-paragraph TL;DR; raw command output,
full diffs, and re-derivations go in collapsed or linked sections. A report
that reads like a session transcript costs reading budget nobody spends.

### `backlog` — capture (this is the todo queue)

Any idea, rabbit hole, defect, or captain note enters as a seed task file:
title, `source`, one-paragraph description. Target cost: under two minutes.
Capturing a seed triggers NO design work — the gate is where the captain
curates what advances. A seed too vague for the captain to triage is the only
"bad" here.

#### Defect lane — skip `ideation` for a bounded fix

A known defect with a mechanical acceptance test does not need a design stage.
When **all four** hold, the FO advances `backlog → implementation` directly and
records the classification and its justification in the task body:

1. The root cause is already identified and cited at `file:line`.
2. Acceptance is mechanical — a test that fails before the fix and passes after.
3. It is a single seam: one surface, no cross-layer ripple, no schema change.
4. No design decision is open. If the fix has two defensible shapes, it is not
   in this lane.

Everything else still applies: RED-before-GREEN, the proof policy, the
validation stage, and the merge bar. **The lane removes a design stage, never
verification** — and a defect whose fix turns out to need a design decision
goes back to `ideation` rather than being decided inside implementation.

Any of the four failing means the main line. When in doubt it is the main line;
the cost of over-shaping one fix is smaller than the cost of designing inside
an implementation stage nobody is reviewing for design.

### `ideation` — one gate for design, plan, and acceptance

The single judgment-heavy stage. Flesh out the problem, decide the approach,
define acceptance criteria and the test plan. The gate reviews all of it at
once. Discipline clauses:

- **The captain authors scope; the agent never infers it for a
  rubber-stamp.** For non-trivial tasks, open ideation by asking the captain
  a few short scope questions (what gets worse without this; the time
  budget; what to keep if forced to cut; what we are happily NOT doing;
  which assumption could be wrong) and compose Problem/Scope from the
  answers verbatim. Skip only with a stated small-scope reason.
- **Appetite is a forcing budget.** Record a time/scope budget in the task
  body. When work is about to exceed it: cut scope (defer a sub-part to
  backlog) or park cleanly with re-enterable state and explicit open
  findings — never extend the budget silently, and never compress
  validation to land inside it. Size or budget variance is a drift signal
  to investigate, never a number to hit by padding artifacts or stripping
  tests.
- **One-sentence pre-mortem.** Before the gate: "if this ships exactly per
  spec and still fails, the most likely cause is ___" — pick one of {wrong
  problem, criteria that pass without delivering value, wrong framing lens,
  hidden assumption, over-conviction}. This is an orthogonal
  future-failure check the AC rubric structurally cannot generate.
- **Design determination is mandatory, never skipped.** Every task records
  `design: required` (UI, contract, interface, schema, or visual surface
  affected — attach the concrete design decision: wireframe reference, API
  shape, before/after) or `design: trivial-pass` with a one-line reason. An
  ideation gate presented without a design determination is returned unread.
- **Reverse-recovery audit before any "build/add X"** (brownfield default):
  assume the abstraction may already exist. Layer-trace the path (UI →
  contract → handler → domain → persistence → readback) and classify each
  layer WORKING / EXISTS_BROKEN / STUB / MISSING with file:line. Greenfield
  is allowed only after proof of absence (multi-strategy, multi-language
  search). A single broken seam means repair scoped to that seam, not a
  rebuild. Full procedure: `_mods/reverse-recovery-audit.md`.
  **Audit against the merge target** (fetch `origin/<trunk>` first), never
  only the working branch — a stale branch shows stale infrastructure, and
  a MISSING verdict read off it can be seven weeks wrong. Implementation
  re-verifies the audit's load-bearing MISSING claims against a fresh
  merge target before building, and escalates instead of building when a
  premise has collapsed.
- **AC are end-state properties with falsifiable proof.** Each AC names a
  property of the finished task (not a stage action) plus a `Verified by:`
  clause citing proof outside the task's own prose. At least one AC measures
  the end value the task exists for, against a baseline that can move the
  wrong way.
- **Run `status --read <ref> --ac-scan` before presenting the ideation gate;
  every AC must resolve.** The extractor is line-based, so a
  `**AC-N — …**` heading whose bold span wraps onto a second line is invisible
  to it — and house style wraps prose near 95 characters, so a long property
  statement hits this by accident. Keep the bold heading short enough to open
  and close on one line and put detail in the body underneath. This is not
  formatting hygiene: the gate's AC cross-check reads that extractor's output,
  so an unparsed AC set gives the cross-check nothing to anchor against and it
  passes by absence. Three sprint-1 tasks shipped ideation with ACs invisible
  this way, each found only downstream.
- **E2E-first acceptance.** When the task changes full-stack or user-visible
  behavior, at least one AC is verified by exercising the real flow end to
  end (browser drive, CLI invocation, service round-trip). Unit-only proof is
  insufficient for wiring claims. Skip only for docs/config/CI-only tasks,
  and record the skip reason.
- **Doc diff proposed here.** When the task changes behavior that PRODUCT.md,
  ARCHITECTURE.md, or any published doc describes, ideation proposes the
  concrete doc diff (before/after wording) in the task body. The gate reviews
  it; implementation applies it; validation verifies behavior diff and doc
  diff landed together.
- **Spike the riskiest unverified mechanism first**, and record the result in
  the task body — or record "no spike needed: {proven mechanisms relied on}"
  so the determination is auditable.
- **Size the implementation dispatch here.** Default is ONE worker session —
  every extra dispatch pays a cold-start (re-reading the README, task body,
  and surrounding code). Split only when the estimate exceeds ~90 minutes,
  the work has 3+ independent behaviors, or parallel worktree lanes buy real
  wall-clock — and always split along behavior boundaries, each slice a
  complete RED→GREEN loop (never "tests in one dispatch, code in the next").
  Record the sizing decision in the task body so implementation inherits it.

### `implementation` — build in a worktree, test-first

- **RED before GREEN, with evidence.** For each behavior: write the failing
  test, run it, record the RED evidence in the stage report (test name +
  failure output digest), then write the minimum code to pass. GREEN without
  recorded RED is treated by validation as unproven — tests written after the
  fact to confirm existing code do not count.
- **Count new assertions against the RED output.** Every assertion added must
  appear as a failure in that run. One that is green in RED holds in the
  pre-fix world too, so it is decoration, not evidence — rewrite it to pin the
  literal expected value, or delete it. This is the mechanical enforcement of
  "evidence must be able to fail"; the RED record aims at it but does not check
  it, and the tell is a RED count lower than the number of assertions written.
- **When you change a behavior, audit the tests that arrange the old one.** A
  suite that goes green after a behavior change can mean a fixture was silently
  re-purposed rather than that coverage held. Grep the suite for scenarios that
  *set up* the behavior under repair, and state per scenario whether the edit
  restored its original intent or quietly narrowed it.
- **A change that adds tests checks the CI job's remaining margin before
  pushing.** Job-level cancellation presents as a red check with **no failing
  assertion** — every suite reports passing and the step is killed anyway —
  which reads like a flake and invites a retry instead of a diagnosis. Thin
  margin is a gate-level disclosure, not a CI discovery.
- **RED and GREEN close in the same session, and commit together.** Never
  commit failing tests as a handoff contract for a later worker: an agent
  handed a red suite optimizes for "make it green", and will drift the
  implementation to fit a possibly-wrong test — or the test to fit the
  implementation — instead of delivering the behavior. The RED record is
  stage-report evidence; committed tests arrive with the code that passes
  them. If a session must stop mid-loop, the unfinished RED work stays
  uncommitted and the stage report says exactly where the loop stopped.
- **Scoped tests in the loop, full suite once at the exit.** During the
  build loop run only the tests scoped to the behavior under change (file,
  module, or tagged subset). Run the full suite exactly once, after scoped
  tests are green, as the stage-exit regression check — not on every
  iteration.
- Minimal diff that satisfies the AC. No unrelated refactoring. Apply the doc
  diff approved at ideation in the same branch.
- The deliverable must be self-contained for a fresh validator: stage report
  says what was produced, where, and how to run it.

### `validation` — fresh eyes, adversarial by default

A fresh-context agent verifies the deliverable against the ideation AC. The
validator checks what was produced; it never finishes the work.

- Reproduce each AC's `Verified by:` clause; report PASS/FAIL per criterion
  with actual evidence (command output, screenshots, on-disk state) — never
  the implementer's self-report. Same execution order as implementation:
  scoped checks per AC first, one full-suite run at the end — a full-suite
  failure outside the diff's blast radius is reported as context, not
  debugged by the validator.
- **Review through distinct lenses**, scaled to the diff: correctness always;
  add silent-failure, security, or type-design lenses when the diff touches
  error handling, auth/input boundaries, or new types. (Use the globally
  installed reviewer agents, e.g. `pr-review-toolkit:code-reviewer`.)
  For prose diffs (skills, agents, hooks-as-instructions), the correctness
  lens is **exercise-based**: actually invoke the changed skill/hook and
  observe behavior, applying `kc-plugin-forge`'s audit discipline — a prose
  change reviewed only by reading is not reviewed.
- **A documented guarantee is a claim, and gets the AC treatment.** When a doc
  diff states an absolute — "only", "always", "never", "exactly one" — name the
  input or edit that would falsify it, and check it, exactly as an AC names its
  falsifier. A guarantee the enforcement point does not make is a defect **in
  the doc even when the code is correct**, and a worse one than an undocumented
  gap, because the next reader builds on it. Validation verifies doc *claims*,
  not just doc presence.
- **Verify reviewer citations before acting on findings.** Check every cited
  `file:line` against the actual file — LLM reviewers fabricate plausible
  citations. If more than roughly a third of one reviewer's citations are
  wrong, discard that reviewer's entire round rather than triaging it. And
  when writing off a failure as pre-existing, prove it per failing line
  (blame against the change's commit range), never per file or surface.
- **Converge by naming residuals.** When a review round's findings stop
  being fixable defects and become a named class the chosen approach
  genuinely cannot solve, stop iterating: record the residual and its
  acceptance reason instead of opening another round. Chasing irreducible
  residuals is gold-plating dressed as rigor.
- **Cross-model gate before merge approval**: run one independent cross-model
  review of the diff. The reviewer is whichever cross-vendor tool is actually
  available, preferred in order `codex` → `agy`; no single vendor is required,
  but skipping the second opinion entirely is not. Unavailability is
  established by an attempted run that failed (quota, auth, missing binary),
  never assumed — record which reviewer ran, and when the preferred one was
  skipped, the observed failure. A P1 finding is fixed or explicitly waived
  with a recorded reason at the gate — never silently dropped.
- Exercise the E2E AC in the real runtime when one exists.
- **Coverage is a ratchet, not a target — scoped to executable code only.**
  This repo is prose-heavy: coverage applies ONLY to executable surfaces
  (scripts/, hooks, MCP/server code), where lines added or changed by a task
  meet an 85% bar via a diff-coverage check (the bootstrap task decides the
  tooling). Markdown skill/agent bodies are n/a-by-design — their proof is
  exercised behavior (a real invoke per the E2E clause), never coverage. A
  red coverage check on an executable diff is fixed or explicitly waived at
  the gate with a recorded reason; coverage percent is never an AC by itself.
- **Adversarial spot-check.** For one or two core behaviors, make a
  claim-breaking edit (revert a guard, flip a boundary) in a scratch copy and
  confirm the suite goes red. A suite that stays green under a claim-breaking
  edit is a hole — route back with that evidence.
- Rejection routes back to implementation (`feedback-to`) with concrete,
  file-anchored fixes. Two consecutive rejections on the same finding →
  escalate to the captain instead of a third round.
- **Every correction round carries a budget record.** Each rework round
  appends one entry: the round's actual effort against the ideation-declared
  estimate, the deviation, and the findings disposition. Past the declared
  tolerance, record a design-reset decision (back to ideation to re-cut)
  before opening any further round — the counter-based escalation above and
  this budget-based brake are independent circuit breakers. A round whose
  findings are all declined records `0 fixed` with every decline named:
  "nothing was found" and "everything found was declined" must never read
  alike.
- **Rework re-anchors on the source requirement.** On any route-back, the
  rework agent re-reads the original requirement and diffs it against the
  current ACs before touching code — rework loops naturally optimize
  against intermediate artifacts and silently drop original constraints.
  Any dropped constraint is restored or explicitly justified first.

### `done` — terminal

Merge after a passed validation gate (merge policy: PR to `main`), set `completed` and `verdict`, archive the task. Record the
measurement ledger row (below) in the same transition.

- **Merge only on observed green CI for the exact HEAD.** A passing local
  suite, a static PR approval, or "CI was green earlier" never substitutes
  for a live CI run observed green on the commit being merged. A red or
  running check at merge time blocks the merge — no exceptions by memory.

## Gate Authority

A gate is a decision point, not a status report. Who holds it depends on the
kind of decision, not on which stage it sits at.

| Seat | Holds | Examples |
|------|-------|----------|
| **Captain** | Direction and irreversibility | Scope authorship; what to work on next; schema / architecture / scope-cut / costly_no; accepting a documented residual against a red gate; any seat disagreement |
| **EM** (`ship-flow:science-officer-em`) | Bounded judgment on completed work | The ideation and validation verdicts — proceed / narrow / return / block |
| **FO** | Nothing adjudicative | Checklist accounting, AC-evidence presence, dispatch, merge mechanics, cleanup |

**Default: EM holds the gate.** The FO assembles the review — checklist
accounting, AC cross-check, reviewer findings — and routes it to EM for the
verdict. The FO neither renders the verdict itself nor forwards a completed,
findings-already-resolved stage to the captain for a rubber stamp.

**Auto-advance.** When a gate has zero Material findings, every AC carries
evidence, and the decision is reversible, EM approves and the FO advances
immediately. The captain is *notified in one line*, not asked. A captain who
wants it back says so; silence is not a gate.

**Escalate to the captain only when one of these holds — and name which:**

- The call is irreversible per Judgment Escalation below.
- Scope is being authored or re-cut. Only the captain holds scope.
- A Material finding survives EM review and changes what ships.
- A gate is red and the ask is to accept the residual on record.
- EM and FO disagree — that goes to the captain, never to a vote.

Anything else reaching the captain is over-escalation, and it costs more than
it protects: a captain pulled into six ceremonies per task stops reading the
two that mattered.

**Approval is scoped to the decision presented.** "The captain approved the
previous gate" is never authority for a later one.

**Speak consequence, not vocabulary.** A gate presented in the system's own
terms — a migration, a claim path, a corpus freeze — is not a decision the
captain can weigh; it is a request to trust the presenter. The tell is a
captain who answers "go with your recommendation" every time: at that point the
gate costs attention and returns nothing, and the seat has quietly moved back
to the FO without anyone deciding that it should.

Every escalation carries a plain restatement — literally "換句話說" — before it
asks for anything:

- **What breaks if this is wrong**, in terms of what a user or the team can no
  longer do. Not the mechanism; the consequence.
- **How expensive it is to reverse.** "Ships to production" and "one commit to
  revert" are different decisions and must not read the same.
- **What is actually being chosen.** Often it is narrower than the technical
  framing suggests — "restore something that was dropped by accident" is not
  "change how the system behaves", and the captain rules differently on each.

If the restatement cannot be written, the escalation is not ready: either the
FO does not yet understand the consequence, or there is no decision here and it
belongs to EM.

## Judgment Escalation

Irreversible calls — schema, architecture, scope-cut, costly_no, anything
merge-governing — are never self-adjudicated by the working agent. Route to a
fresh-context engineering-judgment agent (`ship-flow:science-officer-em`) for
independent synthesis, add one cross-vendor pass (codex/gemini) when the call
is contested, and bring the captain a CONVERGED recommendation. The captain
rules; disagreement between seats goes to the captain, not to a vote.

## Canonical Docs Ownership

| File | Owner | Updated |
|------|-------|---------|
| PRODUCT.md / ARCHITECTURE.md | Task lifecycle (ideation proposes, implementation applies, validation verifies) | In the PR that changes the behavior |
| ROADMAP.md / roadmap indexes | Captain (or sprint Commander) | Sprint boundaries, strategy shifts — never tracks task state (that's a `status --where` query) |
| This README | Captain-approved revision | When ledger data says a clause needs tuning |

## Measurement Ledger

Every task that reaches `done` (or is abandoned after implementation started)
appends one row to `docs/dev/ledger.csv`:

```
task_id, slug, dispatches, rework_rounds, wallclock_hours, tokens_if_known, diff_coverage, escaped_defects_7d
```

`escaped_defects_7d` is back-filled when a defect traced to the task surfaces
within seven days of merge. This ledger is the experiment: it is compared
against the ship-flow historical baseline (006-line dispatch/veto records).
Pre-registered bar — this lean flow wins if it holds ≤60% of baseline tokens
and ≤70% wall-clock with no added Severity-1/2 escaped defects; complexity
(extra stages, skills, mechanisms) earns its way back only through this
ledger, never through argument.

## Task Template

```yaml
---
id:
title:
status: backlog
source:
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

## Proposed approach

## Design determination

`required` (attach decision) or `trivial-pass — <reason>`.

## Acceptance criteria

**AC-1 — <end-state property>.**
Verified by: <reproducible check outside this file>. Falsified by: <the edit that would flip it>.

## Test plan

## Doc diff

<before/after wording for PRODUCT.md / ARCHITECTURE.md, or "none — no described behavior changes">

## Out of scope
```

## Commit Discipline

- Status changes commit at dispatch and merge boundaries (binary-owned).
- State commits are path-scoped per entity in the state checkout — never bare `git add -A`.
- Implementation commits land on the worktree branch; merge only after the validation gate passes.
