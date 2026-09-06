# notify station

**Enforcing script:** `kc-ship-flow/scripts/notify.sh <channel> <batch-id> <doc-path> --dry-run
--state-dir <dir>`

**Input:** a channel, batch id, UAT document path, and state dir.

**Output:** one UAT-ready message per batch id — a deterministic message id keyed on the batch id
makes a second call for the same batch id and state dir a no-op instead of a duplicate send.

**Refusal:** it has no real-send path; the First Officer sends the real message.

Placed segments (`references/placement.tsv`): `73541e486535`, `97b2ae0b2cc8`.
