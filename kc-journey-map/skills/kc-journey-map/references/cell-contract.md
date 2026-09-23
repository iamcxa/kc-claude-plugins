# Cell contract

This contract governs generated-map modes. For a human-drawn architecture review,
use [human-led-review.md](human-led-review.md) instead: a green Action identifies
its role, and a question is not automatically a story or a status-bearing cell.

What each lane may assert, and what it may not. A board that breaks these reads as
"this works today" when it does not — the failure this skill exists to prevent.

## The three surfaces have three evidence standards

They ask different questions, so they are held to different bars. Applying the release
contract's bar to the story map is the mistake that stops a map being drawn at all: during a
requirements conversation there is no code to cite, and a rule demanding citations blocks
the very stage it was never written for.

| Surface | Asserts | Bar |
|---|---|---|
| **Story map** (canvas) | what we want a person to be able to do, and which of those stories exist today | Backbone and story wording: **no citation** — this is intent. In evidence mode, `status: exists` requires `evidence`; citation lint rechecks the symbol. Map-only intent may omit both. |
| **Release contract** (generated document) | what the system actually does today, per release | **Generated only, never authored.** Carries each story's status, evidence symbol and applicable rule ids — this is where "a citation, or it does not count" lives now. |
| **Function map** (canvas) | what each step decides, and what becomes true | A command, its events including the refusals, the state, the read model. Name what is not modelled. |

A story map drawn from a conversation is not unfinished work — it is the finished output of
its own stage. Its stories get a `status` and, where they exist, an `evidence` symbol only
once somebody goes and reads the code — see "Stories" below.

The journey board — a per-release canvas page citing each step's system flow and
constraints — is opt-in, drawn only on request. It carries the same facts as the release
contract, held to the same bar. Lints check the underlying journey file; the generated
contract and board display its authored claims.

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

- In evidence mode, `status: gap | unverified | exists` is required on every story. `gap` means known
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
- `questions:` is optional and orthogonal to status: unresolved decisions, on a story
  in any status. Each carries `id`, which binds it to its board card, `ask`, which
  fills the contract cell, and optionally `answer:` (a short paragraph) and/or `doc:`
  (a link to the technical document chapter that answers it) — either or both. A
  question is answered when it carries one of these; question answeredness is a
  different axis from story status — whether a decision is settled, not whether code
  exists — so the two vocabularies stay apart. `question:` is sugar for a one-element
  list. The earlier shape — `status: open | answered | deferred`, with a `deferred`
  question owing a `because:` — is still read: a `deferred` question's `because:`
  becomes its answer text when no explicit `answer:` was authored (its reason for
  parking is itself an answer to show); a bare legacy `status: answered` with no
  `answer:`/`doc:` text now reads as **unanswered** — a claim with nothing to show is
  not a shown answer. `lintQuestionStatus` still rejects an unsupported `status:` value
  and a `deferred` question with no `because:`, when a `status:` is present at all.
- Every question is its own `note` — not a `geo` rectangle — on both the story map and
  the journey board, bound to its story by a native arrow: never text folded into the
  story card, which stops being readable once a story asks six, and never a status word
  or a dashed/solid outline on the card itself. **Whether a question is answered is
  shown by whether an answer note hangs under it, nothing else.** An answer is its own
  note directly under its question, bound by a short native arrow: a short paragraph
  in the note's text, a link in the note's own `url` prop, or both. The story map
  stacks a story's questions in one vertical column, each answer directly under its own
  question; the journey board spreads a story's questions out horizontally instead, as
  the Captain laid them out by hand, with each answer still straight below its own
  question.
- A story may not be `exists` while any of its questions has no answer; the
  `exists-with-open-question` lint refuses it. The per-release contract renders only
  unanswered questions, so the column says what is still missing rather than what was
  once asked.
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

Journey-board pages display this card. Draw/check output must include these
limits; story-map-only output carries them in its accompanying report.

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
