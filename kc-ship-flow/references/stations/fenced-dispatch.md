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
`adopt refused (fenced, already adopted, or project mismatch)` (exit 3) on *any* non-zero exit from
`intent.sh adopt` -- fenced-dispatch.sh collapses all of `intent.sh adopt`'s own exits (1 no intent
for claim, 3 fenced, 5 already adopted under a different workspace id, 7 could not read the
workspace's project, 8 project mismatch) into this one exit 3, leaving `$WID` for the current
holder's reconcile in every case.

**Sequence enforced:** `intent.sh commit` (writes the claim, token, project, base branch, message
sha256) → `holder.sh check` (confirms the writer) → `conductor workspace create` (called once) →
read-back by id (name, project) → `holder.sh check` again → `intent.sh adopt`. Production entry
issues at most one `conductor workspace create` call after a committed intent — `conductor workspace
create` is not idempotent and a holder can sleep between the call and its receipt, so every external
action follows this one order.

Placed segments (`references/placement.tsv`): `482684f393ea`, `c0974575084d`, `aa07537259c4`.
