# Optional distinct agent installations

This second-story Pilot foundation is disabled unless
`JOURNEY_AGENT_PAIRING=true` is explicitly set on the server. It requires private
storage and the existing verified-human configuration. Keep it disabled outside
fresh synthetic validation: active-stream revocation, hosted/provider proof and
independent native-client collaboration remain separate work. There is no live
deployment, production credential migration, standing CI change or measured
per-PR cost in this change.

The [accepted private-entry plan](../../docs/journey/kc-journey-map/private-entry.md)
owns current product scope; [ADR 0027](../../docs/adr/0027-distinct-agent-families-and-revoke-only-repair.md)
owns authority and recovery decisions. Frozen design reports are historical and
unchanged. A local test or screenshot does not authorize activation.

## Consent and authority

The initiating helper requests an exact member and canonical room set. The
server snapshots existing capabilities: complete-record read/add/change/delete,
whole-document replacement, configured asset access, and only the actual Node
save directory and repository allowlist. No administrator capability is delegated.
Labels are self-reported, never verified model or owner identities.

The signed-in human opens **帳號與代理**, enters the human code, inspects the
exact authorizer/backend/rooms/capabilities and explicitly approves or denies.
Inspection creates one consent context bound to that exact session, original
verified event and original room. A switched identity, stale event, different
room or changed scope requires a new inspection. Code possession alone grants
neither access nor identity. Only the original private verifier can redeem once.
Approval alone issues no credentials. Requests expire after five minutes.

Each redemption creates a separate installation family and fifteen-minute access.
Access and renewal intersect current policy/backend, member and room generations;
remove/regrant or disable/reenable cannot revive old authority. Human seven-day
sign-in deadlines and browser logout do not expire agents; no inactivity expiry
is introduced. Legacy credential behavior/expiries remain unchanged.

Issuance permits at most five requests per intended member/minute and twenty
globally/minute; authenticated code lookup allows thirty attempts globally/minute.
Original-verifier polling permits one request per two seconds per request.
These are bounded local admission limits, not production load-fit measurements.

## Protected helper and normal use

Requires Node 22.13+, macOS with Swift and an unlocked usable user Keychain.
Other operating-system protected-store adapters are explicitly unverified and
refuse use. Native Claude/Codex configuration must point at the stable stdio
helper; it contains IDs/endpoints only. Native-client setup and independent
same-room coedit proof belong to the separate collaboration story.

Create a nonsecret local JSON configuration:

```json
{
  "endpoint": "http://127.0.0.1:5858",
  "backendId": "synthetic-backend",
  "installationId": "generate-a-distinct-installation-id",
  "memberId": "owner",
  "rooms": ["synthetic-room"],
  "label": "My installation (self-reported)"
}
```

Use a distinct installation ID per installation and the exact backend API origin.
HTTPS is required except exact loopback. Unknown configuration fields are
refused; there is no token/config/environment-secret option. The default local
store is `~/.local/share/kc-journey-map/agents`; an optional last argument selects
an owned 0700 directory for synthetic tests. Do not share or copy that directory
between installations. Commands run from this package:

```sh
node scripts/agent-helper.mjs begin /absolute/nonsecret-installation.json
# Inspect/approve the returned human code in the signed-in browser.
node scripts/agent-helper.mjs finish /absolute/nonsecret-installation.json
node scripts/agent-helper.mjs mcp /absolute/nonsecret-installation.json
```

The last command speaks newline-delimited JSON-RPC on stdin/stdout and proxies the
existing MCP tool contract. No new document mutation semantics are introduced.
The helper prints codes, IDs, state and tool replies; it never prints credentials.
Secrets travel only over protected process pipes and the pinned backend channel.
Cross-origin redirects are refused before any follow-up request.

The Swift bridge queries only the exact application service
`dev.kc-journey-map.agent.v1` and backend/installation/slot account. It never
enumerates a user's Keychain. An owned file lock spans the whole helper process;
a second process refuses with `installation_busy`. Calls within one helper are
serialized. Normal short-access renewal is automatic.

Every rotating operation first publishes a paused checkpoint with the old
authenticated repair material. New Keychain slots are saved and read back before
a durable nonsecret slot pointer is published. A separate nonsecret checkpoint
retains the preceding protected repair proof until manifest confirmation succeeds;
failed confirmation quarantines staging for later/queued calls and reopening,
even if the manifest already points at the new slot. Authenticated reconciliation
can still use the preceding verifier or spent refresh proof. Unconfirmed slots
cannot release calls and are cleaned from the application-owned slot journal.
Only IDs are on disk. There is no plaintext secret fallback.

## Conservative repair

Ordinary offline preflight retains the family without starting rotation.
After a rotate/redemption transmission starts, a lost reply, invalid reply or
unknown protected-save outcome leaves calls paused across process restarts.
There is no automatic old-secret retry, grace period or secret retrieval.

```sh
node scripts/agent-helper.mjs status /absolute/nonsecret-installation.json
node scripts/agent-helper.mjs reconcile /absolute/nonsecret-installation.json
# Only a confirmed revoked state permits begin again; repeat human approval.
node scripts/agent-helper.mjs begin /absolute/nonsecret-installation.json
```

Reconciliation uses the original verifier to cancel/tombstone a request and any
family created, or uses validated current/spent refresh proof solely to revoke.
An unknown revoke returns `revoke_pending` and remains paused. A guessed secret
cannot revoke an existing family. A cancellation reservation also blocks a late
original request after its unknown start reply. New pairing creates a new family;
the old family never revives. `forget` removes local items only after confirmed
revocation; it is not a server revoke shortcut.

The human sheet distinguishes awaiting original redemption, active authority,
revocation confirmation, unknown revoke and revoked/fresh-pairing guidance.
Helper status is local; the sheet's active authority does not claim the helper
is healthy or that an established stream has stopped.

## Metadata, rollback and proof

Versioned agent policy, requests, consent contexts, families, access digests,
spent refresh digests, rate buckets and thirty-day lifecycle receipts are keys
inside the existing SQLite metadata table on both Node and the registry Durable
Object. No SQL migration or canvas schema changes. Consume/rotate/revoke and
required receipts share a transaction. Authenticated replay and rate-limit
denials commit their required security effects even when HTTP returns an error;
storage failure rolls back the whole transition. Receipts exclude secrets,
digests and document payloads; detailed evidence remains local. Security
tombstones/spent proof are excluded from ordinary receipt cleanup.

Before activation, preserve the complete current security metadata database and
generations. Rollback means stopping owned processes and removing the optional
setting while preserving tombstones and existing legacy expiry. Never restore
an older security backup or use a binary that bypasses typed admission or the local
confirmation checkpoint. Preserve that checkpoint until the patched helper confirms
revoke; an older helper that ignores it is not a safe rollback. Restarting
with the setting disabled advances policy generation; enabling it again cannot
revive the prior families. New HTTP denial does not prove bounded stream stop.

Three-step fresh-shell local acceptance, normally below five minutes after
locked dependencies and browser are installed:

1. `node --import tsx --test scripts/agent-pairing.test.ts scripts/agent-consent-context.test.ts scripts/agent-confirmation.test.mjs && node --test scripts/agent-installation.test.mjs scripts/agent-protected-store.test.mjs`
2. `JOURNEY_TEST_PAIRING=true node scripts/human-cloudflare-check.mjs`
3. `node scripts/agent-pairing-browser-check.mjs`

Use normal host execution with loopback/browser and Keychain access. Sandboxed
Keychain access can return OSStatus -50 and fails closed; do not weaken storage.
All stores/rooms/items are generated synthetic fixtures. The OS check exercises
real protected roundtrip, restart, unconfirmed-save recovery, process lock and
exact cleanup. Real confirmation regressions make only their owned directory
read-only, cover rotation/redemption and queued/repeated calls, retain a possible
unconfirmed manifest pointer across restart, and prove actual Node revoke/fresh
pairing. Unit fault injection exercises lost reply/save failure; it is
not an induced real-Keychain corruption. The browser check exercises the actual
tldraw app, real helper, pointer/keyboard/focus and light/dark desktop/390px plus
touch-device emulation. Physical phone, live provider, deployment, Free budget
fit, native model-client use and established-stream stop remain unverified.

Canonical API disclosure comes from trusted adapter boot/listener state, separately
from the human-entry origin. Loopback Node uses its fixed127.0.0.1 listener's actual
port; configured same-origin remote Node and Cloudflare use JOURNEY_ORIGIN. Request
Host/forwarding headers and caller endpoint fields do not establish this value.
New pending requests snapshot it and inspection/approval/redemption recheck it.
Missing/changed snapshots on older in-flight requests fail scope_changed: use the
original helper to cancel/reconcile, then seek fresh approval. No backfill or old
family revival occurs; existing issued-family admission/renewal is unchanged.
Arbitrary remote split-origin/alias configurations are unverified.
