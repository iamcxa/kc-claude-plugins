# e2e-gate station

**Enforcing script:** `kc-ship-flow/scripts/e2e-gate.py --root <repo-root> --flows <flows-dir> <plan-receipt.json> <close-receipt.json>`

`--root` and `--flows` are always required, taken from arguments and never derived from the
script's own install location (the plugin can be installed anywhere under a plugin directory,
which is not the checkout to resolve paths against). The FO skill passes the code checkout root
and the commissioned README's Local Profile "E2E flows" row (currently `docs/ship/flows/`).

**Input:** the batch's plan receipt (`dispatch_order`, `milestones`) and close receipt
(per-issue `candidate`).

**Output:** for a milestone with a flow file, runs `e2e-cli.sh` at the resolved head and reports its
log path and exit code; for a milestone with no flow file, records `e2e: not applicable` and exits 0.

**Refusal:** no milestone named exits non-zero and the batch is not UAT-ready; a `--flows` directory
that does not exist exits 2 with `flows directory not found`, checked before any receipt is read.

A Milestone's CLI journey lives at `<flows-dir>/<milestone-slug>.yaml`, consumed read-only by
`e2e-cli.sh`. `e2e-gate.py` computes the slug: lowercase, keep every Unicode letter and digit,
collapse every other run of characters (including underscore) to a single hyphen, strip
leading/trailing hyphens — a name that slugifies to empty refuses with exit 2.

Given a bare milestone name instead of the receipt pair, `e2e-gate.py` only resolves and prints
that milestone's flow path under `--flows`; it does not resolve a candidate or run `e2e-cli.sh`.

Placed segments (`references/placement.tsv`): `5aa826f86c91`, `d7132b42e5fa`.
