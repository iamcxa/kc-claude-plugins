---
title: "Intent-commit fencing: at-most-one worker across holder handover, adopt-or-block reconcile"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started: 2026-09-03T07:55:00Z
completed:
verdict:
worktree:
issue: DEV-84
pr:
mod-block:
id: wxj20tk9h1ndssnehwd4d9ng
gates:
    version: 1
    records:
        - id: gate:wxj20tk9h1ndssnehwd4d9ng:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:wxj20tk9h1ndssnehwd4d9ng-backlog-1
              briefing:
                id: briefing:wxj20tk9h1ndssnehwd4d9ng:backlog:attempt-1:revision-1
                digest: sha256:64974db207fd460a9122ad415bd55b8e6315722a9484b7f76c255f5b256a5cad
                room-ref: ./dev-84-intent-commit-fencing/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:wxj20tk9h1ndssnehwd4d9ng:backlog:1
                briefing: briefing:wxj20tk9h1ndssnehwd4d9ng:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T07:58:01.724962Z"
                decision: approve
                reason: Captain admitted DEV-84 as a standalone Pilot in sprint S9 and authorized the local FO to execute it.
                conn:
                    quote: 好，由1繼續
                    source: Captain chat, this conversation, 2026-09-03, choosing item 1 (intent-commit fencing) as the next step
              application:
                target-stage: ideation
                state: consumed
---

## The problem

DEV-79 proved that a writer-number fence on the state branch stops a resumed stale holder from persisting a claim, but not from the `conductor workspace create` it had already sent: process A slept after the create returned and before persisting, process B took over and created a second workspace, and A's workspace stayed on Conductor as an orphan. Codex round 4 (DEV-79 evidence) ruled check-act-check unsound for external effect and named the contract that can hold: commit a durable intent before the external call, make the new holder reconcile by dispatch token and adopt-or-block, and never create a second workspace for an unresolved intent. Nothing in the repository implements that order, and it is the last blocker before plan-flow and ship-flow can be commissioned.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: Two repo-local scripts plus one README sentence used by this repository's own ship First Officer; limited real use, no adopter-visible contract, release, or rollback obligation.
  obligations:
    architecture: [Intent file on the state branch committed before any Conductor call; reconcile adopts by token or blocks; no lease]
    implementation: [Add scripts/ship-flow/intent.sh, rewire fenced-dispatch.sh to require a committed intent and name workspaces with the token, one README sentence, one contract-test pin]
    testing: [DEV-79 falsifier re-run ends with one adopted workspace; late-arrival variant blocks then adopts; --no-intent produces two workspaces; README pin seen to fail]
  scope_boundary: No lease or unattended failover, no Conductor or spacedock change, no real Issue dispatched, no Linear write.
  semantics_unchanged: true
```

## Accepted outcome

`scripts/ship-flow/holder.sh` and a new `scripts/ship-flow/intent.sh` implement the order intent-commit -> check -> create once -> token read-back -> check -> adopt/persist. An intent is a file on the state branch keyed by claim name carrying the dispatch token and writer number, committed and pushed before the create call; `fenced-dispatch.sh` refuses to call `conductor workspace create` without a committed intent for the claim and names every probe workspace `<claim>-<token>`. On handover the new holder runs `intent.sh reconcile`: for each intent without a persisted workspace id it lists Conductor workspaces whose name carries that token, adopts exactly one (persists its id under the intent), blocks with `ambiguous intent` on two or more, and blocks with `unresolved intent` on zero rather than creating. The DEV-79 falsifier (A creates, SIGSTOP before persist, B handover, B dispatches, A SIGCONT) now ends with exactly one workspace adopted under the one intent, B having created nothing, and A refused before any external action. The honest guarantee stated in the ship-flow runtime README is "at most one automatically started worker; an uncertain create blocks and asks the Captain", not exactly-once.

Falsifier and stop: B creates a workspace while an unresolved intent exists; or A's in-flight create lands after B's reconcile and is not found by a second reconcile; or two intents exist for one claim.

## Non-goals

- No lease or unattended failover; handover stays a human command.
- No change to Conductor, spacedock, the kernel, or kc-dev-flow scripts.
- No real Issue dispatched; probe workspaces are archived at cleanup.
- No Linear write.

## Acceptance evidence

- **AC-1** `intent.sh commit|reconcile|adopt` exists; `fenced-dispatch.sh` exits 2 with `no committed intent` when invoked without one; the run is recorded.
- **AC-2** The DEV-79 falsifier re-run: exactly one Conductor workspace whose name carries the intent token exists at the end, its id is persisted under the intent by B's reconcile, B's own create was never called (log shows `adopted` not `created`), and A's post-resume check logs `fenced` before any Conductor call. Logs recorded.
- **AC-3** The late-arrival variant: B reconciles before A's create is visible (simulated by delaying A's create with a wrapper), B blocks with `unresolved intent` and creates nothing; a second reconcile after A's create lands adopts it. Logs recorded.
- **AC-4** The without-it run: with intent-commit disabled (`--no-intent`), the same falsifier produces two workspaces; recorded.
- **AC-5** `docs/dev/README.md` `## Ship-flow runtime` states the at-most-one guarantee and the intent order; the contract test pins the sentence and reddens when it is removed; recorded.
- **AC-6** Cleanup recorded: probe workspaces archived, intents resolved or removed, holder record at its final writer number.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Dispatch 07:55Z, token acked 32 s. Round 0 (98c723f8) at ~08:34Z: FO without-it retained 0 / removed 1; blocked on `flock` absent on macOS. Round 1 (6573daaa) ~09:28Z: closed flock and count-filter; Codex opened three lock P1s. Cloud quota limit from ~09:30Z to 13:00Z (shared pool, S17/S18). Round 2 (a6ad0c49) after resend: trap-before-acquire and age-only stale closed; Codex keeps pid-only release and a theoretical TOCTOU open, neither reproduced by the FO's two-racer run on macOS. Active FO+worker time about 95 min across three rounds; the cap of two fix rounds held.

## Stage Report: implementation

- DONE: `intent.sh` (locked commit bound to project, base, message hash; fenced compare-and-swap adopt; reconcile adopt-or-block by exact name and project), `holder.sh` fail-closed, `fenced-dispatch.sh` intent-before-create with private message copy and read-back by id, README paragraph and three contract-test pins. Candidate a6ad0c49 on the FO-authored base 3f263c3b.
- AC-1 duplicate claim refused before any Conductor call (exit 4); AC-2 SIGSTOP falsifier ends with one adopted workspace, B created nothing, A fenced; AC-3 late arrival blocks then adopts; AC-4 intent skipped yields two workspaces; AC-5 README pin reddens on removal; AC-6 probes archived, holder at its final writer.
- Outside the Brief, for the Captain: release_lock compares pid only; stale takeover has a theoretical TOCTOU not reproduced; read-back is by workspace name via get-by-id rather than transcript. Commission-relevant limit: the guarantee is at most one create call per canonical claim; unattended failover needs a lease.

## Shape

Working perspective: bounded user-journey owner. The journey is one holder handover during an in-flight `conductor workspace create`. Seams: the state branch (git fetch/ff-merge/push as the only authority), the Conductor CLI (create, get by id, list by exact name), and two OS processes standing in for two hosts. Persistent state: `_holder.json` and `_intents/<claim>.json` on the state branch. Recovery: `intent.sh reconcile` adopts by exact name or blocks. Data safety: no real Issue, probe workspaces only, archived at cleanup. Stop numbers: two fix rounds after the first candidate; more than four probe workspaces alive at once; any falsifier that needs a change to Conductor or spacedock.

Deviation recorded: the First Officer authored the first two commits on this branch (0396916d, 3f263c3b) and ran AC-1 through AC-5 locally before the Captain corrected the seat. Those commits are the worker's starting point, not the worker's output; the worker owns every commit from here and re-verifies the FO-run ACs as its own evidence.

## Stage Report: ideation

- DONE: shape recorded above; Codex rounds 5 and 6 (evidence/codex-round5.md, codex-round6.md) reviewed the FO-authored candidate and left three commission blockers: no process lock around the shared state checkout for parallel claims; intent and read-back not bound to project, base, and message hash; README paragraph and AC-5 mutation to be re-established by the worker.
- NEXT: dispatch a cloud worker on branch head 3f263c3b with the Brief plus the three blockers as scope; the worker delivers one candidate with a fresh Evidence block; the FO verifies at the pinned SHA.

## Stage Report: implementation (in progress)

- Round 0 (98c723f8): lock via `flock`, intent bound to project/base/message hash, read-back by project. FO without-it retained 0 / removed 1; Codex one P2. Blocked on the FO host: `flock` is absent on macOS.
- Round 1 (6573daaa): portable mkdir lock, reconcile filters by project before counting. FO macOS LOCK falsifier: two parallel commits serialized, duplicate exit 4, no lock residue. Codex: both prior findings closed; three new P1 in the lock block (trap installed after acquire; pid-liveness stale rule not host-safe; rm -rf stale TOCTOU).
- Round 2 (final under the cap) dispatched with those three; the worker hit the Claude session usage limit before delivering (resets 2026-09-03T13:00Z). Workspace ad7f12c8 kept alive; the FO re-sends the same round-2 message after reset. No new dispatch.
