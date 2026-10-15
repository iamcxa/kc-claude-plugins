# Private pilot operations

The current delivery scope is local Node, Cloudflare on the Free plan, the
owner-private Sites entry and native Claude Code/Codex CLI cooperation. Remote
Node, hosted photos/assets, the original desktop plugin binding, Netlify and
room/project management are deferred. Their existing code capabilities are preserved.
The room selector is authorized by amendment 7; document formats and concurrent-write rules are unchanged.

This runbook prepares retained use; it does not establish a retained deployment,
valid license, complete bill or ongoing service commitment. Historical native
client, browser and hibernation evidence remains bounded to its tested candidate.
Detailed measurements, resource identities and receipts belong in the operator's
private evidence directory, never in Git or shared page links.

For the candidate-specific switch sequence and pending guard decision, use
[private-delivery.md](private-delivery.md).

## License and build

The locked tldraw SDK is version 5.4.0. Its installed LICENSE links to tldraw's
license, and the [versioned license](https://github.com/tldraw/tldraw/blob/v5.4.0/LICENSE.md)
permits development use by default. Retained end-user functionality on a private
or cloud service needs an applicable alternative license; personal use is not
automatically exempt. The [official license guide](https://tldraw.dev/community/license)
describes discretionary noncommercial hobby licenses and their required watermark.
The owner must obtain or confirm a license covering the actual use and domains;
an agent must not apply, accept terms or start a trial on the owner's behalf.

The pinned SDK already reads `import.meta.env.VITE_TLDRAW_LICENSE_KEY`.
Load the issued key through the operator environment, then build normally:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npx --no-install vite build --mode production --outDir /absolute/private-build
```

The license key is a public client-side license input, distinct from an agent
credential. Never put agent credentials in any `VITE_*` variable. A build with an
invalid synthetic marker proves wiring only; it is not a valid key or rendering
acceptance. Private development-mode work is explicitly authorized; label it accurately and keep licensing as an owner task. Do not remove the watermark or patch license checks. Production rendering is unverified until a suitable key is supplied and actually checked. Preserve the SDK's license notices
with redistributed assets. Use the repository build helper and Sites entry described in [private-delivery.md](private-delivery.md); no bearer belongs in a client build.

## Scoped credentials and native clients

Use one fresh credential ID and principal per agent, exact room allowlists and a
finite expiry. Reuse `scripts/journey-grant.ts`; keep the digest-only policy and
mode-0600 token files in a mode-0700 operator directory outside Git and storage:

```sh
umask 077
mkdir -p /absolute/private-operator
node --import tsx scripts/journey-grant.ts /absolute/private-operator/grants.json agent-a-v1 agent-a shared 2027-01-01T00:00:00Z /absolute/private-operator/agent-a.token
```

Replace the illustrative expiry with the intended finite session period. Never
paste the token into commands, tool arguments, transcripts, URLs or records.
An approved secret wrapper can read the protected file into
`JOURNEY_API_TOKEN` for only the child client process. Do not enable shell tracing.
The journey CLI consumes `JOURNEY_API` and that environment variable unchanged.

For Claude Code, a token-free MCP configuration can reference the environment:

```json
{"mcpServers":{"journey":{"type":"http","url":"${JOURNEY_API}/mcp","headers":{"Authorization":"Bearer ${JOURNEY_API_TOKEN}"}}}}
```

Launch `claude --strict-mcp-config --mcp-config /absolute/private-operator/claude-mcp.json`
from that child environment. For Codex, pass a token-free configuration:

```toml
[mcp_servers.journey]
url = "https://canvas.example.invalid/mcp"
bearer_token_env_var = "JOURNEY_API_TOKEN"
enabled_tools = ["get_doc", "patch_doc", "put_doc", "health"]
```

Use the approved client's normal tool approval policy. The accepted native test
proved specific CLI builds and per-tool permissions; it did not prove the old
desktop plugin or arbitrary client versions. Start with tool discovery and a
read-only `get_doc` for the intended room. Another room must remain forbidden.
For writes, follow the discovered `patch_doc` envelope and acknowledgement/readback
rules in [the bounded native-client recipe](private-native-check.md). Complete
records belong in `body.put` (singular); removals belong in `body.remove`. Process
exit or tool success alone is not evidence that an intended note was saved.

Rotate by issuing a new ID, installing its digest-only grant, and confirming its
scoped read before revoking the old ID through operator control. Existing IDs are
immutable on startup: editing a JSON entry does not update a persisted grant.
Never reuse an old ID. On suspected compromise, revoke before distributing the
replacement and accept the short interruption. Confirm old access is denied;
remove its local secret after successful revocation. Expiry is not a substitute
for early revocation. Labels are operator claims, not verified human identity.

## Node backup, fresh restore and rollback

The existing server accepts live `revoke` on its owned stdin channel. For offline
work, stop the owning Node process and all writers first. Set
`JOURNEY_PRIVATE_DIR`, `JOURNEY_GRANTS_FILE` and `JOURNEY_ORIGIN` as documented in
[private-host.md](private-host.md). Run from this package:

```sh
node --import tsx scripts/private-node-ops.ts backup /absolute/private-operator/backup.json --stopped
node --import tsx scripts/private-node-ops.ts revoke agent-a-v1 --stopped
```

`--stopped` is the operator's explicit precondition, not process detection or a
lock against an unrelated server. Never run this helper alongside the server.
Backup uses the existing export path for every room and asset, plus persisted
digest-only grants. Sessions and raw credentials are excluded. Output refuses
overwrite and uses mode 0600; keep its parent private. Policy and documents are
consistent only while writers remain stopped.

For restore, point `JOURNEY_PRIVATE_DIR` to a fresh empty target and
`JOURNEY_GRANTS_FILE` to deliberately issued **new IDs**. Review each principal's
current allowlist before issuing; do not copy stale authorization automatically.

```sh
node --import tsx scripts/private-node-ops.ts restore /absolute/private-operator/backup.json --stopped
```

Every archived ID is restored as revoked, including one revoked after that
backup was taken. Old sessions are never restored. Existing targets and reused
credential IDs are refused. A failure after partial initialization leaves the
target quarantined: keep evidence, stop it and retry into another fresh target.
Do not repair or merge tldraw tables manually.

Before switching, compare all records/assets and verify fresh allowed credentials
and old denied credentials on the target. Keep source storage unchanged. Save the
old entry/configuration reference and candidate source/build identity locally.
A failure before switching leaves the source entry in place.

After switching, a failure requires pausing writers and exporting the failed
target first, preserving any acknowledged new work. Restore the saved entry and
old compatible code/storage only after reconciling current revocations; never
restore an old grant file to undo a revoke. Reissue fresh IDs if needed. Returning
to an older snapshot does **not** carry later writes backwards: keep those
recoverable and explicitly resolve them before resuming. No automatic reverse
migration is provided.

## Cloudflare deployment inputs and private operator bridge

Use the same locked product source with
`scripts/private-cloudflare.example.json`. Copy configurations into the private
evidence directory, resolve each `main` to its absolute source path, choose a new
isolated Worker identity and exact trusted origin, and record the source/build
digest locally. The example is fail-closed: no routes, workers.dev or preview
URL. A reviewed serving entry is a separate configuration step.

Only SQLite Durable Objects are configured. The `v1` declaration initializes
fresh namespaces; it is not a retained-data migration or a new SQL schema.
Do not apply this example to an existing Worker. Keep the account on Free and
stop if provisioning requests billing, R2 enrollment or a paid plan.
Provide `JOURNEY_GRANTS` as a digest-only secret through the operator's approved
environment/stdin wrapper, never in versioned configuration. No R2 binding is
present: capabilities report `assets:false`; upload returns 501 and missing
download returns 404. Photos and file attachments are outside this hosted slice.

Cloudflare does not support direct remote Durable Object bindings in local
development. Its [documented route](https://developers.cloudflare.com/workers/local-development/#using-remote-resources-with-durable-objects-and-workflows)
is a remote service binding to a Worker that accesses the objects. The isolated
`private-cloudflare-ops.ts` bridge follows that route and exposes only backup,
fresh restore and revoke, delegating existing host functions. It has no public
admin endpoint, arbitrary forwarding or SQL operation.

Copy `private-cloudflare-ops.example.json`, bind both classes to the exact reviewed
backend using `script_name`, set an explicit operator room allowlist, and supply
the same valid digest-only grant binding. Keep `workers_dev:false`,
`preview_urls:false`, `routes:[]` and logs disabled. Verify provider routing
state after deployment; configuration text alone is not absence evidence.

Copy `private-cloudflare-client.example.json` and bind `OPERATOR` to that bridge.
Create a fresh local operator credential in a protected `.dev.vars` file beside
that copied client configuration, outside Git. Wrangler loads it as a local
secret binding; never add it to `vars`, command arguments or shared evidence:

```sh
umask 077
node --input-type=module <<'JS'
import { randomBytes } from 'node:crypto'
import { writeFileSync } from 'node:fs'
writeFileSync('/absolute/private-operator/.dev.vars',
  'JOURNEY_OPERATOR_TOKEN=' + randomBytes(32).toString('base64url') + '\n',
  { mode: 0o600, flag: 'wx' })
JS
```

Run this client **locally only**, through an already authenticated Wrangler:

```sh
wrangler dev --config /absolute/private-operator/client.json --ip 127.0.0.1
```

The `remote:true` is a service binding, not a DO binding. Cloudflare operator
credentials stay in Wrangler's supported authentication storage/environment.
Do not deploy the local client or expose its loopback port to another machine.
Agent grants cannot call this administration surface.
The CLI-only local handler rejects requests with a present Origin header and
requires `Content-Type: application/json` and the fresh local bearer credential
before delegation. Missing configuration or credentials fail closed. This local
credential is separate from agent grants and Cloudflare authentication.
The local caller's compatibility date also works with Wrangler 4.92.0's bundled
runtime. Backend and operator bridge keep their own later compatibility date.

Send one JSON POST to the local client; save backup responses directly to a
mode-0600 local file without logging or displaying their document bodies.
For example, save the intended operation to `request.json`, then use a process
that reads the local credential internally:

```sh
node --input-type=module <<'JS'
import { readFileSync, writeFileSync } from 'node:fs'
const dir = '/absolute/private-operator/'
const token = readFileSync(dir + '.dev.vars', 'utf8')
  .split('\n').find(line => line.startsWith('JOURNEY_OPERATOR_TOKEN=')).split('=')[1]
const response = await fetch('http://127.0.0.1:8790/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
  body: readFileSync(dir + 'request.json', 'utf8'),
})
if (!response.ok) throw new Error('Operator request failed: ' + response.status)
writeFileSync(dir + 'response.json', await response.text(), { mode: 0o600, flag: 'wx' })
JS
```

Supported request bodies:

```json
{"op":"backup","writersStopped":true}
{"op":"revoke","credentialId":"agent-a-v1","writersStopped":true}
{"op":"restore","writersStopped":true,"archive":"replace with complete backup object"}
```

For backup/restore, stop all writers and socket clients. A command assertion is
not an enforced writer lock. Before restore, create a fresh target with new
credential IDs and point a new bridge configuration to it. Existing rooms,
archived IDs in current policy, out-of-scope rooms and hosted assets are refused.
After errors, retain the partial target until understood, then remove only the
owned disposable target. Revocation calls the registry's existing close/readback
path; a partial result must be retried before restoring access.

At completion stop the loopback client, remove its local credential file, delete
only its temporary bridge Worker, and verify the bridge is absent. Deleting that Worker must not delete backend
namespaces. Namespace deletion is reserved for the explicitly disposable backend,
after required backups and rollback checks; never delete retained namespaces as
routine cleanup. Local tests prove binding delegation, not hosted Wrangler
authentication or provider routing. Those must be observed before retained use.

## Sites entry and bounded acceptance

Keep the existing owner-only Site policy and original saved version until the
new entry is independently accepted. Reuse the accepted same-origin proxy mapping:
Sites owner login maps to its own narrow server-side principal; native agents
retain separate credentials. Load secrets through the native Sites environment
API. Never add credentials to static assets, query strings or MCP page links.
Record the exact prior saved version, environment key set and original room
records locally before any mutation. On a pre-switch failure leave it served;
on a post-switch failure pause writers, preserve new work, and restore that exact
version/configuration. Test history may remain saved but unserved.

The supported payload evidence is the existing fictional journey rendered into
its complete pages and the existing book-pickup example. Local measurements are
fixture evidence, not Cloudflare maximums. Larger payloads and hosted assets
remain unverified. If a fresh hosted sizing proof is needed, limit it to the
authorized two synthetic rooms, eight sockets and 200 small application
operations; account for all attempts, use scoped before/after observations and
at most one delayed read. Missing metrics stay NOT SHOWN. Do not run a stress
test, repeat accepted native/browser/lifecycle suites or infer zero cost.

For the new local operational paths only:

```sh
node --import tsx scripts/private-readiness-check.ts /absolute/private-operator/local-checks.json --synthetic
```

This exercises real local storage and Miniflare service bindings, fresh restore,
revocation quarantine, rollback preservation, absent assets and normal production
license-input wiring. It creates only ignored synthetic scratch data and closes
its emulators. No CI or monitor was added; CI cost per PR was not measured.
