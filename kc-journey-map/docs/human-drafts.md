# Origin-local human drafts and explicit restoration

The optional verified-human entry enables this default-off draft candidate.
It uses the existing registered room IDs and complete-record mutation engine.
[ADR 0030](../../docs/adr/0030-human-drafts-restore-explicitly-from-origin-local-versions.md)
records the accepted device-owner and explicit-restoration decision.

An exact URL room wins. Otherwise the same verified person's last successfully
activated room may resume after current permission/registration checks; an
ineligible history shows the chooser. Admission alone does not write history.
An explicit denied/missing target never opens a substitute or empty room.

The local-save bar distinguishes strict local acknowledgment from cloud
connection. Open **本機草稿** to recheck identity/current room, explicitly inspect
one version and confirm its exact full-record puts/removes. A native detached
preview sends no retained document buffer. Reviewing pauses the original editor;
use the separate verified room link for fresh cloud editing afterward.

The guarded native connector preserves the SDK-supplied `sessionId` and
`storeId` for both editing and fresh restore probes. Preexisting values in the
URI are rejected using the native reserved-parameter rule. Authority and pause
checks do not replace the native per-tab sync identity or concurrency behavior.

The operation is sent once after durable local preparation. Lost replies,
unfinalized audit receipts, mismatched readback or unconfirmed sync retain the
selected version. **核對原操作，不重送** checks the original correlated receipt,
exact cloud records/absence and a fresh sync before deleting that version.
The retained canvas also shows an unknown-result notice after uncertain apply.
Only successful original-operation verification clears that notice; the old
editor stays paused. Cancel and permission recheck never clear the draft or
resolve an uncertain cloud operation. Matching state produced by another writer is insufficient. No automatic retry,
whole-room rollback or stronger concurrency guarantee is introduced.

The original verified person can explicitly delete one local version even when
room access is denied; the confirmation reveals no document payload and offers
cancel. A current local apply lease blocks parallel deletion. Expiry permits
inspection/manual deletion, never inferred nonexecution/resend. Newer and
other-tab versions survive exact cleanup. Logout, denial and time do not expire
drafts. Local deletion cannot cancel an already admitted cloud operation.

## Storage and compatibility

`server/client/human-drafts.ts` initializes `journey-human-drafts` at IndexedDB
schema version **2**. `onupgradeneeded` creates the version-1 `roomHistory`,
`draftVersions`, `draftHeads` stores, then adds version-2 `applyAttempts` and
`restoreLease`. Upgrading adds stores without rewriting old versions. Payload
envelope version **1** remains independent of database version 2. Blocked/failed
upgrades preserve prior data and never acknowledge a new save.

Versions use `[backend,member,room,draftId,tabId,version]`; every mount/reload has
fresh random lineage identifiers. Version append and its head commit together
with `durability: strict`. Strict support is checked on the actual transaction.
Unsupported durability, abort, quota or other storage errors keep the save
unacknowledged. The native schema validates document-scope records, including
shared user/agent-authored canvas records; instance/presence/process/credential
payloads are excluded. Each document snapshot is bounded to 5 MB and 20,000 records; a version retains
its base and draft snapshots separately.

Persistent-storage permission is requested and its result is disclosed. Browser
clearing/eviction, private-mode behavior, extensions and the profile/OS owner
remain limits. Origins (including domain aliases/ports) and browser profiles have
separate stores, with no automatic migration, shared secret or encryption layer.
Existing legacy localStorage history is not imported as successful activation.

The existing server metadata table is unchanged. Optional audit correlation
format version **1** adds context/request fingerprints to newly reserved human
mutation receipts. Older/unrelated receipts without these fields return unknown
to draft reconciliation; no SQL migration or server-record rewrite is applied.
The seven-day verified-human deadline and receipt-retention/tombstone rules are
unchanged. Receipt expiry cannot clear a browser draft.

## Local checks and acceptance limits

Use locked dependencies and the same public `@tldraw/assets@5.4.0` fixture as the
[catalog suite](room-catalog.md#local-verification). Existing room data stays
outside these fresh synthetic fixtures. No protected-store pairing is involved.

```sh
node --import tsx --test scripts/return-context.test.ts scripts/human-entry.test.ts scripts/room-catalog.test.ts
JOURNEY_DRAFT_SKIP_QUOTA=true node scripts/human-drafts-check.mjs
node scripts/return-context-browser-check.mjs node
node scripts/return-context-browser-check.mjs cloudflare-local
```

The storage suite's optional fresh-origin quota probe is bounded below 16 MiB
and one attempt; skip it when an earlier quota probe is already recorded. A
reported quota override is not proof of a quota rejection. Its result is separate
from abort injection and crash/reopen observations. The browser process crash
case kills only its own isolated test browser after request success and before
transaction completion; it is not an OS/power-loss guarantee.

Browser suites use actual cookies, local IndexedDB and both local adapters;
desktop/390px viewport hit-testing is separate from physical-device acceptance.
Configured hosted-provider identity, unsupported browsers/devices, storage quota
enforcement on those runtimes, and Free workload/cost fit need their own evidence.
Source presence and local checks do not authorize activation, publication or merge.
