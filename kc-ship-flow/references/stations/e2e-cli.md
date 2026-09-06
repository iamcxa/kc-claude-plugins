# e2e-cli station

**Enforcing script:** `kc-ship-flow/scripts/e2e-cli.sh <sha> <flow.yaml>`

**Input:** a resolved `<sha>` and an e2e-pipeline flow YAML consumed read-only.

**Output:** a timestamped stdout log — the CLI e2e evidence of record — of every `Execute external`
step's command and exit code.

**Refusal:** exits non-zero on the first step whose command's exit code does not match its declared
`expect`.

It runs each of the flow's `Execute external` steps (e2e-pipeline's `execute.cli` step shape). A
terminal recording (`asciinema`, `script(1)`) is not used because both hang without a pty, which
cloud build workers do not have — see `docs/ship/runbooks/conductor-cloud.md` for that host
constraint.

Placed segments (`references/placement.tsv`): `169c2a145c7a`, `c8805a1fa6a1`.
