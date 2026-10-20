# implementation follow-up message 1 (live worker)

Model: sonnet
Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5

## Checklist

1. Retry the isolated local install once (venv and HERMES_HOME under /tmp, pinned 31df1227, gateway on 127.0.0.1 only); on a second refusal stop and report, no workaround.
2. Hand the Captain the exact device-code login command (full HERMES_HOME and venv hermes paths) through FO and wait; never read or handle the token.
3. At rehearsal end: hermes's documented logout if one exists, delete venv and HERMES_HOME including auth.json, and record the commands and an `ls` showing both paths gone.

## Scope notes

Captain's answer, 2026-10-20: 「可以，裝完會移除嗎？」 to Ask 1 (isolated local install) and Ask 2 option (b) (Captain logs in with `hermes auth add openai-codex` himself). Removal after the rehearsal is a condition.
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
