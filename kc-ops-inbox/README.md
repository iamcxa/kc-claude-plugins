# kc-ops-inbox POC artifacts

Disposable proof for an `ops` Spacedock workflow. Not a plugin: no `plugin.json`, no marketplace entry.

Current (Captain amendment 1): the authority boundary is GitHub, not the agent host. `github-probe/` tests
a GitHub App token against rulesets; `slice/` is the vertical slice: a manually dispatched GitHub Actions job runs the
First Officer (`workflows/ops-fo.yml`, `run_fo.sh`); a second job records the gate only from the Captain's own
review (`workflows/ops-gate.yml`, `record_gate_from_review.sh`). `make_scratch_tree.sh OUT` assembles the
files committed to the scratch repository. `ops-workflow/` is its workflow (triage, decision gate, resolution, done).

Shelved, committed as written and not extended: `hermes-profile/`, `rehearsal/` (hermes as the First Officer).

Shelved pin: Hermes Agent `31df1227890643eb9f5f08db6b2a5c37d4a6f5cc`.

- `ops-workflow/README.md` - minimal workflow: `inbox` (initial, gate) -> `resolution` -> `done`.
- `hermes-profile/` - `config.yaml`, `SOUL.md`, `env.example` (names only), skill `ops-first-officer`, plugin `ops-gate-guard`.
- `rehearsal/` - `send_event.py` (signed synthetic event), `spacedock_mechanics.sh` (no hermes, no model), `test_ops_gate_guard.py`.

## Where credentials go (the Captain places them)

| Credential | Where | Placed by |
|---|---|---|
| Codex login (ChatGPT subscription OAuth, not an API key) | `$HERMES_HOME/auth.json`, written by `hermes auth add openai-codex` (device code, works over SSH) | Captain, on the VM |
| Webhook signing secret | `OPS_WEBHOOK_SECRET` in `$HERMES_HOME/.env` | Captain |
| Slack bot and app tokens, allowed user ids | `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_ALLOWED_USERS`, `CAPTAIN_SLACK_USER_ID` in `$HERMES_HOME/.env` | Captain |

## Guard mode

`OPS_GUARD_MODE=block` (default) refuses `spacedock gate record|consume|withdraw` outside the
Captain's Slack session; `OPS_GUARD_MODE=log` only records each decision to
`$HERMES_HOME/ops-gate-guard.log`, so the model's own behaviour stays observable.
