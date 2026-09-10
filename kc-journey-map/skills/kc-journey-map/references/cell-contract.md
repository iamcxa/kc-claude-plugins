# Cell contract

What each lane may assert, and what it may not. A board that breaks these reads as
"this works today" when it does not — the failure this skill exists to prevent.

## The three surfaces have three evidence standards

They ask different questions, so they are held to different bars. Applying the release
contract's bar to the story map is the mistake that stops a map being drawn at all: during a
requirements conversation there is no code to cite, and a rule demanding citations blocks
the very stage it was never written for.

| Surface | Asserts | Bar |
|---|---|---|
| **Story map** (canvas) | what we want a person to be able to do, and which of those stories exist today | Backbone and story wording: **no citation** — this is intent. Every story's `status`, though, is checked: `exists` requires `evidence`, and a lint re-greps the repository for it every run. |
| **Release contract** (generated document) | what the system actually does today, per release | **Generated only, never authored.** Carries each story's status, evidence symbol and applicable rule ids — this is where "a citation, or it does not count" lives now. |
| **Function map** (canvas) | what each step decides, and what becomes true | A command, its events including the refusals, the state, the read model. Name what is not modelled. |

A story map drawn from a conversation is not unfinished work — it is the finished output of
its own stage. Its stories get a `status` and, where they exist, an `evidence` symbol only
once somebody goes and reads the code — see "Stories" below.

The journey board — a per-release canvas page citing each step's system flow and
constraints — is opt-in, drawn only on request. It carries the same facts as the release
contract, held to the same bar; the release contract is the generated form a lint can check,
which a grid never could.

## Columns

One column per journey step. A step carries `system:` (free-text citations of the code
that runs) and `rules:` (which constraints apply) for a person reading the file — but the
checkable claim now lives one level down, on the step's stories. See "Stories" below.

## Lane 1 — User Journey

**Asserts:** what a person does, in that person's language.

- ≤ 12 words. A sticky note, not a sentence from a spec.
- Name the actor when a step changes hands (owner → reviewer → owner).
- No API names, no key paths, no HTTP verbs. Those belong in the stories beneath it.

**Check-mode badges** (rendered in the mismatch table, not on the story map):

| Badge | Meaning |
|---|---|
| `NEW` | the step was missing from the journey being checked |
| `CHANGED` | the step exists but works differently than the checked journey says |

`NOT BUILT` and `NOT RULED` used to be step badges too. They moved to story grain —
`status: gap` and `question:` — because a step is too coarse a unit to say is or is not
built; see "Stories".

## Stories

**Asserts:** whether a specific, nameable piece of the step is proven to exist.

- `status: gap | unverified | exists` is required on every story. `gap` means known
  missing implementation; `unverified` means the required behavior has not yet been
  verified; `exists` means implementation evidence supports its relevant execution
  boundary. Missing evidence alone does not prove absence.
- Story cards use green / red / violet borders for `exists` / `gap` / `unverified`,
  with one shared legend per page. See `canvas.md` for editing and export behavior.
- Only `exists` counts toward the implemented-story total in `buildStoryMap` and
  `buildJourneyBoard`. It does not mean delivery acceptance or release completion.
  A symbol lookup checks citation consistency, not the complete execution boundary.
- `evidence:` is a bare symbol — a function, const, or command name that greps in this
  repository — required whenever `status: exists`. Not a `file:line`: a line number goes
  stale silently and the lint would have nothing stable to search for.
- `question:` is optional and orthogonal to status: an unresolved decision, on a story
  in any of the three states. Story-map question boxes are violet; release-board
  evidence/question boxes are neutral, so their frame is not a second status signal.
- A bare string story (`- "some idea"`) cannot carry any of the three fields — it fires
  the `no-status` lint. Give it an id and object form as soon as it needs one.

The lints diagnose missing/unsupported status and missing/stale evidence — see `lib/lint.mjs` and the per-release
contract generated from them (`lib/release-contract.mjs`).

## Interpret task-derived colors

With the optional progress skill, green means all explicitly required development
tasks are done; red means required development work remains; violet means mapping
or observation is unverified. Unknown stories stay in the release denominator.
An empty scope cannot complete; all required stories done means **pending delivery
acceptance**. Task state and source symbols do not prove target-user usability.
Authored evidence stays separate. `lib/progress.test.mjs` exercises these meanings;
`../../kc-journey-progress/SKILL.md` owns the task mapping contract.

## Lane 2 — System Flow (per step, narrative)

**Asserts:** the call, route, or write the step performs, in prose for a reader of the
file. Not machine-checked — the checked claim is the story's `evidence`, not this text.

- Cite what you name here — a citation you cannot back is a line written from memory;
  delete it and go read the code.
- Name the durable effect, not just the request: what is written, under which key, with
  which write mode (`onlyIfNew`, CAS, verbatim).

## Lane 3 — Constraints

**Asserts:** what must stay true at this step — invariants, rulings, deliberate costs.
Written as `rules:` on the step (ids into the file's `rules:` list) and carried onto every
story in that step's release contract row.

- A constraint is something a future change could *violate*. If it cannot be violated, it
  is a description, not a constraint.
- Accepted costs count and should be named as accepted ("drafts are lost on reload;
  accepted for the Pilot").
- **Open defects are not constraints.** A bug is a thing to fix, not a rule to keep. Bugs
  belong on the status card or in the tracker.
- **Unruled options are not constraints.** If nobody has decided, say so with a story
  `question:` rather than drawing the preferred answer as though it were settled.

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
