# open-pr station

**Enforcing script:** `kc-ship-flow/scripts/open-pr.sh <evidence-file> <batch-dir> [--dry-run]`

**Input:** a worker's accepted Evidence block file, and the batch's own record directory
(`<batch-dir>/README.md` and `<batch-dir>/receipt/plan-receipt.json`).

**Output:** opens the Draft PR — title is the `CANDIDATE_SHA` commit's subject; body is built per the
pr-merge mod's PR body template (`docs/dev/_mods/pr-merge.md` § PR body template): a motivation lead
condensed from the matched issue's `## The problem`, `## What changed` (one bullet per top-level
`FILES` entry), `## Evidence` (`N/N passed`, counted from `TESTS`'s `-> exit` markers, omitted when
`TESTS` is absent), `---`, the audit link, and the issue's `close_line` — and prints the opened PR
number. The issue is the one in the batch receipt whose `branch` equals the Evidence block's
`BRANCH`; the audit link's owner/repo, ref, and path come from `batch-dir`'s own git checkout, never
from `CANDIDATE_SHA` or cwd's repository. `--dry-run` prints the body to stdout and exits 0 without
resolving `CANDIDATE_SHA`, binding `BRANCH` to origin, or calling `gh`.

**Refusal:** see `kc-ship-flow/scripts/contract-test.py` for the BRANCH-binding refusals (fork syntax,
a BRANCH absent from origin) this script enforces before calling `gh`, and for the batch-receipt
refusals (a `BRANCH` matching zero or more than one issue, an untracked `batch-dir/README.md`).

This is the first of the two scripts either side of the `kc-pr-review` session run — see
`references/kernel.md` for the review-station shape and `references/stations/disposition.md` for the
second script.

Placed segments (`references/placement.tsv`): `2c6efbaf14c7`.
