# 0026. Verify human entry before opening an existing private room

Date: 2026-10-19

## Status

Accepted

## Context

The existing private host already authorizes legacy bearer credentials and short
browser sessions through shared policy. Those credentials do not establish a
verified person. A shared URL must select its exact authorized existing room,
without replacing document storage, complete-record writes or concurrency.

## Decision

**Words:** 「可以，確認這份整體設計，照最新版 dev2 的 pilot 分四個切片開始實作。Cloudflare 維持免費方案，既有畫布資料與並發規則不動，用量明細只留本機，正式合併前再讓我確認。」 — Captain, 2026-10-19

**Options considered:**
- Extend shared admission with typed human identity and additive metadata.
- Treat an existing bearer credential or principal label as human identity.
- Replace room authorization and documents with a general identity platform.

**Recommended:** Extend existing admission and metadata; leave the new entry off
until its separate safety and provider evidence is accepted.

An enabled member is bound explicitly to an issuer and stable subject by the
operator, never by a display label, email, raw header or first visit. Browser
sessions have a short expiry and a fixed seven-day deadline anchored to a
verified human event. Renewal preserves that event and deadline. Existing
credentials retain their original expiry and scopes and cannot mint humans.

Owner-local Node uses an explicitly approved, one-use, 60-second original-tab
challenge through a protected Unix socket with actual peer-account verification.
Remote Node and Cloudflare use pinned signed Access assertions correlated with
the provider's original human-login event. Missing evidence fails closed.
Application data routes keep typed errors and their shared authorization policy.

The new human entry checks current membership, exact room grant and registered
room before opening a document. This amends ADR 0018 only at human entry; legacy
explicit document creation and complete-record concurrency remain unchanged.
Persisted authorization generations prevent removed/regranted authority from
reviving old sessions. Original browser context binds backend, member and sign-in
event, so changing a shared cookie cannot reconnect a different human context.

## Consequences

One native entry can use both persistence adapters without migrating canvas
records. Metadata initialization is additive and versioned in the existing
SQLite key/value table; transactional challenge consume and session mint share
one commit. Receipt cleanup never removes security state or live typed sessions.

This first story does not implement agent pairing, secure installation storage,
stream-stop leases or durable drafts. Local proofs are separate from actual
provider login/session precedence, account eligibility and hosted route checks.
Disabling the new entry preserves metadata and revocations; rolling security
metadata backward is never a rollback mechanism. Formal merge remains reserved.
