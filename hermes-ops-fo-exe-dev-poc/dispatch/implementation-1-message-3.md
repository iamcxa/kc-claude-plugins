# implementation follow-up message 3 (resumed worker)

Model: sonnet
Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5

## Checklist

1. Apply Captain amendment 1: move the AC-1 to AC-5 blocks verbatim into the amendment entry under a `Superseded text:` line, and write replacement criteria under fresh ids (AC-6 onward), each saying "Amended by Captain, amendment 1": the GitHub App credential probe (a) push to main refused, (b) API merge refused, (c) approving the App's own PR does not satisfy the required review, (d) push to an ops/* branch and opening a Draft PR succeed, plus the runner holding no other credential; then the vertical slice (fixture event, FO on host claude or codex through `spacedock dispatch build`, one ops task on ops/*, Draft PR with the App token, the gate recorded only after reading the Captain's GitHub review).
2. Prepare the probe locally with no outward action: App permission set (contents:write, pull_requests:write, no administration), the two ruleset definitions, and a probe script that uses only the installation token; then send FO one decision request naming each outward action exactly (scratch repository owner, name and visibility; the App creation and installation the Captain does in his browser; where the App private key is stored and how the probe reads it without you reading it) and wait.
3. Clean the hermes rehearsal residue now: /tmp/hermes-venv, /tmp/hermes-src, /tmp/ops-rehearsal; record the commands and an `ls` showing them gone. HERMES_HOME was never created and no Codex login happened.

## Scope notes

Captain amendment 1 (chat, 2026-10-20) retires "hermes boots as FO" for v1 and moves the authority boundary to GitHub: App token, rulesets, the Captain's own GitHub review. Shelve the hermes skill and guard plugin as committed; do not extend them. Chief-engineer advice (opus, 2026-10-20) is recorded under FO alignment; read it there.
Every outward action still asks first. Never read or print a credential.
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
