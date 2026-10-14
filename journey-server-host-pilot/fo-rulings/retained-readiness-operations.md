# Retained-use operator preparation

This task-only disposition follows Captain amendment 6 and preserves the corrected starting candidate and prior accepted verification. It grants no gate, PR, merge, paid-service or production-rollout approval.

The implementation worker observed that existing room archives exclude authorization policy, while existing Node host metadata and room export/restore controls can support recovery. For an operator relying on a backup, restoring room contents alone would not recover access safely. This is an owned readiness gap against AC-4 and AC-5, not evidence that prior document recovery failed.

FO authorizes one narrow stopped-Node operator helper under scripts/docs: reuse existing metadata/export/restore implementations, require stopped writers and a fresh restore target, preserve document/asset archives with digest-only policy, quarantine archived credentials as revoked, and require newly issued credential IDs to resume. Do not change Node server behavior, APIs, room UI, dependencies or concurrency. Reuse the existing protected local grant-file helper unchanged.

Cloudflare retained operation also needs a concrete private backup/restore/revocation path. Investigation found that direct remote Durable Object development bindings are unsupported, while official documentation supports a remote service binding to a Worker that accesses Durable Objects. The existing application intentionally provides no operator route.

FO authorizes the smallest isolated operator bridge under scripts/config using existing Durable Object controls. It must disable workers.dev and preview URLs, have no public routes, allow only explicit export/restore/revoke operations rather than arbitrary forwarding or SQL, and be invoked through authenticated Wrangler service-binding tooling. Preserve fresh-target restore safety and revoked-policy handling. This adds an operator tool, not a public application API, and must be independently validated.

Local service-binding tests and a concrete deployment/measurement/rollback plan are authorized. Before a cloud action, submit that plan to FO for scope confirmation. The maximum new proof topology is one disposable document-only backend plus one private operator bridge; no retained rooms, R2, paid enrollment or retained serving is authorized before the necessary prerequisites. Cleanup is part of any proof. The licensed retained browser build remains an independent prerequisite; no license-check bypass is authorized.

Only conclusions belong in this public record. Provider details, measurements, exact local receipts and credentials remain local. Independent validation follows the new operational deliverable; accepted green lifecycle and native-client suites are not repeated by default.
