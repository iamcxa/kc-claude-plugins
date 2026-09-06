# fenced-dispatch station

**Enforcing script:** `kc-ship-flow/scripts/fenced-dispatch.sh`

**Input:** `<state-dir> <holder-id> <writer> <claim> <project-id> <base-branch> <message-file>`. The
message file is the dispatch task body; a body longer than the first chat message travels this way —
as a file, hashed — rather than pasted inline or fetched by a bootstrap line.

**Output:** the adopted `workspace-id` on stdout once `intent.sh adopt` succeeds.

**Refusal:** `intent not committed (exists or fenced); reconcile instead of create` (exit 4) when an
intent already exists for the claim; `create call failed` or `create returned no valid workspace id`
(exit 7, intent left unresolved for reconcile) when `conductor workspace create` itself fails;
`read-back failed (<reason>)` (exit 7) when the created workspace's name or project does not match;
`adopt refused` (exit 3) when `intent.sh adopt` itself is fenced.

**Sequence enforced:** `intent.sh commit` (writes the claim, token, project, base branch, message
sha256) → `holder.sh check` (confirms the writer) → `conductor workspace create` (called once) →
read-back by id (name, project) → `holder.sh check` again → `intent.sh adopt`. Production entry
issues at most one `conductor workspace create` call after a committed intent — `conductor workspace
create` is not idempotent and a holder can sleep between the call and its receipt, so every external
action follows this one order.

Placed segments (`references/placement.tsv`): `482684f393ea`, `c0974575084d`, `aa07537259c4`.
