# Authorized Cloudflare hibernation correction

Baseline candidate: 4f678cd88eddbcc171df7e2037dd19d2fbf4065b.
Captain amendment 5 now authorizes a separate minimal Cloudflare-only correction and bounded retest. The prior hold and candidate remain historical evidence; do not rewrite them.

## Finding and FO disposition

- Released user and normal workflow: the private pilot operator and authorized agents leave a hosted Cloudflare room idle between work.
- Observable harm: the current Cloudflare TLSocketRoom uses a finite default client timeout, registering a recurring pruning timer. That timer prevents the coordinator from entering the intended hibernation state and invalidates the claimed lifecycle/usage boundary.
- Affected boundary: value-ac[AC-4] requires actual Cloudflare hibernation/reconnect preservation; captain-ruling[2026-10-13] requires a Free-only hosted check and actual usage observation.
- Trigger evidence: candidate server/host/cloudflare.ts omits clientTimeout; installed sync-core 5.4.0 schedules a pruning interval for the default finite timeout. An unchanged-candidate local runtime observer confirmed timer registration and firings. Detailed receipt stays local in outputs/journey-server-host-pilot-usage/timer-falsifier-result.json.

Classification: owned Material. FO disposition: FIX AUTHORIZED, narrowly under amendment 5, followed by independent validation. This is distinct from the worker's prior advisory classification.

## Concrete assignment and limits

Reuse the existing implementation worker and worktree. Preserve the baseline commit; make a new local commit limited to Cloudflare hibernation configuration and only directly necessary regression evidence/documentation. Start with the supported TLSocketRoom clientTimeout setting; inspect heartbeat and authorization lifecycle interactions before claiming sufficiency. Node, room-switching UI, concurrency, shared API/schema, existing Sites/POC, Netlify and retained data remain unchanged.

Use one disposable Free Worker with at most one deployment-wiring correction, no R2 enrollment, static deployment, paid upgrade or real data. Bound execution to 100 small application operations, two concurrent sockets and two idle/wake rounds; no health polling during idle. Keep timeout/watchdog and cleanup outside the room being observed. If a material code or platform change beyond this repair is necessary, preserve evidence and return the concrete boundary instead of widening scope.

Prove an actual lifecycle transition (for example constructor generation changes with the same accepted socket resuming protocol traffic) separately from timer eligibility and idle readback. External instrumentation may wrap the actual candidate without changing its product bytes; label that evidence honestly. Test stored document recovery and applicable expiry/revocation protections across wake. Read provider usage before/after with bounded, resource/time-scoped queries and respect ingestion delay/throttling; missing metrics are not zero usage or zero charge.

Preserve raw provider counters, timestamps, resource identifiers, endpoints, billing observations and receipts in the local output directory only. Public workflow state contains conclusions and local pointers only. Remove all disposable Worker/classes and confirm absence independently on every outcome; stop owned processes and remove synthetic secrets. No product push, PR, merge, remote Node deployment or message to Claude.

FO retains workflow state ownership until the dispatch record is committed, then hands it to the worker. Return completion only with a durable report and clean new candidate. Independent review follows correction-record handling; no self-validation or full-delivery claim.
