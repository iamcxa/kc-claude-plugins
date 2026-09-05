---
name: kc-plan-flow-dialectic
---

# plan-flow dialectic

Five stations turn one raw requirement into a Development Brief. Each station names the borrowed skill it
prefers when installed, the Brief field it fills, and a fallback of at most three questions — in this plugin's
own wording, not copied from the borrowed skill's text — that a First Officer asks when that skill is absent.
pm-skills (`problem-statement`, `epic-hypothesis`, `user-story-splitting`) is CC BY-NC-SA 4.0: call it when
installed, never vendor its text into this repository. gstack `office-hours` is MIT.

This dialectic is produced from this repository's own planning needs and checked against the pm-skills
licence boundary to prevent unintended derivative work. See `scripts/plan-flow/dialectic-derivation-check.sh`.

## Station 0 — re-verify the observation

Every candidate a plan cuts an Issue from rests on an observation recorded earlier. An observation
decays: the code it describes keeps moving while the record does not. This station refuses a
candidate whose observation no longer reproduces.

- **Borrowed skill (when installed):** none. This station reads this repository's own records.
- **Brief field filled:** `Re-verified:` — one command, its output, and the date, per admitted candidate.
- **Scope:** only candidates this plan intends to cut Issues from. Candidates left in the backlog are
  not re-verified here; an unchecked backlog entry carries no claim that its observation still holds.
- **The check:** for each candidate, run one command today that reproduces the recorded pain, and
  record the command with its output. A candidate whose command shows the pain is gone is dropped
  from the plan with a one-line disposition, not silently re-scoped into something else. A candidate
  whose observation cannot be reduced to a command is admitted only with the Captain's explicit
  ruling on that gap, recorded.
- **Refusal:** no `Re-verified:` line, no Issue cut from that candidate.

**Why this station exists.** On 2026-09-04 a plan round selected "tests run nowhere in CI" from four
recorded observations dated 2026-07-26 to 2026-08-20. Checked against the tree that day, two of the
four had already been fixed by intervening PRs (#173 and #181 wired the e2e-pipeline suite; the
hardcoded corpus path became a skip with an environment override), one was a measurement error in
the plan round itself, and the largest remaining block belonged to a plugin the Captain had ruled
out of investment. The backlog held 69 entries whose observations spanned six weeks, during which
200 PRs merged. Without this station the plan would have dispatched workers to repair work that was
already done, and the resulting failure would have been recorded against those workers.

## Refusal seam

Before station 1 produces a human-shaped narrative, apply this posture (regardless of which skills are
installed): demand behaviour, a current workaround with a cost, one named human, one observation. Missing
any of the four is a refusal, not a persona pick — no problem statement, no user value, no Project, no Issues, no receipt.

When this seam refuses, the discovery assignment it hands back must name the observation it will produce or
the payment it will ask for, never another interview. An assignment that says only "go interview someone" without
a declared result is a refusal: it does not commit to the observation or cost required to discharge it.

## Station 1 — the problem

- **Borrowed skill (when installed):** `problem-statement@pm-skills`.
- **Brief field filled:** `## The problem`.
- **Fallback questions (no more than 3):**
  1. Who specifically hits this, and what were they doing the last time it happened?
  2. What do they do today instead, and what does that cost them?
  3. What in the raw requirement is a fact you can point to, versus something you're assuming?

## Station 2 — user value and scope wedge

- **Borrowed skill (when installed):** gstack `office-hours` Q1–Q4, asked to the Captain in chat by the First
  Officer. This station is always the FO's, never the worker's, regardless of which stations 1/3/4 skills are
  installed.
- **Brief field filled:** the one-line `User value:` (Q1–Q3 evidence) and the scope wedge (Q4) — profile
  selection itself is deferred to `choose-work-profile`, not decided here.
- **Fallback questions (no more than 3):**
  1. What have you actually watched someone do that shows this hurts, and what do they do about it today?
  2. If you had to ship something a real person could use this week, what's the smallest version, and who is
     that person?
  3. What would you keep doing if you did nothing at all, and what already-existing tool comes closest?

## Station 3 — goal and falsifier

- **Borrowed skill (when installed):** `epic-hypothesis@pm-skills` is available for optional review after the fallback.
- **Brief field filled:** `## Accepted outcome` plus a `Falsifier:` line and a chosen approach.
- **Fallback questions (no more than 3):**
  1. What single observable result would show this succeeded, and what must stay true about it to count?
  2. What approach are you betting on to reach that outcome, and what would break your confidence in that approach?
  3. If you removed that approach from the Brief, could the accepted outcome still happen?

**Borrowed skill as optional checklist:** If `epic-hypothesis@pm-skills` is installed, after answering these
questions, apply it to audit whether the outcomes and approach cover the space of user personas, measurement
points, and risk scenarios the skill surfaces. Use its findings to sharpen the outcome or add falsifiers; it
does not replace these fallback questions or produce a second goal statement.

## Station 4 — issue cut

- **Borrowed skill (when installed):** `user-story-splitting@pm-skills` is available for optional review after the fallback.
- **Brief field filled:** the Issue cut (titles, count, `blockedBy` order, Milestone, by-product checklist).
- **Fallback questions (no more than 3):**
  1. Does this only make sense as one shippable piece, or can you point to a boundary — a code path, a
     permission gate, a data entity — where a smaller piece is still useful on its own?
  2. Which piece has to exist before another piece can be tested?
  3. If you could only ship one of these pieces this week, which one, and does it alone deliver something the
     target user notices?

**By-product constraint:** For each Issue after the first in dispatch order, name one surface (a path, a rule,
a data shape, a permission, a query) that this Issue changes, and that no earlier Issue's dispatch changes.
An Issue that cannot name a by-product surface is not cut; it is absorbed into the Issue that created that
surface, or dropped.

**Milestone as recordable journey:** The Milestone chosen for this plan is one recordable journey that a user
could observe from start to finish. Its name is the observable start-to-end outcome. Each cut Issue's
dispatch advances that same journey; Issues that do not advance the named journey are not cut for this plan.

**Borrowed skill as optional checklist:** If `user-story-splitting@pm-skills` is installed, after answering these
questions and cutting Issues, apply it to audit whether the Issue boundaries align with its surface-split patterns
(workflow steps, rule variations, data shape changes). Use its findings to reconsider boundaries; it does not
replace these fallback questions, the by-product constraint, or the Issue cut.
