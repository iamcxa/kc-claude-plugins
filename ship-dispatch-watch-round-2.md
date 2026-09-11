---
title: "ship-flow round 2: watch reads the right signals, the boot message carries identity and conn, and the Conductor CLI is a used-surface contract"
status: implementation
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
