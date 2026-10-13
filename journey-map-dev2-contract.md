---
title: kc-journey-map and kc-dev-flow-2 connect through versioned input/output contracts, each schema owned by its producer, with ADR rulings shown on the map by reference
status: ideation
variant: kc-dev-flow-2
merge: pr
profile: pilot
gates:
    version: 1
    records:
        - id: gate:journey-map-dev2-contract:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:journey-map-dev2-contract-backlog-1
              briefing:
                id: briefing:journey-map-dev2-contract:backlog:attempt-1:revision-1
                digest: sha256:fbb11af93e5d54ff9e1c3680e8c8dc60ac32270a3bce98c5da1286de395a998c
                room-ref: ./journey-map-dev2-contract/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-map-dev2-contract:backlog:1
                briefing: briefing:journey-map-dev2-contract:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T03:04:41.63751Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「可以進入設計」, after the FO presented the loop, timing, no-miss checks and self-repair placement in chat; then 「可以」 to the FO question "journey-map-dev2-contract 要選 Pilot 嗎？選定後，我記下等級和這次的關卡，然後派人做設計。"'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:journey-map-dev2-contract:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:journey-map-dev2-contract-ideation-1
              briefing:
                id: briefing:journey-map-dev2-contract:ideation:attempt-1:revision-1
                digest: sha256:40305c31874741abedc51c9da45a798b424b010f3bc5e38275beb82d6de12c09
                room-ref: ./journey-map-dev2-contract/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-map-dev2-contract:ideation:1
                briefing: briefing:journey-map-dev2-contract:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T03:56:22.19363Z"
                decision: revise
                reason: 'Captain 2026-10-13: 「看看是否拆成兩個範圍？讓 pilot profile 更有設計餘裕？」, then 「可以」 to the FO split. Accepts direction; redo ideation narrowed to scope one only: a ruling reaches the map (gate footprint -> archive fold -> map PR writing answer, status and source -> reconcile counts), two schemas (footprint, map question fields), no renderer change; ACs drawn from AC-4, AC-5, AC-6 and the parts of AC-1/AC-2 those need; D1 and D2 re-asked within that scope. Scope two (evidence ladder, ADR by reference and Map: line, fold-pending marks, drawn-commit provenance, tuple list form and story-id identity, service seam) moves to a new backlog task, designed after scope one is accepted.'
            - id: gate-attempt:journey-map-dev2-contract-ideation-2
              briefing:
                id: briefing:journey-map-dev2-contract:ideation:attempt-2:revision-1
                digest: sha256:f8875bc580c6901d38783d1bf03bf66ba06c1c415f6ac4bcab8fbbcf82f1978a
                room-ref: ./journey-map-dev2-contract/review/ideation/briefing-2
              withdrawal:
                by: agent:first-officer
                at: "2026-10-13T04:15:24.70313Z"
                reason: Briefing 2 was prepared while design_surfaces.py check failed (Visible change was not 'none' with Surfaces none); FO line corrected
started: 2026-10-13T03:05:11Z
---

kc-journey-map (the release slice map) and kc-dev-flow-2 meet today through prose split between workflow.md's Release review section and kc-journey-progress's SKILL.md. Nothing tests that prose, and six defects found in an adopter on 2026-10-13 come from that missing interface.

## Captain's words

- 2026-10-13, answering "Should a dev2 design task in kc-claude-plugins handle the journey-map ↔ dev2 interface?": 「可以」.
- 2026-10-13, same turn: 「切片地圖似乎也很適合放 ADR 重點…怎樣同步比較省時省力？」.
- 2026-09-06, the standing ruling on flows: plan, dev and ship are independent plugins joined only by versioned input/output contracts, and each schema lives with its producer.
- 2026-10-13, on keeping the map service deployable later: 「能否在做 dev2 + 地圖整合之餘，在最小程度調整設計讓它變成未來可以部署到特定環境，變成地圖投影服務是可以寄存在外部的？…怎樣才剛好兼顧但不過度設計？」; then 「照你建議」 to the FO's split: this task takes the seam (the CLI can send a token to the map service; the repo-writing `/save` and `/repo-doc` leave the service and stay local; room storage is already set by `JOURNEY_ROOMS_DIR`), and hosting itself stays with task `journey-canvas-hosted-poc`.
- 2026-10-13, on versioning: 「該怎樣維護版本與更新紀錄？我想後者應該是 ADR？」.
- Relayed by an adopter First Officer session, not heard directly: each plugin should be usable alone, with the integration a written two-sided contract, as Spacedock and Spacedock Review are.

## Inputs: defects reported by an adopter FO, 2026-10-13 (kc-journey-map 1.5.1, kc-dev-flow-2 0.20.0)

1. A slug-id workflow could not be read. Fixed in kc-journey-map 1.5.2 (#623); listed here only as the conformance case to keep.
2. An archived task becomes a permanent orphan. A story moved to another release after its task was archived stays listed under `orphans`, and `spacedock status --set` refuses an archived entity, so nothing can clear it.
3. One task can serve only one story, because `journey-story` is a scalar; a task that carries three stories by a Captain ruling shows progress for one.
4. Three meanings of "done" never meet: the map's `status` (an evidence symbol greps), the progress reader's task `done`, and the adopter's deploy record (for example a `staging-verified` commit status).
5. Answers do not flow back to the map. Captain rulings, ADRs, POC findings and validation findings land in task files and ADRs; the map's story `questions` are written by hand.
6. The canvas has no provenance: a drawing records no journey-file commit, so a map ahead of `main` looks current.
7. Release review signal 2 is honour-system: workflow.md says "no script checks that line".

## Input: ADR rulings on the map

A real adopter map (a booking product, release 8) already cites ADRs by hand in story answers and in flow and constraint text: 61 mentions in one journey file, read with `git show origin/next:docs/journey/<file>.yaml | grep -ci adr` on 2026-10-13. Two hand copies already disagree with their sources: one answer says an ADR question is "still open, to fill in", and the same file cites ADRs by two numbering schemes (a separate file `0034`, and a section `26` inside ADR 0001).

## Input: qnow map refresh, reported by qnow's FO session, 2026-10-13

Relayed by that session, not heard directly: the Captain's aim is 「切片地圖會隨著 ADR 以及對話討論內容，逐步自動寫入最新的現況」.

qnow's FO dispatched an ad-hoc dev2 ideation task (`journey-edits-after-merge`, qnow state branch `spacedock-state/dev2`) to refresh its map; neither plugin has a step that reconciles map questions against rulings. Four sub-agents read only the map's notes, dev2 task files, ADRs and `git grep` at a pinned ref; about 45 of about 58 open map questions were answerable, about 13 stay open (counts as reported, not re-read here). Gaps it reports:

1. Captain rulings live in chat, task files and ADRs; the map moves only when someone opens a map-edit task, so it lags every ruling.
2. Some rulings survive only as the map's own paraphrase (a 2026-09-29 batch has no verbatim source in any task file).
3. Map questions carry answer text without `status: answered`, so release boards show them as open.
4. A release-level task (one that covered all five stories of a release) shows as an orphan, because `journey-story` is one story (same as defect 3 above).

Its proposed shape, a suggestion not a ruling: every Captain ruling FO records also emits one map-change record keyed to a story or question id, with verbatim words and date; a reader periodically folds those records and new ADRs into a draft map, rendered to a separate preview room, read back with `journey-read`, and proposed to the Captain as a docs-only PR.

## Direction the Captain accepted, 2026-10-13

The FO proposed this direction in chat across four turns. The Captain answered 「可以」 to the loop, asked about timing and about missed steps, and then said 「可以進入設計」 to the whole of it, including the self-repair placement. Ideation designs against it; it is not yet a design.

1. **Loop:** the map stores only durable facts and reads progress live from dev2; dev2 writes only a minimal footprint, and only at moments where it already stops.
   - **Map → dev2:** planning a release turns gap stories into dev2 tasks carrying story ids; open questions become ideation inputs; constraints become acceptance boundaries.
   - **dev2 → footprint:** the command that records a Captain ruling also writes a footprint. The footprint schema is owned by dev2 and is one record per story or question id. There are four kinds: a question answered (verbatim words, date, source), a new question, an ADR reference, and evidence advancing.
   - **Footprint → map:** at archive, after observer and learn, footprints fold into a preview room and a docs-only map PR that the Captain approves. A new story changes scope and is always his decision.
2. **Timing:**
   - A footprint is written at the gate, and the map reads it live as "answered, fold pending".
   - The durable YAML write happens once per task, at archive.
   - A ruling made outside any task (release planning in chat) goes straight into a map PR, as today.
   - An ADR reference is written with the ADR; its first sentence becomes visible once its PR merges.
3. **"Done" becomes an evidence ladder:** gap → built (merged; the evidence symbol greps) → verified (validation gate accepted) → shipped (deploy record). The map stores the evidence, and the stage is derived from it.
4. **No step may be missed.** Each new step has all three of these:
   - one command that writes both records;
   - a gate check that a line says done, or not needed and why;
   - an after-the-fact reconcile script whose count of unfolded or unmatched items must reach 0 at each release review. Its first run on qnow is expected near the about 45 answers that qnow's FO folded by hand.

   A step that exists only as workflow.md prose is cut, or gets a check.
5. **Self-repair:** the map joins the 自駕路徑 ("autopilot path": 看見 see → 修復 repair → 學習 learn → 代決 decide by precedent; named by the Captain 2026-10-13: 「就叫做自駕路徑」). It gets no mechanism of its own. This task adds the map's 看見 stage: reconcile findings go to the same kc-claude-plugins issue intake that maintain-flow already serves. Docs-only, reversible map PRs may later move to precedent under ADR 0011.

## Open for ideation

- Each schema's owner and version string: what journey-map produces (story, release, goal and question ids; drawn-commit provenance) and what dev2 produces (task tuple and declaration; answers, ADR references and new questions).
- How ADR rulings reach the map. Proposed: by reference, rendered from the ADR at draw time, so no ADR text is copied.
- One conformance test against both a slug-id and an id workflow.
- Versioning, following subspace-relay ADR 0046 ("Relay's HTTP contract has one version", read 2026-10-13): one version per schema, stated in its producer's machine-readable artifact; documents cite it rather than carry their own; a test fails when the schema changes and its version does not. The change record is the producer plugin's release-please CHANGELOG; an ADR records a shape decision or a breaking change.
- The map-service seam named in the Captain's words above.
- Overlap with task `release-acceptance` (defect 7 is its enforced pre-implementation review) and with `journey-canvas-hosted-poc` (defect 6).

## FO alignment

Release: none (package tooling across kc-journey-map and kc-dev-flow-2).
Release review: not needed: no release.
Needed at ideation: not needed: the Captain accepted the direction in chat on 2026-10-13 (recorded above under "Direction the Captain accepted"); ideation lists its unresolved decisions at its gate.
Surfaces: none
Scope note: scope one draws nothing new; after a fold an answered question shows as answered on today's cards. The renderer change is scope two, task journey-map-progress-and-provenance.
Visible change: none

## Design

Base read: kc-claude-plugins origin/main e2524e93025dd0d5d9217b4d722c2b169d01fda6 (`kc-journey-map` 1.5.2: `lib/model.mjs`, `lib/read.mjs`, `lib/add-story.mjs`, `lib/progress.mjs`, `lib/lint.mjs`; `kc-dev-flow-2`: `scripts/decision_ledger.py`, `extensions/learn/EXTENSION.md`, `references/sd/workflow.md`), Spacedock 0.27.2 (`spacedock --version`, `spacedock gate record --help`), qnow map `docs/journey/qnow.yaml` at origin/next df8ee1d25d595fe34e79e5df866290f18d5deae2 and qnow state branch origin/spacedock-state/dev2 d01c37bc4371412a404f6c214515ee0200a21d2b, relay map `docs/journey/spacedock-review.yaml` at origin/main 0295d1637bca62914afdb4233e040e4383e10af2 and relay state branch origin/spacedock-state/dev2 ed63e6a055f953e49d1ac8c1ac5e56205813b5be; all read 2026-10-13. This session loaded package 0.20.0 and origin/main holds 0.21.0; the design follows origin/main. Ideation wrote no repository file. Profile pilot holds; limits are named under Slices.

### Scope one in one paragraph

Scope one lets a Captain ruling reach the map and nothing else. A ruling given at a gate or in an amendment on a task whose story is on the map leaves one line (a "footprint", the ruling's words, date and source, kept beside the task). When the task is archived, one command writes that answer into a draft of the map file, and the Captain approves it as a docs-only pull request. Two scripts count what did not arrive. Two record shapes are versioned: the footprint (kc-dev-flow-2 owns it) and the map's question fields (kc-journey-map owns them). No renderer changes, so no card, layout or reader output changes.

Moved to task `journey-map-progress-and-provenance` (names only; its body lists them): the evidence ladder, ADR by reference with the `Map:` line, fold-pending marks and the UI preview (`journey-map-dev2-contract/preview/` stays where it is, carried by pointer), drawn-commit provenance, the tuple list form and story-id identity, the map-service seam, the schemas `journey-progress`, `journey-task-tuple` and the rest of `journey-map`, and its criteria AC-3, AC-7, AC-8, AC-9 and AC-10. Criteria ids below keep their old numbers so that task's pointers stay valid; the gaps are deliberate.

### PRFAQ

**Press release (future).** When the Captain rules on a question that the release map asks, FO records one line beside the task: his verbatim words, the date and where he said it. When the task is archived, one command writes the answer, its status and its source into a draft of the map file, changing only that question's lines, and he approves the result as a docs-only pull request. At release review two scripts count every ruling on a finished task that has not reached the map; the count is 0 or FO presents the gap to him. The two record shapes carry a version that a test holds.

**FAQ.**

- *The gate record already holds his words. Why a second file?* The gate record has the words but no map question id. The footprint is the join between them. `add` refuses words that are not inside the cited gate record, so the footprint cannot drift from it (`workflow.md` `## Captain amendments` already requires an amendment to carry his words verbatim).
- *Why not make the gate command write it?* `spacedock gate record` belongs to Spacedock, a separate repository; its `--help` (0.27.2) lists no hook, so this package cannot add a step inside it. The write is a package script run right after, and two checks catch a skipped run. This is decision D2.
- *Why write the map only at archive?* The Captain's timing ruling, 2026-10-13: the durable write happens once per task, at archive. Until then the footprint sits in the state checkout and nothing reads it live; the live read is scope two.
- *What about a ruling made in chat with no task?* Unchanged: it goes into a map pull request by hand, as today. The tool for it was not in scope one's list, so it is not here.
- *Does the map stop being the authority?* No. The map file in git stays the authority; a footprint is a proposal until the Captain approves the pull request. A fold creates no story or question; one that is missing is listed as `no-story` or `no-question`.

### Existing-code check (recorded conclusion)

Journey: gate ruling -> footprint -> map answer. Works today: `decision_ledger.py` (`split_task`, `gate_entries`) already parses gate resolutions, their reasons and dates from task frontmatter; the `learn` extension already joins FO before `merge guard` and right after the archive, and its `<task>/observer.md` shows that a file in the task folder is committed with `spacedock state commit <slug>`; `add-story.mjs` already edits the map by splicing text into the original file; `read.mjs` `applyDiff` already sets `answer` on a question found by story id and question id. Incomplete, measured 2026-10-13 with `parseDocument(src).toString({lineWidth: 0, flowCollectionPadding: false})`, the option set `applyDiff` writes with: qnow's map (951 lines, every question a one-line flow map) comes back with 0 differing lines; relay's map (2047 lines, block style, hand-wrapped) comes back with 3803 differing lines (`diff` counts a removed and an added line separately), and the best of ten option sets (`lineWidth` 0/80/90/100/120 with `indentSeq` true/false) still leaves 705. So whole-file rewriting cannot produce a reviewable pull request on a relay-style map, and the fold must splice text as `add-story.mjs` does. `model.mjs` `normalizeQuestions` also drops any field it does not list, so `source` needs one added line to be read back. Two bounded searches found nothing to reuse for the missing parts: `git grep -n -i "footprint" origin/main -- kc-journey-map kc-dev-flow-2` (CHANGELOGs excluded) matched only card-geometry comments in `records.mjs` and `render.mjs`, and `git grep -n -E "journey-(answer|fold|reconcile)|map_footprint"` over the same paths matched nothing. Need: the Captain's accepted direction items 1, 2 and 4. Conclusion: reuse the parser, the splice helpers (export `serializeItem`, `lineStart`, `afterLine`) and the question lookup; add one dev2 script, two kc-journey-map commands and one question field. Unknown: adopters other than qnow and relay were not read.

### The chain

```mermaid
flowchart TD
    RULE["Captain rules at a gate or in an amendment"] --> REC["spacedock gate record (Spacedock's own command)"]
    REC --> ADD["map_footprint.py add writes one line to footprints.jsonl beside the task"]
    ADD --> CHK["map_footprint.py check, before merge guard"]
    CHK --> ARCH["merge guard passes, task is archived"]
    ARCH --> FOLD["journey-fold.mjs writes a draft map, not the source file"]
    FOLD --> PR["docs-only map pull request, Captain approves"]
    PR --> MAP["map file: answer, status, source"]
    MAP --> RECON["journey-reconcile.mjs: unfolded and stale-open must be 0"]
    ARCH --> AUD["map_footprint.py audit --since: unrecorded and invalid must be 0"]
    RECON -->|"nonzero"| ISSUE["FO presents it; on Captain yes, files a kc-claude-plugins issue"]
    AUD -->|"nonzero"| ISSUE
```

### Two schemas, each owned by its producer

```mermaid
flowchart LR
    subgraph D2["kc-dev-flow-2 produces"]
        FP["journey-footprint/v1: one line per answered question"]
    end
    subgraph JM["kc-journey-map produces"]
        Q["journey-map-question 1.0.0: question fields, with source"]
    end
    FP -->|"consumer pins the string journey-footprint/v1"| F["journey-fold.mjs and journey-reconcile.mjs"]
    F -->|"writes"| Q
```

`journey-footprint` 1.0.0, field table printed by `map_footprint.py schema journey-footprint`; one JSON object per line in `<task folder>/footprints.jsonl`:

| field | rule |
|---|---|
| `schema` | the string `journey-footprint/v1` (wire pin: major only) |
| `id` | `fp:<task slug>:<n>` |
| `kind` | `answered`, the only kind in 1.0.0 |
| `task` | task slug |
| `journey`, `story`, `question` | the map's `journey:` value, a story id, a question id inside that story |
| `words` | the Captain's words, verbatim; a substring of the source text |
| `date` | `YYYY-MM-DD`; equals the source's date |
| `source` | `gate-attempt:<id>` (the resolution `reason`) or `amendment:<n>` (its `Captain:` line) |
| `answer` | one line, FO's statement of the decision; becomes the map's `answer` |

`journey-map-question` 1.0.0, printed by `node lib/schemas.mjs journey-map-question`; it covers one question entry only, and its name is narrow on purpose so scope two can decide how the rest of the map file is versioned:

| field | rule |
|---|---|
| `id` | explicit string, unique inside its story (a question without one cannot be folded; all 110 of qnow's and all 220 of relay's questions have one) |
| `ask`, `status`, `because`, `answer`, `doc` | as `model.mjs` reads them today; `status` is `open`, `answered` or `deferred`; `because` is owed when `deferred` |
| `source` (new, optional) | `{kind: gate or amendment, ref: "<task slug>/<footprint source>", words, date}`; written only by the fold |

Version rule, held by tests. Each producer keeps `contract-versions.json` (`{version: sha256 of the printed table without its version}`). A test fails when the printed table's hash differs from the hash recorded for its current version, or when the current version has no recorded hash. Adding an optional field or a kind is a MINOR; removing, renaming or changing a field's meaning is a MAJOR and changes the wire string; wording only is a PATCH. A consumer refuses a different major and ignores an unknown field or an unknown `kind` (listed as `skipped`, not counted). The change record is the producer's release-please CHANGELOG, written from the Conventional Commit that bumps it; an ADR is written for a schema's first shape and for every MAJOR. This follows subspace-relay ADR 0046 (one version per contract, a test that fails when the contract changes and the version does not). D1 asks the Captain to confirm the change record.

### Footprint: add, check, audit (dev2 owns)

Script `kc-dev-flow-2/extensions/journey-map/map_footprint.py`, standard library only (dev2 holds no YAML parser; it imports `split_task` and `gate_entries` from `scripts/decision_ledger.py`).

- `add <task> --question Q --source gate-attempt:<id> --words '...' --answer '...' [--story S]`: `--story` defaults to the task's `journey-story` and `journey` comes from its frontmatter. It refuses (exit 1, naming the cause) words that are not inside the cited resolution `reason` or amendment `Captain:` line, a `date` that differs from the source's, and a `journey` that differs from the task's. Otherwise it appends one line. It does not read the map: an unknown story or question is found later by reconcile.
- `check <task>`: a "journey task" is one whose frontmatter has both `journey` and `journey-story` non-empty; for any other task it exits 0. For a journey task it exits 1 unless `## FO alignment` holds `Map footprints: <n> in footprints.jsonl` with `n` equal to the valid lines and at least 1, or `Map footprints: not needed: <reason>` with a non-empty reason, and every line passes the `add` rules and names a source that resolves. Known limit: release-level tasks that carry `journey` but no `journey-story` (qnow has 3 archived ones with 23 gate resolutions, and 9 live) are outside `check` and `audit`; `add` still accepts them with an explicit `--story`. Scope two's list form is what brings them in.
- `audit <workflow-dir> --since YYYY-MM-DD`: over archived journey tasks that have at least one resolution or amendment dated on or after `--since`, prints `unrecorded <n>` (neither a valid footprint nor a not-needed line) and `invalid <n>` (a bad line); exit 1 when either is above 0, exit 2 without `--since`. The cutover exists because an archived task cannot take a new line (`spacedock status --set` refuses it, and an archived task's state is publish-only). Measured 2026-10-13: without a cutover the audit would report `unrecorded 7` on qnow (its 7 archived journey tasks hold 35 resolutions) and 2 on relay (2 of its 6 journey tasks are archived, with 9 of 14 resolutions), with nothing anyone could repair. The cutover is the date the adopter lists the extension; a start date after the last existing resolution reports 0.
- `schema journey-footprint`: prints the field table and version.

Where it runs: right after each `spacedock gate record` and each amendment on a journey task, FO runs `add` for each map question the ruling answers, or notes that it answers none; before `merge guard`, FO writes the `Map footprints:` line, runs `check` and commits with `spacedock state commit <slug>`. It cannot run after the archive, because the task is then publish-only.

### Fold and reconcile (kc-journey-map owns)

`journey-fold.mjs <journey.yaml> --footprints <path to footprints.jsonl> --out <draft.yaml>`: refuses an `--out` that exists (as `journey-handoff.mjs --out` does) and does not write the source file (AC-5 compares its checksum). For each `answered` footprint whose `journey` equals the map's, it finds the story (ids are unique; `calculateProgress` already refuses a duplicate) and the question by its explicit id, and writes `answer`, `status: answered` and `source`. It removes no field, so a deferred question keeps its `because` (AC-5 asserts it). A question that already has the same `source.ref` is `already` (folding twice gives the same bytes); one that has a different `answer` or `source` is `conflict` and nothing is written for it. The write splices the edited question's own lines into the original text, as `add-story.mjs` does, so every other byte of the file is unchanged; after splicing it re-parses the draft and refuses to write unless the only differences are those questions' fields. One line per footprint: `applied`, `already`, `conflict`, `no-story`, `no-question` or `wrong-journey`; exit 1 on any of the last four.

`journey-reconcile.mjs <journey.yaml> --workflow-dir <dir>`: lists tasks as `progress.mjs` does (`taskListing`, `spacedock status --archived`), reads each journey task's footprints, and prints:

- `unfolded`: footprints on archived tasks that are not in the map file as given (not `already`); includes the `no-story`, `no-question`, `conflict` cases with the reason on its line.
- `stale-open`: a question that is neither answered nor `deferred` with a `because`, on a story named by an archived journey task and by no live one. It catches a ruling nobody recorded, from the map's side.
- `pending` (information; does not change the exit code): footprints on live tasks, not due until archive.
- `unsourced` (information; does not change the exit code): answered questions with no `source`. Without a backfill these cannot reach 0, so they are a baseline, not a gate.

Exit 1 when `unfolded` or `stale-open` is above 0. The map is read from the path given; at release review FO passes the map as it stands on the trunk (`git show <trunk>:<path>` to a temp file).

### Steps: one write, one gate line, one count

| Step | One-command write | Gate line (done, or not needed and why) | Count (must be 0 at release review) |
|---|---|---|---|
| 1 gate footprint | `map_footprint.py add ...` right after `gate record` or the amendment | `Map footprints: <n> in footprints.jsonl` or `Map footprints: not needed: <reason>` under `## FO alignment`; `check <task>` exit 1 without one, before `merge guard` | `map_footprint.py audit --since D`: `unrecorded`, `invalid`; `journey-reconcile.mjs`: `stale-open` |
| 2 archive fold | `journey-fold.mjs ... --out <draft>`, then FO shows the draft diff | FO's archive message states `journey-map fold: <PR url>`, `not needed: <reason>` or `not run: <reason>`, the form `## Extensions` requires | `journey-reconcile.mjs`: `unfolded` |

Opening the pull request follows `## Delivery authority` unchanged; the extension grants none. Self-repair, the Captain's 自駕路徑 ("autopilot path"): a nonzero count is the map's 看見 (see) step; FO presents it and, on his yes through its existing issue-filing approval gate, files a kc-claude-plugins issue, the intake `maintain-flow` already serves. No new mechanism. `workflow.md` is not edited by scope one: an adopter lists `journey-map` under `extensions:`, and a new `kc-dev-flow-2/extensions/journey-map/EXTENSION.md` carries the instruction lines, so the word budget is untouched.

### Will scope two have data as soon as scope one merges and is synced?

No for the fold-pending part, and yes for everything else, because most of scope two's inputs exist today and scope one writes none of them. The Captain's question was whether relay and qnow, being in dense development, would fill scope two immediately. What scope one writes: one `answered` line, forward only, when a ruling at a gate or in an amendment answers a map question on a task that has `journey` and `journey-story`, and only after the adopter lists the extension on a released, synced package; and, later, `answer`, `status` and `source` in the map file, only after the task is archived and he approves the fold pull request. It writes nothing about evidence, ADRs, provenance or tasks with several stories.

| Scope two piece | Its data | When it exists |
|---|---|---|
| evidence ladder (verified, shipped) | approved validation gates in task files, and the adopter's deploy record; scope one writes neither | today for `verified` (qnow: 7 archived tasks with a story; relay: 6, of which 4 are live); `shipped` has no source in either adopter that I read |
| ADR by reference | ADR paths already in the maps: `grep -o 'docs/adr/[^ )"#]*'` finds 23 in qnow's map and 32 in relay's | today |
| drawn-commit, tuple list form, service seam | none needed | not applicable |
| fold-pending marks, `source` shown | footprints, then folded `source` | after (1) both plugins are released and an adopter syncs and lists `journey-map`, (2) a ruling at a gate or amendment on a live journey task answers an open map question, (3) FO runs `add`; the `source` in the map file comes only after archive and his approval |

The supply of answerable questions is bounded and measured. qnow's map has 31 open questions, but 20 are `deferred` with a `because` and 11 are plain open, all on stories not built yet; none of qnow's 7 journey tasks with a story has an open question left, so qnow has no live task that could produce a footprint today. Relay's map has 22 open, 1 deferred and 21 plain open, all on unbuilt stories; the only story that has a live journey task and open questions is `get-started-page` (5 of its 10 questions), served by tasks `agent-front-door` and `agent-front-door-publish`. So the earliest footprint is relay's next ruling on that pair after relay adopts, and the ceiling from questions that exist today is 11 + 21 = 32 footprints across both. I did not classify how many of the 35 qnow and 14 relay gate resolutions answered a map question; the reasons I sampled in one task per adopter were mostly bare approvals. Recommendation to the FO: scope two's ideation does not need to wait for scope-one data except for the fold-pending marks, which it can design against fixtures and relay's live pair.

### Slices, budget and stop condition (proposed, not asked)

Two pull requests, each releasable alone through release-please. (1) kc-dev-flow-2: `extensions/journey-map/` with `EXTENSION.md`, `map_footprint.py`, `test_map_footprint.py`, `contract-versions.json`, and one new step in `.github/workflows/kc-dev-flow-2-tests.yml` (that workflow lists test files one by one, so an unlisted test would run nowhere). It is inert until the second lands. (2) kc-journey-map: `source` through `model.mjs`, `lib/schemas.mjs` with its test and `contract-versions.json`, the exported splice helpers, `journey-fold.mjs`, `journey-reconcile.mjs`, their tests (`node --test lib/*.test.mjs` already runs them), `scripts/journey-dev2-loop-smoke.sh` and a path-filtered workflow that runs it with the pinned Spacedock install. That workflow's cost per pull request is not measured; its path filter is the narrowest that covers both plugins' files. Stop and return to FO on: a change needed in Spacedock; a YAML parser in dev2; a renderer change; a model-judged check inside a script; a third pull request. Profile limit: no credential, no hosting and no new support duty; scope two's seam work is where that could change.

### Non-goals

A live reader of footprints; any card, layout or `journey-read` change; evidence, ADRs, provenance, multi-story tasks; a tool for a ruling made in chat with no task; a backfill of `source` on existing answers (qnow has 79 answered questions, relay 198); creating stories or questions from a fold; any change to Spacedock or `review-release`; the release walk-through (task `release-acceptance`).

### Draft ADRs (named by ruling and short title, no number; FO reserves numbers)

- "A Captain ruling reaches the map as a footprint at the gate and one fold at archive" (the accepted direction's timing paragraph, Captain 2026-10-13).
- "A version binds one field table, and a test holds the binding" (Captain 2026-09-06 and 2026-10-13, following subspace-relay ADR 0046).

### Proposed `## FO alignment` lines (FO owns them; not edited here)

The two recorded lines no longer fit: `Visible change:` promises words, dates, ADR cards, stage lines and pending marks on the map, which are scope two's renderer work. Proposed replacement:

- `Surfaces: none`
- `Visible change: none`

Why: scope one draws nothing new. After a fold the existing answer card shows the answer the way a hand-written one does today, and the words, date and source live in the map file where no renderer reads them. A person sees an answered question where there was an open one, which is a result and not a new surface. If FO keeps `ui`, a `UI proposal:` and a `Preview:` are owed, and the only preview that exists (`journey-map-dev2-contract/preview/preview.tldr`) shows scope two's marks, so it would not be this scope's.

### Unresolved decisions for the Captain

- **D1 how the two record shapes are versioned.** Plainly: each shape gets one version number in one place, and a test turns red if the shape changes without a new number; the question is where the change history is written. Recommend: the release notes that release-please already writes from each commit, plus an ADR for a shape's first form and for every breaking change. Your words 「我想後者應該是 ADR」 read as an ADR for every change; the cost of that reading is one ADR per small additive change that the release notes already record. Worse under the recommendation: a small addition leaves no ADR, so a reader of the ADRs alone will not see it. No past `Override:` line or ADR contradicts this (`git -C docs/dev2/.spacedock-state grep -n 'Override:'` found only a note in `journey-canvas-hosted-poc.md` saying there were none).
- **D2 what "one command" means for the gate footprint.** Plainly: you asked that the command recording your ruling also writes the footprint. Spacedock's own command takes no hook and is another repository, so we cannot add a step inside it. Recommend: a second script run right after it, with two checks that catch a forgotten run (`check` before `merge guard`, `audit` at release review). A wrapper that runs both is possible, but FO would still have to be told to call it, which is the same dependence. Worse under the recommendation: between the gate and `check`, a ruling can exist with no footprint.

## Acceptance criteria

**AC-1**: Each of the two schemas has a field table printed by its producer and a version bound to that table's hash: `python3 kc-dev-flow-2/extensions/journey-map/map_footprint.py schema journey-footprint` and `node kc-journey-map/lib/schemas.mjs journey-map-question` print the table and version; an edited table with an unchanged version, or a current version with no recorded hash, exits 1 naming the schema.
Source: the Captain's open item on versioning, following subspace-relay ADR 0046 (read 2026-10-13: "a test fails when the generated document changes while `info.version` does not").
Verified by: `python3 kc-dev-flow-2/extensions/journey-map/test_map_footprint.py` and `node --test kc-journey-map/lib/schemas.test.mjs` each print the table, pass, then rename one field in a temp copy without a bump and assert exit 1. Falsifier: hashing the table together with its version lets the unbumped edit pass, which the renamed-field case must catch. Not yet verified: neither file exists.

**AC-2**: Consumers refuse another major and accept growth: `journey-fold.mjs` and `journey-reconcile.mjs` exit 1 on a `journey-footprint/v2` line naming that string, accept a `v1` line with an extra field, and list a line of unknown `kind` as `skipped` without counting it; `map_footprint.py check` reports a `v2` line as `invalid`.
Source: the Captain's 2026-09-06 rule (a schema lives with its producer; the consumer pins it).
Verified by: `node --test kc-journey-map/lib/journey-fold.test.mjs kc-journey-map/lib/journey-reconcile.test.mjs` and `test_map_footprint.py`, one case per clause. Falsifier: a reader that ignores `schema` passes the `v2` case. Not yet verified.

**AC-4**: `add` refuses words that are not inside the cited resolution `reason` or amendment `Captain:` line, a date that differs from the source's and a journey that differs from the task's (exit 1 naming the cause), and otherwise appends one `journey-footprint/v1` line; `check <task>` exits 1 for a journey task with neither a footprint nor a not-needed line with a reason, with a count that differs from the valid lines, or with a source that does not resolve, and exits 0 for a task without `journey-story`; `audit --since` prints `unrecorded` and `invalid` and exits 2 without `--since`; two stories that both carry a question `q1` take separate footprints. Baseline: on qnow's state branch d01c37bc, `audit --since 2026-10-14` prints `unrecorded 0` and `--since 2000-01-01` prints `unrecorded 7`.
Source: the accepted direction items 1 and 4 (verbatim words; a gate line that says done or not needed with a reason); the cutover is this design's, from the measurement above.
Verified by: `python3 kc-dev-flow-2/extensions/journey-map/test_map_footprint.py` in a temp state checkout, one case per clause; the baseline by the audit command on a checkout of qnow's state branch at that commit (a validator run, since the repository is not in this one). Falsifier: replacing the substring test with "the source exists" lets a paraphrase through, which the paraphrase case must catch. Not yet verified: the script does not exist; the baseline counts (7 tasks, 35 resolutions) are from reading frontmatter, not from a run.

**AC-5**: A skipped step is caught twice and the loop closes, against the real Spacedock CLI. In a disposable workflow with one journey task and one open map question, after `spacedock gate record` and no footprint: `check` exits 1, and once the task and its folder are moved to `_archive/` (what `merge guard` does; the move is Spacedock's and not under test) `audit --since` prints `unrecorded 1` and `journey-reconcile.mjs` prints `stale-open 1`; after `add`, `check` exits 0 and reconcile prints `unfolded 1`; `journey-fold.mjs` then writes a draft in which the question has `answer`, `status: answered` and a `source` carrying the words and date, and applying the draft makes `unfolded` 0; folding twice gives identical bytes, the source file's checksum is unchanged, an existing `--out` is refused, a `conflict` writes nothing for that question, and a deferred question keeps its `because`. The fold's diff touches only the folded question's lines on both a flow-style fixture (qnow's shape) and a block-style, irregularly wrapped fixture (relay's shape). The smoke runs in a path-filtered CI workflow.
Source: the accepted direction items 1, 2 and 4; the splice requirement is the measurement under Existing-code check.
Verified by: `bash scripts/journey-dev2-loop-smoke.sh`, printing each exit code and count; the CI claim by the check appearing on the pull request (`gh pr checks`). Falsifiers: dropping the `status: answered` write fails the status assertion; skipping `add` is the first case; replacing the splice with whole-file re-serialization fails the block-fixture diff assertion (the same call leaves 3803 differing lines on relay's real map). Not yet verified: no script, workflow or fold exists.

**AC-6**: Baselines on two real maps, each run against a temp workflow directory holding no journey tasks, with identical output on two runs: `journey-reconcile.mjs` on qnow's map at df8ee1d2 prints 171 stories, 0 duplicate story ids, 110 questions (79 answered, 31 open of which 20 deferred and 11 plain), 6 question ids that occur on more than one story, `unsourced 79` and `unfolded 0`, `stale-open 0`, exit 0; on relay's map at 0295d163 it prints 142 stories, 220 questions (198 answered, 22 open of which 1 deferred and 21 plain), `unsourced 198`, `unfolded 0`, `stale-open 0`, exit 0. Folding one synthetic footprint into each real map changes only that question's lines.
Source: the accepted direction item 4 (the first run on qnow is expected near its 45 hand-folded answers; those 45 are release `r1`'s answered questions, read the same way); the counts are the one-off read of 2026-10-13, re-run at the pinned refs and identical to the first attempt's figures for qnow.
Verified by: the script run and a `diff` of its output against these figures, with `git show <ref>:<path>` as the map source; changing one answer on a temp copy changes `unsourced` by 1; a fixture twin of the same shapes runs in CI. Falsifier: a duplicate story id added to a temp copy must make the run report it. Current evidence: the figures are measured by the one-off read; the script is not built, so this is not yet verified.

Limits across the criteria: release-please version bumps appear only on the Release PR after merge, so no criterion here shows a bump; a consumer can lag a MINOR; reconcile and audit cannot see a ruling the Captain made in chat and nobody recorded, and `stale-open` is the only net for it; the baselines in AC-4 and AC-6 use repositories outside this one.

## Stage Report: ideation

- FAILED: A design that names each schema's producer, version string and consumer pin (journey-map: story/release/question ids and drawn-commit provenance; dev2: task tuple, footprint records, ADR references), consistent with the Captain's accepted direction in the task and subspace-relay ADR 0046's one-version rule
  Not started: held at the ideation entry check, see Hold below.
- FAILED: Every new step in the loop (release-to-task, gate footprint, ADR reference, archive fold, out-of-task ruling) carries its one-command write, its gate line (done or not-needed with reason), and its reconcile-script count; a step with none of the three is cut
  Not started: held at the ideation entry check.
- FAILED: Acceptance criteria with reproducible evidence clauses, including one conformance run against a slug-id and an id workflow and a reconcile-script baseline run on qnow's map, plus the unresolved decisions listed for the Captain
  Not started: held at the ideation entry check; no `## Acceptance criteria` section exists, so `design_surfaces.py check` would also exit non-zero.

### Hold

Cause: the task file has no `## FO alignment` section, and so no `Surfaces:` or `Visible change:` line. Checked with `grep -n -i 'FO alignment\|Surfaces:\|Visible change'` on this file at state commit c493a205 (no match), and the file has no such heading on a full read of 99 lines. The ideation principles (`<package>/skills/ideation/principles.md`) say to stop and report in that case; a sibling task (`journey-canvas-hosted-poc`) does carry the section.

Needed from FO before re-dispatch: a `## FO alignment` section recording alignment result, `Surfaces:` and `Visible change:`. Surface choice is not mine to infer. The one open question it settles: whether showing ADR rulings on the canvas counts as a `ui` surface (then a `UI proposal:` and `Preview:` are owed) or `none`.

No repository file, branch or commit was written; the design, evidence plan and decisions list are not started.

### Summary

Held before design: the entry check requires FO alignment, `Surfaces:` and `Visible change:`, and none is recorded. The Captain's accepted direction, the inputs and the read-only references are untouched and ready once FO records the section.

## Stage Report: ideation

- DONE: A design that names each schema's producer, version string and consumer pin (journey-map: story/release/question ids and drawn-commit provenance; dev2: task tuple, footprint records, ADR references), consistent with the Captain's accepted direction in the task and subspace-relay ADR 0046's one-version rule
  `## Design` "Contract catalogue" table (five schemas: producer, version home, wire pin, consumer pin), the version rule (one version per field table, hash-bound in `contract-versions.json`), the tuple and footprint sections; ADR references are read from an ADR `Map:` line. Read at the cited refs 2026-10-13.
- DONE: Every new step in the loop (release-to-task, gate footprint, ADR reference, archive fold, out-of-task ruling) carries its one-command write, its gate line (done or not-needed with reason), and its reconcile-script count; a step with none of the three is cut
  `## Design` "Steps" table: six rows, each with write, gate line and count (the evidence ladder is row 6); two things cut and named (a "new story" footprint, a task-file line for the fold). Release review enforcement is left to task `release-acceptance`.
- DONE: Acceptance criteria with reproducible evidence clauses, including one conformance run against a slug-id and an id workflow and a reconcile-script baseline run on qnow's map, plus the unresolved decisions listed for the Captain
  `## Acceptance criteria` AC-1..AC-10 (AC-3 is the slug-id and id conformance, AC-6 the qnow baseline); decisions D1-D5 at the end of `## Design`. `design_surfaces.py check` printed "journey-map-dev2-contract.md: design surfaces presentable" (exit 0).
- SKIPPED: AC-1 version binding
  Not yet verified: no schema file exists; verified at implementation by `schemas.test.mjs` and `test_map_footprint.py`.
- SKIPPED: AC-2 consumer pins
  Not yet verified: future implementation test.
- SKIPPED: AC-3 conformance on slug-id and id workflows
  Not yet verified: future change to `progress.test.mjs`; the existing slug-id test (1.5.2) is the base.
- SKIPPED: AC-4 footprint add, check and audit
  Not yet verified: `map_footprint.py` does not exist.
- SKIPPED: AC-5 skipped step caught twice, loop closes
  Not yet verified: needs `scripts/journey-dev2-loop-smoke.sh` and the fold.
- SKIPPED: AC-6 reconcile baseline on qnow's map
  Not yet verified as a script run. Current evidence: a one-off `python3` read of `git show origin/next:docs/journey/qnow.yaml` at 6d958e76 gave 171 stories, 110 questions (79 answered, 31 open), 21 answers without `status: answered`, 0 duplicate story ids, 6 repeated question ids, release r1 45 answered and 13 open; r1's 45 is the "near 45" the Captain expected.
- SKIPPED: AC-7 ADR by reference and provenance render
  Not yet verified: future `render.test.mjs` cases.
- SKIPPED: AC-8 map shows the proposed marks
  Current evidence only for the proposal: `preview/preview.tldr` exported from a disposable room (91 records) and re-imported into a second room (91 records); the page rendered and was read from a screenshot. The marks are typed into today's text fields; the new renderer is not verified.
- SKIPPED: AC-9 token header and local-ops switch
  Not yet verified: future `api-fetch.test.mjs`.
- SKIPPED: AC-10 workflow gates and word budget
  Not yet verified: future `adr_lint.py` change and `lint-skills.py` run.

### Summary

The design gives the map and dev2 five producer-owned schemas under one version rule, a per-task `footprints.jsonl` read live as "fold pending" and folded once at archive, ADRs shown by reference from an ADR `Map:` line, and a stage ladder, in three pull requests; reconcile counts must reach 0 at release review. Mermaid blocks parse with the repository's mermaid 11 build (flowchart-v2, both). Ideation wrote no repository file; the preview folder sits in the task's state folder, and the services I started (ports 5891 and 3791, own rooms directory) were stopped by their captured process ids. Unresolved for the Captain: D1 versions and change record, D2 "one command" reading, D3 story id as identity, D4 three-PR budget, D5 the seam.

## Stage Report: ideation (scope one, after `revise`)

- DONE: A scope-one design: a Captain ruling reaches the map (gate footprint -> archive fold -> docs-only map PR writing answer, status and source -> reconcile counts), with only the footprint schema and the map's question fields, and no renderer change
  `## Design` rewritten: "The chain" (Mermaid), "Two schemas" (`journey-footprint` 1.0.0 and `journey-map-question` 1.0.0), "Footprint: add, check, audit", "Fold and reconcile"; no renderer file is in the plan. Read at origin/main e2524e93, qnow df8ee1d2 and relay 0295d163, 2026-10-13.
- DONE: Each scope-one step keeps its one-command write, its gate line and its reconcile count; everything moved to task journey-map-progress-and-provenance is removed from this design and named there by pointer only
  "Steps" table: two rows (gate footprint, archive fold), each with write, gate line and count. The moved items appear once, as names, under "Scope one in one paragraph"; the preview folder is untouched and named by pointer.
- DONE: Acceptance criteria re-cut from AC-4, AC-5, AC-6 and the parts of AC-1 and AC-2 scope one needs, each with a reproducible evidence clause and falsifier, and D1 and D2 restated for the Captain within scope one
  `## Acceptance criteria` holds AC-1, AC-2, AC-4, AC-5, AC-6 (old numbers kept so the other task's pointers hold); D1 and D2 are restated in plain words at the end of `## Design`, no past `Override:` contradicts either.
- DONE: Answer whether scope two has data once scope one merges and is synced
  "Will scope two have data...": no for fold-pending marks (needs a release, a sync, the extension listed, and a gate ruling on a live journey task); yes today for the evidence ladder's `verified` and ADR links. Measured: qnow has 11 plain-open questions and no live task for them; relay has 21, with the live pair `agent-front-door` and `agent-front-door-publish` on 5 of them; ceiling 32 footprints.
- SKIPPED: AC-1 version binding for the two schemas
  Not yet verified: neither `schemas.test.mjs` nor `test_map_footprint.py` exists; verified at implementation.
- SKIPPED: AC-2 consumers refuse another major and accept growth
  Not yet verified: future tests in `journey-fold.test.mjs`, `journey-reconcile.test.mjs`, `test_map_footprint.py`.
- SKIPPED: AC-4 add, check, audit and the cutover baseline
  Current evidence is a read of frontmatter, not a run: qnow state d01c37bc has 7 archived journey tasks with a story and 35 resolutions; relay ed63e6a0 has 6 (2 archived, 9 of 14 resolutions). The script does not exist; not yet verified.
- SKIPPED: AC-5 skipped step caught twice and the loop closes
  Current evidence for the splice requirement only: re-serializing qnow's 951-line map leaves 0 differing lines; relay's 2047-line map leaves 3803 (best of ten option sets 705). The smoke script, fold and workflow do not exist; not yet verified.
- SKIPPED: AC-6 baselines on qnow and relay
  Figures measured 2026-10-13 with a one-off read at the pinned refs (qnow 171/110/79/31, 0 duplicate story ids, 6 repeated question ids, r1 45 answered and 13 open; relay 142/220/198/22); qnow's match the first attempt's. The reconcile script does not exist; not yet verified.

### FO alignment: proposed lines (FO owns them; not edited)

Surfaces and Visible change both changed. Recorded: `Surfaces: ui`, `Visible change: The journey map shows each answered question with the Captain's words and date, ADR rulings by reference, an evidence stage per story, and answers still awaiting fold marked as pending.` That sentence is scope two's renderer work. Proposed: `Surfaces: none` and `Visible change: none`, reasoning under "Proposed `## FO alignment` lines" in the design. If FO keeps `ui`, a `UI proposal:` and a `Preview:` are owed and the only existing preview shows scope two's marks.

### Checker output

`python3 <package>/scripts/design_surfaces.py check <task>` on the task as recorded: exit 1, "surface 'ui' needs a 'UI proposal:' line with text" and "surface 'ui' needs a 'Preview:' line". On a temp copy with the two proposed lines substituted: "design surfaces presentable", exit 0. `spacedock status --read --ac-scan` lists AC-1, AC-2, AC-4, AC-5, AC-6. The Mermaid blocks were not parsed: no DOM library is installed here to run `mermaid.parse`; both use only the flowchart constructs of the first attempt's diagrams, which did parse.

### Not covered by either scope (noted, not decided)

A ruling made in chat with no task has no tool (`journey-answer.mjs` in the first design was not on scope two's list), and existing answers have no `source` (qnow 79, relay 198); `unsourced` is printed as information for that reason. Neither task's body names these.

### Summary

Scope one is two steps and two record shapes: a footprint line written beside the task at the gate, and one fold at archive that splices the answer into the map as a docs-only pull request, with `unrecorded`, `invalid`, `stale-open` and `unfolded` counted at release review. The fold must splice text, because rewriting relay's map would leave 3803 differing lines. Scope two does not have to wait for scope-one data except for the fold-pending marks. Unresolved for the Captain: D1 (where the schema change history is written) and D2 (what "one command" means for the gate footprint).
