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
Surfaces: ui
Visible change: The journey map shows each answered question with the Captain's words and date, ADR rulings by reference, an evidence stage per story, and answers still awaiting fold marked as pending.

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
