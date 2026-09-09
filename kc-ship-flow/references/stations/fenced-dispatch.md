# fenced-dispatch station

**Enforcing script:** `kc-ship-flow/scripts/fenced-dispatch.sh`

**Dispatched unit:** a dev entity's stage, not a hand-written batch message. The station calls
`spacedock dispatch build --entity-path <dev-task> --stage <stage> --workflow-dir <dir> --host
claude` and treats the JSON envelope it writes to stdout as the built artifact: the artifact's
`dispatch_file_path` file is the message handed to `conductor workspace create --message-file`
(its sha256 is what the intent records), and the artifact's own `model`/`effort` keys — read from
the workflow's stage definition, never invented by this station — are forwarded to `conductor
workspace create` only when present. The Evidence block for that dev entity arrives later, after
its `validation` stage, written by the layer that verified it rather than this dispatching layer.

**Input:** `<state-dir> <holder-id> <writer> <claim> <project-id> <base-branch> --entity-path
<dev-task> --stage <stage> [--workflow-dir <dir>] [--dry-run]`. When `--workflow-dir` is omitted it
defaults to a sibling directory named after the entity file's own basename
(`<entity-dir>/<entity-stem>/`). `--dry-run` prints the would-be `conductor workspace create` argv
and the message sha256 instead of committing an intent or calling `conductor`.

**Output:** the adopted `workspace-id` on stdout once `intent.sh adopt` succeeds.

**Refusal:** `dispatch build failed` (exit 4) when `spacedock dispatch build` itself exits non-zero
— the station never falls back to an inline message; `intent not committed (exists or fenced);
reconcile instead of create` (exit 4) when an intent already exists for the claim; `create call
failed` or `create returned no valid workspace id` (exit 7, intent left unresolved for reconcile)
when `conductor workspace create` itself fails; `read-back failed (<reason>)` (exit 7) when the
created workspace's name or project does not match; `adopt refused (fenced, already adopted, or
project mismatch)` (exit 3) on *any* non-zero exit from `intent.sh adopt` -- fenced-dispatch.sh
collapses all of `intent.sh adopt`'s own exits (1 no intent for claim, 3 fenced, 5 already adopted
under a different workspace id, 7 could not read the workspace's project, 8 project mismatch) into
this one exit 3, leaving `$WID` for the current holder's reconcile in every case.

**Sequence enforced:** `spacedock dispatch build` (produces the message and, if the stage declares
one, the model) → `intent.sh commit` (writes the claim, token, project, base branch, message
sha256) → `holder.sh check` (confirms the writer) → `conductor workspace create` (called once) →
read-back by id (name, project) → `holder.sh check` again → `intent.sh adopt`. Production entry
issues at most one `conductor workspace create` call after a committed intent — `conductor workspace
create` is not idempotent and a holder can sleep between the call and its receipt, so every external
action follows this one order.

Placed segments (`references/placement.tsv`): `482684f393ea`, `c0974575084d`, `aa07537259c4`.
