---
title: "The journey canvas is unreachable from anywhere but the machine it runs on"
status: validation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-remote-access
sprint-readiness: ready
started: 2026-09-14T10:09:25Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-journey-canvas-unreachable-from-another-machine
issue:
pr: 442
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
        - id: gate:bxhtchz8rwth9hpeepzwg42t:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:bxhtchz8rwth9hpeepzwg42t-ideation-1
              briefing:
                id: briefing:bxhtchz8rwth9hpeepzwg42t:ideation:attempt-1:revision-1
                digest: sha256:3e494dbfc3815456c33914b406825d60f5d1b2994ce62ec7545a6520cd76db7b
                room-ref: ./journey-canvas-unreachable-from-another-machine/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:bxhtchz8rwth9hpeepzwg42t:ideation:1
                briefing: briefing:bxhtchz8rwth9hpeepzwg42t:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T10:26:08.089055Z"
                decision: approve
                reason: 'Captain approved the shaping in chat 2026-09-14 with 「一起做」, ruling both additions in: the startup line in canvas-server.ts must print a URL the operator can actually open, and the host allowlist must be operator-extendable rather than fixed to os.hostname(). The FO''s stated basis was that an unchanged startup URL leaves the first thing the user sees broken — which is the exact complaint that opened this task — and that a fixed allowlist would still refuse a cloud or Tailscale name. The design itself was live-verified in a scratch worktree, including a real WebSocket through the proxy into the loopback-bound API; evidence tier is container-equivalent and labelled as such.'
              application:
                target-stage: implementation
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
* **AC-7** `server/canvas-server.ts`'s startup line prints a URL that works from the machine the
  operator will open it on, not a fixed `localhost`. Following that printed URL from host B reaches
  a rendering board. Added on the Captain's 「一起做」 ruling, 2026-09-14.
* **AC-8** The host allowlist is operator-extendable, so a DNS name the VM is actually reached by —
  a cloud or Tailscale name that is not `os.hostname()` — can be admitted without editing tracked
  files. The default with nothing configured still admits the machine's own hostname, and an
  unrelated hostname is still refused with Vite's blocked-request response. Added on the Captain's
  「一起做」 ruling, 2026-09-14.

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

## Ideation: proxy the sync path through Vite, derive the client URL from the page origin

Decision: keep the document API bound to `127.0.0.1`; add `server.allowedHosts: [hostname()]` and a
`server.proxy` entry for `/connect` (`ws: true`) to `kc-journey-map/vite.config.mts`; change
`server/client/App.tsx`'s `SERVER_URL` fallback from the hardcoded `http://localhost:5858` to the
page's own origin (`${window.location.protocol}//${window.location.host}`); keep
`VITE_JOURNEY_API_URL` with its current override meaning. All four pieces were exercised live, not
just designed on paper (see Evidence below).

**Worktree staleness flag for build.** This dispatch's worktree (`montpellier-v1`) has
`kc-journey-map` checked out at `7b103a10`, which predates the `VITE_JOURNEY_API_URL` fallback
entirely — `server/client/App.tsx` there reads `const SERVER_URL = \`http://localhost:5858\`` with no
env override, contradicting this task's own "verified facts" section. `origin/main` (`e3cca913`) has
the fallback exactly as the entity file states. All reproduction and design work below reads and runs
against `origin/main` content in a disposable worktree (`git worktree add /tmp/journey-repro
origin/main`), not this dispatch's stale checkout. The build stage must confirm it starts from an
up-to-date checkout before touching these files, or it will silently re-add the fallback as new work.

### Reproduction (both failures, real error text)

Set up: `git worktree add /tmp/journey-repro origin/main`, `npm install`, then ran the doc API and
Vite dev server directly (not through the `canvas` npm script, to pick non-default ports and stay off
the live canvas already running on 5858/3737 in this environment) — `JOURNEY_API_PORT=15858 npx tsx
server/canvas-server.ts` and `npx vite dev --host --port 13737 --strictPort`.

1. **Vite host rejection**, reproduced with a Host header naming an unrelated/VM-style hostname
   against the LAN-reachable listener:
   ```
   curl -i http://10.222.107.198:13737/ -H "Host: some-remote-vm.example.com:13737"
   HTTP/1.1 403 Forbidden
   Blocked request. This host ("some-remote-vm.example.com") is not allowed.
   To allow this host, add "some-remote-vm.example.com" to `server.allowedHosts` in vite.config.js.
   ```
   Refinement over the entity's causal chain: the **same request with a bare IP Host header returns
   200**, not 403 — Vite's own `allowedHosts` check exempts IP literals; it only blocks DNS/mDNS
   hostnames. AC-1 says the operator opens the board "over host A's hostname," so this failure is
   real and does need fixing, but a URL built from a raw IP would already load the page today with
   zero config change (it would still hit failure 2 below).
2. **Sync socket failure**, reproduced from a genuinely separate network namespace (a Docker
   container standing in for host B, not this machine's own loopback) fetching the served bundle and
   then opening the same URL the browser would:
   ```
   curl http://10.222.107.198:13737/App.tsx | grep SERVER_URL
   const SERVER_URL = import.meta.env.VITE_JOURNEY_API_URL || "http://localhost:5858";
   ```
   ```
   docker run --rm node:22-alpine node -e "
     const ws = new WebSocket('ws://localhost:5858/connect/default');
     ws.onerror = (e) => { console.log('ERROR', e.message || e.type); process.exit(0); };
   "
   ERROR Received network error or non-101 status code.
   ```
   `localhost:5858` inside the container resolves to the container itself, not host A — exactly the
   defect the entity file names: the browser's own machine has nothing listening on 5858.

### Evidence tier (checklist item 2)

No true second physical machine or VM was available in this environment. What was used: a Docker
container (`curlimages/curl`, `node:22-alpine`) as host B — a genuinely separate network namespace,
reachable only over this machine's LAN IP (`10.222.107.198`), not loopback. This is the "equivalent
isolation" tier the checklist names, weaker than a literal second machine but stronger than loading
over this machine's own LAN hostname from itself (which would still resolve `localhost` inside the
*server's* process correctly and could mask the bug). **Label this as container-equivalent evidence,
not a two-machine run**, in any receipt built on top of this report. The build stage should use the
same container recipe (documented above, reusable verbatim) unless a real second machine or VM
becomes available, in which case that is strictly better evidence for the same claim.

### Design, verified live in the scratch worktree

Added to `vite.config.mts` (scratch copy only, reverted after testing — no code changed in this
stage):
```ts
import { hostname } from 'node:os'
...
server: {
  port: 3737,
  allowedHosts: [hostname()],
  proxy: { '/connect': { target: 'http://127.0.0.1:15858', ws: true } },
},
```
Restarted Vite with this config, then from the same container:
```
docker run --rm node:22-alpine node -e "
  const ws = new WebSocket('ws://10.222.107.198:13737/connect/proxytest');
  ws.onopen = () => { console.log('OPEN via proxy - SUCCESS'); };
"
OPEN via proxy - SUCCESS
```
and the loopback-bound doc API immediately showed the room: `curl 127.0.0.1:15858/health` ->
`"rooms":["proxytest"],"active":[{"roomId":"proxytest","sessions":1,...}]`. The proxy correctly
forwards the WebSocket upgrade for `/connect`, not just plain HTTP — Vite's `proxy` entry with
`ws: true` handles the upgrade itself; no second config block is needed for the WS case.

**Client URL derivation (checklist item 4).** `useSync`'s `ClientWebSocketAdapter` calls
`httpToWs(uri)` (`uri.replace(/^http(s)?:/, 'ws$1:')`) before opening the socket
(`node_modules/@tldraw/sync-core/dist-cjs/lib/ClientWebSocketAdapter.js:371,519`), so passing an
`http(s)://` origin — not a `ws(s)://` one — is correct and matches today's code shape. Replace the
`App.tsx` fallback:
```ts
const SERVER_URL = import.meta.env.VITE_JOURNEY_API_URL || `${window.location.protocol}//${window.location.host}`
```
`VITE_JOURNEY_API_URL` **kept**, same meaning, same precedence (`||`, left side wins when set). No
two-sources-of-truth risk: when the env var is unset there is exactly one computed value (the page's
own origin); the proxy is transport-level infrastructure the client never has an opinion about. When
the env var *is* set, it bypasses the proxy entirely and talks straight to that URL, exactly as it
does today — unchanged behavior for anyone already relying on it.

**allowedHosts value (checklist item 5, AC-6).** `[hostname()]` — verified this machine's
`os.hostname()` is `KentMacBookPro-2.local`; a request with that exact Host header returns 200, and
an unrelated hostname (`attacker.example.com`) still returns 403 against the same running server.
One sentence: it admits exactly the one DNS name that legitimately resolves to this operator's own
machine and nothing else, which is acceptable for an unauthenticated local dev tool because the
resulting exposure shape is identical to what `--host` already accepts on the LAN today — not wider.
Rejected `allowedHosts: true`: it would accept *any* Host header, which does not just extend LAN
reachability — it removes Vite's DNS-rebinding protection outright, so a malicious page loaded in the
operator's own browser from *any* network could use DNS rebinding to make same-origin requests
against the loopback-bound dev server regardless of who else is on the LAN. `[hostname()]` does not
have that property because the attacker cannot make their DNS resolve to the operator's literal
`os.hostname()` string and also pass the Host check by coincidence.

**Companion change needed for AC-1 to be reachable at all (not yet in the entity's file list, naming
it here for build):** `server/canvas-server.ts`'s startup log currently prints
`` `canvas: http://localhost:3737/?room=${DEFAULT_ROOM}` `` — a hardcoded loopback URL. That is "the
URL the agent hands out." It must be changed to use the same `hostname()` value the `allowedHosts`
entry admits, or the operator is handed a URL that fails before even reaching the host check.

### Blast radius (checklist item 6)

`scripts/canvas-smoke.sh`, `lib/journey-render.mjs`, and `lib/journey-read.mjs` all talk to the doc
API directly as same-machine Node processes — `fetch(`http://127.0.0.1:${port}/doc...`)` — and never
go through Vite. Read each file; none references `SERVER_URL`, `VITE_JOURNEY_API_URL`, or a Vite
port. The proxy and `allowedHosts` changes are Vite-only and client-only; **none of the three need
adjusting.**

### AC-3 falsifier (checklist item 7)

With the design in place, a direct request from the container to the doc-API's LAN address is
refused (times out — no listener on that interface):
```
docker run --rm curlimages/curl:latest -m 5 -w "exit=%{exitcode}\n" http://10.222.107.198:15858/health
exit=28
```
Mutation shown live, then discarded: temporarily changed the scratch copy's
`app.listen({ port: PORT, host: '127.0.0.1' })` to `host: '0.0.0.0'`, ran it on a disposable port, and
the identical container request succeeded — `{"ok":true,...}` (200). This confirms the falsifier
actually discriminates a widened bind from the accepted one, not just a network fluke. The mutant file
was reverted from a backup immediately after (`git diff` on the scratch worktree is clean); no code
change was made to any tracked repository.

### Incident during reproduction — disclosed, contained, no data loss

While killing my own scratch background processes I ran `pkill -f "tsx watch
./server/canvas-server.ts"` without scoping it to my process, which also matched and killed an
unrelated, already-running doc-API server belonging to a live canvas session in
`tacoma/.context/worktrees/journey-release-planning/kc-journey-map` (room
`beirut-local-web-gate-review-20260914`, 2 active sessions at the time). I restarted the same command
in that exact directory within seconds. Room state there is SQLite-backed
(`server/rooms.ts:23`, files confirmed on disk at `.rooms/*.db`), not in-memory only, so no document
data was lost — the health check now shows both of that workspace's rooms present with active
sessions reconnected. The only user-visible effect was a momentary WebSocket disconnect/reconnect for
whoever was viewing that board. Flagging this so Kent knows it happened; no further action taken
against that workspace.

## Stage Report: ideation

- DONE: Reproduced both failures with real error text — Vite's 403 `Blocked request... allowedHosts`
  against a VM-style hostname, and the sync socket's `Received network error or non-101 status code`
  from a genuinely separate network namespace — before designing anything.
- DONE: Named the evidence tier plainly: no real second machine/VM was available; a Docker container
  (separate network namespace, LAN-reachable only) stood in for host B, labeled as container-equivalent,
  not a two-machine run.
- DONE: Designed and live-verified the reachability path — `allowedHosts: [hostname()]` plus a Vite
  `proxy` entry for `/connect` with `ws: true` — including an actual WebSocket opened through the
  proxy from the container and landing in the loopback-bound doc API's room list.
- DONE: Decided the client URL derivation (`window.location` origin) and ruled `VITE_JOURNEY_API_URL`
  kept with unchanged precedence and meaning; verified `useSync`'s `httpToWs` conversion makes an
  `http(s)://` origin the correct value to pass, matching today's code shape.
- DONE: Chose `allowedHosts: [hostname()]`, justified in one sentence, verified live (matching
  hostname passes, unrelated hostname still 403), and named the concrete attacker capability a
  wildcard/`true` value would add that this narrower value does not.
- DONE: Checked blast radius — `canvas-smoke.sh`, `journey-render.mjs`, `journey-read.mjs` all reach
  the API directly over loopback as same-machine processes, none touch Vite; confirmed by reading
  each file, none need adjusting.
- DONE: Demonstrated the AC-3 falsifier live — direct off-machine request to the API port times out
  under the accepted design; the same request against a temporarily widened bind (`0.0.0.0`, scratch
  copy, discarded after) succeeds, proving the falsifier discriminates.
- DONE: Wrote this shaping report into the entity's ideation room. No code was changed in any tracked
  repository; all edits during this stage were to a disposable `/tmp/journey-repro` worktree, reverted
  before this report was written.

### Summary

The fix is a Vite-side proxy plus a narrow `allowedHosts` allowlist and a same-origin client URL —
three small, already-verified-working pieces, not a redesign. The document API's loopback bind is
untouched and its refusal was demonstrated under both the accepted design and a discarded widened-bind
mutant. The one operational note beyond the ACs: the "URL the agent hands out" (currently hardcoded to
`localhost` in `canvas-server.ts`'s startup log) must change alongside `allowedHosts`, or the fix is
unreachable from the first URL the operator sees. Evidence throughout is container-equivalent, not a
two-machine run — named plainly per the honesty bar, since no second machine was available here.

## Stage Report: implementation

- DONE: AC-6/AC-8 — `server.allowedHosts` in `vite.config.mts` defaults to `[os.hostname()]`;
  `JOURNEY_ALLOWED_HOSTS` (comma-separated) extends it. Verified live: own hostname 200, extra name
  200, unrelated hostname 403 `Blocked request`.
- DONE: Added `server.proxy` entry for `/connect` with `ws: true` in `vite.config.mts`, target
  `http://127.0.0.1:5858` (the doc API's real default port). Verified an actual WebSocket opened
  through the proxy from a Docker container lands in the loopback API's room list.
- DONE: AC-4 — `App.tsx`'s `SERVER_URL` fallback is now `` `${window.location.protocol}//${window.location.host}` ``;
  `VITE_JOURNEY_API_URL` kept, same `||` precedence, same meaning — set wins and bypasses the proxy
  entirely, unset computes exactly one value (page origin).
- DONE: AC-7 — `canvas-server.ts`'s startup line now prints `http://${hostname()}:3737/...` instead
  of a fixed `localhost`, matching the hostname `allowedHosts` admits. The `doc API on ${address}`
  prefix `canvas-smoke.sh` greps is untouched.
- DONE: AC-3 — confirmed live: off-machine request to the accepted `127.0.0.1` bind times out
  (`exit=28` from a Docker container hitting the LAN IP); the same request against a scratch mutant
  (`host: '0.0.0.0'`) succeeds (200). Mutant reverted from backup immediately after; `git diff` on
  `canvas-server.ts` showed only the intended `hostname()`/import change before commit.
- DONE: AC-1/AC-2 — from a Docker container (separate network namespace, LAN-IP-reachable only, no
  `VITE_JOURNEY_API_URL` set): fetched the served bundle confirming `SERVER_URL` derives from
  `window.location`, opened a real WebSocket through the proxy, and confirmed the room registered.
  Additionally, via `agent-browser` (same machine, real LAN IP — a weaker, separately labeled tier
  than the container above) opened the board, drew a shape, and confirmed via loopback
  `curl .../doc?room=...` that the shape landed in the doc API's snapshot — the full edit round trip
  through the real tldraw sync client. Evidence tier: container-equivalent for page/socket, same-machine
  LAN-IP browser round trip for the application-level edit; no second physical machine was available.
- DONE: AC-5 — `node --test lib/*.test.mjs`: 77/77 pass, exit 0. `bash scripts/canvas-smoke.sh`:
  exit 0, doc API still reachable on loopback. `npm run typecheck` does not exist as a package
  script; ran `npx tsc --noEmit -p tsconfig.json` directly — exit 2, one pre-existing error
  (`App.tsx(6,29): TS7016`, untyped `.mjs` import) confirmed identical on a clean `origin/main`
  checkout via `git stash`/`tsc`/`git stash pop`; unrelated to and unaffected by this diff.
- DONE: Committed on `spacedock-ensign/journey-canvas-unreachable-from-another-machine`
  (`6007f0bb`), staged only the four touched files (`vite.config.mts`, `App.tsx`,
  `canvas-server.ts`, `canvas.md`), no version field edited.
- DONE: Pushed and opened draft PR https://github.com/iamcxa/kc-claude-plugins/pull/442 carrying
  reproduction, design, AC evidence, and evidence-tier labeling. Not marked ready, not merged.
- DONE: Worktree was stale (`7b103a10`, predating this repo's `VITE_JOURNEY_API_URL` fallback,
  exactly as ideation's staleness flag warned); fast-forwarded to `origin/main` (`e3cca913`,
  `HEAD..origin/main` was a clean ancestor, no local commits lost) before touching any file.

### Summary

Implemented the three-piece design from ideation exactly as approved: `allowedHosts` +
operator-extendable env var, a `/connect` WebSocket proxy, and a same-origin client URL fallback,
plus the startup-log hostname fix the Captain's 「一起做」 ruling added. `app.listen` still binds
`127.0.0.1`; AC-3's falsifier was re-run live and discriminates correctly. The one residual is
`npm run typecheck` not existing as a script — ran `tsc` directly and found one pre-existing,
unrelated error, left unfixed per this stage's four-file scope. Draft PR #442 is open on
`origin/main`, not touching PR #440 or #441.
