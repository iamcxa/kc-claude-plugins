# Private multi-room delivery

Run commands from `kc-journey-map`. Keep private configuration, credentials,
builds and provider receipts outside Git. Code preparation does not prove a
serving switch. Preserve the old POC address, data, Site audience and immutable
served version; start the new backend with fresh storage. No data migration or
old-service retirement is part of this delivery.

## One backend and separate principals

Use [private-host.md](private-host.md) for Node startup and
[private-operations.md](private-operations.md) for credentials, Cloudflare,
backup/restore and revocation. Both native agents connect directly to the same
backend `/mcp` with separate finite-lived credentials. A Sites browser uses its
own server-side credential and the existing owner-private login. Configure its
allowlist to the browser's reviewed rooms, not an unrestricted operator grant.

Create the intended rooms through the existing authorized GET `/doc?room=A`
and `/doc?room=B`. The selector lists only existing rooms from `/health`, further
filtered by the principal. It does not create or manage rooms. Existing
`?room=...` links still work. Open the compact room menu beside tldraw's native
page menu to search authorized room IDs; the popup shows the full current ID.
Pages remain separate navigation within a room. If the editor cannot mount,
a compact recovery selector keeps the authorized inventory reachable. Refresh
is manual; no inventory polling keeps objects awake.

Switching completes the editor gesture, then makes one authorized GET `/doc`
request to compare document records with the still-unchanged local snapshot.
An unconfirmed edit or failed read leaves the current editor open with a retry
message. This avoids relying on `Connected` as a saved-state signal or on private
SDK queue fields. Concurrent agent writes may cause a safe retry until the
existing sync client catches up; write/concurrency semantics are unchanged.
Browser back/forward uses the same check. Full page reload/closing still follows
the existing browser/sync behavior; save or confirm edits before leaving the page.

On a Node host with save capability, Save opens a bounded filename panel.
The existing filename probe changes Write to Overwrite for an existing file;
that button confirms the write. Cancel or Escape returns focus to Save, and
Dismiss clears a result message. Dismiss the panel before using another popup.
The chapter document popup still reads the room's allowlisted local checkout;
its header stays visible while the document body scrolls.
Cloudflare hides Save/download and reports the existing unavailable-checkout
message; it does not gain filesystem routes.

## Repository-contained Sites entry

Copy `scripts/private-sites.example.json` to private operator storage. Set exact
HTTPS Site/backend origins, one unused route prefix (for example `/journey`) and
canonical room IDs. No token belongs in this JSON. The new backend uses the Site
origin as `JOURNEY_ORIGIN`. Keep existing Site routes intact during preparation.
The normal production build is:

```sh
node scripts/build-private-entry.mjs --config /absolute/private-operator/sites.json --out /absolute/private-operator/production-build
```

Set `VITE_TLDRAW_LICENSE_KEY` in the build environment when available. It is a
public license input, not an agent secret. Production build success alone is not
licensed rendering proof. The explicitly authorized private development option is:

```sh
node scripts/build-private-entry.mjs --config /absolute/private-operator/sites.json --out /absolute/private-operator/development-build --development
```

This uses Vite's supported development definitions, keeps the SDK/license code
unchanged and writes `build-mode.json` stating the mode. Do not call that artifact
a licensed production build. Licensing stays an owner task; it does not block
private development, MCP, code review or the authorized development deployment.
The helper refuses nonempty output directories so earlier artifacts survive.
Preserve SDK notices with redistributed assets.

The output contains `public/<prefix>/`, `sites-entry.mjs`, `sites-config.json`
and the mode receipt. Use the supported Sites helper to open a fresh checkout of
the existing Site, then apply the exact additive integration locally:

```sh
node --import tsx scripts/stage-private-sites.mjs /absolute/sites-source /absolute/private-operator/development-build
```

This stages only `public/<prefix>/`, `lib/journey-private/` and the existing
`build/sites-worker.ts`. It inserts an awaited proxy before the original handler,
leaving old canvas, MCP, probe and connector routing intact. The helper checks the
known Worker signature, refuses existing destinations and saves the exact original
Worker in `sites-worker-before.ts` beside the private build. It does not edit the
hosting manifest, dependencies, old source/data, Git history or provider state.
Review the diff and build the Site with its supported local build helper. Only
then package/publish through the supported native Sites workflow after review.
For an uncommitted preparation rollback, restore the saved Worker bytes and remove
only the two added directories. For a served rollback, redeploy the immutable
prior version instead; do not reset/push source history.

Set only the new `JOURNEY_SITES_BEARER` secret through the native Sites environment
tool. The adapter requires the platform's authenticated visitor ID, exact Site
origin and allowed room. It forwards only fixed backend routes, rejects redirects,
strips browser credentials/cookies and keeps its bearer server-side. It permits
GET `/doc` for switch confirmation, never browser PATCH/PUT duplication. WebSocket
sync remains the existing write transport. Hosted assets remain excluded; the
entry reports `assets:false`. Node save/checkout reads keep their configured
capability. Keep native agents on the direct backend rather than this browser
entry. Do not trust visitor headers on a separately exposed non-Sites host.

Package and save through the supported Sites helper, preserving owner-only access.
Open `<Site origin>/<prefix>/?room=A` after the separately reviewed serving switch.
A latest saved version does not establish which version is served.

## Local candidate checks and native handoff

```sh
npm run typecheck
export JOURNEY_TLDRAW_ASSETS=/absolute/local-assets-5.4.0/package
export JOURNEY_CHECK_OUTPUT_DIR=/absolute/private-evidence
node scripts/room-switch-check.mjs --adapter node --synthetic
node scripts/room-switch-check.mjs --adapter cloudflare-local --synthetic
node scripts/sites-entry-check.mjs
```

The browser checks use synthetic local data, Vite development mode, a temporary
local certificate and ephemeral credentials. Supply an unpacked official
`@tldraw/assets@5.4.0` package at the asset path; the browser harness serves those
bytes locally and blocks other external HTTP requests. No test downloads assets.
The output directory is optional and defaults to the ignored `.host-check`.
They cover actual input, switching, acknowledged and immediate edits,
failure/retry, inventory privacy and forbidden-room recovery. Native menu,
toolbar, drawing, sequence-page and popup checks use desktop, tablet, narrow
phone and landscape viewports. Node checks exercise real disposable save files,
overwrite, errors and allowlisted chapter content; Cloudflare checks its existing
capability limits. Pointer checks wait for stable controls, then assert their
centre hit target before clicking. These are Chromium viewport checks, not
physical iOS or Safari acceptance. To continue a partial run, `--native-only`
skips the switch scenarios and `JOURNEY_CHECK_VIEWPORTS=phone390,phone320` narrows
the native surface checks; each receipt records that subset.
Sites checks exercise the fixed proxy and local Worker upgrade. These do not claim
hosted Sites, provider hibernation, actual native agents or production rendering.
Historical native/lifecycle receipts remain evidence for their original candidate.
For a new native-client check use the local-only recipe in
[private-native-check.md](private-native-check.md). No CI lane was added; CI cost
per PR is unmeasured.

## Switch and rollback inputs

Before any hosted change, independently accept the exact source/build; confirm
current Free-plan availability, owner-private audience, intended fresh resource
names and actual served version. Keep all provider identities and usage local.
Record candidate/build hashes, separate agent/browser grants, current environment
key set, old room readback, immutable Site rollback version, and backend closed
routing configuration. Keep Cloudflare R2 absent; no billing enrollment or upgrade.

After approval, provision only the fresh backend, confirm scoped API access, save
and switch the new Site version, then test bounded A/B browser/native readback.
Do not delete the old POC or silently move its data. If a failure occurs before
switching, leave the old Site served. If after switching, pause writers, back up
new acknowledged work and current policy, restore the recorded Site version and
prior environment keys, and disable only the new backend serving entry. Preserve
its namespaces/data for reconciliation. Namespace deletion is not rollback;
restoring a stale grant file must not revive revoked credentials.

The generic task-aware number guard still reports CONFIG ERROR / NOT PASS because
this fresh-storage implementation has no numbered SQL migration base. The accepted
task exception depends on unchanged persistence source, SDK lock and namespace
declarations. Compare these again for the new candidate; do not invent an SQL
path. ADR 0018 replaces the task's former 0015 and 0016 reservations after
main-branch number collisions. Historical receipts retain their original numbers.
