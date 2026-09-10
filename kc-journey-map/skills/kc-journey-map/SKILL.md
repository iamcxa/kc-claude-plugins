---
name: kc-journey-map
description: Use when drawing a user journey from what a codebase actually does, or checking an existing journey against current reality. Triggers on "journey map", "user journey", "畫 user journey", "產出 journey 圖", "journey vs reality", "現況跟 journey 對不對", "fill the journey board", or a FigJam/screenshot of a journey board handed over to complete. Renders from a journey file kept in the repository onto an editable canvas — the user journey (story map) by default, plus a per-release journey board or a function map of commands and events, each drawn only on request — and generates a per-release contract naming each story's status and evidence, where every claim of `exists` cites a symbol a lint re-checks and a mandatory status card names what is unproven, unmerged, or undeployed.
---

# Journey Map

Draw a journey from the code, or check a journey against the code. Same core either way:
establish the steps, find the evidence for each one, render three lanes plus a status card.

The board's value is not the picture. It is that each column forces three answers next to
each other — what a person does, what the system does, what must stay true — so a step
that nobody can actually perform cannot hide behind a nicely drawn arrow.

Read `references/cell-contract.md` before filling any cell. It is the rule set the output
is judged against.

## Two modes

| Mode | Trigger | Output |
|---|---|---|
| **map** | nothing is built yet, or the question is what to build | a story map with releases, drawn from a conversation — `references/map-from-conversation.md` |
| **draw** | no journey exists yet | the board, derived from code |
| **check** | a journey exists — board, screenshot, or a list of cards | the mismatch table **first**, then the corrected board |

Map mode comes before the other two and is held to a different bar: it asserts intent, so
it cites nothing and badges nothing. See `references/cell-contract.md`.

In check mode the mismatches are the deliverable. Do not quietly redraw someone's board
into the "right" answer: quote their card, state the code fact, name the verdict.

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

**4. Write the journey file.** `references/cell-contract.md` rules what each evidence lane may assert; `references/canvas.md` lists the story-map fields (persona, one_journey, now, stories, ownership, slices). Give every story a `status` (`gap`, `unverified` or `exists`) and, when it exists, an `evidence` symbol — the meanings are defined in `references/cell-contract.md`; these are what the lints in `lib/lint.mjs` check. The board is not the
artifact — the file is. It lives in the consuming repository (`docs/journey/<slug>.yaml`
by convention) and holds the steps, the stories with their status and evidence, the system
lines with their citations, the rules, the slices and the status card. `references/journey.example.yaml` is a worked one. Story map and release-board story cards use yellow fill and green/red/violet status borders, with one shared legend per page; `references/canvas.md` describes native editing and export behavior.

Positions are never written to the file. Every layout number is computed from the model's
order, so a reordered board is a one-line diff instead of a rewritten file.

**5. Render** (see below), then **look at the render**. A rendered board is not a verified
board. A note whose `fontSizeAdjustment` is 0 validates and draws a blank sticky; a geo box
draws its overflow outside itself; a row placed at a fixed offset lands on top of the row
above once its text grows. Every one of those happened here. Export the image and read it.
Ship what you saw, not what you wrote.

**6. Report.** Draw mode: the board, the release contract per release
(`node lib/journey-contract.mjs`), and `node lib/journey-lint.mjs` run against the file — cite
what it found, not just that it ran. Check mode: the mismatch table first.

## Rendering

**Ask what to draw, before rendering.** (`AskUserQuestion`, multi-select): `User journey`
(story map — default, preselected) / `Journey board` (one page per release) / `Function map`
(commands and events). If the tool is unavailable, or nobody answers, render the user
journey alone — that default is load-bearing, not a fallback of convenience.

**The canvas.** The journey file renders onto an editable tldraw board, one page per
projection chosen:

```bash
node lib/journey-render.mjs <journey.yaml> [roomId] --pages story-map,journey-board,function-map
```

Omitting `--pages` renders the default (`story-map` alone). See `references/canvas.md` for
how to run it, what round-trips and what does not. `npm run doctor` says why it will not
start. The release contract — the per-release detail the journey board also draws — is a
generated document, not a board: `node lib/journey-contract.mjs`.

**An image for a report.** Export from the canvas with tldraw's own exporter, which
captures the whole board rather than a viewport:

```bash
node lib/journey-export.mjs <roomId> <out.png> [page]
```

**FigJam.** Requires the Figma MCP and a target file. Ask for the file URL; never create a
new file in someone's workspace without being asked to. If the MCP is not connected, say so
in one line and carry on with the canvas.

**When the canvas will not run**, say so in one line and deliver the journey file and the
`.md` — both are readable, both go in git, and the file is the artifact the board renders
from. Do not stall, and do not hand-draw a substitute board that no file backs.

Artifact path: `docs/journey/<slug>.yaml` in the repository the journey describes, with the
`.md` beside it carrying the citations.

## Hard rules

- **No cell from memory.** Every System Flow cell and every story `evidence` symbol cites a
  file, symbol, route, or key read this session. Recalled facts from a previous session are
  a hypothesis; re-read them.
- **The status card is mandatory** and must name what is unproven, unmerged, or undeployed.
  A board without it reads as a claim that the journey works today.
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

- Every story carries a `status`; every `exists` story carries `evidence`.
- `node lib/journey-lint.mjs <file>` exits 0 — run it, do not eyeball the file for gaps.
- The status card names merge and deployment state.
- The exported image was opened and read, not just written.
- Check mode: every mismatch row names a file or route, not an impression.
- Canvas: the file was re-rendered after the last edit, and `journey-read` reports nothing
  unclaimed that has not been dispositioned.

## Where this fails

If the journey crosses repositories — a client in one, a server in another — cite each side
separately and say which repo was read. A board that mixes two repos' facts without saying
so is the most expensive mistake this skill can make, because every cell still looks right.
