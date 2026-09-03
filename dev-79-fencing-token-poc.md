---
title: "POC: fencing token for ship-flow holder handover — exactly-once dispatch across laptop sleep"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started: 2026-09-03T03:20:00Z
completed:
verdict:
worktree:
issue: DEV-79
pr: local-merge:72f5c21
mod-block:
id: kw05rc5f26qkj8qxk5tcpzy4
gates:
    version: 1
    records:
        - id: gate:kw05rc5f26qkj8qxk5tcpzy4:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kw05rc5f26qkj8qxk5tcpzy4-backlog-1
              briefing:
                id: briefing:kw05rc5f26qkj8qxk5tcpzy4:backlog:attempt-1:revision-1
                digest: sha256:2e718d8e6246673f9a7b7f42f3d714ee4e8d88d595848d37c26f7d66412a39f8
                room-ref: ./dev-79-fencing-token-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kw05rc5f26qkj8qxk5tcpzy4:backlog:1
                briefing: briefing:kw05rc5f26qkj8qxk5tcpzy4:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T03:22:50.83987Z"
                decision: approve
                reason: Captain admitted dev-79-fencing-token-poc as a standalone item in sprint S9 and authorized its dispatch.
                conn:
                    quote: 現在派工，同意你的分工方式
                    source: Captain chat, this conversation, 2026-09-03, approving dispatch of DEV-78 to a cloud worker and DEV-79 to the local FO
              application:
                target-stage: ideation
                state: consumed
        - id: gate:kw05rc5f26qkj8qxk5tcpzy4:validation
          stage: validation
          attempts:
            - id: gate-attempt:kw05rc5f26qkj8qxk5tcpzy4-validation-1
              briefing:
                id: briefing:kw05rc5f26qkj8qxk5tcpzy4:validation:attempt-1:revision-1
                digest: sha256:7609c01e2deb4cc41a181f4c15a6ca32ea4280066a4ba38d3c49d63699ccc81b
                room-ref: ./dev-79-fencing-token-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kw05rc5f26qkj8qxk5tcpzy4:validation:1
                briefing: briefing:kw05rc5f26qkj8qxk5tcpzy4:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T03:33:29.344469Z"
                decision: approve
                reason: 'POC outcome change: writer fence proven for persistence, in-flight create escaped it, contract rewritten per Codex round 4 to intent-commit/adopt-or-block; candidate 72f5c215 retained on branch, PR creation stays a separate Captain decision.'
                conn:
                    quote: 現在派工，同意你的分工方式
                    source: Captain chat, this conversation, 2026-09-03, authorizing the DEV-79 POC run by the local FO; the POC's accepted outcome was the recorded decision, not a merge
              application:
                target-stage: done
                state: pending
---

## The problem

The ship-flow design says ship may run on an always-on host (holding only a Conductor API token and gh credentials) while plan stays on the Captain's laptop. The DEV-67 POC ran ship on the laptop; a 7-hour sleep gap showed workers and pushed candidates survive but the FO's poll loop dies. Codex round 3 (2026-09-03) ruled the holder-transfer design unsound: cloning the Spacedock state branch to another host does not transfer sole writer authority, and a laptop that wakes with its old loop still running can create a second workspace, a second claim, or a duplicate message before the git push conflict reveals the split. The prerequisite script `scripts/dev-flow-state-prereq.sh` requires a unique holder but has no notion of a holder changing. Nothing in the repository fences an old holder out.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: One disposable experiment with two local processes and one probe workspace proves whether a writer-number fence in the state branch yields exactly-once dispatch across a holder handover.
  poc_decision: Is a monotonically increasing writer number in the state branch, checked before every external action, sufficient for exactly-once dispatch when the old holder resumes after handover?
  poc_falsifier: The resumed old holder performs any external action; or two workspaces exist for one claim; or exactly-once needs a lock the state branch cannot express.
  poc_budget: Two probe workspaces at most, one FO hour, no real Issue dispatched
  poc_stop_when: The falsifier run completes once with the fence on and once with it off, or a falsifier hits
  poc_artifact: retained
  poc_safety_boundary: none
  poc_decision_ready_minutes: 60
  poc_decision_ready_reason: Two full falsifier runs each create and archive a cloud workspace at about 10 minutes apiece; the limit is their sum.
```

## Accepted outcome

A fencing token proves exactly-once dispatch across a holder handover. A holder record in the state branch carries a monotonically increasing writer number; every external action in ship (workspace create, message send, branch push, PR create) reads the record first and refuses when its own number is not the current one. A handover increments the number and pushes it before the new host acts. The decision is whether this is enough, on real Conductor and git, for the single commission falsifier: the laptop FO issues a workspace create, sleeps before persisting the returned id, an always-on host takes over with a new writer number, the laptop wakes and its loop resumes. The run must end with one workspace, one claim, one dispatch message, and the laptop refused before any external action, all observable from Conductor and the state branch.

Falsifier and stop: the laptop performs any external action after handover; or two workspaces exist for one claim; or the only way to reach exactly-once is a lock the state branch cannot express (then the design changes to a lease with expiry, and this POC records stop). The always-on host in this POC may be a second local process with its own clone of the state branch; it need not be a separate machine.

## Non-goals

* No Hermes, mini-dispatch, or cron integration; the always-on host is simulated by a second process.
* No change to spacedock, the kernel, or kc-dev-flow scripts beyond a new script under scripts/ship-flow/ and a holder record file in the state branch.
* No worker dispatch of real Issues; the workspace create in the falsifier is a probe workspace archived at cleanup.
* No Linear write.

## Acceptance evidence

* **AC-1 **`scripts/ship-flow/holder.sh claim|check|handover` exists; `check` exits 0 only when the caller's writer number equals the state branch's current number and exits 1 with `fenced` otherwise; the exit-1 run is recorded.
* **AC-2** The falsifier run is recorded: process A creates a workspace and is suspended (SIGSTOP) before writing the id; process B performs handover and dispatches; process A is resumed (SIGCONT); Conductor lists exactly one workspace for the claim and process A's next external action logs `fenced` and exits before calling Conductor.
* **AC-3** The same run with the fence disabled (a `--no-fence` flag or the check removed) produces two workspaces; the run is recorded as the without-it observation.
* **AC-4 **`poc_outcome` records proceed, change, or stop with minutes per station, and names whether a lease with expiry is required for the case where the laptop never wakes to release the holder.
* **AC-5** Cleanup recorded: probe workspaces archived, holder record left at the final writer number.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

AC-1 (claim, handover, fenced check on two state clones): 1 min. AC-2 (fence on, SIGSTOP before persist): 15 s wall, one probe workspace created by each process, A fenced after resume. AC-3 (fence off): 11 s, both processes persisted. Reconcile of A's orphan by claim name: 5 s. Total 8 min including probe archival. Candidate 72f5c2151e5c5d85c64ec7fc6d86520499f53b48.

## POC outcome

```yaml
poc_outcome:
  direction: change
  admitted_at: 2026-09-03T03:20:00Z
  decision_ready_at: 2026-09-03T03:29:00Z
  decision_ready_elapsed_seconds: 540
  captain_interventions_before_decision_ready: 0
  candidate: 72f5c2151e5c5d85c64ec7fc6d86520499f53b48
  evidence: >-
    A writer number committed on the state branch, fetched before every check,
    fences a resumed stale holder: with the fence on, process A (writer 3) created
    a probe workspace, was SIGSTOPped before persisting its id, process B took
    over (writer 4) and dispatched, and A on resume was refused before writing
    its claim (evidence/run-laptop.log, exit 3). With the fence off (AC-3) both
    processes persisted and two claim records exist for one name. Holder record
    ends at writer 6 (evidence/holder-final.json).
  strongest_limit: >-
    The fence gates persistence and later actions, not the create call that was
    already in flight when the holder slept: A's workspace 387f8506 existed on
    Conductor as an orphan. Exactly-once therefore needs a second half the design
    did not have: the new holder reconciles by listing Conductor workspaces by
    claim name and archiving any it did not persist (evidence/reconcile.txt shows
    this works; Conductor renames the second same-named workspace with a -v1
    suffix, which is the detection signal). No lease with expiry is needed for
    the laptop-never-wakes case because the old holder's number is simply never
    current again; a lease would only be needed to let a new holder take over
    without a human running handover.
  reversal_fact: >-
    A resumed stale holder performing any external action after handover, or a
    reconcile that cannot find an orphan by claim name.
  cleanup_status_at_decision: complete
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 60
  cleanup_status: complete
```

## Change returned to planning

Codex round 4 (evidence/codex-round4.md) overturned the first reading of this result: the fence protects the claim record, not the external effect. AC-2 produced two Conductor workspaces; the second check stopped A from persisting, not from creating. The contract returned to planning is therefore:

1. The honest guarantee is "at most one automatically started worker; an uncertain create blocks and asks the Captain", not exactly-once effect. Exactly-once needs an idempotent create or provider-side fencing that Conductor does not offer.
2. Order per external action: commit a durable pending intent (claim name, dispatch token, writer) -> check -> create once -> token read-back from the transcript -> check -> adopt and persist. A new holder that finds an unresolved intent reconciles only: it looks up by dispatch token, adopts the single matching workspace if one exists, blocks if ambiguous, and never creates a second.
3. Reconcile matches on the dispatch token carried in the workspace name and first message, never on Conductor's "-v1" duplicate-name suffix.
4. Planned handover drains first: the old holder stops issuing actions, waits for in-flight calls to return, then transfers. Crash handover follows the adopt-or-block rule above.
5. `dev-flow-state-prereq.sh` treats a fetch failure, non-fast-forward, malformed holder record, writer mismatch, or holder-id mismatch as distinct fail-closed exits.
6. Handover stays a human command; unattended failover needs a lease and is deferred.
7. Commission is blocked until 1-5 have a falsifier run: the same SIGSTOP scenario must end with one adopted workspace and one intent, not one persisted and one archived.
