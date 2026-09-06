# open-pr station

**Enforcing script:** `kc-ship-flow/scripts/open-pr.sh <evidence-file>`

**Input:** a worker's accepted Evidence block file.

**Output:** opens the Draft PR — title is the `CANDIDATE_SHA` commit's subject, body carries
`BASE_SHA`, `CANDIDATE_SHA`, the without-it pair, and the block's own `SELF_CHECK` line — and prints
the opened PR number.

**Refusal:** see `kc-ship-flow/scripts/contract-test.py` for the BRANCH-binding refusals (fork syntax,
a BRANCH absent from origin) this script enforces before calling `gh`.

This is the first of the two scripts either side of the `kc-pr-review` session run — see
`references/kernel.md` for the review-station shape and `references/stations/disposition.md` for the
second script.

Placed segments (`references/placement.tsv`): `2c6efbaf14c7`.
