# implementation follow-up message 6 (resumed worker)

Model: sonnet
Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5

## Checklist

1. Prepare the vertical slice (AC-11, AC-12) to run the FO on a GitHub-hosted Actions runner in iamcxa/ops-inbox-probe-scratch: fixture event in, FO on host claude or codex through `spacedock dispatch build`, one ops task on an ops/* branch, a Draft PR with the App token, and the gate recorded only after reading the Captain's GitHub review. Rehearse every part you can locally with no outward action; read the Claude Code GitHub Actions and Codex docs from their own sources for how each authenticates.
2. Run the credential audit inside the runner job itself (the FO's own environment): no credential other than the App installation token and the one model credential.
3. Send FO one decision request listing each outward action exactly: every repository secret (name, what it is, who sets it; you never read a value), every workflow file to commit to the scratch repository, the trigger, the model and its credential type and billing, and the expected Actions minutes if measurable; then wait.

## Scope notes

Captain's answer, 2026-10-20: 「可以，理論上是否跑在 self host 的 runner 更好？」 to running the slice FO on GitHub Actions in the scratch repository. Use GitHub-hosted runners, not self-hosted.
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
