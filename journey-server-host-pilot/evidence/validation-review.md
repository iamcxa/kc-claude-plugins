# Independent validation — private journey host pilot

Verdict: **PASSED for the dispatched local/emulated pilot validation.** No demonstrated Material defect and no repair authorization requested. This verdict is not hosted readiness, provider hibernation proof, deployment approval, or a claim that the unrun portions of AC-1/AC-4 are complete.

Candidate: `4f678cd88eddbcc171df7e2037dd19d2fbf4065b`; admitted base: `6d0f8da951b5ea9ea50fca6bd3685fc360bf502f`.
Product checkout: `/Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/.worktrees/spacedock-ensign-journey-server-host-pilot`, branch `spacedock-ensign/journey-server-host-pilot`. Tracked product files remained clean throughout validation. Only task evidence/report files are committed.

## Evidence boundary and criteria

| Criterion | Exact-candidate assessment | Limit |
| --- | --- | --- |
| AC-1 — same journey and access configuration | Source has one document core, one policy, one Node adapter for local/remote, and a Cloudflare Durable Object adapter. Read the primary 19-group Node and 20-group Cloudflare-local implementation receipts, CLI output, and real-origin browser screenshots; they show the fictional journey and HTTP/MCP equivalence. The independent cookie/MCP transport probe passed on both adapters. | Hosted Node/Cloudflare were not run. A second loopback port is not remote evidence. No new UI or renderer was introduced. |
| AC-2 — observable compatibility | Compared baseline/candidate core and the CLI/client diff; read the implementation's baseline comparison, invalid-write, immediate inventory, stale full-record PATCH and PUT replacement receipts. Independent authorized inventory/active filters passed. Default page links remain localhost; optional origin changes only new links. | The broad deterministic compatibility suite was read, not rerun. The approved Cloudflare active-field sample differs from Node residency. |
| AC-3 — room and principal isolation | Independently exercised cookie HTTP/MCP/assets/new-socket denial, same-ID A/B bytes, authorized shared writes, initialized socket updates, parent revocation/expiry and persistence of revocation. Both adapters passed. | Local and emulated transports only. No production credentials or real canvas data. |
| AC-4 — persistence and capabilities | Independently exported latest scoped bytes, rejected restore into an existing room and duplicate-asset archives, restored into fresh storage and restarted/read back. Read the primary browser reconnect, Node save/repository capability and Cloudflare unavailable/501 receipts. | Actual provider hibernation and remote recovery are not run. Cloudflare-local restart is eviction/reconstruction evidence only. |
| AC-5 — minimal and recoverable scope | Every retained module maps to the accepted shared-core, access, platform or recovery boundary below. Read the setup/recovery/rollback instructions and the primary unchanged-baseline rollback receipt. Source diff preserves room UI, concurrency, schema and YAML authority. | No retained-data migration, deployment, provisioning, PR publication, merge, release or production rollout. CI was not changed; cost per PR was not measured. |

Primary receipts read: [Node implementation](implementation-node-result.json), [Cloudflare-local implementation](implementation-cloudflare-local-result.json), [implementation checks](implementation-checks.json). The hostname screenshots for both adapters were visually inspected; they show the same fictional canvas, with Node save visible and Cloudflare save absent as documented. Those screenshots and the browser execution are implementation evidence, not a new browser run by this validator.

Independent execution: [Node](validation-node-result.json), [Cloudflare-local](validation-cloudflare-local-result.json), [required checks](validation-checks.json). The focused [probe](validation-probe.py) reuses the exact candidate's disposable host runner and replaces its test body in ignored scratch; it neither edits product bytes nor overwrites implementation evidence. This uses the existing setup and transport helpers rather than adding a product test framework.

## Decisive counterexamples and observed timing

- Cookie principal B tried to read A's room, call MCP PATCH on A, and fetch/overwrite A's same-ID asset. Each returned 403; A and B bytes remained distinct. Removing shared room authorization or using a global asset key would fail these checks.
- An exported shared-room archive contained the latest acknowledged asset bytes. Existing-room restore and duplicate-asset input were rejected; the invalid fresh target remained absent from health. Fresh restore then survived restart with identical records and bytes. Node additionally emitted two explicit operator error receipts, so its timeout-shaped client rejection is not the sole evidence of refusal.
- A real tldraw protocol connection first received an authorized page update. Parent credential revocation then denied cookie document writes, MCP reads, asset reads and new sockets with 401. An initialized socket and an idle pre-handshake socket both reached actual close events with code 1008; no new private update reached either after acknowledgement. At acknowledgement these clients were already CLOSING or CLOSED, so the probe does not claim a post-close frame was successfully sent.
- Parent expiry denied the same cookie routes and new sockets, and no new private update reached the expired initialized socket. Removing the current-grant/deadline checks, leaving a live subscriber attached after revocation, or reimporting revoked grants at startup would fail these observations.

| Observed event | Node | Cloudflare-local |
| --- | ---: | ---: |
| Operator revocation acknowledgement | 6 ms | 31 ms |
| Initialized socket actual close event | 7 ms | 21 ms |
| Idle socket actual close event | 7 ms | 30,023 ms |
| Initialized socket actual close after expiry | 3 ms | 5 ms |

These are one-run local measurements, not latency guarantees. The Cloudflare-local idle client was CLOSING at acknowledgement; its actual close event was required within 35 seconds. The adapter waits for server-side CLOSED and otherwise returns partial/503, and the observed operator response was `complete:true`. This reproduces the implementation's approximate 30-second idle-client delay while separating it from an initialized connection. The initialized expiry test covers deadline enforcement; the original implementation's idle expiry receipt remains separate.

## Goal sufficiency and minimal necessity

| Retained surface | Accepted goal or safety/lifecycle boundary | Without-it observation |
| --- | --- | --- |
| `host/core.ts` | Shared existing GET/PATCH/PUT validation and mutation semantics, AC-1/AC-2 | Separate transport mutations would duplicate the accepted complete-record contract; the core delegates to existing tldraw storage operations. |
| `host/policy.ts` | One deny-by-default grant, room, origin and session policy, AC-3 | Baseline has no private policy; the independent cookie and cross-room counterexamples require one shared admission rule. |
| `host/transport.ts` | Existing HTTP shapes plus thin MCP/session/capability/asset plumbing, AC-1/AC-3 | Agents and browsers otherwise cannot enter the same private operations; MCP calls the same core rather than a second renderer. |
| `host/node.ts` and thinner `canvas-server.ts` | Node persistence, process/socket lifecycle and configured filesystem/checkout capabilities, AC-4 | Deleted `rooms.ts` behavior was moved here. One adapter serves local/remote; separate remote business logic was not added. |
| `host/cloudflare.ts` | Durable Object room ownership, strong inventory, session lifecycle and scoped R2 bytes, AC-4 | Node filesystem/process ownership cannot provide this platform boundary. Registry failures cannot be hidden as acknowledged rooms. |
| `host/recovery.ts` and stdin operator control | Complete snapshot-plus-asset recovery, revocation and explicit partial-failure behavior, AC-3/AC-5 | A document-only snapshot loses assets; public admin/account services would broaden scope. Writes are quiesced for export by documented procedure. |
| `lib/api.mjs`, page-link option and client room query plumbing | Same credential configuration; room-scoped assets/save/repository context, AC-1/AC-3 | Existing fetches lack bearer injection and global assets collide. No room-switching UI or schema migration was introduced. |
| Grant and browser setup scripts | Digest-only issuance, explicit session exchange and trusted origin entry, AC-3 | Private mode otherwise has no bounded setup route. Existing credential IDs remain immutable; rotation uses a new ID and revocation. |
| Cloudflare-local/contract runner; locked esbuild/Miniflare/Playwright dev dependencies | Bundle actual adapter; emulate real platform interfaces; exercise real browser origin and lifecycle, AC-1/AC-4 | A mock or source-only check would not demonstrate these seams. Installed versions match the candidate lockfile; no existing dependency version was intentionally changed. |
| Private-host documentation, ADR 0015 and reference links | Explicit capability gaps, approved telemetry exception, recovery/rollback and deployment stops, AC-4/AC-5 | Users otherwise cannot distinguish local proof from hosted authority or preserve legacy storage during rollback. |

The retained modules serve the current accepted journey or its named safety/lifecycle boundaries, not hypothetical scale. This assesses necessity of responsibilities; it does not claim the implementation has a mathematically minimal line count.

## Findings in workflow categories

**Material:** none demonstrated at this candidate in the supported, dispatched local/emulated workflow.

**Deferred risk — hosted/provider behavior has no execution evidence.**
- Released user and normal workflow: the private pilot operator later selecting an explicitly authorized hosted Node/Cloudflare endpoint with the existing CLI, MCP and same-origin browser.
- Observable harm: none demonstrated locally; remote TLS/proxy/cookie routing, true hibernation/resume, provider limits, costs and formal licensing remain unverified.
- Affected value acceptance criterion or non-negotiable boundary: `value-ac[AC-1]` requires the same hosted journey; `value-ac[AC-4]` requires provider lifecycle readback; `value-ac[AC-5]` forbids silently broadening deployment/cost/license obligations.
- Trigger evidence: all implementation and independent receipts label hosted/provider hibernation/billing/licensing NOT RUN; the delivered setup provisions no hosted target. It becomes Material only if an authorized supported hosted run demonstrates failure of a protected contract, or delivery claims those obligations already passed.

**Polish:** none retained.

**Needs decision:** no new product/scope decision raised. The existing full-number-guard limitation follows the committed FO tooling disposition below. Hosted use still needs its already-recorded separate authorization.

## Required tooling disposition

All exact commands, exits and stdout are in [validation-checks.json](validation-checks.json). ADR lint checked 14 records, 0 legacy, including reserved 0015. Comment ratio is 1148 code lines, 0 added comment lines, 0.0% against 5%; added code was read. Dispatch records: 6 complete. Design surfaces presentable. Diff check clean.

The full task-aware `number_guards.py check` was attempted and exits **2**:
`number_guards: task has Surfaces: db but no migrations-path is declared (pass --migrations-path or set migrations-path: in the workflow README)`.
Disposition: **SKIPPED as unavailable/inapplicable, explicitly NOT PASS**, per [implementation-2](../dispatch/implementation-2.md). The no-task supplementary invocation exits 0 but explicitly skips migration checking and R4. Independently compared the current reservation with the actual diff: sole added ADR is 0015; there is no SQL diff and no task-authorized migration/applied deployment. Runtime metadata initialization is for fresh synthetic storage; no actual candidate migration or reservation conflict was found unprotected. No fake path, changed surface or modified helper was used.

Document impact lists `kc-journey-map/docs/private-host.md` as updated and `docs/journey/kc-journey-map/README.md` for review. Its existing legacy-local import/export journey and canonical YAML authority remain valid; implementation's unaffected rationale is accurate. The private-host instructions and linked canvas/README entries match the opt-in transport behavior and capability gaps.

## Acceptance and cleanup

Run the four exact ordered steps in [validation-acceptance.sh](validation-acceptance.sh) from a fresh shell. [Acceptance notes](validation-acceptance.md) state prerequisites and observations. Focused executed groups total approximately 17 seconds on Node and 36 seconds on Cloudflare-local, plus startup/preflight; allow two minutes, bounded under five with installed dependencies. Broad legacy/type/build suites were not repeated solely for independence.

The initial sandbox attempt failed before binding a loopback port with EPERM; an authorized local test run then passed. Final read-only process inventory found no candidate-owned test server/emulator. Product HEAD and tracked status were rechecked clean. The task remains in validation for FO's unchanged-script run and Captain gate; no stage transition, product push, PR, merge or deployment was performed.
