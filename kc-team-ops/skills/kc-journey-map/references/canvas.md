# The canvas

An editable tldraw board an agent can write to, so a journey can be worked on in a
room with other people instead of only read as a PNG.

## The split that makes it worth having

The journey file in the repository is the source of truth. The room is a rendering of
it. That is the whole design:

- **The file goes in git.** It diffs, it reviews, it survives tldraw.
- **The room is a cache.** Delete `.rooms/` and nothing is lost — re-render.
- **No coordinates in the file.** Position is computed from the model's order. Writing
  `x`/`y` back would make the file a tldraw shadow and destroy the diff.

## Run it

From the plugin directory, once per machine:

```bash
npm install
npm run canvas      # runs the preflight first, and refuses to start if it fails
npm run doctor      # the preflight on its own
```

The preflight names the thing to go fix rather than letting the failure surface as a
Node built-in that "does not exist", a bare module-not-found, or a port bind error. It
checks the Node floor (**22.13.0** — rooms are stored in `node:sqlite`, which needed
`--experimental-sqlite` before that), whether the dependencies are installed, and whether
either port is already answering.

**If the canvas will not run, the skill still works.** The HTML + PNG path has no
dependencies, no server and no ports. Say in one line that the canvas was unavailable
and produce the HTML board — never stall the deliverable on it.

- Board: `http://localhost:3737/?room=<slug>`
- Doc API: `http://127.0.0.1:5858` (loopback only)

## Two pages, one file

A journey renders into one room with two pages, because the two boards ask different
questions and disagree about what the vertical axis means:

| Page | Vertical axis | Answers |
|---|---|---|
| **Story map** | priority under an activity | what should we build, and what is the smallest useful slice |
| **Journey board** | lane | does what we claim exist actually exist, and what does the code say |

The story map follows Jeff Patton's shape and the workshop convention it borrows: blue
for the persona and for release boundaries, green for the backbone, yellow for the
stories beneath it, small labels for ownership and evidence status. Model fields it
reads, all optional:

```yaml
persona: …
now:                       # the status quo — how the job gets done without this product
  - {id: …, card: …, pain: …, workaround: …}
steps:
  - id: …
    card: …                # the journey card; `activity:` overrides it on the story map
    stories: [ … ]         # ordered top to bottom by priority, variants below the main path
    badge: NOT_BUILT       # drawn as a small label, never inside the sticky
later: [ … ]               # activities below the release boundary
ownership:
  - {id: …, owner: …, from: <stepId>, to: <stepId>, note: …}
slices:
  - {id: …, outcome: …}    # the outcome is the label at the line's left edge
```

An unfinished implementation of the thing being proposed does not belong in `now:` —
that is the status card's job, not the user's current world.

## Moving a board somewhere else

tldraw's own file format handles transport; the journey file handles meaning. They
compose because `meta.journey` rides inside the records — a board can leave here, be
opened in any tldraw, come back, and still be read against its journey file.

```bash
node lib/journey-tldr.mjs export <roomId> <out.tldr>
node lib/journey-tldr.mjs import <in.tldr> <roomId>
```

Verified end to end: exported 82 records with 71 carrying journey meta, imported into a
fresh room, and `journey-read` reported no drift against the file — then caught an edit
made inside the imported board, so the read was reading and not finding nothing.

**A `.tldr` is not a journey file.** It stores coordinates and colours, not steps,
citations or rules. Import replaces the whole target document. Use it to carry a board
between tools, never as the artifact that goes in git.

## The two directions

```bash
node lib/journey-render.mjs docs/journey/<slug>.yaml [roomId]   # file  -> canvas
node lib/journey-read.mjs   docs/journey/<slug>.yaml <roomId>   # canvas -> report
node lib/journey-read.mjs   docs/journey/<slug>.yaml <roomId> --write
node lib/journey-read.mjs   docs/journey/<slug>.yaml <roomId> --out <other.yaml>
```

`--write` overwrites the file it read. `--out` saves the result elsewhere and leaves the
original alone; it writes the target even when nothing applied, because a caller who asked
for a save-as should end up with that file.

**Render is a reconcile.** Shapes the renderer owns that the model no longer produces
are removed; shapes a person drew by hand carry no `meta.journey` and are never touched.
A sticky someone added during a workshop survives every re-render.

**Read covers the Journey board page only.** It matches shapes whose kind is `step-card`.
On the story map the same step is an `activity` and its stories are `story` shapes, so
dragging a story up — a priority change, and the most common gesture there is — is not
seen, and neither is rewording an activity. Story-map edits have to be made in the file
until that lands.

**Read reports; `--write` applies a subset.** Two things round-trip: a card's wording and
the order of the columns. A badge is drawn but never read back. Lane 2 and lane 3 have a lossy inverse —
a constraint is stored as a rule id and drawn as that rule's text, so canvas text cannot
be mapped back to an id without guessing. Everything else is reported for a human to act on:

| Report | Meaning |
|---|---|
| `reordered` | columns are in a different left-to-right order than the file |
| `reworded` | a card's text was edited on the canvas |
| `duplicated` | a node id appears on more than one shape |
| `unclaimed` | a note or geo with no `meta.journey` — someone added a card by hand. An arrow or a bare text shape is not seen |
| `missing` | the file has a step with no shape on the canvas |

`--write` **refuses the reorder entirely** when anything is duplicated. tldraw copies
`meta` verbatim on duplicate, so a copy carries its original's `nodeId` and there is no
honest way to tell which is which.

## Two traps, both verified in a browser

- **A note's `fontSizeAdjustment` must be 1.** A `0` passes schema validation and then
  renders the label at font-size 0px — a blank sticky, and the server cannot catch it.
  Build every record with `lib/records.mjs`; never hand-write one.
- **A geo box does not grow to fit its label.** Text past the bottom edge is drawn
  outside the box. `fitHeight()` sizes lane 2 and lane 3 from their content.

## Licence

tldraw is under the [tldraw licence](https://github.com/tldraw/tldraw/blob/main/LICENSE.md),
not an open-source one. It permits use in a Development Environment — internal hosting for
development, testing or staging, not reachable by customers or the public. It forbids
Production use without a commercial licence and forbids interfering with licence-key
enforcement, which is why the board shows a "Get a license for production" watermark.
Do not deploy this board for anyone outside the team.
