# Private journey host pilot

This opt-in pilot retains the canvas, YAML, record schema and complete-record
PATCH/PUT contract. It adds private grants, scoped assets and a shared HTTP/MCP
entry for Node or Cloudflare. Local emulator results do not establish hosted
readiness, billing, formal tldraw licensing or real provider hibernation.

The current bounded delivery and retained-use prerequisites are in
[Private pilot operations](private-operations.md). That runbook owns credential
rotation, document-plus-policy backup, fresh restore, private cloud administration,
license setup and entry-switch rollback. The protocol details below also describe
existing remote Node and optional asset capabilities deferred from this delivery.

## Install and test

Use Node >=22.13, Git, OpenSSL and the locked public packages. From this package:

```sh
mkdir -p .host-check
touch .host-check/empty.npmrc
npm ci --ignore-scripts --no-audit --no-fund --userconfig=.host-check/empty.npmrc --globalconfig=/dev/null
npx --no-install playwright install chromium
node scripts/host-contract-check.mjs --adapter node --synthetic
node scripts/host-contract-check.mjs --adapter cloudflare-local --synthetic
npm run typecheck
node --test lib/*.test.mjs
```

The runner owns ephemeral loopback ports, separate synthetic storage, an HTTPS
test certificate, Chromium DNS mapping and a fresh browser context. It writes
results/screenshots under ignored `.host-check/run-*/` and closes owned processes.
Its hostname and IP tests use actual HTTPS top-level origins with test-only
certificate validation disabled. Never use that browser setting for retained use.

The runner compares baseline records including stacking order; tldraw's random
index suffixes are excluded from equality. It records runtime/package versions,
candidate SHA and dirty status. Its baseline source is the admitted commit
`6d0f8da951b5ea9ea50fca6bd3685fc360bf502f`, archived inside its own scratch folder.
Full history containing that commit is needed for the rollback control.

## One agent interface

Keep `JOURNEY_API` (default `http://127.0.0.1:5858`). Private agents also receive
`JOURNEY_API_TOKEN`; the CLI helper injects it as a bearer header and fails on
HTTP/credential errors. A new `JOURNEY_CANVAS_BASE` changes newly rendered
page-link URLs; unset it to preserve `http://localhost:3737/`. Existing records
are not rewritten on startup.

```sh
node lib/journey-render.mjs /absolute/synthetic.yaml shared
node lib/journey-read.mjs /absolute/synthetic.yaml shared
```

A stateless Streamable HTTP MCP client connects to `<JOURNEY_API>/mcp` with the same
bearer header. It supports initialization, tool discovery, `get_doc`,
`patch_doc`, `put_doc` and `health`; document tools take `room` and write tools
take `body`. Results contain the existing HTTP result body. No SSE subscription,
OAuth discovery or public grant-management endpoint is provided.

## Grants and sessions

Use fresh synthetic/private storage. An operator owns a JSON grant array with
credential ID, SHA-256 secret digest, principal ID, canonical room allowlist,
expiry in epoch milliseconds and revoked flag. Principal labels are operator
claims, not verified human identities. A credential is `credentialId.secret`;
the secret contains 256 random bits. Do not put it in tool arguments, URLs,
records, logs or YAML.

The optional helper creates a fresh credential file with mode 0600 and appends
its digest-only grant. Keep both paths outside the new data directory:

```sh
node --import tsx scripts/journey-grant.ts /absolute/grants.json agent-a principal-a shared,room-a 2027-01-01T00:00:00Z /absolute/new-agent-a.token
```

Existing credential IDs are immutable in the persisted policy. Issue a fresh ID
and revoke the old one to rotate. Startup imports missing IDs from the configured
grant document; it preserves stored revocations. Protect operator files/backups
with filesystem permissions. There is no account or invitation service.

`POST /session` accepts the bearer header and exact configured Origin. It sets
a host-only HttpOnly, Secure, SameSite=Strict cookie, expiring within 15 minutes
and no later than its parent grant. The response contains no credential. Cookie
writes and WebSocket admission require the exact configured Origin; agents can
use bearer HTTP without a browser origin. Every request checks the current grant.

Each new session insertion checks at most 64 stored session rows and removes
expired entries. A persistent primary-key cursor resumes across host restarts and
wraps to revisit earlier keys, including old sessions and later expirations.
Cleanup runs on session creation only: idle hosts and bearer-only traffic do not
trigger it, so there is no idle deletion deadline or total-row cap. It adds no
timer, alarm or room wakeup; valid/malformed sessions and other metadata remain.

For a same-origin HTTPS canvas, the browser setup command consumes the credential
from `JOURNEY_API_TOKEN`, exchanges it in its own browser context and opens the
existing canvas. Close that window when done:

```sh
node scripts/journey-browser.mjs https://canvas.example.invalid shared
```

A remote host needs a trusted HTTPS origin that serves the canvas and proxies its
API/WebSocket paths to the same adapter. Plain HTTP custom hostnames and private IPs
are not supported by Secure cookies. Loopback development is the narrow exception.
Cross-origin Sites embedding and third-party-cookie/export automation are untested.

## Node local and remote

The same Node adapter serves both. Leave `JOURNEY_PRIVATE_DIR` unset for the old
loopback mode, room/asset layout and unauthenticated defaults. In private mode,
set the following before launching; keep the data directory empty on first use:

```sh
JOURNEY_PRIVATE_DIR=/absolute/new-pilot-data JOURNEY_GRANTS_FILE=/absolute/grants.json JOURNEY_ORIGIN=https://canvas.example.invalid JOURNEY_CONTROL_STDIO=1 node --import tsx server/canvas-server.ts
```

The API binds loopback; an operator-owned HTTPS reverse proxy is needed for remote
access. Do not expose legacy mode through that proxy. `JOURNEY_API_PORT` and the
existing body limit remain configurable. For local development `npm run canvas`
keeps the existing Vite entry and proxies the private API routes. A production
frontend can be built with `npx --no-install vite build` and served by the
operator's existing HTTPS boundary. This task provisions no proxy or hosted target.

Private Node stores metadata in `metadata.sqlite`, per-room databases in
`rooms/` and associated asset blobs in `assets/`. The first-use marker prevents
an implicit import from a nonempty directory. Do not copy retained databases
into it or edit tldraw's tables.

Private Node requires POSIX effective-user ownership support. A missing data root
is created with mode 0700. Before writing its marker or opening databases, startup
requires a real directory owned by the service's effective user, with no group or
other permission bits. Existing insecure roots, files and leaf symlinks are refused;
the server never changes their permissions or ownership. An owned 0700 root can
reopen normally, including through the offline operations helper.

For an existing insecure root, stop all writers, verify the intended application
directory and its owner, then deliberately restrict that root to 0700 before
retrying. For a foreign-owned path or symlink, choose a real directory owned by the
service user instead. Do not recursively chmod/chown data or change a shared parent.
This is a new startup requirement for private Node; legacy mode is unchanged.

Use an operator-controlled trusted parent and application-owned contents. This
leaf mode/owner check does not inspect extended ACLs or ancestor symlinks, prevent
concurrent path replacement, or isolate same-user/privileged processes. Child files
retain their existing format and mode behavior behind the private root; copied-out
files and external credentials/backups still need operator protection. Non-POSIX
private mode is unsupported. The focused disposable check is
`node --import tsx scripts/private-storage-permission-check.mjs`.

Private attachment replacement uploads a fresh blob, atomically exchanges its
mapping, then deletes the acknowledged predecessor. Concurrent replacements keep
the last committed mapping; document and canvas concurrency rules are unchanged.
A read that loses its old blob retries once if the mapping changed, then returns
503 on another replacement race. Failed uploads leave the mapping unchanged.
Confirmed Node rollback permits removal of the new blob; an unknown commit result
retains both blobs. A deletion failure returns 503 even though the new mapping is
already committed, and never rolls it back. Missing predecessor blobs are already
clean. Crashes, ambiguous commits and failed deletions can still leave orphans;
this is not a background collector or cleanup of historical unreferenced blobs.

Node `/save` is enabled in private mode only with `JOURNEY_SAVE_DIR`. This grants
the configured save-directory capability to authorized rooms. For `/repo-doc`,
configure existing `JOURNEY_DOC_REPOS=owner/repo=/absolute/checkout` plus
`JOURNEY_ROOM_REPOS='{"shared":["owner/repo"]}'`. The room map grants only those
configured checkout capabilities. `GET /capabilities?room=shared` reports
`save`, `repoDoc` and `assets`.

## Cloudflare-local and hosted wiring

```sh
JOURNEY_PRIVATE_DIR=/absolute/new-emulator-data JOURNEY_GRANTS_FILE=/absolute/grants.json JOURNEY_ORIGIN=https://canvas.example.invalid JOURNEY_CONTROL_STDIO=1 node scripts/cloudflare-local.mjs
```

This starts Miniflare/workerd locally, with SQLite Durable Objects and a local R2
bucket. It is not a hosted endpoint. The delivered Worker module is
`server/host/cloudflare.ts`: bind `ROOMS` to `JourneyRoom`, `REGISTRY` to
`JourneyRegistry`, `ASSETS` to a scoped R2 bucket, and optional `STATIC` to the
built canvas. Configure `JOURNEY_ORIGIN` and the digest-only `JOURNEY_GRANTS`
binding. The current Free-only hosted setup omits R2 and reports assets unsupported;
see the operations runbook for deployment inputs and its private operator bridge.
A live run requires exact isolated resources, credential handling, measurement
bounds and cleanup established before mutation.

The registry owns grants, sessions, room inventory and asset associations.
Each room owns tldraw SQLite and its sockets. A successful creation waits for
registry acknowledgement; registry failure returns 503, and a retry can register
the initialized room. Health inventory is strongly consistent and authorization
filtered. Cloudflare `health.active` is sampled telemetry that can wake rooms;
Node reports its resident room map. This difference is explicitly accepted.

Cloudflare returns `save:false`, `repoDoc:false`; `/save` is a non-JSON 501 and
`/repo-doc` retains the unavailable-result shape. Assets require R2. Hibernated
socket attachments retain tldraw session snapshots; wake-up rechecks grants before
resuming. The Cloudflare room disables tldraw's recurring idle pruning with
`clientTimeout: Infinity` and automatically answers the exact tldraw JSON
ping/pong pair without waking the room. Alarms still enforce session deadlines,
and revocation closes attached sockets. Hosted lifecycle and usage require
separate provider observations; emulator checks alone do not prove them.
Large-body limits and formal licensing remain NOT RUN.

## Operator control, recovery and rollback

With `JOURNEY_CONTROL_STDIO=1`, the owned host accepts one JSON command per stdin
line and returns a matching `control` ID on stdout. This is a local operator
channel, not an HTTP admin endpoint. It supports:

```json
{"id":"revoke-a","op":"revoke","credentialId":"agent-a"}
{"id":"backup-shared","op":"export","room":"shared"}
{"id":"restore-shared","op":"restore","archive":{"format":"journey-private-room-1","room":"shared","document":{},"assets":[]}}
```

For restore, replace the illustrated `archive` with the complete `result` from
export. It contains the snapshot plus every associated asset's ID, MIME type and
bytes. It contains no grants or sessions. Treat it as private data; stop writers
before exporting, since a document-plus-assets archive is not a cross-store
transaction. The runner exercises this control path on both adapters.

Restore into a fresh namespace/directory with explicitly configured grants.
An existing room is refused. If a restore fails after initialization, discard
only that disposable target after stopping it and retry into another empty target;
do not describe a partial restore as complete. Compare records, every asset and
browser/socket reconnection before switching any entry. Overwritten/unacknowledged
blobs may remain orphaned until that private namespace is discarded; no background
garbage collector or reconciliation service is introduced.

Revocation marks the persisted grant first, closes its allowlisted room sockets,
and reads back the policy. A close/refresh failure is partial revocation and must
be retried; never reuse the old ID to reactivate it. Node closes tracked sockets;
Cloudflare closes attached sockets, including on wake. Stop the host after
export/revocation when rolling back. Restore the prior code and point it at its
unchanged legacy room/asset directories. Private storage stays separate; no
automatic reverse migration or real retained-data import is provided.

Before a serving switch, complete the operating prerequisites in the operations
runbook and independently validate the exact delivery. Private development mode
is authorized; production licensing remains a separate owner task. Accepted bounded
native/browser and lifecycle evidence may be reused within its stated limits;
it is not complete cost or retained-deployment acceptance. No CI was added;
CI cost per PR was not measured.
