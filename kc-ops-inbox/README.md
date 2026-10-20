# kc-ops-inbox POC artifacts

Disposable proof that one hermes instance can act as the First Officer of an `ops`
Spacedock workflow. Not a plugin: no `plugin.json`, no marketplace entry.

Pinned third-party: Hermes Agent `31df1227890643eb9f5f08db6b2a5c37d4a6f5cc`.

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
