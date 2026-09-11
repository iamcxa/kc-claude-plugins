---
session-date: 2026-09-11
sequence: 3
first-commit: 639027fc
last-commit: 06c43766
duration: ~3 days (2026-09-08 09:36 -> 2026-09-11)
scope: ship-flow redesign as a cloud wrapper over kc-dev-flow; batch First Officer for sprint ship-cloud-wrapper
---

# Session Debrief — 2026-09-11 #3

The Captain redirected kc-ship-flow (2026-09-10): ship is a wrapper over dev flow whose only job is to
send a set of planned dev tasks to Conductor cloud, watch the cloud first officers to their gates,
verify, and hand over one UAT; nothing dev flow already does per task stays in ship. The design
(`ship-cloud-dispatch-and-watch/design/2026-09-10-ship-flow-cloud-wrapper-design.md` on this branch)
became three POC tasks under `sprint: ship-cloud-wrapper`; task 1 was built locally, tasks 2 and 3
were delivered by cloud first officers that task 1's `dispatch.sh` created — ship's second batch was
ship itself. All three merged.

## Shipped
- **zb** `ship-cloud-dispatch-and-watch` — [#406](https://github.com/iamcxa/kc-claude-plugins/pull/406). dispatch.sh (one Conductor workspace + FO boot per task, claim fence) and watch.sh (four exits, transcript only via conductor sql); docs/ship re-commissioned to five stages; conductor CLI pin.
- **pz** `ship-remove-duplicated-stations` — [#410](https://github.com/iamcxa/kc-claude-plugins/pull/410). Removed 14 per-task stations that duplicated kc-dev-flow/Spacedock (−4577 lines); skill renamed `run-batch`.
- **7e** `ship-verify-uat-close` — [#411](https://github.com/iamcxa/kc-claude-plugins/pull/411). uat-doc.py reads docs/dev entities; close.py + kc-ship-close-receipt/v2; workers write their own debriefs after merge.

## Filed (backlog)
- **rc** `dev-flow-pr-merge-extension` — kc-dev-flow ships the pr-merge extension (Residuals, without-it sections) as a canonical resource synced to adopters; #414 in validation.
- **7z** `ship-dispatch-watch-round-2` — the eight defects the first real batch exposed in watch/boot, the conductor-cli used-surface contract, and the new suites running in CI.
- **es** `ship-verify-uat-close-round-2` — close.py/uat-doc.py read archived and folder-form entities from the dev root, two-root flags, debrief recording.

## Non-PR commits (workflow-only)
- The design spec moved from a code branch (PR #408, closed) to the state branch as a task input under `ship-cloud-dispatch-and-watch/design/` (Captain: the spec is an input to the dev tasks, not a repo file).
- `spacedock-state/ship` initialized (orphan) with the claim fence and the batch question log `_ship_fence/ship-cloud-wrapper.questions.md` (5 worker questions answered, 2 feedback rounds, 1 Captain-typed conn).
- Recovery refs `spacedock-state/dev-recovery-9826ffcf` and `-4b20a918` preserve commits that gate records pin after the FO's replay rewrote them.

All other session commits are rolled up in the shipped PRs above.

## Decisions
- A: each cloud worker is a Spacedock first officer running the full docs/dev route for one task, not an ensign stage (「Ａ，我可以證明可以跑通」).
- Batch key is dev flow's `sprint`; ship calls it a release, renames nothing (「同意」).
- No Linear read or write in this stretch (「這一段不要去管 linear」); tasks are standalone Captain-approved briefs.
- The spec is a dev-task input on the state branch, not a repository file (「不應該上傳 sp 的檔案，應該把它作為輸入放給 dev flow task」).
- Do not edit the Spacedock upstream; formalize the pr-merge Residuals/without-it sections as a kc-dev-flow resource synced to every adopter (「不要去動那個上游」/「可以」).
- Workers write their own `spacedock debrief` after merge; one debrief per cloud worker landed for pz and 7e.
- The Captain typed the push conn into the 7e session himself when the pr-merge mod's rule stopped the worker.

## Issues — Workflow
- watch.sh misreads `initializing` and subagent-idle as `stopped`, misses two of three question shapes, and does not read folder-form entities → 7z.
- The boot message names no sender and carries no Captain conn; one worker treated the FO's answer as an injection, one refused `git push` → 7z.
- close.py reads only `<state-dir>/*.md`: archived and folder-form entities are invisible, one state dir is assumed for two roots, nothing records debrief status; the first real close was hand-written → es.
- dispatch.test.sh/watch.test.sh are skipped in CI without a real conductor → 7z.

## Issues — Spacedock
Not filed (Captain's standing rule: no issues to spacedock).
- Gate records pin commit SHAs; with several writers on one split-root branch, `pull --rebase` sync rewrites them in both directions (FO could not record on a cloud FO's entity; cloud FO could not prepare after the FO's replay).
- `status --set` edits the file without committing; two sets were lost until `state commit` was used.
- `gate record --round` has no documentation; a worker inferred its arguments from binary strings (7e testimonial).
- The engine's own sync fails when the shared checkout holds another session's unstaged file.

## Observations
- The first batch's questions were about authority and identity, not engineering: two missing sentences in the boot message cost more than every script bug together.
- Two first officers read the same pr-merge mod's push rule two ways; the mod's wording on push authorization needs to converge (now a kc-dev-flow resource, #414).
- Evidence first, code after held: every hardening item in round 2 traces to a defect observed in a real run.

## Agent Testimonial
- Date: 2026-09-11
- Harness/runtime: Claude Code
- Model: claude-fable-5-1
- Model version/build: unknown
- Session scale: 6 tasks touched (3 shipped, 3 filed); 5 local workers dispatched plus 2 cloud first officers; 4 PRs touched/merged (#406, #410, #411 merged; #414 open)

Spacedock earned its keep where two cloud first officers that could not see each other were still
checkable by one batch FO through gate records and the state branch; the durable revise → correction
→ re-review → approve chain is legible from the entity files alone. The cost sat in split-root
multi-writer sync: the engine's pull --rebase refuses on a peer's dirty file, and my workaround (replaying
commits through a temporary worktree) rewrote SHAs that gate records pin — the one incident this batch
that was mine. `status --set` not committing and `gate record --round` being undocumented each cost a
round.

## What's Next
- #414 validation → gate → merge; then adopters run the adopt-dev-flow sync.
- Backlog gates for 7z and es; dispatch them as the next ship batch (`sprint: ship-cloud-wrapper-r2`).
- Close receipt for `ship-cloud-wrapper` hand-written and validated with `close.py --validate`; the script regenerates it after es.
- Captain rulings pending: 34 fixtures pinning real SHAs (without-it unanswered on #410); `Integrated head` row default.
- Release kc-ship-flow after the round-2 tasks land; adopters (relay) re-key their batch entities to a sprint value.
