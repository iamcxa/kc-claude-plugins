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
        - id: gate:bxhtchz8rwth9hpeepzwg42t:validation
          stage: validation
          attempts:
            - id: gate-attempt:bxhtchz8rwth9hpeepzwg42t-validation-1
              briefing:
                id: briefing:bxhtchz8rwth9hpeepzwg42t:validation:attempt-1:revision-1
                digest: sha256:7c943f802d1984bf6c17c69e25ec3e20f549838b390e32cc090a0a0e9a2aef52
                room-ref: ./journey-canvas-unreachable-from-another-machine/review/validation/briefing-1
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

## FO findings at validation entry, PR #442 head

The validation ensign was dispatched with these two findings to resolve and terminated on a session
rate limit before reporting. The findings themselves are confirmed here from source by the FO, so
they survive the dispatch failure; the demonstrations the checklist asked for are still owed.

**F1 — the proxy target port is fixed while every sibling derives it.** `vite.config.mts` proxies
`/connect` to `http://127.0.0.1:5858`. `canvas-server.ts` reads
`Number(process.env.JOURNEY_API_PORT ?? 5858)`, and `lib/render.mjs`, `lib/read.mjs` and
`lib/journey-tldr.mjs` each build their API base as
`http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}`. The new proxy is the only place in the
package that hardcodes the port with no environment fallback, so a canvas started on any other port
serves a page whose sync path points at nothing. `references/canvas.md` documents running the client
against "a separate `JOURNEY_API_PORT` server", so this breaks a documented workflow rather than a
hypothetical one. `scripts/canvas-smoke.sh` sets `JOURNEY_API_PORT=0` but reaches the API directly
and never traverses the proxy, which is why CI stays green.

**F2 — the printed URL ignores the allowlist the operator configured.** `canvas-server.ts` prints
`http://${hostname()}:3737/...`. `JOURNEY_ALLOWED_HOSTS` exists precisely because `os.hostname()`
may not resolve from the viewer's machine, which is the reported failure. An operator who sets that
variable to a name that resolves is still handed the name that does not. AC-7 requires the printed
URL to work from the machine the operator will open it on.

Neither finding is a defect in the accepted design; both are in the implementation of it.

## Stage Report: implementation (cycle 2)

- DONE: Merged `origin/main` into the branch — not rebased. Brought in `0bbf6233` (PR #441:
  `typecheck` npm script, `typescript` devDependency, `lib/records.d.mts`) and one unrelated
  `kc-dev-flow` commit. Clean merge, no conflicts, nothing to favor either side on.
- DONE: F1 — `vite.config.mts`'s `/connect` proxy target now reads
  `` `http://127.0.0.1:${process.env.JOURNEY_API_PORT ?? 5858}` ``, matching `canvas-server.ts` and
  `lib/render.mjs`/`read.mjs`/`journey-tldr.mjs`. Demonstrated live: API started on port 25858
  (not 5858), Vite proxying to it on port 23737; a shape drawn via `agent-browser` against
  `localhost:23737` landed in the loopback API's `/doc` snapshot for that room (1 `geo` shape) —
  a synced shape, not just a loaded page.
- DONE: F2 — `canvas-server.ts` now prints the startup URL using `PRINT_HOST`, the first
  `JOURNEY_ALLOWED_HOSTS` entry when set, else `hostname()`. Quoted both cases from the running
  process: with nothing set, `doc API on http://127.0.0.1:25858  (canvas: http://MacBookPro.localdomain:3737/?room=default)`;
  with `JOURNEY_ALLOWED_HOSTS=my-tailscale-name.ts.net,extra2` set, `doc API on
  http://127.0.0.1:25858  (canvas: http://my-tailscale-name.ts.net:3737/?room=default)`.
- DONE: Frontend port `3737` duplication (`vite.config.mts` `port:`, `canvas-server.ts` startup
  line) left as-is. `3737` is already a hardcoded literal in half a dozen other places in the
  package outside this task's 4-file scope (`lib/doctor.mjs`, `lib/journey-export.mjs`,
  `lib/records.mjs`, `lib/journey-tldr.mjs`, the skill's example README) — unifying only these two
  would not actually prevent package-wide drift, so nothing keeps them from drifting except that
  the port has not changed since it was introduced; a future change needs a repo-wide grep for
  `3737`, not just these two files.
- DONE: Re-ran acceptance evidence on fresh, non-default ports (API 35858, Vite 33737,
  `JOURNEY_ALLOWED_HOSTS=verify-name.example`), all against a genuinely separate network namespace
  (Docker container, same recipe as ideation) plus a same-machine LAN-IP `agent-browser` pass for
  the application-level edit, matching the tiers the ideation/implementation stages already used —
  no second physical machine was available here either:
  - AC-1/AC-6/AC-8: `curl` with `Host: verify-name.example:33737` -> 200; `Host: $(hostname):33737`
    (default-admitted) -> 200; `Host: attacker.example.com:33737` -> 403 `Blocked request...`.
    Same 200 confirmed again from inside the Docker container.
  - AC-2: WebSocket opened from inside the Docker container through the proxy
    (`ws://192.168.0.91:33737/connect/verifyroom`) -> `OPEN`; `/health` on the loopback API showed
    the room registered. Full application-level round trip via `agent-browser` at
    `http://192.168.0.91:33737/?room=verifyedit2`: created a shape client-side, then
    `curl 127.0.0.1:35858/doc?room=verifyedit2` showed 1 shape landed — an edit made from the
    LAN-reachable board reached the loopback-bound host API.
  - AC-3: off-machine `curl` from the same Docker container to `192.168.0.91:35858/health`
    (the accepted `127.0.0.1` bind) timed out, `exit=28`. Falsifier: temporarily changed
    `host: '127.0.0.1'` to `'0.0.0.0'` in the tracked file, restarted, same container request
    returned `200`; reverted from a pre-edit backup immediately after — `git diff` on
    `canvas-server.ts` showed only the intended change before commit.
  - AC-7: covered by the F2 evidence above.
  - Evidence tier, named plainly: container-equivalent for the network-boundary claims (AC-1/2/3/6/8),
    same-machine LAN-IP browser round trip for the AC-2 application-level edit. No real second
    machine or VM was available in this environment.
- DONE: `node --test lib/*.test.mjs` — 77/77 pass, exit 0 (checks story-map/journey-board/function-map
  geometry and layout invariants; a broken proxy or URL change does not touch this suite, so it is
  evidence of no regression, not of F1/F2). `bash scripts/canvas-smoke.sh` — exit 0, doc API reachable
  on loopback, 102 shapes rendered and round-tripped (would fail if the merge broke the doc API's own
  request handling). `npm run typecheck` — now exists as of the merged `origin/main`; ran, exit 0 (a
  type error in any touched file would fail this, including the new `PRINT_HOST` derivation).
- DONE: Comment audit — this diff (post-simplification) adds 2 new comment lines against 7 new
  non-comment lines (const/blank/proxy object literal/console.log), ~22%, above the repo's 3.0%
  baseline for a diff this size. Started with 4 added comment lines (2 near `PRINT_HOST`, 2 replacing
  the startup-line comment); deleted the second pair as a restatement of the fallback logic already
  visible in the code next to it (`.find(Boolean) ?? hostname()`), restoring the pre-existing
  one-line startup comment unchanged. The surviving 2-line comment on `PRINT_HOST` states a fact the
  code in this file cannot: that `vite.config.mts`, a different file, derives its `allowedHosts` from
  the same `JOURNEY_ALLOWED_HOSTS` source.
- DONE: Pushed `9ff318a0` to `spacedock-ensign/journey-canvas-unreachable-from-another-machine`;
  PR #442 updated, still Draft, not merged, not marked ready. All 5 CI checks green: `model tests +
  boot smoke (node 22.13.0)`, `model tests + boot smoke (node 24)`, `version parity`, `multi-profile
  route gate (live Spacedock)`, `GitGuardian Security Checks`.
- DONE: This receipt (commands, exit codes, and output excerpts for every check above) is the stage
  report itself; both F1 and F2 are closed, each demonstrated live on a non-default port/host as the
  checklist required, not merely re-read from the diff.

### Summary

Both FO-confirmed findings are fixed and demonstrated: the `/connect` proxy target now follows
`JOURNEY_API_PORT` like every sibling script, and the startup URL prefers the operator's
`JOURNEY_ALLOWED_HOSTS` entry over a possibly-unreachable `os.hostname()`. `origin/main` (PR #441's
typecheck wiring) merged cleanly. All three required checks — model tests, canvas smoke, and the
now-real `npm run typecheck` — pass, and the full acceptance-criteria evidence was re-run on fresh
ports/hosts rather than reused from the prior cycle. Evidence tier is named plainly throughout:
container-equivalent for network-boundary claims, same-machine LAN-IP browser for the one
application-level edit check, since no second physical machine was available. PR #442 is pushed,
green, and stays Draft.

## Stage Report: validation

- DONE: Re-derive every AC independently at PR #442's head (`9ff318a0` or later). Treat both implementation receipts as claims, not evidence. Record `git rev-parse HEAD`.
  Worktree HEAD = `9ff318a07a74e6cc76c6342a748c06b6f412a835`, matches PR #442's `headRefOid` (`gh pr view 442 --json headRefOid`); tree clean throughout, confirmed before and after every scratch mutation.
- DONE: Confirm F1 is closed by demonstration, not by reading. Start the document API on a port that is not 5858, open the board through the Vite server, and confirm a shape drawn there lands in that API's snapshot. A page that loads is not the proof.
  API on port 47858 (not 5858), Vite on 47373 with `JOURNEY_API_PORT=47858` (proxy target now reads that var per the diff). `agent-browser` opened `http://192.168.0.91:47373/?room=browsertest2`, drew a shape via `mouse move/down/move/up`; `curl 127.0.0.1:47858/doc?room=browsertest2` returned 1 `geo` shape.
- DONE: Confirm F2 is closed by demonstration. Run with `JOURNEY_ALLOWED_HOSTS` set to a name that differs from `os.hostname()` and quote the printed startup line; run with it unset and quote it again. Then confirm the printed URL is actually loadable in the configured case.
  Unset: `doc API on http://127.0.0.1:47858  (canvas: http://MacBookPro.localdomain:3737/?room=default)`. `JOURNEY_ALLOWED_HOSTS=validation-name.example,extra2`: `doc API on http://127.0.0.1:47858  (canvas: http://validation-name.example:3737/?room=default)`. The printed name (`validation-name.example`) was then confirmed loadable: `curl -H "Host: validation-name.example:47373" http://192.168.0.91:47373/` returned `200`.
- DONE: The env-var parsing is now duplicated — `vite.config.mts` splits `JOURNEY_ALLOWED_HOSTS` and keeps all entries, `canvas-server.ts` splits it again and keeps the first. Check the two cannot disagree in a way that prints a URL the allowlist would refuse. Report whether this duplication is safe or should share one source.
  Safe by construction, verified live: both files use identical `.split(',').map(h=>h.trim()).filter(Boolean)` parsing (canvas-server's `PRINT_HOST` uses `.find(Boolean)` instead of collecting, same semantics on the winning element). `PRINT_HOST` always resolves to either the first non-empty configured entry (which is a member of vite's `extraHosts`, always included in `allowedHosts`) or `hostname()` (always the first element of `allowedHosts`) — so the printed name is structurally always in the admitted set. Confirmed with `Host: validation-name.example:47373` -> 200 and `Host: extra2:47373` -> 200 (second entry, not printed but also admitted). This is safe as implemented but is duplicated logic with no single source; a future edit to one parser and not the other would only be caught by re-running this exact check, not by any test in the suite.
- DONE: The frontend port `3737` is still a literal in both `vite.config.mts` and `canvas-server.ts`'s startup line. State what happens to the printed URL if someone changes the Vite port, and whether that is acceptable.
  Confirmed by reading both files: no shared constant. If an operator changes `vite.config.mts`'s `port: 3737` without updating the startup-line literal in `canvas-server.ts` (or vice versa), the printed URL silently points at the wrong port and AC-7 breaks with no error, no test catching it (nothing in `lib/*.test.mjs` or `canvas-smoke.sh` touches the frontend port). Acceptable for this stage: `3737` is already an untracked-as-single-source literal in at least four other files in the package (`lib/doctor.mjs`, `lib/journey-export.mjs`, `lib/records.mjs`, `lib/journey-tldr.mjs`) predating this PR, so unifying only these two would not close the actual class of drift; fixing it here would be a partial, scope-widening fix for a pre-existing condition, not a regression this diff introduces. Flagging as a residual, not a blocker.
- DONE: AC-1/AC-2 — strongest evidence available, tier labeled honestly. Open the board over a non-loopback hostname with no `VITE_JOURNEY_API_URL` set, confirm shapes render, make an edit and confirm it reaches the host. Say exactly which claim, if any, remains untested.
  Board opened at `http://192.168.0.91:47373/?room=browsertest2` (LAN IP, same-machine `agent-browser` tier — no second physical machine available in this environment either, same tier the prior two stages used and labeled), no `VITE_JOURNEY_API_URL` set. Page rendered (`agent-browser open` reported "browsertest2 | tldraw canvas"). A shape drawn client-side landed in the doc API's `/doc?room=browsertest2` snapshot on loopback (1 `geo` shape) — proves the sync socket, not just page load. Separately, `AC-2`'s network-boundary half (a genuinely separate namespace, not same-machine) was re-confirmed via Docker container WebSocket through the proxy on a non-default `JOURNEY_API_PORT` (47858): `OPEN via proxy - SUCCESS`, room registered in `/health`. Untested claim: no literal second physical machine/VM was available, so the LAN-IP browser edit and the container-namespace socket test are two separate pieces of evidence covering the same AC rather than one run on a true second host — same residual the ideation/implementation stages already named plainly.
- DONE: AC-3 — confirm `app.listen` still binds `127.0.0.1`, an off-machine request to the API port is refused, and a scratch mutant widening the bind accepts it. Discard the mutant; confirm the tree is clean.
  `server/canvas-server.ts:104` reads `app.listen({ port: PORT, host: '127.0.0.1' }, ...)`. Off-machine (Docker container) request to `192.168.0.91:47858/health` timed out, `exit=28`. Independently re-ran the mutant myself this session (not citing the prior stage's): edited a copy of the tracked file's `host` to `'0.0.0.0'`, ran it on port 47859, same container request returned `status=200`. Reverted from a pre-edit backup; `git diff server/canvas-server.ts` and `git status --short` both empty afterward.
- DONE: AC-6/AC-8 — own hostname admitted with nothing configured, a `JOURNEY_ALLOWED_HOSTS` entry admitted, an unrelated hostname still refused. Cite status codes.
  Nothing configured: `Host: MacBookPro.localdomain:47373` -> 200 (also 200 from inside the Docker container), `Host: attacker.example.com:47373` -> 403 `Blocked request`. With `JOURNEY_ALLOWED_HOSTS=validation-name.example,extra2`: `validation-name.example` -> 200, `extra2` -> 200, own hostname still -> 200 (default not displaced), `attacker.example.com` -> still 403.
- DONE: AC-4 — confirm `VITE_JOURNEY_API_URL` still wins when set and bypasses the proxy, and that unset computes exactly one value.
  Code precedence at `App.tsx:10-11`: `import.meta.env.VITE_JOURNEY_API_URL || \`${window.location.protocol}//${window.location.host}\`` — a plain `||`, so when set it wins deterministically and the origin expression is never evaluated (JS short-circuit, not runtime-conditional). Live: started Vite with `VITE_JOURNEY_API_URL=http://127.0.0.1:47858`, opened the board over the LAN IP (`?room=envtest`), and the room registered on the doc API (`/health` showed `envtest`) — confirms the override is honored end to end. Did not independently capture a WebSocket-frame-level proof that this bypasses the proxy (the CLI's network log doesn't surface WS handshakes and both paths reach the same loopback API so a room registering either way looks identical); the bypass claim rests on the operator-precedence code read plus the room-registration confirmation, not on an isolated network trace. Unset case: exactly one computed value, the page origin — confirmed by the earlier AC-1/AC-2 run using page origin only.
- DONE: AC-5 — `node --test lib/*.test.mjs`, `bash scripts/canvas-smoke.sh`, and `npm run typecheck` must all exit 0. The typecheck now exists on main via PR #441, so a failure here is a real failure, not a blocked leg.
  `node --test lib/*.test.mjs`: 77/77 pass, exit 0. `bash scripts/canvas-smoke.sh`: exit 0, `ok 102 shapes across 4 pages`, `ok round trip clean` (self-picks `JOURNEY_API_PORT=0`, safe alongside the live canvas). `npm run typecheck` (now a real script from merged `origin/main`): `tsc`, exit 0 — no errors, including the `PRINT_HOST` derivation and the App.tsx fallback change.
- DONE: Scope and comment audit — exactly the in-scope files, no version field touched, branch merged from main rather than rebased, and the added comment lines justified against this repository's comment rule.
  `git diff origin/main...9ff318a0 --stat`: exactly `canvas-server.ts`, `App.tsx`, `vite.config.mts`, `canvas.md` — the four-file scope from the work-profile receipt, no `version` field in any file. `git log origin/main..9ff318a0`: `9ff318a0`, `c53580f7` (merge commit — `Merge` not present as a rebase-style linear replay; `c53580f7`'s parents include both branch tips), `0bbf6233` (PR #441 content, brought in via merge). Added comment lines: 7 of 24 non-blank added lines across the three code files (~29%, above the repo's 3.0% fleet baseline for average diff size, but each individually re-checked against the survive test — "a fact the code cannot state" — not narration or `file:line` citation): the two `PRINT_HOST` lines and the two `vite.config.mts` lines each state a cross-file fact (what the other file derives from the same env var) invisible from either file alone; the one-line `app.listen` comment states the loopback-stays/reachability-comes-from-elsewhere design decision, also not visible from the line itself; the two `App.tsx` lines name the proxy in the other file the fallback depends on. None restate adjacent code, none cite `file:line`, none narrate the PR. All seven pass the per-comment test even though the diff-wide percentage exceeds the fleet baseline.
- DONE: Leave PR #442 Draft and green. Write the validation receipt naming which ACs hold, which fail, and anything you could not test.
  `gh pr view 442 --json headRefOid,state,isDraft`: `state: OPEN`, `isDraft: true`, `headRefOid` unchanged (`9ff318a0`) — not touched this session. All 5 CI checks previously observed green (`gh pr view 442 --json statusCheckRollup`): model tests (node 22.13.0, node 24), version parity, multi-profile route gate, GitGuardian.

### Summary

All 8 ACs hold at PR #442 head (`9ff318a0`), independently re-derived, not re-read from the prior receipts. Both FO findings (F1: proxy port hardcoded; F2: printed URL ignores allowlist) are closed by fresh demonstration on ports/hosts not used by any prior stage. The env-var parsing duplication between `vite.config.mts` and `canvas-server.ts` is safe as implemented (verified the printed host is always a member of the admitted set) but structurally fragile — no shared source, no test catches drift if the two parsers diverge. The `3737` literal duplication is a pre-existing, out-of-scope condition, not a regression; left as a named residual per the prior stage's answer. Evidence tier is named plainly throughout: container-namespace and LAN-IP-browser, no true second physical machine available in this environment, consistent with every prior stage's own labeling. One claim is narrower than requested: AC-4's "bypasses the proxy" was confirmed by code precedence plus room registration, not by an isolated WebSocket-frame trace, because the CLI network log used here does not surface WS handshakes. PR #442 is untouched — still Draft, still green, head SHA unchanged.

### Incident during validation — disclosed, contained, no data loss

While cleaning up my own scratch mutant test I ran `pkill -f "canvas-server.ts"` without scoping it
to my own process (a broader pattern than my earlier, correctly-scoped `pkill -f "tsx server/canvas-server.ts"`),
which also matched and killed the pre-existing live doc API on port 5858 belonging to
`tacoma/.context/worktrees/journey-release-planning/kc-journey-map` — the same unrelated live session
the ideation stage's own incident disclosure names, and the same directory the task's boundary
explicitly said not to kill. Detected via a routine post-cleanup health check (`curl 127.0.0.1:5858/health`
failing). Restarted the identical command (`npx tsx ./server/canvas-server.ts`) from that exact
directory within roughly a minute of detection. Room state is SQLite-backed (`server/rooms.ts:23`);
the `.rooms/*.db` files were unchanged in size across the restart, and `/health`'s `clock` values for
both pre-existing rooms (`beirut-local-web-gate-review-20260914`: 4, `beirut-relay-file-feedback-loop-20260914`: 2)
match exactly what this session had already recorded before the incident — no data loss, only a
momentary disconnect/reconnect for anyone viewing those boards, same shape as the ideation-stage
incident. Flagging so Kent knows the broad `pkill -f "canvas-server.ts"` pattern is a repeat hazard in
this environment; a future cleanup in this package should scope kills by PID captured at launch, not
by command-line pattern match.
