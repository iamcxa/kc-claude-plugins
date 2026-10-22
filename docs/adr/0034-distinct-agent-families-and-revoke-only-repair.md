# 0034. Bind each agent installation to exact human consent and rotating authority

Date: 2026-10-19

## Status

Accepted

## Context

Human entry establishes a current verified member but cannot identify an agent
installation. Persistent agents need independent attribution, current room
authority and protected rotating secrets. A lost rotation/redemption reply cannot
safely be retried with old material. The accepted Pilot design supplies these
boundaries while retaining existing complete-record operations.

## Decision

**Words:** 「可以，確認這份整體設計，照最新版 dev2 的 pilot 分四個切片開始實作。Cloudflare 維持免費方案，既有畫布資料與並發規則不動，用量明細只留本機，正式合併前再讓我確認。」 — Captain, 2026-10-19

**Options considered:**
- Distinct installation families, exact inspected human consent, atomic rotation
  and authenticated revoke-only recovery.
- Treat legacy credentials or installation labels as verified human authority.
- Retry spent refresh secrets or return replacement secrets after unknown outcomes.

**Recommended:** Distinct attributed installation families and conservative
revoke-only repair, retained behind a disabled default.

Only the exact current human approves an immutable room/capability disclosure.
Consent binds the inspected session, verified event, backend and original room.
The original initiating verifier consumes a five-minute request once, creating
one family with short access and a rotating refresh secret. Every admission and
rotation intersects current backend/policy, member and room generations.
Human seven-day sign-in age and inactivity never expire a valid agent family.

Store only digests on the server. SQLite transactions cover consume, rotation,
revocation and required lifecycle evidence. Typed-error results commit rate
accounting and authenticated replay tombstones; actual storage failures roll
back the entire transaction. A guessed secret changes no existing family.

The minimal stdio MCP helper pins its endpoint/backend, refuses redirects,
serializes operations and holds an operating-system process lock. On macOS,
versioned application-owned Keychain items protect secrets. A nonsecret durable
pointer publishes a new slot only after protected-save confirmation and
readback. A separate nonsecret checkpoint protects the preceding repair slot until
manifest confirmation completes. Failed or uncertain confirmation quarantines
staging for queued/later calls and restart, including a manifest already pointing
at the new slot. Reconciliation retains original or spent authenticated repair
material. No plaintext secret fallback exists.

Unknown redemption, refresh or protected-save outcomes permit only authenticated
cancel/revoke confirmation and then fresh human-approved pairing. Current or
spent refresh proof can revoke, never mint or retrieve a secret. Unknown revoke
remains paused. Disabling and reenabling policy advances its generation; rollback
must retain security metadata and cannot resurrect old authority.

## Consequences

This adds versioned keys to the existing metadata table, without SQL/schema files,
canvas migration or core/concurrency changes. Node file scopes and Cloudflare
capability differences are disclosed exactly. Legacy grants keep their original
expiry and semantics, including preexisting identifiers sharing an agent prefix.

This foundation stays disabled. Active-stream stop, real provider acceptance,
independent native Claude/Codex collaboration and physical-phone acceptance are
separate obligations; local denial is not stream-stop or hosted proof.
No provider setting, production credential migration, publication or merge is
authorized by this record. Formal merge remains the Captain's decision.
