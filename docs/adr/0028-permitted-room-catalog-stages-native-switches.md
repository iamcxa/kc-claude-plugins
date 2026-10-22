# 0028. Read room metadata and stage a target before leaving the source

Date: 2026-10-20

## Status

Accepted

## Context

The accepted private canvas design keeps the native editor, original room IDs
and complete-record concurrency. Its human-entry prerequisite at
`afcf5bc2dad60c485efd07e8fda01a48245229ae` establishes current member admission.
The old room selector used health telemetry and destroyed the source editor
before target sync succeeded. Cloudflare health samples each permitted document.

## Decision

**Words:** 「可以，確認這份整體設計，照最新版 dev2 的 pilot 分四個切片開始實作。Cloudflare 維持免費方案，既有畫布資料與並發規則不動，用量明細只留本機，正式合併前再讓我確認。」 — Captain, 2026-10-19

**Options considered:**
- Read registered metadata through current human policy and stage target sync.
- Reuse document health for room discovery and navigate before target connection.
- Replace document storage or add a room-management platform.

**Recommended:** Extend existing metadata and native controls; keep the opt-in
human entry disabled until separate provider and stream-safety acceptance.

`GET /auth/rooms` intersects current human grants with existing `room:` metadata.
It returns stable IDs and optional display names, without constructing document
stubs, reading documents, sampling activity or registering rooms. Labels grant
no authority. A, B and qnow-day2 retain their exact IDs; future registered rows
need no frontend allowlist change. Legacy health and agent contracts remain.

A switch checks source authority, completes the existing gesture and performs
one bounded source readback. Failed or unequal confirmation retains the same
editor. The selected target is admitted and synchronizes without an editor;
activation rechecks both rooms and the unchanged source document fingerprint.
The source editor/socket survives until that activation, while failed, timed-out
or stale targets are disposed. The URL and successful-room history change with
activation. Source changes during staging require a visible retry.

A known source denial freezes the retained editor and disconnects its sync
client. It does not reread or flush that source. A separate explicit action opens
another room in a new tab, where entry admission runs independently. This local
preservation is not generalized stream-revocation or durable-draft proof.

## Consequences

Both metadata adapters use their existing SQLite key/value storage, with no SQL
or document-schema migration. Native menus keep search, bounded scrolling,
exact identifiers, focus return, themes, page controls, document popup and save.
Unconfirmed complete-record changes can conservatively delay a switch; this is
not an atomic write acknowledgement or a changed conflict-resolution contract.

Pairing, durable interrupted-context recovery, credentials, generalized outgoing
stream stops, provider deployment and final merge remain separate work. The
human entry remains off by default; retained production activation is unapproved.
