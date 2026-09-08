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
npm run canvas
```

- Board: `http://localhost:3737/?room=<slug>`
- Doc API: `http://127.0.0.1:5858` (loopback only)

## The two directions

```bash
node lib/journey-render.mjs docs/journey/<slug>.yaml [roomId]   # file  -> canvas
node lib/journey-read.mjs   docs/journey/<slug>.yaml <roomId>   # canvas -> report
node lib/journey-read.mjs   docs/journey/<slug>.yaml <roomId> --write
```

**Render is a reconcile.** Shapes the renderer owns that the model no longer produces
are removed; shapes a person drew by hand carry no `meta.journey` and are never touched.
A sticky someone added during a workshop survives every re-render.

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
