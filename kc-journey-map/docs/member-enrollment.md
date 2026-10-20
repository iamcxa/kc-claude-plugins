# Private member enrollment

This local Pilot capability is **off by default**. It adds an ordinary member to
explicit existing rooms; it does not enable sharing UI, invitations, provider
policies, room creation, reenable or administrator promotion. No deployment or real
enrollment is established by the synthetic tests. See [ADR 0032](../../docs/adr/0032-enroll-only-explicitly-resolved-private-members.md).

## Recipient sequence

1. The operator resolves the exact email in the configured provider account.
2. If no supported prior identity exists, the command refuses `identity_not_ready`.
   Give the recipient the existing room URL through an approved channel. They use
   ordinary email-code login and can receive `member_unbound` before enrollment.
   If provider policy blocks this login, stop for a separate provider setup decision.
3. The operator reviews and confirms the exact resolved identity and complete grant.
4. After `created` or an exact `no-op`, the recipient retries ordinary login. Signed
   issuer, application audience and live `user_uuid` equality still control entry.

The recipient needs no terminal, cookie export or agent credential. An app grant
neither proves current provider admission nor changes provider policy.

## Protected command

Run `node --import tsx scripts/journey-member.ts enroll --profile private-host --input-fd 3 --receipt-fd 4`
from this package. `inspect` uses the same arguments, resolves the same exact target
and reads state only; it never displays enrollment confirmation or sends enrollment.
Descriptor 3 is a pre-opened owner-only regular input file; descriptor 4 is a new
empty owner-only receipt file outside Git. They and credentials must have no group
or other access, one hard link and at most 64 KiB. Keep their containing directory
0700 and files 0600. Input, credentials, assertions and OTP codes never belong in
argv or Git. The command writes only a result/category/readback summary to stdout.
The detailed review is displayed only on an interactive owner terminal.

Profiles live at `~/.config/journey/profiles/<name>.json` (an explicitly controlled
`JOURNEY_MEMBER_PROFILE_DIR` can select another owner directory). Profile names are
IDs, never arbitrary paths. Profiles are owner-only files with:

- `enabled: true`, `writersStopped: true`, and the exact tested `candidate` revision;
- `binding`: exact `accountId`, `applicationId`, `providerId`, `backendId`, `origin`,
  `issuer`, `audience` and complete operator `rooms`;
- `providerFd`: inherited protected descriptor containing the provider-read token;
- `transport`: either `mode: node`, `inputFd`, `outputFd` for the existing owning
  process's private control pipes; or `mode: cloudflare-private`, exact private
  `url`, and separate protected operator `credentialFd`;
- optional `allowedTarget`: the exact owner-approved input for a delegated
  invocation. Any difference refuses before discovery or sending a request.

An assistant needs this protected, exact invocation plus Kent's specific approval.
An ordinary paired client or chat message does not create operator authority.
Tokens remain behind the existing approved credential wrapper. The command does
not discover credentials or configure accounts. Close the descriptor after use.

Input is a strict closed JSON object containing `backendId`, `origin`, `issuer`,
`audience`, exact `email`, immutable `memberId`, `label`, and 1–64 explicit
`rooms: [{ "roomId": "one", "expiresAt": <future epoch milliseconds> }]` entries.
Unknown properties, duplicate JSON keys, wildcards, duplicate/noncanonical rooms,
expired grants and unsupported roles refuse. The review includes exact provider
identity, complete scope and existing ordinary document create/edit/delete power.
To enroll, type `CONFIRM ` followed by the complete review exactly. Cancellation
before send leaves app state unchanged. SIGINT cancels discovery; reads have a
15-second timeout. There is no force or retry switch.

## Server configuration and transport

Only a separately approved activation may set `JOURNEY_MEMBER_ENROLLMENT=true`.
Both adapters also require existing signed-provider human configuration and
`JOURNEY_MEMBER_BINDING`, JSON with the same exact binding fields above. The
server checks backend/issuer/origin/audience, provider binding, proof freshness,
operator room scope and registered rooms again inside its transaction. Provider
credentials stay local and are not included in the transport command.

For Node, retain `JOURNEY_CONTROL_STDIO=1` on the sole owning process. Connect
owner-only inherited pipes; do not launch a second host against live storage.
The allowlisted commands are `member-enroll` and `member-inspect`, with
`writersStopped: true` and an `input` containing resolved `target`, `proof` and
`operationId`. The CLI provides these fields after trusted resolution. This
private channel must not be bridged to a browser, agent or generic HTTP proxy.
Existing local-owner mode refuses remote-email enrollment.

For Cloudflare, retain the separate credential-checking private client and service
binding described in [private operations](private-operations.md). Neither service
has public routes, workers.dev or preview URLs. The client rejects Origin, requires
POST JSON and its separate operator credential, and removes that credential before
the service binding. The operator bridge rechecks stopped writers and its explicit
room scope; the authoritative registry applies the atomic operation. The bridge
and product must reference the exact intended namespace/backend. No route is added
to the public product worker. These are configuration requirements, not proof of a
deployed boundary. Keep Cloudflare Free and usage/account details local.

## Outcomes and recovery

- `created`: transaction commit confirmed, exact member/index/room rows and existing
  audit finalized together. The local receipt includes resulting generations.
- `no-op`: identical current ordinary enabled member, generation one, same exact
  unrevoked generation-one grants and original expiries; no metadata/audit write.
- `conflict`: retained, inconsistent or different identity/member/grant history;
  no policy write. Missing restored indexes never erase disabled identity history.
- `refused`: invalid authority, identity, scope, default-off or confirmed rollback.
- `unknown`: response/commit effect or saving the local receipt cannot be established.
  Never retry enrollment automatically. The command attempts protected exact
  `inspect` after a lost send response; retain its result separately.

Inspection reports `matching-current-state`, `absent`, `conflict` or `unknown`,
with receipt availability separately. Matching current state is not proof of which
past request caused it. An absent result permits only a newly reviewed explicit
retry. An uncertain operation ID still in the audit cannot be reused. Deleting a
local receipt or pruning 30-day server receipts is not authority to replay.

The receipt contains exact target, candidate, provider account/application/binding,
API lookup ID distinct from authenticated subject, original login/observation time,
result, audit reference, resulting generations and readback. It contains no token,
assertion, OTP, unrelated identity, usage or canvas data. It is a local evidence file,
not a server pending-invitation or compatibility format.

Stop the command first for rollback. Existing grants remain until an independently
approved disable/revoke advances generations; never delete retained identities,
indexes, audit/tombstones or restore older metadata. The immutable bootstrap and
supported security-version guards remain authoritative after restart. No canvas,
asset, clock, draft, session/family lifetime or concurrent editing rule changes.

## Local evidence

`member-enrollment.test.ts` exercises actual Node SQLite and local workerd registry
transactions with synthetic provider reads and injected write/commit/reply faults.
`member-enrollment-cli.test.ts` exercises typed exact confirmation in a pseudo-terminal, actual owning-process
control pipes, protected descriptors and summary-only inspect output. `member-enrollment-browser-check.mjs --adapter node|cloudflare-local --synthetic`
exercises recipient browser HTTP/session and agent seams, including synthetic signed
login, unbound-first, explicit grant, exact catalog and revocation. It does not claim
visual browser acceptance or real OTP. Real provider fields/subject correlation,
deployed private routing, native recipient devices and Free usage remain with the
separate private-host verification workflow. No test authorizes activation or merge.
