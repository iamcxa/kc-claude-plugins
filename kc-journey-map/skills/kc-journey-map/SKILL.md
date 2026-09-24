---
name: kc-journey-map
description: Draw or check a user journey, prepare a selected release for development, add one deferred story to an existing journey, add an editable Mermaid sequence companion, or answer architecture questions on a human-drawn journey canvas. Triggers on "journey map", "user journey", "畫 user journey", "journey vs reality", "fill the journey board", "plan this release", "準備這個 release 開發", "add a story to the journey", "not in this release", "記一個延後的功能", "sequence companion", or human-led architecture review. Generated maps use repository YAML; human-led review preserves the drawing and connects one question at a time to technical documentation and separate implementation evidence.
---

# Journey Map

**Route human-led review first.** When the human owns the drawing and asks architecture
questions on it, use [human-led architecture review](references/human-led-review.md).
Claude and Codex share that reference. In that mode it replaces the generated-map
cell, process, rendering, source-placement and verification defaults below: preserve
the native drawing, answer one selected question, and separate the technical contract
from implementation evidence. Do not infer check mode merely because a board exists.
The remaining defaults apply to the existing generated-map modes.

Map intent, draw or check a journey against code, or prepare an existing release for
development. Draw/check establish evidence and render the requested projections.
Journey-board pages include system flow, constraints and a status card.

The board's value is not the picture. It is that each column forces three answers next to
each other — what a person does, what the system does, what must stay true — so a step
that nobody can actually perform cannot hide behind a nicely drawn arrow.

Read `references/cell-contract.md` before filling any cell. It is the rule set the output
is judged against.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| **human-led architecture review** | human-drawn actions and questions; the human directs the review | one short bound answer, its owning technical chapter, then separate evidence; stories stay in the journey YAML and reach it only by authorized promotion — `references/human-led-review.md` |
| **map** | nothing is built yet, or the question is what to build | a story map with releases, drawn from a conversation — `references/map-from-conversation.md` |
| **plan-release** | planning/resuming an existing board or preparing a selected release for development | reviewed Development Brief, or draft with the missing decision — `references/map-from-conversation.md` |
| **draw** | no journey exists yet | the board, derived from code |
| **check** | a journey exists — board, screenshot, or a list of cards | the mismatch table **first**, then the corrected board |
| **sequence companion** | a sequence is requested, or handoffs/branches need explanation alongside a journey | an optional native editable page from repository `.mmd` — `references/sequence.md` |
| **interrogate** | a release is cut and about to go to development, or built stories need their gaps found | every question on the release's stories answered, deferred, or linked to a decision record — `references/interrogation.md` |
| **add-story** | a capability was named and deferred in conversation ("not in this release") and a journey for it already exists | one appended `gap` story under its step, no evidence, no `release` — see "Adding one deferred story" below |

Claude and Codex use this same entrypoint and sequence reference. Offer a sequence
companion when actors, handoffs, or branches would clarify a journey; do not make it
a required projection or change a settled story-map-only choice. Default new sequence
sources to `autonumber`, while respecting an explicit numbering preference.

Map mode comes before draw/check and is held to a different bar: it asserts intent, so
it cites nothing and badges nothing. See `references/cell-contract.md`.

On an explicit planning/resume request, inspect the relevant existing journey source
and selected release before asking questions. Follow the conversation reference for
map and plan-release; read `references/release-slicing.md` when proposing release
boundaries or preparing a handoff. Show the whole map before the prose reduction
proposal, use Ask UI for unresolved human choices, and change boundaries after
acceptance. `lib/journey-handoff.mjs` refuses a development handoff that fails the
recorded slice checks; drawing a broad map remains allowed. The evidence process
below is for draw/check. Preparing an existing-map brief does not require re-rendering
or start development. Claude and Codex share these planning and handoff instructions.

In check mode the mismatches are the deliverable. Do not quietly redraw someone's board
into the "right" answer: quote their card, state the code fact, name the verdict.

## Adding one deferred story

A capability named and set aside mid-conversation — "the shop should be able to create
a booking itself, but not this release" — is not nothing. It belongs in the journey the
moment it is said, not only when someone next runs draw or check.

```bash
node lib/journey-add-story.mjs docs/journey/<slug>.yaml <stepId> <storyId> "<card>"
```

- `<card>` is the words the person used for the capability, quoted — not a rewrite. Same
  rule as check mode's "do not silently rewrite someone's card text."
- The story is always written `status: gap`, no `evidence` — nothing has been read to
  support it yet — and no `release`: a deferred capability is scheduled by a separate
  decision, not invented here.
- Name the step it belongs to from what was said. If that is unclear, ask; do not guess
  and place it wherever the diff looks smallest (`references/canvas.md`'s `unclaimed`
  handling is the same instinct — an ambiguous placement is a question, not a default).
- This appends one story to one step and nothing else: it does not re-derive other
  stories' evidence, resolve open questions, or touch a human-drawn canvas
  (`lib/add-story.test.mjs` asserts that only the new story's lines change, even in a file whose wrapping and indentation this plugin would not have written).
- On a map-mode-only journey (no story carries `status` yet — `references/map-from-conversation.md`),
  the added story still gets `gap` as this operation requires; the pre-existing
  `no-status` lint findings on every other story are not this operation's to fix.
- Then run `node lib/journey-lint.mjs <journey.yaml> <repoRoot>` — omitting `<repoRoot>`
  checks evidence against the plugin directory, not your repository, and fails
  confusingly (see "Verify before presenting" below).
- Re-render only if a canvas room for this journey is already open: query
  `http://127.0.0.1:${JOURNEY_API_PORT:-5858}/health` and check whether the room id —
  the file's `journey:` field, unless the last render passed a different `roomId` —
  appears in its `rooms` list (`GET /doc` would silently create the room, which
  proves nothing — `/health` only reports rooms that already exist on disk). If the API
  is unreachable or the room is not listed, no board is open; a file edit alone does not
  need a canvas started for it.

## Process

**1. Establish the spine.**
Check mode: take the steps as given, in the user's own words. Draw mode: derive them from
entry points — routes, CLI subcommands, published clients — not from documentation.
Documentation describes intent; the spine must describe reachability.

**2. Find the evidence, one column at a time.**
For each step, locate the handler, the route registration, and the durable write. Record
`file:line` as you go. Three questions decide the column:

- Can a person reach this step today? Split it into stories where the answer differs story
  by story, and give each the `status` the answer implies — `gap`, `unverified` or `exists`.
- What does the system durably do here — which key, which write mode?
- What would break if a future change ignored this step's rule?

A story whose handler exists but has no route is `status: gap`, not `exists`. Code that only
tests can call is not a journey story.

**3. Check the trunk, not just the branch.**
State plainly which ref was measured. Work living only in open PRs, worktrees, or a stack
is not the current system, and the status card must say so.

**4. Write the journey file.** `references/cell-contract.md` rules what each evidence lane may assert; `references/canvas.md` lists the story-map fields (persona, one_journey, now, stories, ownership, slices). In draw/check mode, give every story a `status` (`gap`, `unverified` or `exists`) and, when it exists, an `evidence` symbol — the meanings are defined in `references/cell-contract.md`; these are what the lints in `lib/lint.mjs` check. The board is not the
artifact — the file is. It lives in the consuming repository (see [Source placement](#source-placement))
and holds the steps, the stories with their status and evidence, the system
lines with their citations, the rules, the slices and the status card. `references/journey.example.yaml` is a worked one. Story map and release-board story cards use yellow fill and green/red/violet status borders, with one shared legend per page; `references/canvas.md` describes native editing and export behavior.

Positions are never written to the file. Every layout number is computed from the model's
order, so a reordered board is a one-line diff instead of a rewritten file.

**5. Render** (see below), then **visually check the live canvas**. On the first map,
inspect the requested views; on updates, inspect the changed views and confirm the
expected content and shapes are visible. A note with `fontSizeAdjustment: 0` can be blank,
a geo box can overflow, and growing rows can overlap. Check these failures on the
actual canvas.

Promptly return the usable live-board link after that check. Export a PNG only when the
user requests it or the conversation context justifies an image; if exported, open and
inspect it. Do not repeat unrelated outputs before returning an updated live link.

**6. Report.** Draw mode: the board, the release contract per release
(`node lib/journey-contract.mjs`), and `node lib/journey-lint.mjs <file> <repoRoot>` run
against the file — cite what it found, not just that it ran. Without `<repoRoot>` the
evidence check runs against the plugin directory instead of your repository and every
`exists` story fails confusingly. Check mode: the mismatch table first.

For optional local task development progress, use the sibling
`../kc-journey-progress/SKILL.md`. Its derived display leaves authored status and
evidence intact; drawing alone does not require Spacedock.

## Rendering

**Reuse the settled projection choice within the same request.** Ask what to draw when
that choice is missing or changes (`AskUserQuestion`, multi-select): `User journey`
(story map — default, preselected) / `Journey board` (one page per release) / `Function map`
(commands and events). If the tool is unavailable, or nobody answers, render the user
journey alone — that default is load-bearing, not a fallback of convenience.

**The canvas.** Omit `--pages` to draw the default story map. Use
[canvas.md](references/canvas.md) for startup, projection selection, native export,
and safe readback commands. The release contract is generated as a document;
`npm run doctor` diagnoses canvas prerequisites.

**FigJam.** Requires the Figma MCP and a target file. Ask for the file URL; never create a
new file in someone's workspace without being asked to. If the MCP is not connected, say so
in one line and carry on with the canvas.

**When the canvas will not run**, say so in one line and deliver the journey file and the
`.md` — both are readable, both go in git, and the file is the artifact the board renders
from. Do not stall, and do not hand-draw a substitute board that no file backs.

## Source placement

Paths are relative to the consuming repository root:

| Repository scope | Journey source |
| --- | --- |
| Single repository or single-product monorepo | `docs/journey/<journey>.yaml` |
| Multi-product monorepo | `docs/journey/<product>/<journey>.yaml` |

Organize by user journey and product: one source spans frontend, API and shared packages;
do not duplicate it per technical package. Reuse an existing canonical source instead
of creating a competing copy. YAML is the versioned authority; optional `.md` citations
and native editable `.tldr` snapshots sit beside it (see [canvas.md](references/canvas.md)).

The fictional book-pickup teaching fixture is packaged in `references/journey.example.yaml`
and `references/example/`. This plugin's ongoing product plan lives in the consuming
marketplace repository at `docs/journey/kc-journey-map/draw-a-journey.yaml`, with its
evidence README and native snapshot beside it; installed-plugin examples do not depend on it.

## Hard rules

- **No cell from memory.** Every System Flow cell and every story `evidence` symbol cites a
  file, symbol, route, or key read this session. Recalled facts from a previous session are
  a hypothesis; re-read them.
- **Journey-board status cards are mandatory** for draw/check output and name
  unproven, unmerged and undeployed work. For story-map-only output, include these
  evidence limits in the accompanying report; its canvas has no full status card.
- **A gap is drawn on the story, not dropped, and not put on the step.** `status: gap` and an
  unresolved `question:` are outputs at story grain; a step is too coarse a unit to be
  in-or-out. Silence is not an output.
- **`exists` without `evidence` does not pass.** The `exists-without-evidence` lint exists
  because a status typed with no proof behind it is worse than no status at all.
- **Defects are not constraints, and unruled options are not constraints.**
- **Never present local or unit evidence as journey evidence.** If nothing has been deployed
  or exercised end to end, the status card says exactly that.
- **Do not rewrite the user's card text silently.** Show their words and the code fact side
  by side.
- **A card someone added by hand is not noise.** On the canvas it comes back as `unclaimed`.
  Ask where it belongs; never delete it to make a re-render clean.

## Check-mode output

Lead with this table, then the corrected board:

| Card | Verdict | Code fact |
|---|---|---|
| their wording | matches / superseded / missing / not built | the fact, with `file:line` |

`superseded` means a later decision changed it — name that decision. `missing` means the
journey has a step the board never drew. `not built` means the card describes something no
route can reach.

## Verify before presenting

- In draw/check mode, every story carries a `status`; every `exists` story carries `evidence`.
- For evidence checks, `node lib/journey-lint.mjs <file> <repoRoot>` exits 0; run it and
  report its findings. Omitting `<repoRoot>` checks the plugin directory, not your
  repository, and reports evidence missing that is actually there.
- Journey-board status cards, or the story-map-only report, name merge and deployment state.
- The current or changed canvas views passed the visual check in Process step 5.
- Check mode: every mismatch row names a file or route, not an impression.
- Canvas: the file was re-rendered after the last edit, and `journey-read` reports nothing
  unclaimed that has not been dispositioned.

## Where this fails

If the journey crosses repositories — a client in one, a server in another — cite each side
separately and say which repo was read. A board that mixes two repos' facts without saying
so is the most expensive mistake this skill can make, because every cell still looks right.
