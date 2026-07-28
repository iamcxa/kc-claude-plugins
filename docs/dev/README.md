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

**The state checkout is wired per workspace, not per repo, and only one workspace
is meant to hold it.** This repo is worked through Conductor worktrees, so
`docs/dev/.spacedock-state/` is a *per-workspace* git worktree tracking the
`spacedock-state/dev` branch, and the path is gitignored in the code tree. Plain
`git worktree add` refuses a branch already checked out elsewhere, so at most one
workspace is the **holder**; every other workspace is a **non-holder** and writes
through the detached path below. That refusal is the whole enforcement, and
`git worktree add --force` overrides it — so single-holder is a convention this
section asks you to keep, not an invariant git will hold for you. The two
wirings are not interchangeable and the check that tells them apart is the same
command.

In a workspace where the worktree was never created, the same path is just an
ignored directory — and the degradation is silent: `spacedock new` reports
`created`, `spacedock status` reads the task back, and only
`spacedock state commit` fails (exit 1, git refusing to add an ignored file).
Tasks filed that way exist nowhere but that workspace. Run this before filing and
branch on what it says:

```bash
git -C docs/dev/.spacedock-state rev-parse --abbrev-ref HEAD
```

- `spacedock-state/dev` → **holder**. File normally; `spacedock state commit`
  works.
- a fatal error, or any other branch → **non-holder**. Do not try to check the
  branch out here, and never write into the holder's tree, which may carry a
  sibling session's uncommitted work. Append through a private detached worktree
  and a fast-forward push. Use a path unique to this workspace — a fixed
  `/tmp/sd-state` collides with a concurrent session doing the same thing — and
  **remove the worktree only after a push you watched succeed.** Two non-holders
  can detach from the same tip; the second push is rejected, and a cleanup that
  runs anyway strands a committed task in a directory nobody will look in again:

```bash
SD=$(mktemp -d /tmp/sd-state-XXXXXX)
git worktree add --detach "$SD" origin/spacedock-state/dev
# copy files in, commit, then push — rebasing onto whatever landed meanwhile:
pushed=no
for _ in 1 2 3; do
  git -C "$SD" push origin HEAD:refs/heads/spacedock-state/dev && { pushed=yes; break; }
  git -C "$SD" fetch origin spacedock-state/dev &&
    git -C "$SD" rebase FETCH_HEAD || break
done
if [ "$pushed" = yes ]; then
  git worktree remove "$SD"     # a cleanup failure here is not a push failure
else
  echo "unpushed commit left in $SD"
fi
```

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | SD-B32 stored ID from `status --next-id --id-seed <slug>` |
| `title` | string | Human-readable task name |
| `status` | enum | backlog, ideation, implementation, validation, done |
| `source` | string | Where the task came from (captain note, defect, audit) |
| `started` / `completed` | ISO 8601 | `started` at the first transition out of `backlog`, `completed` at the `done` transition — `wallclock_hours` is their difference, so a task that sits in the queue for a week does not bill that week |
| `verdict` | enum | PASSED or REJECTED — set at final stage |
| `worktree` | string | Set on first worktree dispatch, cleared at terminal merge |
| `issue` / `pr` | string | External references |
| `design` | enum | `required` or `trivial-pass` — set at ideation, or, for a `lane: defect` task that has no ideation stage, at the moment the FO classifies it into that lane. Empty during seed capture and through `backlog`; on the main line it is produced inside `ideation`, so the invariant starts at the ideation gate — never empty at that gate, and never empty in `implementation` or later |
| `lane` | enum | `defect` or `main` — the FO's Defect-lane classification, written when the FO routes the task out of `backlog` (not at seed capture, which authors no classification), so it is queryable (`status --where lane=defect`) instead of re-derived by re-reading every body. `defect` asserts all four conditions in the Defect-lane section hold |

## Proof Policy

Inherited from the spacedock proof discipline; the seven rules below are
binding in every stage report and every gate review.

1. **No prose-grep, and provenance decides independence.** A string match
   over an instruction file the model reads never proves a behavioral claim.
   A grep may serve as one-off evidence for an existence fact in a validation
   report; the same grep committed as a test is banned. Not because it can
   never go red — editing the matched wording, moving the file, or changing the
   pattern all turn it red — but because every edit that turns it red is an edit
   to the *text*: it tracks wording and is blind to behavior, so it passes
   straight through the regression it was committed to catch and goes red on
   rephrasings that broke nothing. And
   a check the author wrote to grade the author's own artifact is a self-issued
   stamp, not a gate. This is about what closes a gate, not about who may write
   a test: the worker's own RED-before-GREEN tests are exactly the evidence
   this workflow asks for, and they become insufficient only when they are also
   offered as the independent verdict on themselves. Independence at a gate
   comes from the fresh-context validator and the cross-model pass, never from
   the artifact grading itself.
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
5. **Automatic must-pass behavior checks live at stage boundaries, never in
   the worker's inner loop.** Hooks that fire on every commit/edit inside a
   work session are limited to fast mechanical checks (format, lint,
   typecheck). Behavioral or corpus/consistency checks, *as must-pass gates*,
   belong to the validation gate and CI: a must-pass check inside the inner
   loop turns "implement the behavior" into "make the check shut up", and the
   worker will drift the implementation — or the check's inputs — to satisfy
   it. This governs checks the tooling forces, never tests the worker chooses
   to run: RED-before-GREEN requires running the behavior's own tests inside
   that loop, and that is the mechanism working, not an exception to it.
6. **A claim must be able to fail, and it is checked when written.** An
   absolute — "exactly", "only", "always", "never", "cannot", "byte-for-byte"
   — written into a reference, a code comment, or a commit message either
   names the enforcement point that makes it true, or is rewritten as the
   bounded claim the code actually supports. This is rule 2 applied to prose:
   the same discipline an AC's evidence gets, because a documented guarantee
   *is* a claim and the next reader builds on it. Two consequences worth
   stating outright. **It binds at authoring time, and the author is the
   enforcement point** — there is no mechanical check behind it, which is why
   it is written as a rule the writer applies rather than a gate someone else
   runs. The validation-stage clause is the backstop for what slips through,
   and a backstop that fires every time is a cost, not a control.
   **Coverage past the author is uneven, and that is the point.** A reference
   or doc diff reaches validation. A code comment reaches it only
   incidentally, inside a diff a reviewer happens to read closely. A commit
   message reaches no gate at all. The thinner the downstream coverage, the
   more the authoring moment is the only moment — four of these shipped in two
   days, and the two nobody caught until later were a commit message and a
   comment, which are exactly the two thin cases. A claim inherited from a
   report, a reviewer, or an external contributor is not exempt — adopt it
   only after checking it, and say which.
7. **A negative result is a claim, and carries the same bar as a positive
   one.** "The search found nothing" is evidence about the search. "The file is
   unchanged" is evidence about the file, not about the failure. A number
   measured while you were perturbing the system is evidence about the
   perturbation. Before reporting an absence — no such skill, no such caller,
   nothing tracked, not a regression — name the scope actually searched and why
   that scope is the population, or run a second strategy that would have found
   the thing if it existed: one tool, one pattern, one filter is a sample, not a
   census. In this repo the sampling trap is concrete — a plugin's behavior can
   live in `skills/*/SKILL.md`, an `agents/*.md`, a hook script, or the local
   install under `~/.claude/plugins/`, so a single `grep` over one plugin
   directory is never the population. And an unexplained signal is traced, never
   assigned an invented origin — "probably another session" is a story, not a
   cause.

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
When **all four** hold, the FO advances `backlog → implementation` directly. The
verdict goes in the `lane` frontmatter field so it is queryable, and its
justification in the task body — a classification that lives only in prose gets
re-derived by re-reading every open task, which is the expensive way to learn
something already decided:

1. The root cause is already identified and cited at `file:line`.
2. Acceptance is mechanical — a test that fails before the fix and passes after.
3. It is a single seam: one surface, no cross-layer ripple, no schema change.
4. No design decision is open. If the fix has two defensible shapes, it is not
   in this lane.

Everything else still applies: RED-before-GREEN, the proof policy, the
validation stage, and the merge bar. **The lane removes a design stage, never
verification** — and a defect whose fix turns out to need a design decision
goes back to `ideation` rather than being decided inside implementation.

The lane removes the stage, never the stage's outputs. Ideation produces four
things later stages read back — a design determination, the ACs validation
checks against, the appetite and tolerance the correction-round budget measures
against, and the implementation dispatch sizing — so **the FO writes all four
when it classifies the task into this lane**: `design: trivial-pass` reasoned by
the fourth condition above, one AC that is the mechanical test named by the
second, a one-line estimate with its tolerance, and the sizing (for a bounded
fix, one dispatch, unless the classification says otherwise). That record is the
lane's ideation of record; every clause elsewhere that says "the
ideation-declared X" reads it here. The lane's AC bar is that mechanical test
alone — a bounded fix restores behavior rather than delivering new value, so the
value-AC requirement does not apply, and a defect that needs one is not a bounded
fix and belongs in the main line.

**`design: trivial-pass` here does not contradict the ideation clause that makes
`design: required` mandatory for a UI, contract, interface, schema, or visual
surface.** That list asks whether the task *decides* something about the surface,
not whether it touches one. A bounded repair restores behavior the surface
already documents and decides nothing, so `trivial-pass` is the accurate
determination even when the seam is a UI or a contract. A fix that would change
the surface's shape has an open design decision by definition, which is condition
four failing — so it was never in this lane, and the `required` clause reaches it
in `ideation` where it belongs. If the two readings ever seem to both apply, that
is the tell that condition four is not actually satisfied.

**This attaches to the classification, not to capture.** Seed capture stays what
the `backlog` clause says it is: title, `source`, one paragraph, under two
minutes, no design work, `lane` empty. The four outputs are owed at the moment
the FO advances `backlog → implementation`, which is the moment the task skips a
stage — and a task advanced into this lane missing any of the four is not in it:
that advance is returned for the same reason an ideation gate without a design
determination is returned unread.

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
  body, plus the deviation past which the work stops and gets re-cut rather
  than continuing. Those two numbers are the "ideation-declared estimate" and
  the "declared tolerance" the validation stage's correction-round budget
  measures each rework round against; a task that declares neither has nothing
  for that brake to read. When work is about to exceed it: cut scope (defer a
  sub-part to backlog) or park cleanly with re-enterable state and explicit open
  findings — never extend the budget silently, and never compress
  validation to land inside it. Size or budget variance is a drift signal
  to investigate, never a number to hit by padding artifacts or stripping
  tests.
- **The cheapest path that satisfies the AC is the default, and the gate is
  told which one it took.** Ideation answers two questions in the task body
  before choosing an approach: *what is the fastest path?* and *what is the
  smallest cut?* It then records the cheaper option it is taking, the more
  thorough option it is not taking, and why the difference is not needed to
  satisfy the AC. **Default to the cheap one.** This is a scope default, never
  a quality one — the proof policy, the AC bar, RED-before-GREEN and the
  validation stage are untouched, and "cheap" never means thinner evidence.
  **Two cases, and they route differently.** When the cheaper option is a
  different way to satisfy the same ACs — fewer moving parts, a narrower
  mechanism, an existing seam instead of a new one — nothing is being cut, so
  the FO surfaces it at the gate in one line ("taking the cheap path: X") and
  proceeds. When the cheaper option **defers or drops a sub-part** — anything
  phrased "deferring Y" — that is a scope cut, and Gate Authority gives scope
  cuts to the captain alone: it is escalated for an explicit answer, not
  presented for a silent override. A cheap path taken silently is the agent
  authoring scope, which the clause above forbids — and an expensive path taken
  by default is the more common and more expensive mistake, because nobody is
  ever asked to approve it.
- **One-sentence pre-mortem.** Before the gate: "if this ships exactly per
  spec and still fails, the most likely cause is ___" — pick one of {wrong
  problem, criteria that pass without delivering value, wrong framing lens,
  hidden assumption, over-conviction}. This is an orthogonal
  future-failure check the AC rubric structurally cannot generate.
- **Design determination is mandatory, never skipped.** Every task records
  `design: required` (the task **decides** something about a UI, contract,
  interface, schema, or visual surface — its shape, not merely its behavior;
  attach the concrete design decision: wireframe reference, API shape,
  before/after) or `design: trivial-pass` with a one-line reason. **Touching
  such a surface is not the trigger; deciding about it is** — a repair that
  restores behavior the surface already documents decides nothing and is a
  `trivial-pass`, which is what lets the Defect lane classify a single-seam UI
  or contract fix without contradicting this clause. An ideation gate presented
  without a design determination is returned unread.
- **Reverse-recovery audit before any "build/add X"** (brownfield default):
  assume the abstraction may already exist. Layer-trace the path (UI →
  contract → handler → domain → persistence → readback) and classify each
  layer WORKING / EXISTS_BROKEN / STUB / MISSING with file:line. Greenfield
  is allowed only after proof of absence (multi-strategy, multi-language
  search) — the general bar for any absence claim is Proof Policy rule 7.
  A single broken seam means repair scoped to that seam, not a
  rebuild. Full procedure: `_mods/reverse-recovery-audit.md`.
  **Audit against the merge target** (fetch `origin/<trunk>` first), never
  only the working branch — a stale branch shows stale infrastructure, and
  a MISSING verdict read off it can be seven weeks wrong. Implementation
  re-verifies the audit's load-bearing MISSING claims against a fresh
  merge target before building, and escalates instead of building when a
  premise has collapsed.
  **Enforcement facts are read live, never inferred from repo files**: what
  CI actually requires comes from the platform API
  (`gh api repos/iamcxa/kc-claude-plugins/branches/main/protection`), not from
  reading `.github/workflows/`. Most workflow files here are *not* required
  checks, and the required contexts are matched by the **job `name:` string**.
  Adding steps to a required job is identity-safe. Renaming the job does not
  loosen the protection — it **wedges** it: branch protection still requires the
  old context, nothing reports it any more, and the PR sits at "Expected —
  waiting for status to be reported" until either the old name is restored so
  something reports that context again, or the protection is edited to require
  the new one. So a job rename is a change to the merge rules, which
  Judgment Escalation puts on the captain. And the symptom to look for is the
  *missing* context, not a red one: the renamed job still runs and can fail on
  its own merits, but nothing goes red merely because the required context
  stopped being reported — which is why this is caught by reading the
  protection rather than by watching the checks.
  The live-read matters more than usual in this repo because a required check's
  display name can outlive what it checks: the parity context still names the
  README even though per-plugin version badges were retired from it.
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
- **Count new assertions against the RED output.** Every assertion added must be
  *able* to appear as a failure in that run. A case stops at its first failing
  assertion, so later assertions in the same case never execute — compare failing
  *cases* against the cases that should fail, and for the rest ask per assertion
  whether any RED run could reach it. An assertion reachable in RED and green
  anyway holds in the pre-fix world too, so **as evidence for the behavior** it
  is decoration — rewrite it to pin the literal expected value, or delete it.
  The exception is the assertion that is not claiming the behavior: a
  precondition or arrangement check, green by construction in both worlds,
  exists to prove the case exercised what it says it exercised, and deleting it
  makes a later green less trustworthy, not more. Keep those, and say in the RED
  record which they are — an unlabelled green assertion is read as a claim about
  the behavior. This is the mechanical enforcement of "evidence must be able to
  fail"; the RED record aims at it but does not check it, and the tell is an
  added behavior-claiming assertion no RED run can reach.
- **When you change a behavior, audit the tests that arrange the old one.** A
  suite that goes green after a behavior change can mean a fixture was silently
  re-purposed rather than that coverage held. Grep the suite for scenarios that
  *set up* the behavior under repair, and state per scenario whether the edit
  restored its original intent or quietly narrowed it.
- **Name what CI will do differently, before pushing.** Local green is a fact
  about your machine. Two failures here came from that gap and a third case is
  documented as a hazard that has not bitten yet; each has its own cheap
  check — run the one the diff earns, not all three:
  - *Tests added, or materially slowed* → measure the job's remaining margin.
    Job-level cancellation presents as a red check with **no failing
    assertion** — every suite reports passing and the step is killed anyway —
    which reads like a flake and invites a retry instead of a diagnosis. Thin
    margin is a gate-level disclosure, not a CI discovery.
  - *Behavior that depends on OS, libc, locale, or clock* → run that check on
    CI's OS family. A differential's Python reference rendered year 1 as
    `0001` on this macOS and `1` on glibc, so the suite read 139/0 locally and
    red on CI.
  - *A file governed by a CI-pinned tool* → run that exact version, not the
    local one. A newer local ShellCheck retires checks CI still enforces
    (`kc-pr-flow/CLAUDE.md`). This is the documented case, not the bitten one:
    unlike the two above, no red CI here has been traced to it.

  What this is **not**: a general "reproduce CI locally" obligation. The job
  runs on mutable `ubuntu-latest`, so a local container reproduces the
  platform and never the job — setup time, runner speed, and the job-wide cap
  are not in it. Exact-head CI remains the merge authority; this clause only
  moves a predictable red into the minute before the push.
- **RED and GREEN close in the same session, and commit together.** Never
  commit failing tests as a handoff contract for a later worker: an agent
  handed a red suite optimizes for "make it green", and will drift the
  implementation to fit a possibly-wrong test — or the test to fit the
  implementation — instead of delivering the behavior. The RED record is
  stage-report evidence; committed tests arrive with the code that passes
  them. If a session must stop mid-loop, the unfinished RED work stays
  uncommitted and the stage report says exactly where the loop stopped.
- **Scoped tests in the loop, full suite plus ripple at the exit.** During the
  build loop run only the tests scoped to the behavior under change (file,
  module, or tagged subset). Run the full suite once, after scoped
  tests are green, as the stage-exit regression check — not on every
  iteration. Once is the *entry* count, not a cap: a failure that run surfaces
  is fixed and the suite re-run, because the exit condition is a green
  full-suite run on the code being handed over, and a rule that forbade the
  second run would trade the regression for the ceremony. For a change to a surface something else reads, also run the checks
  that actually consume *that* surface — they are not interchangeable, so run
  the ones the diff earns, not all of them:
  - a version value or propagation target — `<plugin>/.claude-plugin/plugin.json`,
    `<plugin>/.codex-plugin/plugin.json`, a `marketplace.json` version string,
    `release-please-config.json`, `.release-please-manifest.json` →
    `scripts/version-parity-check.sh`, which is the required check and the only
    one that reads the release config.
  - `marketplace.json` structure — an added, removed, or retargeted entry, a
    changed `source` → `scripts/marketplace-verify.sh` (schema + clean-`HOME`
    installability).
  - a `*/skills/*/SKILL.md` frontmatter block →
    `scripts/skill-frontmatter-lint.sh`.
  - adding or removing a plugin directory → `version-parity-check.sh` *and*
    `marketplace-verify.sh`, since parity fails closed on a directory with no
    marketplace entry and vice versa, and the entry also has to resolve.
  - a workflow under `.github/workflows/` → no local script validates these;
    the check is the live run, so say in the stage report which workflow was
    touched and whether it is a required context (read it live, per the
    ideation clause).
  **The exit condition is never "the reported error is gone."** That is a
  not-a-regression claim and Proof Policy 7 governs it: the one spec that named
  the bug was never the population. A failure surviving the exit run is written
  off as pre-existing only by the per-failing-line rule the validation stage
  states — never per file, never per impression.
- Minimal diff that satisfies the AC. No unrelated refactoring. Apply the doc
  diff approved at ideation in the same branch.
- The deliverable must be self-contained for a fresh validator: stage report
  says what was produced, where, and how to run it.

### `validation` — fresh eyes, adversarial by default

A fresh-context agent verifies the deliverable against the ideation AC. The
validator checks what was produced; it never finishes the work.

The gate is presented with a filled **evidence block** — one line of *specific,
falsifiable* evidence per item (presence of text is not the bar), and anything
left blank counts as not-done, never a silent pass. It records five lines —
`Lenses:` (the diff classification, and per fired lens its verdict and finding
count), `Diff coverage:` (the measured %), `Adversarial:`, `Cross-model:`,
`E2E:` — each naming what was actually run and what it returned.

**A field whose own clause permits a skip is written `N/A — <why>`, never a bare
`N/A`.** A skip without its reason and a skip with one do not read alike. Three
fields have such a clause — `Adversarial:`, `Diff coverage:`, `E2E:`; `Lenses:`
and `Cross-model:` have none and are therefore never `N/A`. **The condition that
permits the skip lives in that field's own clause, and is not restated here** — for
`E2E:` that is the E2E-first acceptance clause at ideation; for the rest, the
validation clauses in this section. Only two are set here, because nowhere else
states them: `Adversarial: N/A — <why>` for a diff with no behavioral guard to
break, and `Diff coverage: N/A — prose-only diff, no executable surface` for the
markdown-only diffs that are this repo's common case (the coverage clause below
scopes what counts as coverable). `Lenses:` and `Cross-model:` are never `N/A`.
Scale changes how deep each item goes, never whether it runs — this block is
where an agent is tempted to convert "small" into "skipped", and small is not a
skip condition for any of the five. A gate presented without the block is
returned unread — the same bar the ideation stage's design determination is held
to.

- Reproduce each AC's `Verified by:` clause; report PASS/FAIL per criterion
  with actual evidence (command output, screenshots, on-disk state) — never
  the implementer's self-report. Same execution order as implementation:
  scoped checks per AC first, one full-suite run at the end — a full-suite
  failure outside the diff's blast radius is reported as context, not
  debugged by the validator.
- **Lens selection is mechanical, not a judgment call.** Classify the diff and
  fire every matching lens; a "touches none" is justified by naming the surfaces
  the diff *does* touch (so a reviewer can check the classification — not by an
  adversarial revert, which tests code, not a skipped lens). Correctness always
  fires; then, by what the diff touches: **security** (auth / permission / trust
  boundary, a hook that runs shell, a workflow with secrets) · **silent-failure**
  (error handling, input validation, fallbacks, swallowed errors) ·
  **type-design** (a new or changed type) · **concurrency** (locks, async
  ordering, shared/mutable state) · **resource-lifecycle** (processes, handles,
  memory, unbounded growth) · **manifest/back-compat** (a change to
  `marketplace.json`, a `plugin.json`, skill frontmatter, or any other contract
  an already-installed copy reads — does an existing install still resolve?).
  The independent cross-model gate (below) always runs and is recorded
  separately; it is not one of these lenses. For prose diffs (skills, agents,
  hooks-as-instructions) — this repo's common case — the correctness lens is
  **exercise-based**: actually invoke the changed skill/hook and observe
  behavior, applying `kc-plugin-forge`'s audit discipline. A prose change
  reviewed only by reading is not reviewed. (Reviewer agents, fully qualified so
  the identifier can be dispatched as written:
  `pr-review-toolkit:code-reviewer`, `pr-review-toolkit:silent-failure-hunter`,
  `pr-review-toolkit:type-design-analyzer`, `kc-pr-flow:tob-security-reviewer`,
  `kc-pr-flow:tob-actions-auditor` for workflow diffs.)
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
  (blame against the change's commit range), never per file or surface — and
  never from a run whose conditions you were perturbing yourself.
- **Converge by naming residuals.** When a review round's findings stop
  being fixable defects and become a named class the chosen approach
  genuinely cannot solve, stop iterating: record the residual and its
  acceptance reason instead of opening another round. Chasing irreducible
  residuals is gold-plating dressed as rigor.
- **Cross-model gate before merge approval**: run one independent cross-model
  review of the diff. **Cross-vendor is relative to the model running the gate**,
  not a fixed list: pick the first available tool from a different vendor than
  the reviewing model — from a Claude session that is `codex` → `agy`, from a
  codex session it starts at `agy`. A lighter variant from the same family is
  not a second vendor and does not satisfy this. No single vendor is required,
  but skipping the second opinion entirely is not. **Unavailability is
  established by an attempted run that failed** (quota, auth, missing binary),
  never assumed — record which model ran the gate, which reviewer ran, and when
  a preferred one was skipped, the observed failure. A P1 finding is fixed or
  explicitly waived with a recorded reason at the gate — never silently dropped.
- Exercise the E2E AC in the real runtime. Whether the task owes one at all is
  decided by the E2E-first clause at ideation, not here.
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
- **Live-CI red evidence short-circuits per step.** When an AC requires proving
  a required check actually fails on bad input, use a non-draft probe PR
  observed red on live CI — and plan one probe commit per step: steps within a
  CI job short-circuit, so a single red run proves only the first failing step,
  and proving N steps each go red takes N sequential probe commits. Close the
  probe PR without merging, delete its branch, and record the run URLs as gate
  evidence.
- Rejection routes back to implementation (`feedback-to`) with concrete,
  file-anchored fixes. A second consecutive rejection at this gate ends the
  loop and goes to the captain, per Gate Authority. **The trigger is the count,
  not the findings** — a cycle that closes every prior finding and immediately
  surfaces new ones on adjacent surfaces is the stronger stop signal, not a
  fresh start: the approach cannot hold the boundary, and the next cycle finds
  the next surface. Counting only repeated findings never fires on that case,
  and it is the common one.
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
  Any dropped constraint is restored or explicitly justified first. **The diff
  runs the other way too: name every changed file no AC requires, and either
  delete it or state which AC it serves.** A rework loop adds machinery as
  readily as it drops constraints, and added machinery is the more expensive
  direction — it arrives with its own defects and its own review rounds, and
  each round it survives makes it look more load-bearing than it is.
- **One scope checkpoint before the first validation dispatch.** The FO maps
  each changed file to the AC it serves and identifies the ones that map to
  none — do not ask whether an AC *names* the file. ACs are end-state properties
  and rarely name an implementation path, so a name-matching check reports every
  legitimate file as unnamed while a stray one whose path happens to appear in
  an AC slips through.
  **What the FO does with the result depends on whether the set is empty.** Zero
  unmapped files is a notification: one line to the captain (files and lines
  changed, all mapped), and the FO proceeds without waiting. A non-empty set is
  not — an unmapped file is scope nobody authorized, and Gate Authority puts
  scope on the captain. The FO first tries to resolve it itself, exactly as the
  clause above says: delete the file, or state which AC it serves. Whatever
  cannot be resolved that way is escalated by name and the FO waits for an
  answer.
  The checkpoint sits here because the cheapest moment to cut is after the diff
  is real but before review rounds have compounded on it. A round spent
  reviewing machinery nobody wants is paid twice: once to find its defects, once
  to fix them.

### `done` — terminal

Merge after a passed validation gate (merge policy: PR to `main`), set `completed` and `verdict`, archive the task. Record the
measurement ledger row (below) in the same transition.

- **Merge only on observed green CI for the exact HEAD.** A passing local
  suite, a static PR approval, or "CI was green earlier" never substitutes
  for a live CI run observed green on the commit being merged. A red or
  running check at merge time blocks the merge — no exceptions by memory.

## Continuation & handoff

Picking up an in-flight branch — a closed sibling Conductor workspace, a
session-limit resume, a `/kc-session-handoff` record — does **not** inherit the
prior agent's validation. Before advancing: inventory what the prior agent left
(committed **and** uncommitted/WIP working-tree state), re-anchor on the source
requirement, re-classify the diff, and reconcile any upstream drift that landed
on `main` during the hiatus. Those four are owed at whatever stage the work
resumes. The validation evidence block is **not** re-run by the resuming
implementer — that would be the self-report this workflow forbids; it is owed on
entering or re-entering `validation`, against a fresh merge target, by the
fresh-context validator that stage requires.

A prior agent's "mostly done / green tests / one review passed" is a starting
point to verify, never a validation to trust — the continuation frame is exactly
where a half-done validation gets silently inherited as complete. Re-verify every
inherited finding's load-bearing claim against the code, not the prior narrative.
This is the `Rework re-anchors on the source requirement` clause with a broader
trigger (any resumed work), not a separate workflow. In this repo the frame
arrives more often than elsewhere, and the contended surface is **a shared
working tree, not a sibling worktree**: each Conductor workspace has its own
`HEAD`, so a sibling *workspace* cannot move yours, but a second session
operating in the *same* workspace can `git checkout` under you mid-task and take
files with it. So the inventory step reads the working tree it is standing in,
not the last thing you remember writing — and commits from an isolated
`git worktree add` when the tree is contended, since a commit is safe by SHA and
a working tree is not.

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
- Two consecutive rejected cycles closed at the same gate — see the validation
  stage's rejection clause. Unlike the bullets above it, this one fires on
  cycle count alone, whatever the findings were.

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
merge-governing — are never self-adjudicated by the working agent.
**Merge-governing means a change to the merge rules themselves** — branch
protection, a required check, the merge policy, the release-please config that
propagates versions — **not a gate verdict that lets this one merge proceed.** A
passed validation gate is the second kind, so it stays inside the auto-advance
rule above; reading it as the first kind would make auto-advance dead for the
only stage it matters at. Route to a
fresh-context engineering-judgment agent (`ship-flow:science-officer-em`) for
independent synthesis, add one cross-vendor pass (codex/gemini) when the call
is contested, and bring the captain a CONVERGED recommendation. The captain
rules; disagreement between seats goes to the captain, not to a vote.

## Canonical Docs Ownership

| File | Owner | Updated |
|------|-------|---------|
| PRODUCT.md / ARCHITECTURE.md | Task lifecycle (ideation proposes, implementation applies, validation verifies) | In the PR that changes the behavior |
| ROADMAP.md / roadmap indexes | Captain (or sprint Commander) | Sprint boundaries, strategy shifts — never tracks task state (that's a `status --where` query). The same pass sweeps overdue `pending:` cells in the ledger, per Measurement Ledger |
| This README | Captain-approved revision | When ledger data says a clause needs tuning |

## Measurement Ledger

Every task that reaches `done` appends one row to `docs/dev/ledger.csv`. So does
a task **abandoned** after implementation started — the FO writes that row in the
same action that archives the task, since no later transition will come along to
write it:

```
task_id, slug, dispatches, rework_rounds, wallclock_hours, tokens_if_known, diff_coverage, escaped_defects_7d
```

**Instrumented at the boundary, never reconstructed.** `dispatches` and
`tokens_if_known` cannot be recovered after the fact — nothing in git history or
the archived task bodies carries them, so a row left at `n/a` stays `n/a`.

**The boundary is earlier than the row, so the counters need somewhere to live
before the row exists.** The row is written once, at whichever terminal boundary
the task reaches — the `done` transition, or archival for a task abandoned after
implementation started; the numbers accrue across every dispatch before it. They
accumulate in the task body's `## Measurement` section (see the task template) —
one line appended per dispatch, `dispatches` incremented at launch and the token
figure filled in on return. The terminal boundary sums that section into the row.
A task reaching `done` with no `## Measurement` lines was never instrumented, and
**that is a defect to repair before the transition, not a licensed `n/a`** — the
invariant below says a `done` transition may not leave `tokens_if_known` at
`n/a`, and this section carves no exception out of it. An abandoned row is the
one that may close at `n/a`, because the work stopped rather than shipped.

**Rolling up a mixed section has exactly one right answer**, and it is the `+`
convention below rather than a judgment call: sum the dispatches whose tokens are
known, suffix the total with `+`, and the row is a floor excluded from baseline
and bar comparisons. Every dispatch unknown means there is nothing to sum, and
the cell is `n/a`. Silently summing the known ones without the `+` is the one
move that must not happen — it reports a floor as a measurement.

**Both are the FO's to record, at opposite ends of the same dispatch.** The FO
increments `dispatches` at the launch boundary, *before* control passes to the
worker, and appends the token figure when that worker returns. Neither belongs to
the worker: a subagent asked to self-report its consumption answers that it is
not observable to it. Treat that as the harness's current state rather than a
law, and re-test it the next time a worker is asked. And a worker that dies
before writing anything still consumed a dispatch that has to be counted, which
no harness change fixes.

**Two token notations, and they mean different things.** A leading `~` is a
rounded measurement (`~461K`) and still counts as a measurement. A trailing `+`
marks a **floor** — a dispatch that died on a session limit reports no usage at
all, so its tokens are unrecoverable and the row's total is a lower bound rather
than a measurement. An unmarked floor silently flatters the ≤60% comparison, so
mark it (`2205805+`); such a row still closes, but is excluded from baseline and
bar comparisons. "Reports no usage at all" is an observation about today's
harness, not a law — it is falsified the day a session-limit death still returns
a usage figure to the parent, so check it on the next such death and drop the `+`
convention when it stops being true. An underestimate presented as a measurement
is worse than an admitted gap, because it errs toward "we are doing well".

Recording is not checking — it writes a number at a stage boundary and gates
nothing, so Proof Policy 5 does not apply to it.

`escaped_defects_7d` is back-filled when a defect traced to the task surfaces
within seven days of merge; until that window closes the cell reads
**`pending:<YYYY-MM-DD>`** — the date the window shuts, never a bare `pending`,
never `0`, never blank. An unobserved window and a clean one must not read alike,
and a bare `pending` cannot say which of the two it is *becoming*: it reads the
same on the day it is written and a year later. Carrying the date makes
overdueness a property of the file: a reader — or a one-line `awk` over the
eighth column comparing the suffix against today — can tell at a glance which
cells are owed, without reconstructing when anything merged.
Record the closed value as a Severity-1/2 count, because that
is the only severity the bar reads; lower-severity escapes go in the task's
archive note, where they inform without moving a threshold they were never meant
to move.

Two cases where a `pending:` cell would never close, so it is not written: a task
**abandoned** after implementation started never merges, so its window never
opens and the cell reads `n/a — abandoned`; and rows that predate this clause
were filed with the cell blank, which is exactly the ambiguity the clause
forbids, but rewriting them now would assert a window state nobody observed.
**The rule binds rows written from here on**; the pre-existing rows in
`docs/dev/ledger.csv` keep their blank cell, which is read as unknown, not as
clean.

**Two pieces of ledger upkeep happen after a row is written, and they need
different triggers**, because only one of them can be reached by writing another
row.

**Closing a `pending:` cell needs a trigger independent of task completion.**
The FO sweeps overdue cells before any ledger append — that covers the common
case at no extra cost — but an append cannot be the *only* trigger: a queue that
goes quiet, a sprint that ships nothing, or the last task of a cycle leaves
`pending:` cells whose windows shut with nobody scheduled to look. So the sweep
also belongs to the captain's sprint-boundary pass over `ROADMAP.md`, which the
Canonical Docs Ownership table already schedules and which happens whether or not
any task reached `done`. Either party sweeping is enough; the point is that the
obligation does not depend on work arriving. This is why the cell carries its own
due date — a sweeper needs to recognise an overdue cell from the file alone, not
reconstruct merge dates.

**Freezing the baseline medians does not need one.** The cohort can only complete
when a qualifying row is *appended*, so the append is not merely a convenient
trigger, it is the only event that can change the answer. The FO writes its row
first and counts after: if that row was the tenth qualifying one, it computes the
two medians *from the ten rows now present* and edits them into this section with
the task ids and the date. Counting before the append reads nine rows and freezes
the wrong number. If no further row ever arrives the cohort stays incomplete,
which is the correct state and not a missed obligation.

Neither is a gate; both are bookkeeping.

This ledger is the experiment. **Its baseline is a prospective control cohort
recorded here, not a historical record someone has to go find**: the first ten
rows carrying a complete `wallclock_hours` and a `tokens_if_known` that is
neither `n/a` nor `+`-suffixed. Their medians become `baseline_tokens_per_task`
and `baseline_wallclock_hours`, written into this section with the task ids and
the date computed, and **frozen** — a moving baseline measures nothing. As of
2026-07-28 the cohort stands at 8 of 10 qualifying rows, so no baseline is
computed yet. Those are the only two baselines because they are the only two
terms of the bar expressed as a ratio to one; its third term,
`escaped_defects_7d`, is an absolute threshold and needs no baseline.
`rework_rounds` stays a recorded column with no baseline, and any later use of it
computes its own from the rows then present.

**Say plainly what that can and cannot answer.** It measures whether this flow is
getting cheaper over time. It cannot answer whether it beats what it replaced.
The original comparison cited "the ship-flow historical baseline (006-line
dispatch/veto records)", and three searches on 2026-07-28 — a
`git log --diff-filter=A` over any `*006*` path across all refs, a
commit-message sweep for `006`, and a grep over `docs/dev/` — found that no
`006-*` entity is present in this repo's history and no dispatch/veto record set
appears to have been committed. **That is a bounded claim, and Proof Policy 7
says so out loud** — `--diff-filter=A` misses a record that arrived by rename,
and a grep over the current `docs/dev/` misses one that was later deleted or
lived elsewhere, so even inside the repo this is a strong sample rather than a
census. Outside it, agent session transcripts, harness telemetry, and the
`context-lake` journal were not searched at all, and a durable per-dispatch token
record, if one survives, is most likely in one of those. So the honest state is
**unavailable, not proven absent**: the bar that rested on that denominator does
not stand today and is retired, and reinstating it needs a located record rather
than an assumption that one is out there.

Until the cohort is complete and its medians are written above, a clause added on
this bar's strength must say in its own text that it rests on argument rather
than data — the ledger held to the Proof Policy 2 it enforces on every AC.
Pre-registered bar — this flow is improving if a row holds ≤60% of baseline
tokens and ≤70% of baseline wall-clock with no added Severity-1/2 escaped
defects; complexity (extra stages, skills, mechanisms) earns its way back only
through this ledger, never through argument. **That bar reads three columns —
`tokens_if_known`, `wallclock_hours`, and `escaped_defects_7d`.** Only the first
two are knowable at the transition, so **those two — not `dispatches` — are what
a `done` transition may not leave at `n/a`**; `escaped_defects_7d` closes at
`pending:<date>` by design and is back-filled when that date passes.

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
lane:
---

## Problem

## Proposed approach

## Design determination

`required` (attach decision) or `trivial-pass — <reason>`.

## Acceptance criteria

**AC-1 — <end-state property>.**
Verified by: <reproducible check outside this file>. Falsified by: <the edit that would flip it>.

## Test plan

## Measurement

<one line per dispatch, appended by the FO: `D<n> launched <when> | tokens: <figure on return, or n/a>`>

## Doc diff

<before/after wording for PRODUCT.md / ARCHITECTURE.md, or "none — no described behavior changes">

## Out of scope
```

## Commit Discipline

- Status changes commit at dispatch and merge boundaries (binary-owned).
- State commits are path-scoped per entity in the state checkout — never bare `git add -A`.
- Implementation commits land on the worktree branch; merge only after the validation gate passes.
