# The canvas

An editable tldraw board an agent can write to, so a journey can be worked on in a
room with other people instead of only read as a PNG.

For human-drawn architecture review, [human-led-review.md](human-led-review.md)
owns meaning, preservation and verification. The YAML authority, regeneration,
projection and readback rules below concern generated maps, not that mode. Reuse
the service lifecycle and native sizing guidance where applicable; do not import a
whole document over an existing human drawing to add one answer.

## The split that makes it worth having

The journey file in the repository is the source of truth. The room is a rendering of
it. Follow [Source placement](../SKILL.md#source-placement) for the canonical path:

- **The file goes in git.** It diffs, it reviews, it survives tldraw.
- **The room preserves native edits.** Read edits back or export a `.tldr` backup
  before deleting `.rooms/`; re-rendering cannot recover unexported manual state.
- **No coordinates in the file.** Position is computed from the model's order. Writing
  `x`/`y` back would make the file a tldraw shadow and destroy the diff.

A `.tldr` snapshot beside the source is an optional, deliberate backup or sharing
artifact, not an export required after every update; YAML remains the authority.
Keep room databases (`.rooms/*.db`) out of git: they are local runtime data.
`server/rooms.ts` uses `JOURNEY_ROOMS_DIR`, or `./.rooms` relative to the service working
directory by default; it does not automatically place rooms in the consuming repository.

## Run it

Before starting, inspect any existing service's source/version provenance and the
capabilities needed for this request. Reuse a suitable running service of the required
version. Do not stop or restart a service you did not start merely to free a port or
clean up. Unknown provenance is not proof of compatibility; report that limit and
resolve setup within the user's authority, without killing the existing service.
Keep services backing a delivered board link running, even if this session started
them. Unless the user asks to stop, cleanup may stop only owned test services that
serve no delivered board link.
These are operator checks, not automatic version detection or lifecycle protection.

Identify an owned service by a process id captured when you started it, and stop that
id. A command-line pattern is not an identifier: several worktrees of this repository
run this same server on one machine, so `pkill -f canvas-server` matches a canvas
someone else is reading. Without a captured id, read every line of `pgrep -fl` for the
pattern and confirm the match set before stopping anything. Give each test service its
own port and its own `JOURNEY_ROOMS_DIR` at startup; that is what makes a narrow match
possible later. Also set `JOURNEY_DOC_REPOS=<owner>/<repo>=<absolute path>` at startup,
from `git -C <the repository being drawn for> remote get-url origin` and that
repository's own absolute path — this is what lets a technical-document chapter link
on the canvas open in place; an adopter configures nothing beyond this. After stopping
anything, health-check the services you did not intend to touch.

From the plugin directory, when installation or startup is needed:

```bash
npm ci
npm run canvas      # runs the preflight first, and refuses to start if it fails
npm run doctor      # the preflight on its own
```

The preflight names the thing to go fix rather than letting the failure surface as a
Node built-in that "does not exist", a bare module-not-found, or a port bind error. It
checks the Node floor (**22.13.0** — rooms are stored in `node:sqlite`, which needed
`--experimental-sqlite` before that), whether the dependencies are installed, and whether
either port is already answering.

**If the canvas will not run**, report the unavailable canvas and provide the
journey YAML with its Markdown explanation. Native PNG export requires the running
canvas and `agent-browser`; it is not a dependency-free fallback.

- Board: `http://<host>:3737/?room=<slug>` — `<host>` is the machine's own hostname, printed at
  startup, and reachable from another machine on the network; a `/connect` proxy in
  `vite.config.mts` forwards the sync socket to the doc API, so no separate port needs opening.
- Doc API: `http://127.0.0.1:5858` (loopback only — reachability comes from the board's proxy, not
  from widening this bind)
- Share board: `npm run share` serves the same rooms on `http://127.0.0.1:3738` for viewers. It
  proxies the board and its images and nothing else; the operator endpoints exist only on the
  board above, so a viewer cannot control the tunnel or write into the repository.

`JOURNEY_API_PORT`, `JOURNEY_CANVAS_PORT` and `JOURNEY_SHARE_PORT` move all three; the preflight,
the export scripts and the proxies read the same variables, so a second canvas does not need any
file edited.

Vite refuses a request whose Host header isn't the machine's own hostname or a name listed in
`JOURNEY_ALLOWED_HOSTS` (comma-separated). Set that env var to admit a cloud or Tailscale DNS name
without editing tracked files.

Browser tabs show `<journey title> | tldraw canvas`. Rendering copies the YAML
`title` into tldraw's native document name; changing that name updates connected
tabs without a reload. An empty name falls back to the room identifier. Room
storage and `.tldr` exports preserve native names, while re-rendering restores the
YAML title (or clears the name when the YAML has no title). Native renames do not
write back to YAML. For isolated local checks, `VITE_JOURNEY_API_URL` can point the
client at a separate `JOURNEY_API_PORT` server.

Open the live canvas for normal review; Process step 5 in `SKILL.md` owns visual
verification and optional PNG output. A native `.tldr` backup preserves unread canvas
edits and is separate from image output. Read back or preserve those edits before
redrawing; the renderer does not apply them to the source automatically.

## Images, sharing and saving

**Images.** Paste or drop one and it is stored as a file under `JOURNEY_ASSETS_DIR`
(`./.assets`), while the record keeps an `asset:<name>` src rather than an absolute origin —
so the same record resolves against whatever host each viewer typed. A `.tldr` export inlines
the bytes as a data URL, which makes the file self-contained and large.

**Sharing.** The board's top-right panel opens a Cloudflare quick tunnel to the share
front-end and shows the URL; stopping it closes the tunnel, and so does stopping the doc API.
The tunnel is refused with 409 when the share front-end is not running, and the panel says so
when a front-end dies under a tunnel that is still open — Cloudflare serves 502 for that, which
looks like a broken link rather than a stopped process.

**Saving.** The same panel writes the board to `JOURNEY_SAVE_DIR` (`./docs/journey`) under a
name you confirm, or downloads a `.tldr` through the browser when the repository is not where
it belongs. Writes are confined to that directory, an empty board is refused, and the
button reads `overwrite` when the target already exists — these files are usually untracked,
so an overwrite has no undo.

**There is no identity check on a shared board.** Anyone holding the link can edit or clear
it. That is the whole access control, which is why the tunnel is meant for one ad-hoc
discussion and not for a standing URL.

## Three projections, drawn by request

Select projections per render call: `story-map` (default), `journey-board`, or
`function-map`. The invocation skill owns the selection conversation. See
[cell-contract.md](cell-contract.md) for each surface's evidence standard.

```bash
node lib/journey-render.mjs docs/journey/<slug>.yaml [roomId] [--pages story-map,journey-board,function-map]
```

| Surface | Kind | Answers |
|---|---|---|
| **Story map** (`story-map`, default) | canvas, one page | what should we build, what is the smallest useful slice, and which of those stories exist today |
| **Journey board** (`journey-board`, opt-in) | canvas, one page per release (or one whole-journey page with none) | given we want *this* release, what does the system do today and what is missing |
| **Release contract**, one per release | generated document, not canvas | authored story status, evidence and shared rule ids for one release — `lib/journey-contract.mjs` |
| **Function map** (`function-map`, opt-in) | canvas, one page | what does each step decide, and what becomes true when it does |

**The release board is a zoom-in of the story map onto one slice, not a parallel
style.** Its activity and story cards are drawn by the exact same builders the story
map uses (`records.mjs:activityCard`, `records.mjs:storyCard`) — same shape type
(`note`), same colour, same size, same status border, same text (`story.card` alone;
evidence and task progress live in the release contract and the story-status meta, not
on the card). What the release board adds sits below: one light-blue flow card per
`system:` line, one orange constraint card per rule id (showing that rule's text) —
still `geo` rectangles spanning the group's full width, unlike the note-sized activity
above them — then the release's story notes, then each story's own questions. A step
with neither `system:` nor `rules:` still gets one placeholder card of each kind, so
the render never reads as having silently dropped a step's flow or constraints. With
no releases, the whole-journey board also shows unassigned stories and marks
activities that have no stories yet.

**Questions and answers are `note` shapes, not `geo` rectangles** — a note has the
native "+" handles on its edges that let a reader add an adjacent card in one click.
Colour means kind, never status: question notes are light-green, answer notes are
light-blue (matching the flow card's colour is intentional — both read as
"informational" — but a different shape and position tell them apart). A small legend
in each release page's top-left names every card colour plus the story-status border
so a reader never has to guess. There is no OPEN label and no dashed/solid outline on
a question any more — **whether a question is answered is shown by whether an answer
note hangs under it, nothing else.** Questions on the release board spread out
horizontally beneath their story rather than stacking in one column, as the Captain
laid them out by hand; the story map keeps its single vertical column, with each
answer note directly under its own question, before the next question. Every question
or answer is bound to what it hangs under by a native tldraw arrow
(`records.mjs:connector` + `connectorBindings`), so the connection survives an editor
drag. Story cards carry a solid 10 px status border (`records.mjs:storyBorder`) with
green/red/violet for `exists`/`gap`/`unverified`; `EXISTS` describes implementation
evidence, not delivery acceptance.

`records.mjs:storyBorder` keeps each story as a native yellow note with a locked,
empty geo child. `App.tsx:syncStoryBorders` updates that child after note creation
and changes, including measured text height and scale, and repairs loaded borders.
Moving the note moves its border without changing the page parent or coordinates
read by `read.mjs`. Plain notes without a story status keep their native behavior.
PNG, SVG and `.tldr` exports include standard shapes; other tldraw hosts retain
the saved border geometry, while subsequent height/scale edits need this canvas
for synchronization. `node --test lib/render.test.mjs` checks generated geometry.

Flow and constraint cards span each activity group once, not once per story. The file
currently stores `system`, `cites`, `rules` and `note` on the activity, so the board
draws them as shared context with no recorded mapping to individual stories. It does
not copy those claims into each story's evidence. This is a **release story detail
board**, not a sequence diagram: left-to-right story order alone does not establish
calls or causality.

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

`evidence-not-found` uses `git grep`, so it only sees
tracked content — a symbol added in the same uncommitted change as the story that cites it
needs `git add` before the lint sees it too.

`[repoRoot]` looks optional but is not, in practice: omit it and the evidence check runs
`git grep` against the plugin directory instead of the repository the journey describes,
so real evidence reports as missing and every `exists` story fails.

The function map is **Event Modeling** (Adam Dymitruk's swimlane form) over the journey's own
columns: Command,
Event, State, Read model. The vocabulary is fmodel's tactical grammar borrowed as nouns —
a decider takes a command and the current state and emits events; a view folds events into
something readable — not the library, and nothing here event-sources anything.

Event order comes from the authored model. The projection does not infer causality
or implementation order; each event has its own sticky for discussion.

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
story status and open questions. Status/evidence fields are required for an evidence
check, not for drawing intent in map mode:

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
        status: exists      # gap | unverified | exists — required for evidence checks
        evidence: …          # a bare symbol that greps in the repo; required when status is exists
        questions:            # optional — unresolved decisions, one card per question
          - {id: …, ask: …, answer: …, doc: …}   # answer: a short paragraph, doc: a link to the chapter that answers it — either or both
        question: …          # sugar for a single-element questions: list
ownership:
  - {id: …, owner: …, from: <stepId>, to: <stepId>, note: …}
slices:
  - {id: …, outcome: …}    # the outcome is the label at the line's left edge
```

An unsupported or missing status fails evidence lint; the journey-board detail
labels it UNASSESSED. The story-map card does not promise that label. See `cell-contract.md` for the status meanings and evidence boundary.
Drawing without task progress, a release's label carries how many of its stories have `status: exists` — computed from `status` on every
render, never typed by hand.

An unfinished implementation of the thing being proposed does not belong in `now:` —
that is the status card's job, not the user's current world.

## Draw a task observation

Use [the progress skill](../../kc-journey-progress/SKILL.md) for explicit local-task
refresh and its mapping contract. Its derived snapshot supplies release counts and
story colors without entering editable wording or authored evidence. All required
stories complete means **pending delivery acceptance**. Native wording, order and
release edits still round-trip; `node --test lib/progress.test.mjs` exercises both
routes from the plugin root.

## Moving a board somewhere else

tldraw's own file format handles transport; the journey file handles meaning. They
compose because `meta.journey` rides inside the records — a board can leave here, be
opened in any tldraw, come back, and still be read against its journey file.

```bash
node lib/journey-tldr.mjs export <roomId> <out.tldr>
node lib/journey-tldr.mjs import <in.tldr> <roomId>
```

Check an imported room with `journey-read` against its source, then edit a card and
read again. The [worked example](example/README.md) provides exact reproduction
commands; record counts depend on the model and selected projections.

**A `.tldr` is not a journey file.** It stores coordinates and colours, not steps,
citations or rules. Import replaces the whole target document. Where a journey file exists it
stays the artifact of record, and a `.tldr` never replaces it. A board with no journey behind
it — an ad-hoc discussion canvas — has nothing else to keep, and the save button exists to
put that snapshot in the repository.

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

**Render is a reconcile, scoped to the pages drawn this call.** Shapes the renderer owns
that the model no longer produces are removed; shapes a person drew by hand carry no
`meta.journey` and are never touched. A sticky someone added during a workshop survives
every re-render. `--pages journey-board` only reconciles journey-board pages — a
story-map page this call did not draw is untouched, even though its shapes also carry
`meta.journey`.

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

## Native sizing boundaries

For the pinned tldraw 5.4.0 runtime:

- **A note's `fontSizeAdjustment` must be 1.** A `0` passes schema validation and then
  renders the label at font-size 0px — a blank sticky, and the server cannot catch it.
  Build every record with `lib/records.mjs`; never hand-write one.
- **A geo box does not grow to fit its label.** Text past the bottom edge is drawn
  outside the box. `fitHeight()` sizes every card from its own content.

## Licence

tldraw is under the [tldraw licence](https://github.com/tldraw/tldraw/blob/main/LICENSE.md),
not an open-source one. It permits use in a Development Environment — internal hosting for
development, testing or staging, not reachable by customers or the public. It forbids
Production use without a commercial licence and forbids interfering with licence-key
enforcement, which is why the board shows a "Get a license for production" watermark.
Do not deploy this board for anyone outside the team. A quick tunnel puts the board on a
public hostname, so the link belongs to the people in that discussion and the tunnel is closed
when it ends.
