---
title: "The journey canvas is unreachable from anywhere but the machine it runs on"
status: ideation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-remote-access
sprint-readiness: ready
started: 2026-09-14T10:09:25Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: bxhtchz8rwth9hpeepzwg42t
gates:
    version: 1
    records:
        - id: gate:bxhtchz8rwth9hpeepzwg42t:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:bxhtchz8rwth9hpeepzwg42t-backlog-1
              briefing:
                id: briefing:bxhtchz8rwth9hpeepzwg42t:backlog:attempt-1:revision-1
                digest: sha256:007faf1e65a7bcea86cc524eb49c563d28ff89b0e12b1ad3cc2389a8a31c4a0f
                room-ref: ./journey-canvas-unreachable-from-another-machine/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:bxhtchz8rwth9hpeepzwg42t:backlog:1
                briefing: briefing:bxhtchz8rwth9hpeepzwg42t:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T10:08:35.846834Z"
                decision: approve
                reason: Captain approved in chat 2026-09-14 with 「Pilot」 to the FO's recommendation, after the FO verified all three causes against the working tree and corrected the report's inaccurate hard-coded claim. Pilot rather than POC because the fix shape is not in doubt but its proof is a cross-machine run, which is an evidence round rather than a one-shot exploration. The loopback-only document API bind is held as an accepted-outcome property, not an implementation detail.
              application:
                target-stage: ideation
                state: consumed
---

A user ran the journey canvas on a remote VM, was handed a URL by the agent, and could not open
the board from their own machine (reported to the Captain 2026-09-14). Three separate causes stack,
and the report named two of them.

* `kc-journey-map/vite.config.mts` sets only `server: { port: 3737 }`. With no `server.allowedHosts`,
  Vite rejects a request whose Host header is anything but a loopback name or a bare IP, so the page
  never loads under the VM's hostname. The `canvas` npm script already passes `vite dev --host`, so
  the listener is exposed; only the host check refuses.
* `server/client/App.tsx` derives `SERVER_URL` from `import.meta.env.VITE_JOURNEY_API_URL` and falls
  back to `http://localhost:5858`. It is not hard-coded as the report states, but the default sends
  the viewer's browser at the viewer's own machine, and `useSync` builds its socket URI from it
  (`${SERVER_URL}/connect/${roomId}`), so the board renders empty.
* Not named in the report, and the reason the reporter's own fix works: `server/canvas-server.ts`
  calls `app.listen({ port: PORT, host: '127.0.0.1' })`. The document API is loopback-only, so no
  value of `VITE_JOURNEY_API_URL` pointing at port 5858 is reachable from outside the VM. Proxying
  `/connect` through the Vite server is what routes around that bind from inside the VM.

## Accepted outcome

A journey canvas started on a remote machine opens and syncs from another machine over the URL the
agent hands out, with no environment variable the operator has to discover. The document API keeps
its loopback-only bind; reachability comes from the frontend the operator already exposes, not from
opening a second port.

## Non-goals

* Authentication, TLS, or any access control on the canvas.
* Binding the document API to a non-loopback interface.
* A hosted or multi-tenant deployment mode.
* Any change to PR #440, PR #441, or the Mermaid sequence companion.

## Acceptance criteria

* **AC-1** With the canvas started on host A, a browser on host B opens the board over host A's
  hostname and the board renders its shapes, with no `VITE_JOURNEY_API_URL` set. Evidence is a
  two-machine run or an equivalent isolation that does not resolve to loopback, named in the receipt.
* **AC-2** The sync socket connects and an edit made on host B appears on host A, proving the
  `/connect` path works end to end and not merely that the page loads.
* **AC-3** `server/canvas-server.ts` still binds `127.0.0.1`; a direct request to the document API
  port from outside the machine is refused. A mutation that widens the bind is not the accepted fix.
* **AC-4** `VITE_JOURNEY_API_URL`, if still supported, keeps its current meaning for an operator who
  sets it; if it is removed, the removal is named and nothing in the repository still references it.
* **AC-5** `node --test lib/*.test.mjs`, `bash scripts/canvas-smoke.sh`, and `npm run typecheck`
  pass. `canvas-smoke.sh` still starts and reaches the API on loopback.
* **AC-6** The `allowedHosts` value is justified in one sentence: what it admits and why that is
  acceptable for a local development tool that carries no authentication.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    A real user hit this on a remote VM and could not open the board at all.
    The fix shape is not in doubt, but its proof is a cross-machine run: a page
    that loads on one host proves nothing about a sync socket reaching another.
    That is an evidence round, not a one-shot exploration. Scope stays inside
    this package's own dev-server wiring; no consumer migrates.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep the document API bound to 127.0.0.1; reachability comes from the exposed frontend.
      - Do not add authentication, TLS, or an access-control surface to a local development tool.
    implementation:
      - The board opens over a non-loopback hostname with no environment variable set.
      - The sync path reaches the document API from inside the machine, not across the network.
      - Name the decision on VITE_JOURNEY_API_URL — kept with its current meaning, or removed cleanly.
    testing:
      - Two machines, or an equivalent that does not resolve to loopback.
      - An edit on the remote viewer appears on the host, not merely a page that renders.
      - A mutation widening the API bind is rejected, not accepted as the fix.
      - Existing model tests, canvas smoke, and the new typecheck still pass.
  scope_boundary: >-
    kc-journey-map's vite config, client sync URL derivation, and the dev-server
    proxy only. Excludes authentication, TLS, hosted or multi-tenant modes,
    binding the document API off loopback, and PR #440 / PR #441.
  semantics_unchanged: false
  promote_when:
    - The canvas is exposed to an untrusted network or beyond the operator's own machines.
    - Any access control, credential, or tenancy boundary is accepted.
```
