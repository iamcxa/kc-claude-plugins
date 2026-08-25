---
title: Six defects from one dogfood run and one adopter run, delivered outside the stages
status: ideation
source: kc-rules-review dogfood run 2026-08-25 (501 sessions, 1224 human turns) plus an adopter's independent run; filed after the workflow's second-PR trigger fired and was walked past
product: kc-team-ops
sprint: S1
started: 2026-08-25T07:11:35Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: kmg9zdxg2h2n2k0c7j86peq0
gates:
    version: 1
    records:
        - id: gate:kmg9zdxg2h2n2k0c7j86peq0:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kmg9zdxg2h2n2k0c7j86peq0-backlog-1
              briefing:
                id: briefing:kmg9zdxg2h2n2k0c7j86peq0:backlog:attempt-1:revision-1
                digest: sha256:c285ade92fa8bca8a40e77c83ab2720fc4369094023a1616ac6ac6fc73ccb352
                request-digest: sha256:3818b1150b4683132cfa9f3ee87cf1ebdd6c5d359e779ae866c632affbbf2202
                room-ref: ./kc-rules-review-dogfood-defects/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kmg9zdxg2h2n2k0c7j86peq0:backlog:1
                briefing: briefing:kmg9zdxg2h2n2k0c7j86peq0:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-25T06:59:32.381202Z"
                decision: approve
                reason: 'Captain approved at the backlog gate: the direction — bring the remaining kc-rules-review defects back inside the stages — is accepted; sprint scheduling and the v2 profile receipt remain the Captain''s to supply before the route''s first working state.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:kmg9zdxg2h2n2k0c7j86peq0:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:kmg9zdxg2h2n2k0c7j86peq0-ideation-1
              briefing:
                id: briefing:kmg9zdxg2h2n2k0c7j86peq0:ideation:attempt-1:revision-1
                digest: sha256:c1a688c1ed382c6a957ac9ca6bc879a02f269e6b0d2c023df09483885d94a60d
                request-digest: sha256:716ec1691dbbee918e6466a5e81b2ffa59df87772fa7a7bbbf46171e62231743
                room-ref: ./kc-rules-review-dogfood-defects/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kmg9zdxg2h2n2k0c7j86peq0:ideation:1
                briefing: briefing:kmg9zdxg2h2n2k0c7j86peq0:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-25T07:25:25.993881Z"
                decision: approve
                reason: 'Captain approved the shape at the ideation gate: two slices, trunk-only, seniority experiment explicitly out of scope; slice 1 (the defect-reporting slot) branches from main now.'
              application:
                target-stage: implementation
                state: pending
sprint-readiness: ready
---

## Problem

One full dogfood run of `kc-team-ops:kc-rules-review`, plus one adopter's independent
run, produced six defects in the skill and its script. Two are already carried by
open pull requests; four are not started. The work has outgrown a single task and is
being delivered outside the stages.

`docs/dev/README.md` names the countable trigger:

> The countable trigger is a **second pull request for the same piece of work**: one
> PR may be a small task, a second says it is not — stop there and take the work
> through the stages.

Two PRs are open on this piece of work. The trigger fired and was walked past; this
entity is the correction.

## Evidence

The dogfood run measured 501 sessions and 1224 human turns over 2026-08-11 →
2026-08-25 against `~/.claude/CLAUDE.md`. Its own coverage line is the headline:
**4 of 29 rule units carry an observable marker**, so the audit is structurally blind
to the other 25 and says so.

Two of its findings were reached only after re-reading friction categories with the
agent turn that preceded them. Measured head to head, same model and brief, differing
only in what was dispatched to the Step 4 reviewer:

| Dispatched | Verdict on the necessity-test cluster |
|---|---|
| bare human turns | "the job is done and disbelieved" — remedy: make the claim carry its evidence |
| + the paired turns | "0 of 17, vacant at that trigger" — remedy: move the trigger |

Opposite diagnosis, opposite remedy.

The adopter's run supplies the defect neither dogfood pass could reach: `<teammate-message>`
relays from parallel sessions entered the human population and inflated every friction
row by roughly 38% (553 of 1449 turns). This machine's corpus carries that tag once, in
a conversation about the defect, so no window size would have surfaced it here.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "kc-team-ops ships publicly from this marketplace and at least one adopter already runs kc-rules-review against their own corpus, so the audit's output is real use with persistent value. The run keeps no service state and makes no external mutation, but the six items have already grown a follow-on each, so iteration is expected rather than disposable."
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - "Keep the human-population filter a single allowlist in the script, not a second shape-matching rule per relay tag."
      - "Keep a defect-reporting slot an output contract of the existing Completion gate, adding no second tracker or transport."
    implementation:
      - "Anchor every relay filter at turn start so a turn that merely mentions the tag stays in the population."
      - "Make the reporting body carry the operator's skill version and any local patch, because an adopter's uncommitted fix is the drift this item exists to catch."
      - "Leave prose items that change the same paragraph unstacked; local base policy is trunk-only."
    testing:
      - "Prove each filter change RED before GREEN, with one assertion for the dropped case and one for the kept case."
      - "Prefer a measurement the next audit run can reproduce from artifacts that already exist over a marker the skill prints about itself."
  scope_boundary: "Excludes the operator's own rule files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`), any change to the kc-rules-review scoring model, and any new standing CI lane or lint. The seniority question is an experiment that may correctly produce no diff."
  promote_when:
    - "A reporting slot starts accepting submissions from outside this machine, or gains any automatic transport to an issue tracker."
    - "The script begins reading a corpus it does not own, or writes anywhere outside its run directory."
  decision:
    authority: person:captain
    at: "2026-08-25T07:02:03Z"
```

## Scope

Six items, in delivery order.

1. **`<teammate-message>` filter** — script + test. **PR open.** RED confirmed before the
   fix; suite 20/20 after.
2. **Five prose fixes from the dogfood run** — paired-context fallback, Step 4 dispatch,
   remedy falsifiability, Step 6 contradiction check, counting unit. **PR open.**
3. **Skill-defect reporting** — a required Completion-gate slot plus an issue-ready body
   the operator files. The adopter's bug lived only in a pasted report, and their local
   patch is drifting from canonical.
4. **Step 4 `unknown` is not a terminal value** — legal only when it names the blocker and
   offers the dispatch as a decision. Also resolve which wins when a session forbids
   spawning agents and the skill mandates a fresh-context reviewer. Touches the same
   paragraph as item 2, and local policy is trunk-only, so this waits for item 2 to merge
   rather than stacking.
5. **Seniority vs function in the role step** — junior / senior / chief engineer share one
   set of duties. The skill's sixteen-run evidence varied *function*, not seniority, so the
   question is untested. Experiment, not a diff; may correctly change nothing.

## Out of scope

The rule-file changes the audit produced are already applied to `~/.claude/CLAUDE.md` and
`~/.codex/AGENTS.md`; they are the operator's own rules, not this repository's.

## What would falsify this

Item 3 is the load-bearing claim: that a reporting channel would have carried the
adopter's defect here. If the next adopter-found defect still arrives as a pasted
report after item 3 lands, the slot is ceremony and should be removed.

## Shape — accepted outcome

Two people end up doing something different, and neither change is a marker the
skill prints about itself.

**The adopter** stops pasting a prose bug report into a chat and patching their own
copy of the script. When a run exposes a defect in the skill or the script, the
Completion gate's report now has a slot that cannot be left out, and when that slot
is non-`none` the session hands the operator an issue-ready body carrying the
installed skill version and whether the install has local edits. The adopter files
it with `gh issue create`. The drift this exists to catch is the adopter's
uncommitted fix, so the version and patch fields are the payload, not decoration.

**The operator** stops reading `unknown` as an answer. Today Step 4 tells the
reviewer to say `unknown` when a question maps to an unmeasurable rule, and the
Completion gate accepts `unknown` in the Role slot as a filled slot — so the step
terminates there and nobody is asked anything. After this, `unknown` is legal only
when it names the blocker and puts the dispatch to the operator as a Step 5
decision. The operator answers a named question instead of reading a terminal value.

That same rule settles the conflict the entity records as unresolved: a session
that forbids spawning subagents against a skill that mandates a fresh-context
reviewer. Neither wins silently. The session does not skip Step 4; it reports
`unknown`, names the prohibition as the blocker, and offers the dispatch as the
decision. Declining is a recorded answer and the run completes.

### The six, and what this shape leaves out

The Scope list above numbers five entries but the count is six: entry 4 carries two
defects — `unknown` is not a terminal value, and the spawn-forbidden versus
mandated-reviewer conflict. That is the only reading where six = two already in PRs
plus four unstarted.

| # | Defect | State |
|---|---|---|
| 1 | `<teammate-message>` filter | PR #286 open |
| 2 | Five prose fixes from the dogfood run | PR #285 open |
| 3 | Skill-defect reporting slot | unstarted — **in this shape** |
| 4a | `unknown` is not a terminal value | unstarted — **in this shape** |
| 4b | Spawn-forbidden vs mandated fresh-context reviewer | unstarted — **in this shape**, resolved as one rule with 4a |
| 5 | Seniority vs function in the role step | unstarted — **left out** |

Item 5 is left out. It is an experiment that may correctly produce no diff, the work
profile's `scope_boundary` already names it as such, and it changes no observable
behaviour, so it cannot be one of at most two slices that must each change what
someone sees. It stays a separate backlog entity.

## Shape — accepted journey

Every step is marked OBSERVED (someone watched it run) or DESIGNED (written, not yet
exercised), and names the acting program rather than a role.

One journey — a defect a run exposes reaches resolution inside the stages — with two
legs, one per slice.

### Journey A — a skill defect reaches this repository

1. **OBSERVED** — the adopter's session runs `rule-firing-report.sh`, which writes
   `run.json`, `human-turns.tsv`, `incidents.txt` and `firing-hits.txt` into the run
   directory.
2. **OBSERVED** — the adopter reads the counts, finds `<teammate-message>` relays
   inflating the human population, edits their own copy of `rule-firing-report.sh`,
   and pastes a prose report into a chat. Nothing in this repository records either
   the defect or the edit.
3. **OBSERVED** — the fix reaches canonical only because a human carried it. The
   adopter's copy stays ahead of canonical with no record of the delta.
4. **DESIGNED** — the session executing `SKILL.md`'s Completion gate fills a
   required defect slot: `none`, or one entry per defect naming what it does, what
   it should do, and the run directory that shows it.
5. **DESIGNED** — when the slot is non-`none`, the same session emits an issue-ready
   body carrying the installed skill version read from the plugin's `plugin.json`
   and the local-patch state read from `git status` of the install directory. The
   operator runs `gh issue create`. The skill never files anything itself.
6. **DESIGNED, unhappy** — the operator declines to file. The slot still carries the
   defect in the report kept with the run artifacts, so the next run shows it
   unfiled rather than losing it.
7. **DESIGNED, unhappy** — the install directory is an rsync copy, not a git
   checkout. The patch field records `not a checkout` rather than being omitted; a
   silently missing field is exactly the drift this item exists to catch.

### Journey B — `unknown` stops being an answer

1. **OBSERVED** — `SKILL.md` line 265 tells the reviewer that a question mapping to
   an unmeasurable rule is `unknown`; line 408's Role slot accepts `unknown` as
   filled. On the dogfood run the step terminated there.
2. **OBSERVED** — a session that forbids spawning subagents cannot dispatch the
   fresh-context reviewer Step 4 mandates. The text resolves neither which authority
   wins nor what the run should report.
3. **DESIGNED** — `unknown` is legal only when it names the blocker — which rule is
   unmeasurable, or that dispatch was unavailable — and puts the dispatch to the
   operator as a Step 5 decision.
4. **DESIGNED** — the spawn conflict resolves inside that same rule: the session
   reports `unknown`, names the prohibition as the blocker, offers the dispatch, and
   the operator answers.
5. **DESIGNED, unhappy** — the operator declines the dispatch. `unknown` stands with
   the declined decision recorded, and the run completes.

### Observable semantics this work may change

The Completion gate's required report grows one required slot, and Step 4's
`unknown` gains a legality condition. No command grammar changes, no script changes,
and no file in the run directory changes shape — `run.json` in particular is
untouched, which is why the version and patch facts are read from the install rather
than emitted by the script.

### Non-goals

Lifted from the work profile's `promote_when`, so building any of these is a scope
violation, not a stretch goal:

- no automatic transport from the slot to any issue tracker — the operator files;
- no submissions from outside this machine;
- no change to the kc-rules-review scoring model;
- no new standing CI lane or lint;
- no edits to `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`.

## Shape — acceptance checks

Each check reads an artifact that already exists — a filed GitHub issue, the session
corpus the audit itself reads, the run directory — never a marker the skill prints
about itself. The completion report's own text is excluded on purpose: it is the
thing being changed, so it cannot also be the evidence.

**AC1 — the slot carries a defect out of a session (slice 1).** The next skill or
script defect found by a kc-rules-review run appears as a GitHub issue on this
repository whose body carries the skill version and the local-patch state. Checked
with `gh issue list --search kc-rules-review` and reading the body. Falsified if the
next adopter-found defect still arrives as a pasted report — then the slot is
ceremony and is removed, which is this entity's own stated falsifier.

**AC2 — the version and patch fields are derivable with no script work (slice 1).**
Reading `version` from the installed plugin's `plugin.json` and running `git status`
against the install directory reproduces, by hand, the two fields the filed issue
carries. Falsified if either field can only be produced by adding an emitter to
`rule-firing-report.sh` — barred by the work profile's testing obligation ("prefer a
measurement the next audit run can reproduce from artifacts that already exist over a
marker the skill prints about itself") and its architecture obligation keeping the
slot an output contract of the existing Completion gate. The `scope_boundary` field
does not reach it.

**AC3 — `unknown` is followed by an answered decision (slice 2).** In the session
corpus the next audit run already reads, a turn where the session reports `unknown`
is followed by an operator turn answering the offered dispatch. This is checkable
with the skill's own `incident` mechanism, which pairs a human turn with the agent
turn before it — the same paired-context device PR #285 installs. Falsified if an
`unknown` appears with no operator answer after it: the rule changed the wording and
not the behaviour.

**AC4 — the spawn-forbidden path reports rather than skips (slice 2).** In a run
where subagent dispatch was unavailable, the run directory holds no reviewer result
and the corpus holds a turn naming the prohibition as the blocker plus the offered
decision. Falsified if the run directory holds no reviewer result and the corpus
holds no such turn — that is the silent skip this rule exists to stop.

## Shape — where it touches

| Path | Lines now | Lines after | Basis |
|---|---|---|---|
| `kc-team-ops/skills/kc-rules-review/SKILL.md` — slice 1, base `main` | 476 | ~505 | verified against the current tree |
| `kc-team-ops/skills/kc-rules-review/SKILL.md` — slice 2, base `main` after #285 and slice 1 | ~551 | ~566 | **unverified** — inherited from #285's `+53/-7` and slice 1's own estimate; recount at slice 2's branch point |
| `kc-team-ops/scripts/rule-firing-report.sh` | 430 | 430 | unchanged — read by the journey, not written |
| `kc-team-ops/scripts/rule-firing-report.test.sh` | 241 | 241 | unchanged |

Reconciled both ways. The journey names two things the table omits — the installed
plugin's `plugin.json` and the install directory's git state. Both are read, neither
is written, and that is the design decision the omission is meant to raise: the
version and patch facts come from the install so the script keeps no self-report.

## Shape — stop numbers

Measured as the diff against the delivery base, which for both slices is `main` at
the slice's branch point (local base policy is trunk-only; neither slice stacks).

- **changed files: 2.** Each slice plans one file. A second file means the report
  template grew a companion document, which is the runaway below.
- **changed lines: 60 added.** Slice 1 estimates ~29, slice 2 ~15; 60 leaves room
  for a rewrite at the same length without stopping on noise.
- **runaway area: the Completion-gate report template.** The failure to stop on is
  the slot growing into a separate defect-report template file with its own format
  rules. If that starts, halt and report rather than continuing.

## Shape — delivery order

Trunk-only base policy, so nothing stacks; each item branches from `main` and waits
for whatever it would otherwise conflict with.

1. **Item 3, the reporting slot — starts now, parallel to both open PRs.** PR #285's
   last `SKILL.md` hunk covers old lines 377-388 and the Completion gate begins at
   390, so there is no overlap, textual or semantic. PR #286 touches only the two
   script files.
2. **Item 4a + 4b, `unknown` is not terminal — one PR, after #285 merges.** The
   dependency is semantic, not mechanical, and the diff says which. PR #285's Step 4
   hunk covers old lines 253-259; the `unknown` instruction item 4 rewrites is at
   line 265, six lines below it and outside git's three-line context, so a textual
   conflict is unlikely. What couples them is that both rewrite the "Dispatch it, do
   not answer it yourself" section, and item 4's rule — `unknown` must name the
   blocker and offer the dispatch — has to be written against #285's new statement of
   what gets dispatched, not against the text it replaces. Item 4 also edits the Role
   slot at lines 408 and 414, so it waits for item 3 as well. Both halves ship
   together because 4b is the condition that makes 4a's rule complete, not a
   separate change.
3. **Item 5, seniority versus function — last, and outside this shape.** An
   experiment with no planned diff; it stays a backlog entity and does not gate
   anything above.

Items 1 and 2 are out of the shape by fact rather than by choice — they are already
in flight as PRs #286 and #285, and this shape is the correction that keeps the
remainder inside the stages.

## Shape — conditional reference receipts

```yaml
reverse_recovery:
  trigger: "Item 3 claims kc-team-ops has no path by which a kc-rules-review defect reaches this repository, and proposes adding one."
  boundary: "Journey A, bounded to kc-team-ops/ plus the sibling plugins' completion-gate text; excludes the operator's own rule files and any external tracker."
  layers:
    - surface: "Completion gate required report"
      location: "kc-team-ops/skills/kc-rules-review/SKILL.md:390-419"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "Every slot is about the audit's findings; none is about the audit tool. The adopter's defect had nowhere to go."
      disproof_hook: "grep -n 'defect' kc-team-ops/skills/kc-rules-review/SKILL.md"
    - surface: "Any defect-reporting capability elsewhere in kc-team-ops"
      location: MISSING
      need: REQUIRED
      completeness: MISSING
      evidence: "Two searches: (1) grep -rn -i 'gh issue create|file an issue|report a defect|skill defect' kc-team-ops/ returned nothing; (2) grep -rln 'Completion gate' across kc-team-ops, e2e-pipeline and kc-dev-flow returned only this SKILL.md. Boundary: the three plugin trees; external and dynamic consumers not searched because the capability would have to be textual."
      disproof_hook: "Re-run both greps; a hit disproves MISSING."
    - surface: "Skill version and local-patch state"
      location: "<install>/.claude-plugin/plugin.json and git status of the install directory"
      completeness: WORKING
      need: REQUIRED
      evidence: "Both facts are already obtainable from the install; run.json emits neither and is not being changed."
      disproof_hook: "jq -r .version on the installed plugin.json; git -C <install> status --porcelain"
    - surface: "run.json as a carrier for version or patch state"
      location: "kc-team-ops/scripts/rule-firing-report.sh:381-390"
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: "run.json carries ran_at, since, patterns, sessions, human_turns and counts. Nothing reads a version from it."
      disproof_hook: "grep -n 'version' kc-team-ops/scripts/rule-firing-report.sh"
  decision: build

journey_slices:
  demo: "A real kc-rules-review run that finds a skill defect produces a filed GitHub issue on this repository carrying the skill version and the install's patch state."
  slices:
    - "Slice 1 — item 3, the Completion-gate defect slot and its issue-ready body. Stops at the stop numbers above, or when the slot needs a companion template file."
    - "Slice 2 — items 4a and 4b, unknown made non-terminal in Step 4 and in the Role slot. Starts only after PR #285 and slice 1 are on main; stops on the same numbers."
  shortcut_inventory: []

project_context:
  classification: no_context_change
  reason: "kc-team-ops carries no CLAUDE.md, and the repository-level CLAUDE.md describes release and gate policy, which this work does not touch. No described product behaviour, architecture boundary, public contract, scope decision, or durable constraint changes."
```

`retained_document_change` also fires: `SKILL.md` is a retained contract document.
It takes no receipt. Both slices comply by rule 2 — the new clauses carry the
incident that bought them (the pasted adopter report; the dogfood run that
terminated on `unknown`) and no in-flight status, so neither sentence goes stale on
its own.

## Stage Report: ideation

- DONE: One accepted outcome recorded in the work item: the shape of the reporting slot and the unknown-terminal rule, stated as what an adopter and an operator each end up doing differently.
  `## Shape — accepted outcome` — adopter files an issue carrying skill version and install patch state instead of pasting a report; operator answers a named dispatch decision instead of reading `unknown` as terminal.
- DONE: Task-specific acceptance criteria that a later run can check from artifacts the work already produces, not from a marker the skill prints about itself.
  `## Shape — acceptance checks` AC1-AC4, reading a filed GitHub issue, the installed `plugin.json` plus `git status`, and the session corpus the audit already parses; the completion report's own text is excluded as evidence because it is what changes.
- DONE: A delivery order for the four unstarted items that respects trunk-only base policy, and names which of the six the shape leaves out.
  `## Shape — delivery order` — item 3 from `main` now, items 4a+4b as one PR after #285 and item 3 merge, item 5 last and outside the shape; the six are enumerated in the table under `### The six, and what this shape leaves out`.
- DONE: Pilot shape contract required output — journey, boundaries, `where it touches`, stop numbers, conditional receipts.
  `## Shape — accepted journey` (steps marked OBSERVED/DESIGNED with unhappy paths), `## Shape — where it touches`, `## Shape — stop numbers`, `## Shape — conditional reference receipts` carrying `reverse_recovery`, `journey_slices` and `project_context`.

### Summary

Resolved the entity's own arithmetic first: the Scope list numbers five entries but
the count is six, because entry 4 carries two defects — `unknown` is not terminal,
and the spawn-forbidden versus mandated-reviewer conflict. Both halves ship as one
rule, since 4b is the condition that makes 4a complete. Item 5, the seniority
experiment, is the one the shape leaves out; it changes no observable behaviour and
so cannot be a slice.

Two claims in the entity were checked against the diffs rather than inherited. PR
#285 does not touch the Completion gate — its last `SKILL.md` hunk covers old lines
377-388 and the gate starts at 390 — so item 3 branches from `main` immediately
instead of queueing. And item 4's dependency on #285 is semantic, not textual: #285's
Step 4 hunk covers 253-259 while the `unknown` instruction sits at 265, outside git's
context window, so the reason to wait is that item 4's rule must be written against
#285's new statement of what gets dispatched.

The acceptance checks deliberately avoid the completion report as evidence, since the
report is the artifact being changed. AC3 leans on the audit's own paired-turn
mechanism — the same device #285 installs — so the next run can falsify the
unknown-terminal rule from the corpus it already reads.
