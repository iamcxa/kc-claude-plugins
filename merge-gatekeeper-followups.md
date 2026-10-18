---
title: merge-gatekeeper follow-ups declined at the #666 delivery gate (file list head binding, ready-event run, record fields)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #666 delivery gate (head a05b18a0, 2026-10-18); reasons also in that task's gate summary.

- Codex round 4 P2 (review:5563313524), declined under the round-3 rule: `kc-dev-flow-2/scripts/delivery_gate.py` reads the PR facts and the file list in two calls, so a force push between them with the same file count mixes two revisions in the class, points and ask record. Fix shape: re-read the head after the file list, or read files pinned to the recorded SHA.
- Deferred risk (validation-4 F1): a workflow run started by the ready event itself appears about 2 seconds after `ready_for_review` and can be missed; zero runs beside a non-empty rollup does not hold. The restored README wait-for-jobs clause is the backstop.
- Deferred risk (validation-4 F2, security findings 1 and 3): the per-ask record is not read at merge time and `verdict` reads "merge" for class `other` or `script-with-test` from filenames alone; nothing consumes either until POC task merge-grant-need-poc.
- Polish: mutation gaps (request head not asserted, no `next:` assertion for the runs hold, no row for a sole skipped or neutral newest run, `gate|budget` and `adr-path` rows), doc_impact lines owed for sizing-simulation.py and adoption.md, a docstring that omits the runs hold, and the 12-point cap dropping the profile and path points on a PR with many never paths.
