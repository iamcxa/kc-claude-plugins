# intent station

**Enforcing script:** `kc-ship-flow/scripts/intent.sh commit|adopt|reconcile|show ...`

**Input:** `commit` takes the claim, dispatch token, project, base branch, and message sha256;
`adopt` takes the workspace id; `reconcile` takes only the holder/writer identity.

**Output:** `commit`/`adopt` persist to the state branch and push; `reconcile` adopts the one live
workspace whose name carries the intent's token and whose project matches.

**Refusal:** `reconcile` blocks with `unresolved intent` on zero matching live workspaces and
`ambiguous intent` on two or more; `adopt` refuses a candidate workspace with `project mismatch` when
its project id does not match the one committed; `commit` refuses `intent exists for <claim>
(<workspace-or-unresolved>); reconcile, do not create` (exit 4) whenever a claim already has an
intent file, which is the basis for "a new holder never creates a workspace for an intent it did not
commit" -- the second call for the same claim hits this `commit` refusal, not a fresh create.

`intent.sh commit` and `intent.sh adopt` hold a lock on the state directory around their whole
sync-write-commit-push sequence, so two concurrent calls on the same checkout serialize instead of
racing the shared working tree.

Placed segments (`references/placement.tsv`): `6df22fa5c1de`, `a86300c3e55a`.
