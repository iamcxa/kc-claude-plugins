# Native account and app session controls

This local pilot candidate adds My account and own-agent dialogs to the native
tldraw menu, using native group separators. The owner shortcut in My account and
the room menu opens the same **目前房間成員與存取** destination for the current
room. It reads actual member/grant metadata and says **目前可查看成員；邀請與移除尚未提供**.
There are no invitation/removal controls or browser administration bridge.

## Configuration and owner initialization

Off by default. The backend requires JOURNEY_NATIVE_ACCOUNT=true alongside the
existing private human-entry configuration. Without it, owner-read HTTP endpoints
are unavailable and the previous account UI is retained. The browser learns the
flag through /auth/config; a query string, member label or operator role cannot
enable ownership.

The one new logical key is owner:<backendId> in existing metadata, with
schemaVersion: 1, exact backend/member/issuer/subject, initialization operation ID
and time. Provision only through the existing protected operator channel, with
writers stopped and an explicit active verified human session digest matching all
four identity fields. Node uses owner-owned mode-0600 FIFO/socket stdio and
JOURNEY_CONTROL_STDIO=1; the separate Cloudflare private operations service
accepts owner-bind with writersStopped: true. Neither path is proxied to the
browser. Input fields: backendId, ownerMemberId, issuer, subject, sessionDigest
and initializationOperationId; these must be exact server-verified bindings.

The operation is create-once. The same exact initialization can be inspected again
while the verifying session is valid; changed identity/operation conflicts.
There is no replacement, transfer or recovery command. An operator role alone is
not owner. Missing/invalid owner binding stops the owner action; ordinary account
and own-agent operations remain available.

GET /auth/account and GET /auth/room-members require the existing exact
_human, _backend, _humanAt, _humanRoom context and a current human cookie.
The latter additionally requires the bound owner. Reads validate the session,
member generation and registered current-room grant transactionally. The list
contains only that room's actual member/grant rows, labels and current status,
never other-room grants, emails, provider proof or agent secrets.

## Logout and re-entry

Logout confirmation can be cancelled. Confirmation first awaits pending local
draft persistence. If that fails, it stops before logout and retains the canvas.
Then the canvas/dialogs/sockets unmount, client requests abort, and the existing
context/CSRF /auth/logout is submitted once. Other app tabs with the same
backend/member/original sign-in stop without clearing unrelated browser data.

A failed/unknown reply never claims confirmed server logout and never retries the
write automatically. A per-tab session hold contains only a status string; reload
keeps private content hidden. An explicit **重新驗證入口** action rechecks the actual
session; ordinary local-owner or Cloudflare login remains available. Cancelling a
pending entry invalidates late replies. No fake email/code form is introduced.

The same entry URL retains explicit-room precedence. Denied explicit rooms stop
in recovery; without a room URL, existing same-identity history returns only a
currently permitted room, otherwise the chooser/no-room stop remains. Re-entry
reads current cloud content and never automatically applies a draft. Draft
restore/delete still requires its existing explicit review. Agent installations,
member grants, generations, concurrency and fourteen-day/original-sign-in limits
do not change. App logout is not Cloudflare global logout and does not guarantee
a new code when provider verification is still valid.

## Local verification

Run from this package with its declared dependencies installed and Node >=22.13:

- node --import tsx --test scripts/native-account.test.ts scripts/human-entry.test.ts scripts/return-context.test.ts scripts/room-catalog.test.ts scripts/agent-consent-context.test.ts
- node scripts/native-account-browser-check.mjs
- node scripts/human-cloudflare-check.mjs

Browser checks use a fresh loopback host, real app/API, OS-owner approval and
synthetic storage only. The operator fixture uses mkfifo with mode 0600; no
global install or existing provider/account configuration is needed.
Cloudflare checks run the actual SQLite Durable Object adapter in local workerd
with locally signed assertions and synthetic identity endpoints, not a real
provider account. Desktop 1280/mobile-width 390 and light/dark screenshots do not
prove physical iOS/Android keyboard behavior, real provider availability or
human acceptance. No source-service review, production deployment, activation,
push, PR or merge is performed by these checks.
