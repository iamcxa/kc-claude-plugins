# Accept a release by walking it

Read this for `accept-release`. A caller (for example a workflow's first officer) uses this mode
once every story of a release has its development tasks done: `journey-progress.mjs` prints
`acceptance: pending delivery acceptance` for it, and `cell-contract.md` says that label is not
delivery acceptance. Someone has to operate the release as one journey, from the person's first
situation, and see whether each story can be reached and used. This mode gives that walker the
list and takes the result back to the map. It writes no map and no code, and it does not walk.

**Order: walk list -> a walk, done by the caller -> proposals back -> the Captain accepts.**

## 1. Produce the walk list

```bash
node lib/journey-walk.mjs docs/journey/<slug>.yaml <releaseId>
```

It prints one `release-walk/v1` document: the stories with `release: <releaseId>`, in step order and
then story order inside the step, each with its step card and activity, status, evidence symbol, the
step's `system` lines and its rules. `proof_line` is the release `goal`, verbatim, the same text
`journey-contract.mjs` prints; the map has no separate field for it. It refuses a release with no
goal or no stories (exit 1).

The map stores no URL or route, so the list names no entry point. The walker finds the way in from
where the previous story left the person; failing to find one is itself a finding. `source.commit`
is the last commit that touched the journey file, or null while the file has uncommitted edits, so a
walk is pinned to a map revision only when the map is committed.

```json
{
  "schema": "release-walk/v1",
  "journey": "book-pickup",
  "persona": "A reader collecting a reserved book from a neighborhood library.",
  "one_journey": "Reserve a book, learn when it is ready, and collect it at the desk.",
  "release": {
    "id": "r1",
    "name": "RELEASE 1 — Reserve and collect",
    "goal": "A reader can reserve a book, check readiness and collect it."
  },
  "source": {
    "file": "docs/journey/book-pickup.yaml",
    "commit": "0123456789abcdef0123456789abcdef01234567"
  },
  "proof_line": "A reader can reserve a book, check readiness and collect it.",
  "stories": [
    {
      "order": 1,
      "id": "reserve-copy",
      "card": "Reserve a copy for pickup",
      "step": {
        "id": "reserve",
        "card": "Chooses a book to collect",
        "activity": "Reserve a book"
      },
      "status": "unverified",
      "evidence": null,
      "system": [
        "Proposed: record a reservation when a copy can be held."
      ],
      "rules": [
        {
          "id": "one-active-hold",
          "text": "Proposed: a reader may hold one active reservation per book."
        }
      ]
    },
    {
      "order": 2,
      "id": "check-ready",
      "card": "See that the book is ready to collect",
      "step": {
        "id": "ready",
        "card": "Checks whether the book is ready",
        "activity": "Know when to visit"
      },
      "status": "unverified",
      "evidence": null,
      "system": [
        "Proposed: show the pickup location and hold deadline after staff prepare the book."
      ],
      "rules": [
        {
          "id": "hold-deadline",
          "text": "Proposed: show the hold deadline before the reader travels to collect the book."
        }
      ]
    },
    {
      "order": 3,
      "id": "collect-book",
      "card": "Collect the reserved book",
      "step": {
        "id": "collect",
        "card": "Collects the book at the desk",
        "activity": "Take the book home"
      },
      "status": "unverified",
      "evidence": null,
      "system": [
        "Proposed: confirm the reservation before recording collection."
      ],
      "rules": [
        {
          "id": "hold-deadline",
          "text": "Proposed: show the hold deadline before the reader travels to collect the book."
        }
      ]
    }
  ]
}
```

`node lib/schemas.mjs release-walk` prints the field table and version, and exits 1 when the table
changed without a new version. History lives where `journey-map-question`'s does: this plugin's
`CHANGELOG.md`, and the ADR titled "a release is accepted by walking it, and the plugins meet at two
named schemas".

## 2. Take the result back

```bash
node lib/journey-accept.mjs docs/journey/<slug>.yaml <report.json>
```

The report is a `release-acceptance/v1` document, a shape this plugin does not own: its producer is
the caller's side, and this command reads only the fields named here. It refuses (exit 1) a report
whose `schema` is not `release-acceptance/v1`, that walks another journey or a release the map lacks,
that names a story not on the release, or whose story `result` is not one of `works`, `broken`,
`missing-entry-point` or `not-reachable`. Otherwise it prints proposed edits and writes neither file:

| Result on a story | Proposal |
|---|---|
| `works` | nothing: acceptance is not a status, and `exists` needs an evidence symbol |
| `broken`, story `exists` | `unverified` |
| `missing-entry-point`, story `exists` or `unverified` | `gap`: a handler with no route is `gap` (`cell-contract.md`) |
| `not-reachable` | no status change; the story ids and the report's `not_tested` entries are proposed as the text of the status card's `unproven` line, printed beside the current line |

A proposal is not a map edit. Present it as a reviewable change to the journey file in a docs pull
request, as `release-review.md` step 1 does, and the Captain accepts it. A clean walk leaves no mark
on the map: the acceptance lives in the caller's own gate record.

## Which mode when

- `interrogate` (`interrogation.md`, "On stories that already exist") has a stranger read the code for
  gaps between story and build. Nobody operates the product. Use it before a release goes to
  development, or to find gaps in built stories.
- `accept-release` is for a release whose stories are all built: the walk operates it end to end.
- A walk finding that crosses two or more tasks, or names a story with no task, goes to
  `review-release` (`release-review.md`); that mode starts with an interrogation (step 0), which needs `codex`.

## Limits

The list is the map's words, not a script of clicks. `works` is the walker's claim, so this mode
proves nothing the walker did not operate. `journey-accept.mjs` checks the schema string, the journey,
the release, the story ids and the result values; it does not check that every story of the release
was walked or that a finding is right. A report that names fewer stories than the release proposes
fewer edits.
