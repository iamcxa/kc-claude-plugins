# Permitted room catalog and native switching

The opt-in verified-human canvas uses `GET /auth/rooms`. The response contains
`backendId`, `memberId` and `rooms: [{ roomId, displayName }]`; a missing label
uses the exact room ID. The server intersects current enabled member grants
with registered metadata. A denied or unregistered room is absent. An authorized
empty catalog is a successful empty list; invalid responses, policy denial and
registry failures remain visible failures. Responses use private no-store caching.
The catalog reads metadata without document opens, health samples or per-room
Durable Object stubs. Agent/legacy health retains its existing contract.

A, B and qnow-day2 are stable document IDs. Day2 can be a display name stored as
`displayName` in its existing `room:qnow-day2` metadata; names do not route or
create documents. Existing registration plus a current member grant adds a
future room without a frontend change. This slice adds no registration/admin UI.

The room control sits beside the native page control. Search matches names and
IDs, long rows wrap, and a bounded list scrolls normally. Loading, empty,
no-match, unavailable, source confirmation and target connection are distinct.
Refresh retries inventory; Escape returns focus to the trigger. Selecting an
exact room first confirms source authority and the existing single bounded
complete-record readback. A target sync client is staged without a target editor.
The original editor stays mounted until target sync and final admission succeed
and the source fingerprint is unchanged. Only then do URL/history and the active
native editor change. Failure or a changed source retains the original editor.

A known source denial disconnects its sync client and freezes received work.
No further source confirmation is attempted. Explicit selection can open a
separately admitted room in a new tab; closing/reloading the retained source can
still lose unsynced work because durable drafts belong to the return-context
story. Save/document-popup controls belong to the activated room; a frozen
source has neither action. A delayed source request cannot write to the target
through its pinned room context.

## Local verification

Use Node >=22.13 and the locked dependencies. The native browser suites require
an unpacked public `@tldraw/assets@5.4.0` package and installed Playwright Chromium:

```sh
npm ci --no-audit --no-fund
npx --no-install playwright install chromium
npm pack @tldraw/assets@5.4.0 --pack-destination /tmp
mkdir -p .host-check/assets
tar -xzf /tmp/tldraw-assets-5.4.0.tgz -C .host-check/assets
node --import tsx --test scripts/room-catalog.test.ts
JOURNEY_TLDRAW_ASSETS="$PWD/.host-check/assets/package" JOURNEY_CHECK_VIEWPORTS=desktop,phone390 node scripts/room-catalog-browser-check.mjs --adapter node --synthetic
JOURNEY_TLDRAW_ASSETS="$PWD/.host-check/assets/package" JOURNEY_CHECK_VIEWPORTS=desktop,phone390 node scripts/room-catalog-browser-check.mjs --adapter cloudflare-local --synthetic
```

These commands own fresh synthetic stores, loopback ports and browser contexts;
results and screenshots stay under ignored `.host-check/`. A typed synthetic
session is the catalog fixture; prerequisite suites separately exercise actual
owner-peer and simulated-provider login. Desktop and 390px native light/dark
browser operation is separate from a physical phone or hosted provider test.
Cloudflare Free workload/cost fit and generalized stream revocation are unproved.
No live canvas, credential migration, provider change or deployment is authorized
by running the suite. Human entry remains default-off.
