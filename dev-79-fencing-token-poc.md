---
title: "POC: fencing token for ship-flow holder handover — exactly-once dispatch across laptop sleep"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-79
pr:
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

Not yet measured.
