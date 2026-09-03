---
name: kc-plan-flow-dialectic
---

# plan-flow dialectic (draft)

Four stations turn one raw requirement into a Development Brief. Each station names the borrowed skill it
prefers when installed, the Brief field it fills, and a fallback of at most three questions — in this plugin's
own wording, not copied from the borrowed skill's text — that a First Officer asks when that skill is absent.
pm-skills (`problem-statement`, `epic-hypothesis`, `user-story-splitting`) is CC BY-NC-SA 4.0: call it when
installed, never vendor its text into this repository. gstack `office-hours` is MIT.

This is a draft produced by a DEV-89 POC run comparing the borrowed-skill path against the fallback path on one
real requirement; see that work item's evidence for the comparison.

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

- **Borrowed skill (when installed):** `epic-hypothesis@pm-skills`.
- **Brief field filled:** `## Accepted outcome` plus a `Falsifier:` line.
- **Fallback questions (no more than 3):**
  1. If this ships, what's the one thing you expect to become true that isn't true now, and how would you check
     it?
  2. What's the cheapest way to find out you're wrong before you build the whole thing?
  3. What number or observation, and by when, tells you this worked?

## Station 4 — issue cut

- **Borrowed skill (when installed):** `user-story-splitting@pm-skills`.
- **Brief field filled:** the Issue cut (titles, count, `blockedBy` order).
- **Fallback questions (no more than 3):**
  1. Does this only make sense as one shippable piece, or can you point to a natural seam — a step, a rule, a
     data type — where a smaller piece is still useful on its own?
  2. Which piece has to exist before another piece can be tested?
  3. If you could only ship one of these pieces this week, which one, and does it alone deliver something the
     target user notices?

## Refusal seam

Before station 2 commits to a persona, apply the office-hours posture (regardless of which skills are
installed): demand behaviour, a current workaround with a cost, one named human, one observation. Missing any of
the four is a refusal, not a persona pick — no profile, no Project, no Issues, no receipt.
