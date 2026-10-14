# ideation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for a kc-dev-flow-2 Spacedock mod with `## Hook: merge`, `## Hook: idle` and `## Hook: startup` sections: for each FO step the task's Scope lists, keep it in the mod (naming the hook point, the README rule it carries and the command, for example /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/pr_watch.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/observer_check.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py) or leave it in the README with a reason; the mod filename and its order against _mods/pr-merge.md; where learn runs relative to the archive; what the README keeps as the authority and the word-budget effect, counted; and how adopters receive and keep the mod in sync
Acceptance criteria with reproducible evidence clauses and falsifiers, including a replay of the relay PR #362 situation (an FO at the merge ask and at the merged PR) with and without the mod, using the package's replay helper /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/replay_dispatch.py or a stated alternative, with the measurement it records
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. The Captain's words and the evidence are in the task file. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`); the released package is 0.22.1. Spacedock's mod convention is in /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0/skills/first-officer/references/first-officer-shared-core.md ("Mod Hook Convention" and «hooks.run») and its own mod in /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0/mods/pr-merge.md; read Spacedock's source and docs for how mods are discovered, ordered and run, not an adopter's usage. Evidence of the relay miss (read only): the transcript /Users/kent/.claude/projects/-Users-kent-conductor-workspaces-subspace-relay-dhaka/d2b0a847-f238-4bc3-ad1c-532e738e9a37.jsonl (read progressively, never whole) and /Users/kent/conductor/workspaces/subspace-relay/dhaka/.context/relay-dev2-fo/docs/dev2/. Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found. Spacedock is not changed (the Captain's ruling). Tasks followup-dispatch-records-checked (in implementation) and extension-instruction-reaches-dispatch (backlog) own the dispatch-time checks; name any file you expect to share with them.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
