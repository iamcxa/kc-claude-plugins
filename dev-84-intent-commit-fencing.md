---
title: "Intent-commit fencing: at-most-one worker across holder handover, adopt-or-block reconcile"
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
                state: pending
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

Not yet measured.
