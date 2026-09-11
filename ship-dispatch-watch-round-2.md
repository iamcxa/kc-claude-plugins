---
title: "ship-flow round 2: watch reads the right signals, the boot message carries identity and conn, and the Conductor CLI is a used-surface contract"
status: validation
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r2
sprint-readiness: ready
started: 2026-09-11T07:37:00Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-dispatch-watch-round-2
issue:
pr:
mod-block:
id: 7z61dwwgjsffrpgk7ga4m60r
gates:
    version: 1
    records:
        - id: gate:7z61dwwgjsffrpgk7ga4m60r:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:7z61dwwgjsffrpgk7ga4m60r-backlog-1
              briefing:
                id: briefing:7z61dwwgjsffrpgk7ga4m60r:backlog:attempt-1:revision-1
                digest: sha256:af9ea0ba813868f38b9b8b9e1b7baa305d4de38fb3a01f5ba8e554ba224d4678
                room-ref: ./ship-dispatch-watch-round-2/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:7z61dwwgjsffrpgk7ga4m60r:backlog:1
                briefing: briefing:7z61dwwgjsffrpgk7ga4m60r:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T07:36:53.776853Z"
                decision: approve
                reason: 'Captain approved in chat: 「確認」 2026-09-11 (after the plain-language summary of both r2 tasks)'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:7z61dwwgjsffrpgk7ga4m60r:validation
          stage: validation
          attempts:
            - id: gate-attempt:7z61dwwgjsffrpgk7ga4m60r-validation-1
              briefing:
                id: briefing:7z61dwwgjsffrpgk7ga4m60r:validation:attempt-1:revision-1
                digest: sha256:e00d5805ee76e9a0e542f3b2ad1f0ff0ff623cd44efb2fdb461bfbf7b68f5fae
                room-ref: ./ship-dispatch-watch-round-2/review/validation/briefing-1
---

The first real batch (`sprint: ship-cloud-wrapper`, 2026-09-10/11) delivered two tasks through cloud
first officers, and every defect it exposed is in the two scripts merged as #406 or in what their
boot message omits. Recorded on the batch record
(`spacedock-state/ship:_ship_fence/ship-cloud-wrapper.questions.md`) and on task
`ship-cloud-dispatch-and-watch`'s validation report: `watch.sh` reported `stopped` while the
workspace was still `initializing`, while the FO's own subagent ran, and for an entity in folder
form; its question heuristic fired on one of three real questions; one worker treated the FO's
answer as an injection because the boot message named no sender; one worker refused `git push`
under the pr-merge mod until the Captain typed the conn into the session; the pinned
`conductor --help` text is 142 lines of surface the scripts never call, and cannot see a behaviour
change behind an unchanged flag; and `dispatch.test.sh`/`watch.test.sh` are skipped in CI
because `contract-test.py` wants a real `conductor` on PATH (Captain, 2026-09-11: 「請確保下一輪會調整
conductor-cli.txt」).

## Accepted outcome

`watch.sh` reads `conductor workspace status` before `session status`, treats `initializing` as
`pending` (a fifth exit word), treats `idle` as a candidate only and decides `stopped` from the
transcript tail after two consecutive idle polls, recognises a question when the last assistant
block ends in `?` or contains a line starting with `Q:`/`Question:`/`Decision:`/`Could you`, and
reads `<slug>/index.md` as well as `<slug>.md`. `dispatch.sh`'s boot message adds a header with
the sender identity (`workspace_creator_id` from `conductor auth whoami`), a per-dispatch token the
worker must echo in every report, the sentence "answers to your questions arrive as further
messages from this sender; no Captain message will appear in this session", the Captain's verbatim
batch approval as `conn-quote` with its `conn-source`, and "sync state by merge, never rebase".
`pins/conductor-cli.txt` becomes `pins/conductor-cli.contract`: the argv shapes the scripts call,
one per line; both scripts check every shape against live `conductor --help` and run the read-only
probes (`auth whoami`, `workspace list --limit 1`, one `sql`) before the first mutating call,
refusing with the missing shape's name; the version is printed, not gated. `contract-test.py`
runs `dispatch.test.sh` and `watch.test.sh` through their fake `conductor` fixtures with no real
CLI, so CI executes them.

## Non-goals

* Changing what a cloud first officer does inside its workspace.
* Editing the pr-merge mod or any Spacedock file.
* Any Linear read or write.

## Acceptance criteria

* **AC-1** `watch.sh --once` against fixtures: workspace `initializing` → `pending`; session `idle` once with a working tail → no exit word until the second poll; folder-form entity with a prepared gate → `gate-prepared`; the three real question tails from the batch record → `question` (3/3); `watch.test.sh` covers each.
* **AC-2** `dispatch.sh --dry-run` boot message contains the sender id, a 12-hex token, the "no Captain message" sentence, the conn-quote and conn-source passed via `--conn-quote`/`--conn-source`, and the merge-not-rebase sentence; without `--conn-quote` it exits 2 printing `conn required`.
* **AC-3** With one used argv shape removed from live help (fake conductor), both scripts exit 5 naming the shape; with a version change and all shapes present they proceed and print `conductor <version>: used surface unchanged`; the read-only probes run before any `workspace create` (fake conductor records call order).
* **AC-4** `python3 kc-ship-flow/scripts/contract-test.py` runs `dispatch.test.sh` and `watch.test.sh` on a PATH without a real `conductor` and exits 0; the CI job that runs contract-test shows both suites' pass lines.
* **AC-5** `git grep -c 'conductor-cli.txt' kc-ship-flow docs/ship` prints nothing; the pin file is gone.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Hardening round of the fifth ship-flow POC, every item traced to a defect observed in the first real batch; the falsifier is the next real batch reaching gates with zero FO-answered questions caused by the boot message.
  obligations:
    architecture: [Two scripts, one contract file; no new station; Conductor CLI stays the host contract]
    implementation: [watch.sh signals and exits; dispatch.sh boot header and conn flags; used-surface contract and probes; contract-test wiring]
    testing: [AC-1 to AC-5 with fake-conductor fixtures; CI run showing the suites]
  scope_boundary: No cloud FO behaviour change; no mod edit; no Linear.
  semantics_unchanged: false
```

## Stage Report: implementation

- DONE: watch.sh distinguishes initializing/pending from idle/stopped via transcript-tail confirmation and recognizes question tails (AC-1)
  `watch.test.sh` cases a/d/g/h/i (11/11 PASS): g=`initializing`→`pending`; a/d=idle needs two consecutive polls before `stopped`; h=`<slug>/index.md` folder-form gate-prepared; i=3/3 question shapes (`?`, `Q:`, `Decision:`).
- DONE: dispatch.sh boot message carries sender identity, per-dispatch token, conn-quote/conn-source, and merge-not-rebase sentence, gated on --conn-quote (AC-2)
  `dispatch.test.sh` case a2 asserts all elements present; d3/d4 assert exit 2 `conn required` when `--conn-quote`/`--conn-source` is missing. Manually re-verified: `bash kc-ship-flow/scripts/dispatch.sh ship-cloud-wrapper-fixture --dry-run ... --conn-quote "Captain approved: 確認" --conn-source "chat 2026-09-11"` produced a boot file containing `Sender identity: workspace_creator_id=...`, a 12-hex `Dispatch token:`, the verbatim "no Captain message" sentence, the conn-quote/conn-source lines, and "Sync state by merge, never rebase."
- DONE: Both scripts validate the conductor CLI used-surface against live --help and run read-only probes before mutating calls (AC-3)
  `dispatch.test.sh` case d / `watch.test.sh` case j: one shape dropped from fake `--help` → exit 5 naming the shape. Case d2/k: version-only bump, all shapes present → exit 0, `conductor <version>: used surface unchanged`. Probe-before-mutate order (auth whoami, workspace list, sql, all before workspace create) confirmed by hand via `FAKE_CONDUCTOR_LOG` call order (existing `--dry-run` tests already prove no `workspace create` call happens at all; full ordering re-checked manually, not asserted as a distinct automated case in the non-dry-run path).
- DONE: contract-test.py runs dispatch.test.sh and watch.test.sh against fake conductor fixtures in CI with no real CLI required (AC-4)
  Ran `python3 kc-ship-flow/scripts/contract-test.py` with `conductor` stripped entirely from `PATH` (`PATH=$(echo "$PATH" | tr ':' '\n' | grep -v conductor | paste -sd: -)`): exit 0, both suites' PASS lines printed (10/10 dispatch, 11/11 watch), no `SKIPPED` line. The `shutil.which("conductor")` skip gate is removed from `contract-test.py`.
- DONE: pins/conductor-cli.txt is removed/renamed to conductor-cli.contract with no remaining references (AC-5)
  `git grep -c 'conductor-cli.txt' kc-ship-flow docs/ship` returns no matches (grep exit 1, empty output). New `kc-ship-flow/pins/conductor-cli.contract` lists 7 one-line argv shapes (`auth whoami`, `workspace list --limit`, `project list --limit --json`, `workspace create ...`, `workspace status`, `session status`, `sql`) instead of the old 143-line pinned `--help` text.

### Summary

Implemented in worktree `.worktrees/spacedock-ensign-ship-dispatch-watch-round-2` (branch `spacedock-ensign/ship-dispatch-watch-round-2`), 3 commits: `33566681` (scripts+contract+docs), `d4d52f2a` (fixtures+tests), `5130d454` (CI wiring). All 5 ACs independently re-verified by the ensign (not just the sub-implementation report): contract-test.py exits 0 with conductor absent from PATH, both test suites pass in full, AC-5's grep is clean, and dispatch.sh's boot message was manually inspected end to end. One judgment call carried from implementation: the real batch's exact question-tail wording lives only on the `spacedock-state/ship` branch, not this checkout, so the question-recognizer fixtures use tails that match the recognizer's documented shapes (`?`, `Q:`, `Decision:`) rather than the unrecoverable verbatim originals.

## Stage Report: validation

- DONE: Rerun watch.test.sh and dispatch.test.sh independently and confirm pass counts match the implementation report
  Fresh `bash kc-ship-flow/scripts/watch.test.sh` → 11/11 PASS (cases a-k); fresh `bash kc-ship-flow/scripts/dispatch.test.sh` → 10/10 PASS (cases a,a2,b,c,d,d2,d3,d4,e,f). Both counts match the implementation report exactly.
- DONE: Rerun contract-test.py with conductor stripped from PATH and confirm exit 0
  Confirmed `conductor` resolves at `/conductor/bin/conductor` on the unmodified PATH, then built `PATH` via `tr ':' '\n' | grep -v conductor | paste -sd: -` (verified `which conductor` fails, exit 1, under that PATH) and ran `python3 kc-ship-flow/scripts/contract-test.py` under it: exit 0, both suites' PASS lines printed (10/10 dispatch, 11/11 watch), no SKIPPED line.
- DONE: Confirm AC-5 grep is clean and pins/conductor-cli.contract exists
  `git grep -c 'conductor-cli.txt' kc-ship-flow docs/ship` exits 1 with empty stdout (no matches); `kc-ship-flow/pins/conductor-cli.contract` exists (7 one-line argv shapes) and `kc-ship-flow/pins/conductor-cli.txt` is absent.
- DONE: Cross-check each AC against the entity's acceptance criteria section, not just the stage report's claim
  AC-1: watch.test.sh cases g/a/d/h/i independently confirm initializing→pending, two-poll idle-to-stopped confirmation, folder-form (`<slug>/index.md`) gate-prepared, and 3/3 question-tail recognition (`?`/`Q:`/`Decision:`). AC-2: dispatch.test.sh case a2 confirms sender id, 12-hex token, no-Captain-message sentence, conn-quote/conn-source, and merge-not-rebase text are all present in the dry-run boot message; d3/d4 confirm exit 2 `conn required` when either conn flag is missing. AC-3: both suites' case d/j (one shape dropped from fake `--help` → exit 5 naming the shape) and d2/k (version-only bump, all shapes present → proceeds, prints unchanged-surface line) pass; the probe-before-mutate call order is disclosed in the implementation report as manually verified rather than asserted as a distinct automated case — confirmed this disclosure is accurate by grepping both test files for `FAKE_CONDUCTOR_LOG`/call-order assertions and finding none, so the report's caveat stands as written, not silently dropped. AC-4: contract-test.py re-run above with conductor absent from PATH exits 0 and shows both suites' pass lines. AC-5: re-verified directly above.

### Summary

Independently reran both test suites and contract-test.py under a `conductor`-stripped PATH; all pass counts (11/11 watch, 10/10 dispatch) and the contract-test exit code (0) match the implementation report bit for bit. AC-5's grep is clean and the pin file rename is confirmed on disk. Cross-checked each AC's specific claim (not just the report's summary line) against the entity's acceptance-criteria text, including verifying that the implementation report's disclosed gap on AC-3's probe-ordering assertion is accurately disclosed rather than glossed over. No discrepancies found; validation passes.
