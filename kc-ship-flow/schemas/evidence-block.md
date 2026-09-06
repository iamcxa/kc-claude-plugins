# Evidence block grammar

A worker's Evidence block defines `CANDIDATE_SHA`, `BRANCH`, `BASE_SHA`, `WITHOUT_IT_COMMAND`, and
`WITHOUT_IT_REMOVED_VARIANT`.

`WITHOUT_IT_COMMAND` is one self-contained shell line: it references no file outside the candidate
tree, it exits 0 on the candidate and non-zero once `WITHOUT_IT_REMOVED_VARIANT` is applied, and the
First Officer runs it verbatim, unchanged, in a worktree with no secrets.

**Enforcing script:** `kc-ship-flow/scripts/without-it.sh <sha> <command> <removed-variant>` runs the
pair and returns the retained/removed exit codes this grammar requires — see
`references/stations/without-it.md`.

Placed segments (`references/placement.tsv`): `f348a6450677`, `d999717871ef`.
