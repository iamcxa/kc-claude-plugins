---
title: "ship-flow POC: dispatch one cloud first officer per dev task and watch the set to its validation gates"
status: ideation
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
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
---

kc-ship-flow re-implemented per-task acceptance, PR opening, review disposition and merging that
kc-dev-flow and Spacedock already own, and its dispatch station sent a hand-written message to one
ensign stage. The Captain's ruling (2026-09-10): ship is a wrapper over dev flow whose only job is
to send a set of planned dev tasks to Conductor cloud, watch the cloud first officers until they
finish, verify, and hand over one UAT; if Conductor cloud cannot run, ship cannot be used. Design:
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`.

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
