# 0029. Commit denial before bounded stream stopping and preserve security recovery state

Date: 2026-10-20

## Status

Accepted

## Context

The implementation candidate remains disabled pending independent validation and provider evidence.

The prior human-entry fixture denied a new HTTP request while an existing viewer
received a later update. Pairing preserved family denial but outgoing delivery
checked credential expiry alone. The accepted private-entry journey needs an
authoritative denial transaction and a separately observed stream stop.

## Decision

**Words:** 「可以，確認這份整體設計，照最新版 dev2 的 pilot 分四個切片開始實作。Cloudflare 維持免費方案，既有畫布資料與並發規則不動，用量明細只留本機，正式合併前再讓我確認。」 — Captain, 2026-10-19

**Options considered:**
- App-issued authority, transactional denial, bounded outgoing leases and separate close acknowledgment.
- Provider-only removal or admission-only denial: does not stop an already admitted stream.

**Recommended:** transactional app denial plus 30-second outgoing authorization leases, bounded indexed notification and explicit close acknowledgment.

Every actual outgoing send checks its absolute lease, original credential expiry
and known invalidation. The current exact room grant also caps the lease;
notification visibility precedes final authoritative registration and initial
sync. An aborted upgrade emits no private snapshot and clears its unused index. Incoming writes require fresh policy. Node uses existing
per-socket one-shot timers. Cloudflare stores exact attachments, refreshes at most
64 due sockets concurrently per wake/alarm and closes excess due sockets for
reconnect; one persisted earliest room alarm replaces any permanent interval.
The observed stop target is at most 60 seconds; it is experimental, not a provider
service guarantee. Already admitted operations retain their existing semantics.

A member revokes their own family or browser session. Member-disable, room policy,
legacy authority and audit/recovery remain protected operator operations. Reserve
audit before mutation, preserve uncertain final outcomes, and reject reuse of an
uncertain operation ID. Close confirmation requires registered stream close
acknowledgment, independently of durable denial or notification success.

Security records stay in the existing metadata table. Generations, tombstones,
consumed requests and spent repair proof outlive ordinary 30-day receipts.
Synthetic cutover inventories every declared consumer and verifies original-room
sentinel read/write before matching legacy revoke; inventory completeness is an
explicit operator attestation, never inferred from labels. No expiry extension.
Fresh restore quarantines archived authority and requires new backend/member and
credential IDs. The Node directory version and immutable human configuration
version refuse the tested older binary; rollback retains current security state.

## Consequences

The account sheet distinguishes denial, stopping, unknown and confirmed close.
Missed notification can still use leases; policy outage refuses renewal. Local
emulation proves tested seams, not provider scheduling, physical transport bounds
or Free workload fit. Arbitrary filesystem/provider rollback by an administrator
is outside the supported recovery path and must stay offline. Activation,
production cutover, deployment and formal merge need their separate evidence and
Captain decision. No paid service, SQL migration, new table or canvas schema was
introduced. Captain's 2026-10-20 narrow exception skips SQL-numbering success only;
the raw configuration error remains recorded by the task.
