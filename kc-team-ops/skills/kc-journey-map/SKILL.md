---
name: kc-journey-map
description: Use when drawing a user journey from what a codebase actually does, or checking an existing journey against current reality. Triggers on "journey map", "user journey", "畫 user journey", "產出 journey 圖", "journey vs reality", "現況跟 journey 對不對", "fill the journey board", or a FigJam/screenshot of a journey board handed over to complete. Produces a three-lane board — FigJam when a file is available, self-contained HTML + PNG otherwise — where every system claim cites the code it was read from and a mandatory status card names what is unproven, unmerged, or undeployed.
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
| **draw** | no journey exists yet | the board, derived from code |
| **check** | a journey exists — board, screenshot, or a list of cards | the mismatch table **first**, then the corrected board |

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

- Can a person reach this step today? If not, the column is badged `NOT BUILT`.
- What does the system durably do here — which key, which write mode?
- What would break if a future change ignored this step's rule?

A step whose handler exists but has no route is `NOT BUILT`. Code that only tests can call
is not a journey step.

**3. Check the trunk, not just the branch.**
State plainly which ref was measured. Work living only in open PRs, worktrees, or a stack
is not the current system, and the status card must say so.

**4. Build the grid**, per `references/cell-contract.md`.

**5. Render** (see below), then **look at the render**. A generated diagram is not a
verified diagram: Mermaid silently eats text after `#`, prints literal `\n` in some node
types and not others, and passes `parse()` while displaying the wrong label. Screenshot the
HTML and read the image; open the FigJam and read it back. Ship what you saw, not what you
wrote.

**6. Report.** Draw mode: the board, plus the steps that came back `NOT BUILT` or
`NOT RULED`. Check mode: the mismatch table first.

## Rendering

**FigJam (preferred).** Requires the Figma MCP and a target file. Ask for the file URL;
never create a new file in someone's workspace without being asked to. Use the Figma
plugin's FigJam skill for placement. If the MCP is not connected, say so in one line and
fall back — do not stall the deliverable on it.

**HTML + PNG (always available, and always produced).**

1. Copy `references/board-template.html` to the artifact path.
2. Replace only the JSON block in `<script type="application/json" id="data">`. The
   template renders itself from that object — do not hand-write table markup.
3. Screenshot it and read the PNG:

```bash
agent-browser open "file://$PWD/<path>.html" --viewport 1760x1040
agent-browser screenshot "$PWD/<path>.png" --full
```

The output path is positional. `--path` is not a flag this CLI has, and passing one writes
a file literally named `--path` in the working directory.

Artifact path: `.context/journey-<slug>.{html,png,md}` when `.context/` exists (Conductor
workspaces), otherwise a path the user names. Write the `.md` too — it carries the
paste-ready sticky text plus the citations, which the PNG cannot hold.

## Hard rules

- **No cell from memory.** Every System Flow cell cites a file, line, route, or key read
  this session. Recalled facts from a previous session are a hypothesis; re-read them.
- **The status card is mandatory** and must name what is unproven, unmerged, or undeployed.
  A board without it reads as a claim that the journey works today.
- **A missing step is drawn, not dropped.** `NOT BUILT` and `NOT RULED` are outputs; silence
  is not.
- **Defects are not constraints, and unruled options are not constraints.**
- **Never present local or unit evidence as journey evidence.** If nothing has been deployed
  or exercised end to end, the status card says exactly that.
- **Do not rewrite the user's card text silently.** Show their words and the code fact side
  by side.

## Check-mode output

Lead with this table, then the corrected board:

| Card | Verdict | Code fact |
|---|---|---|
| their wording | matches / superseded / missing / not built | the fact, with `file:line` |

`superseded` means a later decision changed it — name that decision. `missing` means the
journey has a step the board never drew. `not built` means the card describes something no
route can reach.

## Verify before presenting

- Every column has all three cells; every System Flow cell has a citation.
- Column count in lane 2 and lane 3 equals column count in lane 1.
- The status card names merge and deployment state.
- The PNG was opened and read, not just written.
- Check mode: every mismatch row names a file or route, not an impression.

## Where this fails

If the journey crosses repositories — a client in one, a server in another — cite each side
separately and say which repo was read. A board that mixes two repos' facts without saying
so is the most expensive mistake this skill can make, because every cell still looks right.
