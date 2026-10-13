# 0012. A Captain ruling reaches the map as a versioned footprint

Date: 2026-10-13

## Status

Accepted

## Context

kc-journey-map and kc-dev-flow-2 met only through prose, and an adopter's First Officer
reported six defects from that gap on 2026-10-13 (kc-journey-map 1.5.1, kc-dev-flow-2
0.20.0). One of them: Captain rulings land in task files and ADRs while the map's question
answers are written by hand, so the map lags every ruling. On the adopter's map about 45 of
about 58 open questions were answerable from rulings already recorded elsewhere. The
Captain's standing rule of 2026-09-06 is that plan, dev and ship are independent plugins
joined only by versioned input and output contracts, each schema owned by its producer.
`spacedock gate record` belongs to Spacedock, whose `--help` (0.27.2) lists no hook, so this
package cannot add a step inside it.

## Decision

**Words:** 「可以進入設計」 — Captain, after the FO presented the loop, its timing and the no-miss checks, 2026-10-13; and 「那就照建議，這裡的議題應該是要讓讀者或是說 FO 意識到 ARD, release changelog 等都存在，且必要時要去讀」 — Captain, approving the scope-one ideation gate with the two decisions as recommended, 2026-10-13.

**Options considered:**
- a footprint line beside the task at the gate, one fold at archive, two shapes each carrying one version that a test holds to its field table, history in the release notes plus an ADR for a first shape and each MAJOR (chosen)
- an ADR for every schema change instead of release notes — rejected: one ADR per small additive change that the release notes already record
- a wrapper that runs `gate record` and the footprint write together — rejected: FO would still have to be told to call it, the same dependence as a second script, with `check` and `audit` catching a forgotten run
- the map reading task files live and writing at every ruling — rejected by the Captain's timing: the durable map write happens once per task, at archive

**Recommended:** the first option, for both decisions put to the Captain (where the change history is written; what "one command" means for the gate footprint).

A Captain ruling that answers a map question on a journey task is recorded as one `journey-footprint/v1` line in `<task folder>/footprints.jsonl`, with his verbatim words, date and source, by `map_footprint.py add` right after the gate or amendment. `check` runs before `merge guard`, and `audit` and `journey-reconcile.mjs` count what is missing at release review. At archive one `journey-fold.mjs` run splices the answer into a draft of the map file, and the Captain approves it as a docs-only pull request; the map file in git stays the authority. Each of the two shapes (`journey-footprint`, owned by kc-dev-flow-2; `journey-map-question`, owned by kc-journey-map) has one version in its producer's `contract-versions.json`, bound to the hash of the printed field table; a test fails when the table changes and the version does not. Adding an optional field or a kind is a MINOR, removing, renaming or changing a field's meaning is a MAJOR and changes the wire string, wording only is a PATCH; a consumer refuses another major and ignores an unknown field or kind. The change record is the producer's release-please `CHANGELOG.md`; an ADR is written for a schema's first shape and for every MAJOR. Each producer's `schema` command prints where that history lives, and the extension and the journey-map docs say when to read it. Later work must keep the history pointer in the `schema` output and must not copy ADR text into a footprint.

## Consequences

A ruling can exist with no footprint between the gate and `check`; `check` and `audit` catch it, and `stale-open` is the only net for a ruling nobody recorded. A small additive change leaves no ADR, so a reader of the ADRs alone will not see it; the CHANGELOG and `schema` footer carry it. A consumer can lag a MINOR. Not built: the live reader of footprints, evidence stages, ADR cards on the map, drawn-commit provenance, tasks with several stories and the map-service seam (task `journey-map-progress-and-provenance`). Reopen if a Spacedock release adds a gate-record hook, or if a footprint is found whose words differ from its gate record.
