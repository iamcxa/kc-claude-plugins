# Evidence block grammar

**Enforcing scripts:** `kc-ship-flow/scripts/accept-evidence.sh <evidence-file>` and
`kc-ship-flow/scripts/open-pr.sh <evidence-file>` — the two scripts that actually parse a worker's
Evidence block. Between them they read `CANDIDATE_SHA`, `BASE_SHA`, `BRANCH`, `FILES`,
`WITHOUT_IT_COMMAND`, `WITHOUT_IT_REMOVED_VARIANT`, `WITHOUT_IT_OBSERVED`, and `SELF_CHECK`.
`accept-evidence.sh` requires `CANDIDATE_SHA`, `BASE_SHA`, `WITHOUT_IT_COMMAND`, and
`WITHOUT_IT_REMOVED_VARIANT` to be non-empty (refusing an "incomplete Evidence block" otherwise) and
reads `BRANCH` and `FILES` without requiring them; `open-pr.sh` separately requires `CANDIDATE_SHA`,
`BASE_SHA`, `BRANCH`, `WITHOUT_IT_COMMAND`, `WITHOUT_IT_REMOVED_VARIANT`, and `SELF_CHECK`.

`WITHOUT_IT_COMMAND` is one self-contained shell line with three properties, each checked by a
different script:

- It references no file outside the candidate tree — checked by `accept-evidence.sh`'s
  `check_command_for_out_of_tree`/`is_out_of_tree_path`, which refuses the block outright when either
  `WITHOUT_IT_COMMAND` or `WITHOUT_IT_REMOVED_VARIANT` resolves to a path outside the repository.
- It exits 0 retained and non-zero once `WITHOUT_IT_REMOVED_VARIANT` is applied — this is
  `kc-ship-flow/scripts/without-it.sh <sha> <command> <removed-variant>`'s own contract (see
  `references/stations/without-it.md`); `accept-evidence.sh`'s own AC-1 check separately re-runs
  `WITHOUT_IT_COMMAND` at `BASE_SHA` in a fresh worktree and refuses if that exit is 0 or 126/127.
- The First Officer runs it verbatim, unchanged — a procedural rule with no script today (see
  `references/kernel.md`'s residuals).

`without-it.sh` runs `WITHOUT_IT_COMMAND` with exactly seven credential environment variables
stripped — `LINEAR_API_KEY`, `GH_TOKEN`, `GITHUB_TOKEN`, `CONDUCTOR_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, and `CODEX_API_KEY` — while `PATH`, `HOME`, `TMPDIR`, and every other environment
variable are kept; see `references/stations/without-it.md`. It does not run in a network- or
HOME-isolated sandbox — that is a separate, currently unenforced claim (kernel.md's residuals).

Placed segments (`references/placement.tsv`): `f348a6450677`, `d999717871ef`.
