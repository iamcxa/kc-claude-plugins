# 0030. Human drafts restore explicitly from origin-local versions

Date: 2026-10-20

## Status

Accepted

## Context

The accepted private-room journey preserves interrupted human work without
adopting a different account, overwriting current cloud records on return, or
discarding an uncertain apply. Existing catalog activation, native editor/store
lifecycle, shared audit reservation and complete-record PATCH provide the seams;
they do not provide browser durability or original-attempt reconciliation.

## Decision

**Words:** 「保留到成功恢復或手動刪除（建議）」 — Kent, 2026-10-19

Kent also authorized the accepted four Pilot slices on 2026-10-19 and accepted
「接受本切片的非 SQL 例外（建議）」 on 2026-10-20, bounded to browser storage,
actual schema/upgrade/data-preservation proof and independent review. That
exception does not authorize server tables or SQL migrations.

**Options considered:**
- Origin-local immutable IndexedDB versions with strict transaction completion,
  explicit review/apply and exact-version cleanup.
- One mutable draft per room or automatic cloud restoration; these cannot
  preserve independent/newer versions and the accepted confirmation boundary.
- A remote draft backend, custom encryption service or new cloud concurrency
  protocol; these exceed the accepted architecture and device-owner trust scope.

**Recommended:** Origin-local immutable IndexedDB versions and explicit restoration.

`server/client/human-drafts.ts` owns the browser schema and upgrade. Each mount
has fresh draft/tab identifiers; writes append a validated document snapshot and
advance its lineage head in a strict transaction. Only transaction completion
acknowledges local saving. History records a successfully activated room, scoped
to origin, backend and original verified person. Browser storage loss and denied
persistent-storage permission remain visible limits.

`HumanDraftPanel` checks the original person/current room before reading or
rendering content. Its native preview uses a detached `not-synced` store. It
never attaches that retained payload to a live sync client. `humanSocket`
checks current identity before delivery/send/connect and closes on failure;
reverting cookies or regranting permission does not reopen the old mount.

An explicit apply rechecks current cloud fingerprints and durably records the
exact-version attempt and local lease before sending the existing complete-record
PATCH. The shared audit reserves before mutation and stores a versioned optional
context/request fingerprint in the existing metadata value. Receipt readback
requires the same verified person and current exact room. Older receipts without
correlation remain inconclusive; no server table changes or receipt backfill occur.

Cleanup requires original committed-attempt evidence, exact record/absence
readback and a fresh cloud sync observation. Unknown replies, finalization gaps,
expired leases and crashes never imply nonexecution or automatic resend. An
explicit original-person deletion targets one local version and has no cloud
cancellation or rollback effect; a denied room permits content-free deletion
but no content review. Other/newer versions and unknown attempt evidence remain.

## Consequences

The document engine and complete-record last-writer semantics stay unchanged;
preflight is not compare-and-swap and a concurrent writer can act afterward.
Audit and document commits are separate, so some outcomes can remain unknown.
There is no exactly-once, encrypted-at-rest or remote-erasure promise. Same-origin
scripts and the OS/browser-profile owner remain trusted; credentials, private
transcripts and agent process state are not draft payload sources.

The feature follows the existing default-off human-entry opt-in. Real browser
fault/reopen/crash, account isolation, both local adapters and usability evidence
are separate from configured provider, physical-device and Cloudflare Free fit
acceptance. A server schema/table change or new concurrency requirement reopens
the scope with the Captain rather than extending this exception.
