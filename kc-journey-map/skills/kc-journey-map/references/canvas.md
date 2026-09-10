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

## Three projections, drawn by request

A render draws whichever projections were asked for — never more. Ask (`AskUserQuestion`,
multi-select) before rendering: `story-map` (user journey, preselected), `journey-board`,
`function-map`. No answer, or the tool unavailable, means the default: `story-map` alone.

```bash
node lib/journey-render.mjs docs/journey/<slug>.yaml [roomId] [--pages story-map,journey-board,function-map]
```

| Surface | Kind | Answers |
|---|---|---|
| **Story map** (`story-map`, default) | canvas, one page | what should we build, what is the smallest useful slice, and which of those stories exist today |
| **Journey board** (`journey-board`, opt-in) | canvas, one page per release (or one whole-journey page with none) | given we want *this* release, what does the system do today and what is missing |
| **Release contract**, one per release | generated document, not canvas | the same question as the journey board, as a document a lint can check instead of a picture a person has to notice is wrong — `lib/journey-contract.mjs` |
| **Function map** (`function-map`, opt-in) | canvas, one page | what does each step decide, and what becomes true when it does |

**Journey boards use stories as the review unit.** Each release page shows its selected
stories as yellow cards under green activity headings (`activity`, falling back to
`card`). A separate box below each story shows its status, evidence symbol and open
question. `EXISTS` describes recorded implementation evidence, not delivery acceptance.
With no releases, the whole-journey board also shows unassigned stories and marks
activities that have no stories yet.

System flow and constraints span each activity group once. The file currently stores
`system`, `cites`, `rules` and `note` on the activity, so the board labels them as shared
context with no recorded mapping to individual stories. It does not copy those claims
into each story's evidence. This is a **release story detail board**, not a sequence
diagram: left-to-right story order alone does not establish calls or causality.

**The release contract is generated, never authored.** It reads the stories in a release
and prints their status, evidence symbol, and shared activity rule ids in a document.
See `lib/release-contract.mjs`.

**Lints run against the file itself**, not the board:

| Lint | Fires on |
|---|---|
| `no-status` | a story with no `status` field at all — including a bare-string story, which cannot carry one |
| `invalid-status` | a status outside `gap`, `unverified`, `exists` |
| `exists-without-evidence` | a story marked `exists` with no `evidence` symbol |
| `evidence-not-found` | an `evidence` symbol that no longer greps anywhere in the repository outside the journey file itself |

```bash
node lib/journey-lint.mjs docs/journey/<slug>.yaml [repoRoot]
node lib/journey-contract.mjs docs/journey/<slug>.yaml <releaseId> [--out <path>]
```

`evidence-not-found` is the one a grid could never do: a table does not notice that the
symbol it cites was renamed out from under it. Because the grep is `git grep`, it only sees
tracked content — a symbol added in the same uncommitted change as the story that cites it
needs `git add` before the lint sees it too.

The function map is **Event Modeling** (Adam Dymitruk's swimlane form) over the journey's own
columns: Command,
Event, State, Read model. The vocabulary is fmodel's tactical grammar borrowed as nouns —
a decider takes a command and the current state and emits events; a view folds events into
something readable — not the library, and nothing here event-sources anything.

Events earn the lane: they carry causal order, and story order does not, so a build order
derived from this page is derived from something real. Each event is its own sticky because
an event is the unit a ticket and an acceptance criterion get written against.

The page draws whenever `function-map` is selected, whether or not anything is modelled: a
step nobody has modelled shows `— not modelled —` rather than an empty column, so the gaps
are the point:

```yaml
steps:
  - id: …
    command: "ApplyDiff(journeyFile, roomId, outPath?)"
    events: ["CardReworded", "ReorderRefused"]   # name the refusals, not only the successes
    state: "the journey file"
    readmodel: "the diff report"
```

The function map is not read back yet — edits to it have to be made in the file.

The story map follows Jeff Patton's shape and the workshop convention it borrows: blue
for the persona, the release boundaries and the one-sentence banner above the backbone,
green for the backbone, yellow for the stories beneath it, small labels for ownership,
story status and open questions. Model fields it reads, all optional except a story's
`status`:

```yaml
persona: …
one_journey: …            # one sentence: what is true when the whole loop works. Drawn above the backbone.
now:                       # the status quo — how the job gets done without this product
  - {id: …, card: …, pain: …, workaround: …}
steps:
  - id: …
    card: …                # the journey card; `activity:` overrides it on both canvas projections
    stories:                # ordered top to bottom by priority, variants below the main path
      - id: …
        card: …
        release: …
        status: exists      # gap | unverified | exists — required; labeled per story
        evidence: …          # a bare symbol that greps in the repo; required when status is exists
        question: …          # optional — an unresolved decision, drawn violet
later: [ … ]               # activities below the release boundary
ownership:
  - {id: …, owner: …, from: <stepId>, to: <stepId>, note: …}
slices:
  - {id: …, outcome: …}    # the outcome is the label at the line's left edge
```

Both projections label story states; an unsupported or missing value shows UNASSESSED
and fails lint. See `cell-contract.md` for the status meanings and evidence boundary.
A release's label carries how many of its stories have `status: exists` — computed from `status` on every
render, never typed by hand.

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

**Wording round-trips across projections.** `lib/read.mjs` reads activity headings and
story cards on the story map and release boards, plus legacy `step-card` records.
One changed projection is enough; an untouched copy does not veto the edit. Matching
edits apply once. Different edits of the same field produce a conflict and that field
is not applied. A copied node within one page is ambiguous and is excluded from wording
readback across projections; the same story rendered on different pages is expected.

**Position has a projection-specific meaning.** Activity column order is read from the
story map or a whole-journey board. A release board is a subset, so moving its groups
cannot reorder the whole journey. Release membership and story priority are read from
the story map; dragging cards on a release detail board does not change either.

**`--write` applies a subset.** It applies wording, supported column order, story-map
release membership and story priority. Status, evidence, questions, system flow and
constraints are display-only here; edit those in the journey file. Constraint text
cannot be mapped back to rule ids without guessing.

| Report | Meaning |
|---|---|
| `reordered` | supported activity columns have a different left-to-right order |
| `reorderConflict` | the story map and whole-journey board disagree on order |
| `reworded` | a card, activity or story was edited; carries its page and field |
| `rewordConflict` | distinct edits target the same field across projections |
| `releaseMoved` | a story crossed a release boundary on the story map |
| `storiesReordered` | stories changed priority within a story-map activity and release |
| `duplicated` | a node id occurs more than once within a page's activity or story cards |
| `unclaimed` | an untagged note or geo, with its page and activity column when unambiguous; straddling cards carry `candidates`. Arrows and bare text shapes are not read |
| `missing` | the file has an activity with no activity shape among the selected pages |

`applyDiff` skips activity/card/story wording if the file no longer matches the
value read for that edit; read the canvas again before applying a fresh diff.

`--write` refuses activity reordering when any node is duplicated. tldraw copies
`meta` verbatim, so the original and copy cannot be distinguished by `nodeId`.

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
