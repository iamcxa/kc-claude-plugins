# Retained-use operator preparation

This task-only disposition follows Captain amendment 6 and preserves the corrected starting candidate and prior accepted verification. It grants no gate, PR, merge, paid-service or production-rollout approval.

The implementation worker observed that existing room archives exclude authorization policy, while existing Node host metadata and room export/restore controls can support recovery. For an operator relying on a backup, restoring room contents alone would not recover access safely. This is an owned readiness gap against AC-4 and AC-5, not evidence that prior document recovery failed.

FO authorizes one narrow stopped-Node operator helper under scripts/docs: reuse existing metadata/export/restore implementations, require stopped writers and a fresh restore target, preserve document/asset archives with digest-only policy, quarantine archived credentials as revoked, and require newly issued credential IDs to resume. Do not change Node server behavior, APIs, room UI, dependencies or concurrency. Reuse the existing protected local grant-file helper unchanged.

Cloudflare retained operation also needs a concrete private backup/restore/revocation path. Investigate authenticated local operator tooling with remote Durable Object bindings using official documentation and existing internal controls. Preparation is allowed; no public admin endpoint or provisioning is approved by this ruling. Return a concrete plan or evidence-backed limitation before any runtime change. The licensed retained browser build remains an independent prerequisite; no license-check bypass is authorized.

Only conclusions belong in this public record. Provider details, measurements, exact local receipts and credentials remain local. Independent validation follows the new operational deliverable; accepted green lifecycle and native-client suites are not repeated by default.
