# validation dispatch 1

Model: sonnet
Dispatched: f08a1f141004ea525a226a16111ee1e94768a458
Candidate: aae7041b2de840befcf2aee5915dca46231e958c

## Checklist

1. Independently verify AC-6 to AC-12 against the exact artifacts (candidate aae7041b on spacedock-ensign/hermes-ops-fo-exe-dev-poc and the live state of iamcxa/ops-inbox-probe-scratch) with read-only checks, and name any claim only the implementer's report supports.
2. Write a minimal acceptance script of read-only commands the First Officer can run exactly as written in a fresh shell, each with its expected output.
3. Give the verdict on goal sufficiency and minimal necessity for the outcome as amended by Captain amendment 1, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/scripts/adr_lint.py docs/adr --since ad44f0cbf42274ff65802cabc52ebe919f159fd5` with its exit code, and list unverified obligations.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (pass it as --workflow-dir on every spacedock command).

Read-only: use the Captain's gh login only for reads (gh api GET, gh pr view, gh run view --log, git ls-remote). Do not push, comment, review, re-run workflows, mint the App token, toggle rulesets or touch secrets. If a check needs a write, stop and send FO a decision request naming it.
Never open ~/.config/ops-inbox-probe/app.pem or any token.
The accepted outcome is the task's Captain amendment 1 and AC-6 to AC-12; AC-1 to AC-5 are superseded. The candidate is a POC: say whether any work crossed the POC boundary.
