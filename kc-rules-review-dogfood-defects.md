---
title: Six defects from one dogfood run and one adopter run, delivered outside the stages
status: backlog
source: kc-rules-review dogfood run 2026-08-25 (501 sessions, 1224 human turns) plus an adopter's independent run; filed after the workflow's second-PR trigger fired and was walked past
product: kc-team-ops
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: kmg9zdxg2h2n2k0c7j86peq0
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
