---
title: "ship-flow POC: dispatch one cloud first officer per dev task and watch the set to its validation gates"
status: validation
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper
sprint-readiness: defer
started: 2026-09-10T04:22:51Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-cloud-dispatch-and-watch
issue:
pr: 406
mod-block:
id: zbkw7v9dsgxgf048qvrmxmwy
gates:
    version: 1
    records:
        - id: gate:zbkw7v9dsgxgf048qvrmxmwy:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:zbkw7v9dsgxgf048qvrmxmwy-backlog-1
              briefing:
                id: briefing:zbkw7v9dsgxgf048qvrmxmwy:backlog:attempt-1:revision-1
                digest: sha256:83c3464183c7028de813d07f783af997e216d08e25d6ac1b3d60da57607492cb
                room-ref: ./ship-cloud-dispatch-and-watch/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:zbkw7v9dsgxgf048qvrmxmwy:backlog:1
                briefing: briefing:zbkw7v9dsgxgf048qvrmxmwy:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T04:19:51.471578Z"
                decision: approve
                reason: 'Captain approved in chat: 「批」 2026-09-10'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:zbkw7v9dsgxgf048qvrmxmwy:validation
          stage: validation
          attempts:
            - id: gate-attempt:zbkw7v9dsgxgf048qvrmxmwy-validation-1
              briefing:
                id: briefing:zbkw7v9dsgxgf048qvrmxmwy:validation:attempt-1:revision-1
                digest: sha256:b1e3d87bc8ff3e6b6f7538903834086b32a3275029e8eaf8b53097fc75c1b899
                room-ref: ./ship-cloud-dispatch-and-watch/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:zbkw7v9dsgxgf048qvrmxmwy:validation:1
                briefing: briefing:zbkw7v9dsgxgf048qvrmxmwy:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T14:12:46.910776Z"
                decision: approve
                reason: 'Captain approved in chat: 「批」 2026-09-10 (validation gate + merge #406)'
              application:
                target-stage: done
                state: pending
---

kc-ship-flow re-implemented per-task acceptance, PR opening, review disposition and merging that
kc-dev-flow and Spacedock already own, and its dispatch station sent a hand-written message to one
ensign stage. The Captain's ruling (2026-09-10): ship is a wrapper over dev flow whose only job is
to send a set of planned dev tasks to Conductor cloud, watch the cloud first officers until they
finish, verify, and hand over one UAT; if Conductor cloud cannot run, ship cannot be used. Design:
`docs/dev/.spacedock-state/ship-cloud-dispatch-and-watch/design/2026-09-10-ship-flow-cloud-wrapper-design.md (on spacedock-state/dev)`.

## Accepted outcome

`kc-ship-flow/scripts/dispatch.sh <sprint>` creates one Conductor workspace per `docs/dev` task
whose `sprint` matches and whose `sprint-readiness` is `ready`, each with a boot message that makes
the worker the `docs/dev` first officer for exactly that task, running it to a prepared
`validation` gate and a Draft PR through the `pr-merge` mod, never merging. The claim fence records
`<sprint>/<slug> -> workspace id, session id, message sha256` on the state branch before each
create. `kc-ship-flow/scripts/watch.sh <sprint>` polls the state branch and `conductor session
status` and exits per task with exactly one of `gate-prepared`, `quota`, `question`, `stopped`,
reading the transcript tail only through `conductor sql`. Both scripts compare the installed
`conductor --version` to `kc-ship-flow/pins/conductor-cli.txt` before any other call and refuse with the
help diff when it differs. `docs/ship/README.md` is re-commissioned
to `dispatched -> watching -> verified -> uat -> closed`.

## Non-goals

* Removing the old stations (second task in this sprint).
* Slimming `uat-doc.py`, the close receipt, or writing `close.py` (third task).
* Any Linear read or write.
* A local-subagent dispatch path.

## Acceptance criteria

* **AC-1** `bash kc-ship-flow/scripts/dispatch.sh ship-cloud-wrapper --dry-run` prints one `conductor workspace create` argv per ready task in the sprint, each with `--message-file` whose sha256 matches the fence record it would write, and exits 0; with `conductor auth whoami` failing it exits 2 printing `conductor unavailable`.
* **AC-2** `bash kc-ship-flow/scripts/watch.sh ship-cloud-wrapper --once` against a fixture state dir prints one line per task `<slug> <exit>` where `<exit>` is one of the four words above, and a fixture whose transcript tail carries the usage-limit banner yields `quota`, not `stopped`.
* **AC-3** The real run: the other two tasks of this sprint, dispatched by `dispatch.sh`, each reach a prepared `validation` gate with a Draft PR opened by the cloud first officer, observed by `watch.sh` as `gate-prepared`; the batch record lists every question a worker asked and the answer sent.
* **AC-4** `python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md` exits 0 on the re-commissioned README and exits 1 naming the row when the `Integrated head` row is removed.
* **AC-5** With `kc-ship-flow/pins/conductor-cli.txt` matching the installed `conductor --version`, `dispatch.sh --dry-run` proceeds; with the pin's version line edited to another value, both `dispatch.sh` and `watch.sh` print a `diff` of the pinned help against live `conductor --help` and exit 5 printing `conductor cli changed`, making no other call.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Fifth ship-flow POC; the wrapper shape (one cloud FO per task, watch by state branch) is unproven and the other two tasks of this sprint are its falsifier run. Outcome is evidence that the shape holds, not production code; the scripts will be rewritten after the POC.
  obligations:
    architecture: [Two scripts only; no per-task acceptance, review or merge logic; Conductor CLI is the host contract]
    implementation: [dispatch.sh with dry-run and claim fence; watch.sh with the four exits; conductor CLI pin file and version check in both; README re-commission]
    testing: [AC-1, AC-2 and AC-5 on fixtures; AC-3 on the real sprint; AC-4 on the README]
  scope_boundary: No removal of old stations; no close receipt change; no Linear; no local dispatch.
  semantics_unchanged: false
```

## Stage Report: implementation

- DONE: dispatch.sh --dry-run prints one create argv per ready task with a matching message sha256, exits 2 conductor unavailable on auth whoami failure (AC-1)
  `kc-ship-flow/scripts/dispatch.sh`; `dispatch.test.sh` cases a-c, f; verified live against the real sprint (3 real tasks, all print correctly) at 8b27fae1.
- DONE: watch.sh --once prints one of gate-prepared\|quota\|question\|stopped per task against a fixture state dir, usage-limit banner yields quota (AC-2)
  `kc-ship-flow/scripts/watch.sh`; `watch.test.sh` cases a, b, f.
- DONE: both scripts refuse exit 5 "conductor cli changed" with a help diff on a conductor-cli.txt pin mismatch, before any other call (AC-5)
  `kc-ship-flow/pins/conductor-cli.txt`; `dispatch.test.sh` case d, `watch.test.sh` case d — the fake conductor exits 64 if anything past --version/--help is called.
- DONE: neither script calls intent.sh, holder.sh, or any accept/review/merge/notify/debrief script — task 2 can remove all of them
  grep confirms zero references from `dispatch.sh`/`watch.sh` to those scripts; the claim fence is dispatch.sh's own JSON file under `_ship_fence/`, not intent.sh's.
- DONE: docs/ship/README.md re-commissioned to dispatched -> watching -> verified -> uat -> closed; local-profile-check.py passes it and names Integrated head when removed (AC-4)
  `python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md` → `LOCAL_PROFILE_OK: 9 required rows present`; row-removed run → `LOCAL_PROFILE_MISSING_ROW: Integrated head`, exit 1.
- DONE: shell values (slug, message sha256, workspace/session ids) reach Python only via sys.argv, never interpolated into `-c` source
  Falsifier: `spacedock new "it's-a-slug"` mints a real entity with a literal quote in its slug (spacedock accepts one). At ba9daeb7, `dispatch.sh ... --dry-run` against a fixture containing that entity exits 1 with `SyntaxError: unterminated string literal`; `watch.sh ... --once` likewise exits 1. At 8b27fae1 both exit 0 and print a line for the slug (`dispatch.test.sh`/`watch.test.sh` case f pin this in permanently).
- DONE: quota check reads only the transcript tail, not the whole transcript
  Falsifier: a transcript with the usage-limit banner in an earlier assistant turn and plain prose in the last one read `quota` before the fix, `stopped` after (`watch.test.sh` case e).
- SKIPPED: RoboRev implementation-exit observation (`implementation_exit_observation_declared` / `roborev-implementation-exit.md`)
  This build is retained, not disposable (dispatch.sh/watch.sh are the real artifact AC-3 will run next, not a throwaway demo) — fresh proof, so the build contract keeps the RoboRev observation and independent decision in validation, not implementation. Not invoked here by design, not omitted by oversight.
- SKIPPED: AC-3 (the real dispatch of the other two sprint tasks)
  Not in this stage's checklist (items 1-3 only); requires this dispatch.sh to exist first.

### Residuals (not fixed, flagged for the next stage/task)

- Task 1 itself keeps `sprint-readiness: ready` throughout its own lifecycle; a later `dispatch.sh ship-cloud-wrapper` real run will re-select it unless it is fenced or done first.
- A `conductor workspace create` failure after the claim-fence pre-commit leaves a committed null-workspace record with no reconcile path; a re-run reports `already-recorded` and does not retry.
- `docs/ship/.spacedock-state` does not exist in any local checkout; the remote `spacedock-state/ship-flow` branch holds unrelated superpowers-spec archive content, not batch entities. Which branch ship's real state lives on is a First Officer decision before the AC-3 real run, not resolved here.
- `dispatch.sh` resolves `docs/dev` relative to its own script path, so the literal AC-1 command (no `--workflow-dir`) must be run from the main workspace checkout, not a task's feature worktree — confirmed by testing both ways.
- `spacedock status --workflow-dir docs/ship --validate` could not be exercised (no local state checkout, previous point) — the re-commissioned README is unverified against any existing batch entity in the old six-stage schema.
- `dispatch.test.sh`/`watch.test.sh` are standalone, not wired into `kc-ship-flow/scripts/contract-test.py` (which still enumerates the old station chain this design removes) — left for task 2. Ran `contract-test.py` in full: one pre-existing, unrelated failure (`fenced-dispatch.test.sh`, reproduces identically on HEAD before this change).
- watch.sh's question heuristic is "last non-blank line of the last assistant turn ends in `?`" only; no other question shape is recognized.
- The `Integrated head` README row defaults to `trunk` as a placeholder, not a Captain ruling.

### Summary

dispatch.sh and watch.sh implement the cloud-wrapper design's `dispatched`/`watching` stages: one Conductor workspace + fixed FO-boot message per ready task with a claim fence, and a poll that reads the state branch for a prepared gate before falling back to the session transcript. `docs/ship/README.md` is re-commissioned to the five-stage route with an `Integrated head` Local Profile row. A background review caught a real defect (shell values interpolated into `python3 -c` source, breaking on a slug containing a quote) and a second pass on my own found the quota check reading whole-transcript instead of tail-only; both are fixed with falsifiers proving the before/after behavior change, not just a pass count.

## Stage Report: validation

- DONE: AC-1, AC-2, AC-4, AC-5 reproduce from the recorded commands with the recorded exit codes in a fresh checkout of candidate 8b27fae1
  Fresh `git clone` + `checkout 8b27fae190a5f09fdd3fe41fce1d65692ac20585` at `/tmp/ship-validation/fresh-8b27fae1` (not the worktree that authored the commits). `dispatch.test.sh` 6/6 PASS, `watch.test.sh` 6/6 PASS. `local-profile-check.py docs/ship/README.md` → `LOCAL_PROFILE_OK: 9 required rows present` exit 0; with the `Integrated head` row deleted → `LOCAL_PROFILE_MISSING_ROW: Integrated head` exit 1. Pin mismatch (edited `pins/conductor-cli.txt` first line) run directly (not via test harness) against the real `docs/dev`: both `dispatch.sh ship-cloud-wrapper --dry-run` and `watch.sh ship-cloud-wrapper --once` print only `conductor cli changed: read the diff, then re-pin` and exit 5 — no other line, so no other `conductor` call happened first.
- DONE: the quote-slug falsifier fails at ba9daeb7 and passes at 8b27fae1
  Case f (and its fixtures) did not exist as of `ba9daeb7`; introduced in the same commit as the fix. Backported `dispatch.test.sh`/`watch.test.sh` + `fixtures/` from `8b27fae1` onto a fresh `ba9daeb7` checkout's own `dispatch.sh`/`watch.sh` (unmodified) and ran the suites: both report `SyntaxError: unterminated string literal (detected at line 4)` and case f FAILs (`dispatch.test: 2 passed, 4 failed`, `watch.test: 2 passed, 4 failed` — cases b/e cascade-fail too, sharing the polluted fixture). At `8b27fae1` case f PASSes in both suites (part of the 6/6 above), same fixture, same slug.
- DONE: at least one mutation per script the suites must catch, and one they must not
  `dispatch.sh` must-catch: reverted the argv pass-through (interpolated `$slug`/`$existing_copy` straight into the `python3 -c` source) → `dispatch.test: 2 passed, 4 failed`, case f fails with the identical `SyntaxError`. `dispatch.sh` must-not-catch: added a comment + an aliased `here=$script_dir` local, no behavior change → `dispatch.test: 6 passed, 0 failed`. `watch.sh` must-catch: quota regex read `transcript` instead of tail-only `last_block` → `watch.test: 5 passed, 1 failed`, case e fails (`task-resumed-after-quota` now reads `quota` instead of `stopped`). `watch.sh` must-not-catch: renamed local `session_id`→`sid` + comment, no behavior change → `watch.test: 6 passed, 0 failed`. All four mutations reverted; working tree confirmed byte-identical to the fetched commit after each (`diff` against a saved pre-mutation copy, and `git status --short` clean).
- DONE: the generated FO boot message carries exactly the three design-spec instructions and nothing that re-implements a dev-flow per-task mechanism
  Ran `dispatch.sh ship-cloud-wrapper --dry-run --workflow-dir <repo>/docs/dev --project-id <dummy>` (read-only against the real `docs/dev`; `--dry-run` prints argv and never calls `conductor workspace create`) and read the generated `ship-cloud-dispatch-and-watch.boot.md`. Its three numbered steps ("Become the first officer... `spacedock claude`... `spacedock state init`"; "Run that entity through its route to a prepared `validation` gate (`spacedock gate prepare`); deliver the Draft PR through the `pr-merge` mod..."; "Stop at the gate. Do not merge. Push every state change...") match `docs/dev/.spacedock-state/ship-cloud-dispatch-and-watch/design/2026-09-10-ship-flow-cloud-wrapper-design.md (on spacedock-state/dev)`'s (found on branch `docs/ship-flow-cloud-wrapper-spec`) `boot.md` section verbatim in substance and count — no acceptance, review, disposition, or merge logic is embedded.
- SKIPPED: AC-3 (the real dispatch of the other two sprint tasks reaching a prepared validation gate)
  Real cloud run is the First Officer's action after the Captain approves the sibling tasks' backlog gates. No Conductor workspaces were created and nothing was pushed to any ship state branch during this stage — the only Conductor calls made were `--version`/`--help`/`auth whoami` (via the pin-check and dry-run paths) and one read-only `--dry-run` against the real `docs/dev`, none of which create a workspace or session.

### Residuals (not fixed, flagged for the next stage/task)

- The `ba9daeb7` falsifier reproduction backported the newer test file + fixtures onto the older script rather than running `ba9daeb7`'s own committed test suite (which does not have case f yet) — the fairest same-SHA comparison available, but note it for anyone re-deriving this evidence.
- All test/mutation work ran in a scratch clone under `/tmp/ship-validation`, never in the assigned worktree or the state checkout, so the worktree remains at 8b27fae1 with a clean `git status` and there is nothing to commit for this stage's checklist items 1-2; only this report is new.

### Summary

Items 1, 2, and 4 of the completion checklist reproduce cleanly in a fresh 8b27fae1 checkout: all four fixture-based ACs pass with the recorded exit codes, the quote-slug regression is bisected precisely (fails pre-fix, passes post-fix), both scripts' guards are proven to actually gate behavior (one must-catch and one must-not-catch mutation per script), and the generated FO boot message matches the design spec's three instructions with no re-implemented per-task logic. AC-3 is explicitly out of scope for this stage per item 3 and is marked SKIPPED with no Conductor workspace created and no state-branch push.

### AC-3 — the real run, recorded by the First Officer (2026-09-10)

- DONE: `dispatch.sh ship-cloud-wrapper` (candidate 8b27fae1, run from /tmp/zb-verify with `--workflow-dir` and `--state-dir`) created two Conductor workspaces — `ship-remove-duplicated-stations` → 20c25f00 / session b2811dee, `ship-verify-uat-close` → 9081b7d7 / session abc9855f — with claim fences committed to `spacedock-state/ship` before each create; both cloud first officers reached a prepared `validation` gate with a Draft PR (#410 at e5c2df15, #411 at 3053f925), observed by `watch.sh --once` as `gate-prepared`.
  Questions asked by the workers and every answer sent are on `spacedock-state/ship` at `_ship_fence/ship-cloud-wrapper.questions.md` (5 rounds; one required the Captain to type "push it" into the session).

Findings from the run, for the next round (validation → implementation feedback):
1. `watch.sh` reports `stopped` while the workspace is still `initializing` (session already `idle`); it must read workspace state before session status.
2. `watch.sh` reports `stopped` when the session flickers to `idle` while the FO's own subagent runs; `idle` is a candidate signal only, the transcript tail decides.
3. `watch.sh`'s question heuristic missed two of three real questions (they did not end in `?`); it fired once.
4. The boot message carries no sender identity or dispatch token, so a worker treated the FO's later answer as an injection until the senderId was pointed out.
5. The boot message carries no Captain conn for the push; one worker refused `git push` under the pr-merge mod's "captain-approved push" rule until the Captain typed the line into the session. The Captain's verbatim batch approval must ride in the boot message as `conn-quote`/`conn-source`.
6. State-branch sync from a shared checkout with a peer's dirty file fails; the FO's replay rewrote two commits that gate records pinned (recovered under `spacedock-state/dev-recovery-*` refs). dispatch.sh/watch.sh need their own state worktree or a no-replay path.
