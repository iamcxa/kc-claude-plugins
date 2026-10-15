# ideation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for giving each caller of kc-dev-flow-2/scripts/pr_watch.py its own view of changes on main (after #643 merged at ab9334ed): the state key (per workflow directory, per session, or per-caller seen markers), how the default path is chosen without FO passing --state, how existing entries in ~/.local/state/kc-dev-flow-2/pr-watch.json migrate, and what the merged mod and README text need, if anything, counted under the task's learning rule (words FO reads at each moment must not rise)
Acceptance criteria with reproducible evidence clauses and falsifiers, including a test where two callers watch overlapping PRs and each still sees a change the other already read, and a replay of the 2026-10-14 loss (one session's wait consuming relay#368's checks pending -> green)
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. The Captain's words and the evidence are in the task file. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`); #643 (the lifecycle mod) is merged there and the released package is still 0.22.1. Root learning.md on main holds the rule "Measure the words FO reads at each moment, not one file's size"; apply it to any text this change adds. Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found. The two tasks pr-watch-state-per-session and delivery-gate-verdict-form are designed in parallel; name any file you expect both to change.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, qnow, ss-web) only through read-only commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
