# worker-transcript station

**Enforcing script:** `kc-ship-flow/scripts/worker-transcript.sh <session-id>`

**Input:** a Conductor cloud session id.

**Output:** the session's last fenced `## Evidence` block, printed to stdout.

**Refusal:** exits 1 with `no evidence block` when the transcript has none.

One read per invocation; no polling loop, retry, or daemon. The First Officer reads through
`conductor sql` rather than `conductor session message --after` — see
`docs/ship/runbooks/conductor-cloud.md` for why that other CLI path is avoided.

Placed segments (`references/placement.tsv`): `f8f92d5da8fb`, `87bb44ce5e4c`.
