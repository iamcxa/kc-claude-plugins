---
title: Use one private kc-jmap server contract on Node and Cloudflare
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:journey-server-host-pilot:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:journey-server-host-pilot-backlog-1
              briefing:
                id: briefing:journey-server-host-pilot:backlog:attempt-1:revision-1
                digest: sha256:bd36dba2158df768c3c5ad5568ae62601e9e9ed6e69a02ba7b3a593bcfdea025
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-server-host-pilot:backlog:1
                briefing: briefing:journey-server-host-pilot:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T08:47:12.490245Z"
                decision: approve
                reason: Captain accepted the minimal scope with 可以，就照這個最小範圍 and authorized starting dev2; after the explicit profile question, Captain selected 改用 pilot（建議）. This accepts direction and entry to ideation only; no implementation/design acceptance, deployment, PR or merge authority is inferred.
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-13T08:47:34Z
---

Kent approved a minimal reusable server-host refactor, with the same agent access model (base URL and a per-agent credential) for Node.js locally/remotely and Cloudflare. This is a new pilot task; it does not reopen, migrate, or replace the older hosted POC tasks.

## Scope

Captain authorization, 2026-10-13: "可以，就照這個最小範圍，用 dev2 的 poc profile 開始做，保留 Node 本機／遠端跟 Cloudflare 兩種接法，房間切換 UI 跟並發規則先不動。還是你認為應該走 pilot？" The explicit subsequent profile decision was "改用 pilot（建議）" in response to the question describing a retained Node/Cloudflare shared server with room-switching UI and concurrency unchanged.

Preserve kc-jmap's canvas behavior, YAML authority, record/schema formats, current API paths and read/write semantics. Extract shared room/doc operations; keep platform storage, room lifecycle, room inventory, assets and transport adapters separate. MCP wraps the same operations and authorization policy, never another business-logic implementation. Node local and remote use the same adapter. Cloudflare uses Durable Objects. Agent configuration is base URL plus credential; do not add provider-specific agent workflows.

Preserve GET-created rooms and immediate /health room visibility after successful creation. Preserve the current absence of expected-version checks; POC 409 rejection is not the baseline contract. Keep default local output unchanged. Explicit minimal exceptions: configurable pageLink base and optional CLI credential injection; authentication and room authorization are new access conditions across HTTP, MCP, WebSocket and assets. Node /save and /repo-doc remain available when their filesystem/checkout capability is configured, including remote Node. Cloudflare capability gaps must be visible and explicitly bounded, not described as full parity.

Use the existing repository and the simplest adapters that can serve this one private journey. Sites remains the existing entry; do not replace or redeploy the accepted live POC in this task's design stage. Netlify integration, room/project management UI, room switching UI, new /api/v1 paths, concurrency upgrades, record migrations, new product behavior, broad exposure, paid-plan upgrades, merge and production rollout are excluded. Local hostname/IP coexistence is configuration documentation, not a DNS service or certificate-authority project.

Execution budget: one bounded ideation worker before the design gate; no provider spend or deployment during ideation. Implementation and independent validation follow the approved design. Stop and return a concrete decision if preserving an existing observable contract is impossible, credentials or shared resources must be broadened, a paid service is necessary, or real-data migration is needed. Do not silently widen scope to satisfy a check.

## Evidence and context

Source baseline at admission: iamcxa/kc-claude-plugins main 6d0f8da951b5ea9ea50fca6bd3685fc360bf502f; installed dev2 and adopted source workflow are 0.21.0.

Accepted consultation: /Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-refactor-consultation-2026-10-13.md. Two live FO rounds agreed to preserve read-created rooms and immediate room-list visibility; /save and /repo-doc require a capable Node host, not literal localhost.

Existing POC evidence is at /Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-sync-poc/.worktrees/spacedock-ensign-durable-room-free-probe/durable-room-probe/evidence/validation-canvas-review.md. It proves bounded A/B synthetic-note MCP behavior, not full journey-render/read parity. Do not inspect credential files in neighboring directories. Formal tldraw licensing, actual billing, large PATCH free-tier limits and new A/B hibernation remain unverified.

## FO alignment

Alignment: not needed before ideation: Kent approved the exact minimal scope and explicitly selected pilot. Design authors may resolve routine mechanisms within it but must identify actual capability gaps and decisions at the design gate.
Surfaces: db
Visible change: none
Release review: not needed: this is a server-host infrastructure refactor with no user-approved journey release membership; do not invent or alter release mappings.

## Acceptance criteria

**AC-1**: The same journey read/render operations and MCP wrapper can access an authorized room on Node local, Node remote and Cloudflare using only endpoint and credential configuration, preserving record formats and existing canvas behavior.
Verified by: One reproducible fictional journey exercised through the existing CLI and thin MCP entry on each adapter, with browser readback and explicit separation of local/emulated versus hosted evidence. Design must name actual commands and unavailable steps; implementation must not claim all three from a local-only run.

**AC-2**: Existing observable doc and room contracts remain unchanged apart from the explicitly approved authentication conditions and configurable origin.
Verified by: Baseline-versus-candidate checks for GET/PATCH/PUT response and mutation semantics, immediate /health visibility after successful room creation, unchanged local output and page links by default, and unchanged concurrent-write rules.

**AC-3**: Allowed principals share the same room while unauthorized access and A/B cross-room access are denied consistently across supported HTTP/MCP/WebSocket/assets entry points.
Verified by: At least two independent test principals, positive same-room read/write readback and negative credential/room checks; no production credentials or personal data in evidence.

**AC-4**: Platform adapters preserve stored room data and provide explicit file/checkout capability boundaries suitable for bounded real use.
Verified by: Node restart and Cloudflare hibernation/reconnect readback, room-inventory consistency, asset roundtrip where supported, and tests/documented behavior for Node /save and /repo-doc and Cloudflare unsupported capability handling. Evidence distinguishes existing proof from checks rerun on this candidate.

**AC-5**: The retained implementation is minimal, recoverable and does not broaden the approved product scope.
Verified by: Shared operation ownership and adapter dependency review, a bounded setup/recovery/rollback procedure using synthetic data, no room-switching UI/concurrency/API-v1 changes, and explicit remaining deployment, cost and license limitations.

## Number guards

Not applied: design stage only; no migration, provider provisioning or deployment authorized at this stage. Reserve ADR/migration numbers only at implementation dispatch when the approved design determines they are required.
