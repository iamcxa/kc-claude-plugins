# Cell contract

What each lane may assert, and what it may not. A board that breaks these reads as
"this works today" when it does not — the failure this skill exists to prevent.

## Columns

One column per journey step. Every column carries exactly one cell in each of the three
lanes. A column with an empty System Flow cell is not allowed: either cite the code, or
badge the step `NOT BUILT`.

## Lane 1 — User Journey

**Asserts:** what a person does, in that person's language.

- ≤ 12 words. A sticky note, not a sentence from a spec.
- Name the actor when a step changes hands (owner → reviewer → owner).
- No API names, no key paths, no HTTP verbs. Those belong in lane 2.
- Steps a user cannot perform today still appear here — badged, never omitted.

**Badges** (rendered next to the step number):

| Badge | Meaning |
|---|---|
| `NEW` | the step was missing from the journey being checked |
| `NOT BUILT` | no code implements this step; nobody can perform it today |
| `NOT RULED` | the step depends on a decision nobody has made |
| `CHANGED` | the step exists but works differently than the checked journey says |

## Lane 2 — System Flow

**Asserts:** the call, route, or write that this exact step performs.

- **Every cell carries a citation** — `path/file.ts:120`, a route path, or a storage key
  read this session. A cell with no citation is a cell written from memory; delete it and
  go read the code.
- Name the durable effect, not just the request: what is written, under which key, with
  which write mode (`onlyIfNew`, CAS, verbatim).
- Two to four short lines. If a cell needs a paragraph, the column is really two steps.
- Never describe a route that does not exist. A planned route is `NOT BUILT` in lane 1.

## Lane 3 — Constraints

**Asserts:** what must stay true at this step — invariants, rulings, deliberate costs.

- A constraint is something a future change could *violate*. If it cannot be violated, it
  is a description, not a constraint.
- Accepted costs count and should be named as accepted ("drafts are lost on reload;
  accepted for the Pilot").
- **Open defects are not constraints.** A bug is a thing to fix, not a rule to keep. Bugs
  belong on the status card or in the tracker.
- **Unruled options are not constraints.** If nobody has decided, say so in lane 1 with
  `NOT RULED` rather than drawing the preferred answer as though it were settled.

## The status card

Mandatory. It is the one place the board is allowed to talk about time.

It must answer, in this order, whichever apply:

1. What is unproven — which acceptance criteria have no evidence
2. What is unmerged — open PRs, branches, work that is not on the trunk
3. What is undeployed — and whether anything has ever run in production
4. Which single step is irreversible, if one is

Do not soften it, and do not move it into a lane. A board whose cells are all accurate but
whose status card is missing still reads as a claim that the journey works today.

## Language

Board text follows the repository's language (English by default). Keep the user's own
wording when checking an existing journey — quote their card, then state the code fact.
Never silently rewrite someone's card text; show both and let them choose.
