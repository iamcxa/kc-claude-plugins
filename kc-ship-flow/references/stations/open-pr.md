# open-pr station

**Enforcing script:** `kc-ship-flow/scripts/open-pr.sh <evidence-file> <batch-dir> [--dry-run]
(--entity-path <dev-entity-file> | --what-changed-file <file>)`

**Input:** a worker's accepted Evidence block file, the batch's own record directory
(`<batch-dir>/README.md` and `<batch-dir>/receipt/plan-receipt.json`), and either the dev entity
`fenced-dispatch.sh` dispatched or an FO-authored what-changed file.

**Output:** opens the Draft PR — title is the `CANDIDATE_SHA` commit's subject; body is built per the
pr-merge mod's PR body template (`docs/dev/_mods/pr-merge.md` § PR body template, "Extraction
rules"):

- **Lead** (`<=25` words, no heading): the source paragraph's `## The problem` text, condensed,
  skipping any leading sentence that is only a quoted attribution (`Speaker, date: 「...」.`) so a
  quote never becomes the motivation lead.
- **`## What changed`**: with `--entity-path`, one bullet per `- [x] ...` item in the entity's last
  `## Stage Report: implementation` section (`[x]` dropped, duplicates collapsed, capped at 5).
  Without it, `--what-changed-file <file>`'s lines verbatim (FO-authored, one bullet per line).
- **`## Evidence`**: with `--entity-path`, one bullet per suite-labeled `N/N` or `exit 0` token found
  in the entity's last `## Stage Report: validation` section. Without it, the same scan applied to
  the Evidence block's own `TESTS` field — never a count of ACs. Omitted when no such token is
  found (e.g. `TESTS` absent).
- **`---` + audit link + `Fixes`**: unchanged by either mode — the issue matched to the Evidence
  block's `BRANCH` in the batch receipt (see below), always.

With `--entity-path`, the lead also comes from the entity file itself, not the batch receipt; the
issue lookup below still runs, for `close_line` only. `--dry-run` prints the body to stdout and exits
0 without resolving `CANDIDATE_SHA`, binding `BRANCH` to origin, or calling `gh`.

The issue used for `close_line` (and, in `--what-changed-file` mode, the lead) is the one in the
batch receipt whose `branch` equals the Evidence block's `BRANCH`. The audit link's owner/repo, ref,
and path come from `batch-dir`'s own git checkout, never from `CANDIDATE_SHA` or cwd's repository.

**Refusal:** see `kc-ship-flow/scripts/contract-test.py` for the BRANCH-binding refusals (fork syntax,
a BRANCH absent from origin) this script enforces before calling `gh`; the batch-receipt refusals (a
`BRANCH` matching zero or more than one issue, an untracked `batch-dir/README.md`); and
`what-changed required` (exit 2) when neither `--entity-path` nor `--what-changed-file` is given.

This is the first of the two scripts either side of the `kc-pr-review` session run — see
`references/kernel.md` for the review-station shape and `references/stations/disposition.md` for the
second script.

Placed segments (`references/placement.tsv`): `2c6efbaf14c7`.
