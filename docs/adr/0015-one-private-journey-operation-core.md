# 0015. Keep one private journey operation core across Node and Cloudflare

Date: 2026-10-13

## Status

Accepted

## Context

The existing journey canvas uses one tldraw room coordinator, SQLite persistence,
YAML-derived records and complete-record writes. A private pilot needs Node local
and remote endpoints plus Cloudflare without a second renderer, document protocol
or provider-specific agent workflow. The accepted design is recorded in
`journey-server-host-pilot` on the existing workflow state branch.

## Decision

**Words:** 「可以，接受這個監控例外，照設計進入實作，房間切換 UI 跟並發規則維持不動。」 — Kent, 2026-10-13

**Options considered:**
- One shared operation and authorization core with Node and Cloudflare adapters.
- Independent document logic per HTTP, MCP and provider transport.
- Multiple room coordinators sharing a database.
- Require identical process-residency meaning for Cloudflare health telemetry.

**Recommended:** One shared core with platform-specific persistence and socket lifecycle, accepting sampled Cloudflare health telemetry.

`server/host/core.ts` owns validation and GET/PATCH/PUT mutations;
`policy.ts` owns grant/session/room admission. HTTP and the stateless MCP endpoint
use `transport.ts`; socket admission and assets use that policy. Preserve GET
auto-create, acknowledged room inventory, complete-record last-writer PATCH,
snapshot PUT, tldraw-owned schema and existing YAML/readback behavior. No version
precondition, room switcher or record migration is introduced.

Node local and remote use the same adapter. Cloudflare uses one SQLite Durable
Object per room plus a strongly consistent metadata registry and scoped R2 assets.
Its `health.active` samples authorized registered rooms and can wake them; it is
not Node's resident-map metric. Registry failure must prevent a successful room
acknowledgement and a retry can register an initialized room.

Private mode starts in separate empty storage. Explicit room-associated assets
cannot adopt old global files by guessing. Node save and checkout capabilities
require operator configuration; Cloudflare reports them unsupported. Credentials
stay out of records and URLs. Browser access uses same-origin Secure HttpOnly
sessions; configured page-link base and CLI bearer injection are the accepted
transport changes.

## Consequences

A synthetic journey can exercise the same CLI/MCP and canvas against local
adapters. Session expiry, revocation, inventory failure and snapshot-plus-asset
recovery need behavioral evidence. The local emulator is not hosted parity or
real hibernation evidence. No resource provisioning, paid service, production
rollout, retained-data migration or formal tldraw licensing decision is authorized.
Those needs, broader browser origins or changed write semantics reopen the
appropriate Captain decision.

### Delivery scope amendment

**Words:** 「可以，照最小範圍恢復交付：本機 Node、Cloudflare、Sites 入口跟 Claude／Codex CLI 共編，先補齊持續使用條件。Cloudflare 維持免費方案，用量明細只留本機，房間切換 UI 跟並發規則不動。」 — Kent, 2026-10-14

**Options considered:** Resume the full original host matrix, or prepare the
smaller local Node/Cloudflare/Sites/native-CLI slice while preserving existing
capabilities and historical evidence.

**Recommended:** Prepare the smaller slice with explicit license, scoped
credentials, policy-aware backup, fresh restore and rollback prerequisites.
Remote Node, hosted assets/photos, the original desktop plugin binding and Netlify
are deferred. Independent operator scripts reuse the existing host metadata and
recovery functions; no public admin route or new identity service is added.
Restore quarantines all archived credentials because a backup cannot establish
which IDs were revoked later. New IDs require deliberate current allowlists.
Detailed operational evidence stays local; readiness, deployment and acceptance
remain separate decisions.
