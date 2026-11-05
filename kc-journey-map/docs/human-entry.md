# Optional verified-human entry

This first-story Pilot candidate is off by default. It does not configure an
identity provider, deploy a host, change existing credentials or authorize a
cutover. [Accepted design](../../docs/journey/kc-journey-map/private-entry.md)
owns product rules; [ADR 0058](../../docs/adr/0058-verified-human-entry-preserves-private-room-core.md)
owns the admission decision. Use synthetic rooms while validating.

## Operator configuration

`JOURNEY_HUMAN_CONFIG` configures server entry: an absolute JSON file path on Node, or JSON
binding on Cloudflare. Keep the trusted operator file outside Git. Configuration
version 1 pins an immutable backend ID, exact origin, mode, issuer and member
bindings. Node additionally requires the existing private storage/grants settings.
The browser build separately enables the gate with
`VITE_JOURNEY_HUMAN_ENTRY=true`; the Node development config enables it when
`JOURNEY_HUMAN_CONFIG` is present. Legacy/share/Sites builds default to their
existing entry without an `/auth/config` dependency. An enabled gate fails closed
if its configured server cannot be reached.
For example, a synthetic owner-local configuration has this shape:

```json
{
  "version": 1,
  "backendId": "synthetic-backend",
  "origin": "http://127.0.0.1:3737",
  "mode": "local",
  "issuer": "local:synthetic-backend",
  "localOwnerUid": 1000,
  "localMemberId": "owner",
  "members": [{
    "id": "owner", "issuer": "local:synthetic-backend", "subject": "uid:1000",
    "label": "Local owner", "role": "operator",
    "rooms": [{"id": "synthetic-room", "expiresAt": 1893456000000}]
  }]
}
```

Use the actual service OS account for the local UID and subject. Register the
synthetic room explicitly with the existing authorized document API first; human
entry never creates missing rooms. Labels never establish identity. Initialization
adds `human-schema:v1`, immutable backend configuration, unique issuer/subject
indexes, enabled members and exact room grants to the existing metadata table.
It does not touch canvas records or reimport existing policy. Subsequent startup
accepts only the same bootstrap configuration and never reenables revoked state.

For `mode: cloudflare`, pin an HTTPS `issuer`, application `audience`, exact
HTTPS app `origin`, and members bound to the provider's stable subjects. Remove
local-owner settings. Node remote entry supports this same configured Access
adapter; there is no arbitrary forwarded-header or generic provider fallback.
Protect only `/auth/login` with the provider and make the original state query
survive its return. App HTTP/MCP/assets/socket routes use app policy, with typed
errors, rather than provider redirects. Actual account/path setup must be
separately authorized and verified before use.

Cloudflare assertion verification fetches keys only from the configured issuer's
`/cdn-cgi/access/certs`, verifies RS256 and claims, then requests its
`/cdn-cgi/access/get-identity` using that same signed token. `user_uuid` must
match the signed subject and provider login `iat` must establish a human event.
Token issuance never substitutes for login time. Non-2xx responses, redirects,
service identities, unknown/expired login time or mismatches fail closed.
See [Cloudflare's identity fields](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/application-token/).
No app session outlives seven days from that event, even after renewed assertions.

## Owner-local sign-in

Use Node 22.13 or newer and Python 3. The Python socket channel verifies actual
peer UID using macOS/BSD `getpeereid` or Linux `SO_PEERCRED`; unsupported systems
remain stopped. The service and configured owner must be the same account. The
private root must be a real owned 0700 directory; the Unix socket is 0600.
The operating system also limits socket path length; use a short private path.
A stale/foreign/symlink socket is refused and never silently replaced.

Run the API and browser bound to loopback. The existing `canvas` script's broad
`--host` flag is intentionally refused when local human entry is configured;
start the API and `vite dev --host 127.0.0.1` separately with the same settings.
The browser proxy checks its actual loopback peer. LAN/public/tunnel origins
cannot use owner-local sign-in. Mac peer verification has been exercised locally;
other advertised OS paths still need their own host proof.

Open the original room URL, choose local verification, then explicitly inspect
and approve its non-secret request ID in the owner terminal:

```sh
python3 scripts/owner-login.py /absolute/short/private/owner-login.sock REQUEST_ID
```

The CLI displays the exact origin, member and request, and asks for `approve`.
Return to the original tab and confirm approval. Its private verifier stays in
memory, never a URL or log. The 60-second challenge is consumed atomically with
one session mint; wrong owner/tab/origin, reuse and expiry deny. This proves an
explicit signed-in OS-account action, not fresh password or biometric proof.
Same-account processes and root are inside this trusted-device boundary.

## Session and denial behavior

Human app cookies use separate names from legacy sessions. The secret is stored
only as a server digest; CSRF uses a separate same-origin cookie/header proof.
Healthy renewal preserves original identity/event and the absolute deadline.
Member generation changes deny existing sessions even after remove/regrant.
Human data/socket requests require the original-context query fields
(`_backend`, `_human`, `_humanAt`, `_humanRoom`); missing or mismatching fields deny. Explicit
authentication routes remain context-free where needed for first entry.
Browser requests carry their immutable original backend/member/event context;
a replacement shared cookie cannot reconnect a different human context.

`session_expired` is normal short expiry; `human_revalidation_due` requires a
fresh human event; `authority_denied`/`member_denied` mean current authority is
refused. `provider_unavailable` is an outage, not a claim of revoked membership.
A generic host failure is an unknown operation outcome; no automatic mutation
retry is introduced. The UI never says connected before target sync succeeds.

The protected Node stdio operator channel accepts `disable-member` and
`set-room` for current member policy; Cloudflare operator access uses its private
registry control, not a public route. These commit denial/generation first and
return `streamsStopped: unverified`. The later stream-lease story owns bounded
active-stream stop; neither a denial receipt nor this response proves it.
Lifecycle receipts contain only internal IDs, category/outcome and server time.
Creation processes at most 64 oldest receipt rows and removes those older than
30 days; idle retention has no deletion deadline. Security records and revocation
tombstones are outside receipt cleanup. No public usage endpoint is added.

## Local checks and activation hold

From this package, after installing locked dependencies:

```sh
node --import tsx --test scripts/human-entry.test.ts
node scripts/human-cloudflare-check.mjs
node scripts/human-entry-browser-check.mjs
```

The first checks owned policy and generated signatures; the second runs the
Cloudflare adapter in local workerd with synthetic provider responses; the third
uses fresh Node storage, real owner peer approval and an isolated browser. These
are local evidence. Actual provider login/session precedence, seven-day account
revalidation, route protection, HTTPS human-cookie behavior on real hosts,
unsupported peer platforms and Free workload/cost fit remain unrun.
There is no CI change or measured per-PR cost.

Rollback before activation: keep the deployed legacy default unchanged and
remove the optional entry setting from the candidate service after stopping its
owned processes. Retain the entire metadata database, generations, revoked
sessions, member state and legacy grant expiries. Never restore an older security
backup or run a version that bypasses those checks. If an enabled test deployment
needs immediate denial, disable its member through the protected control first;
active-stream stop remains explicitly unverified until the later safety story.
This candidate is not authorization for production activation or formal merge.

The native permitted-room menu and retained-source switching are described in
[room-catalog.md](room-catalog.md). Generalized stream safety and durable drafts
still require their separate stories; the entry remains disabled by default.
