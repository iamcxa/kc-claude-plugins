# ideation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for how the copilot extension and FO treat a Copilot answer that is not a review (today's quota-limit refusal at minimum): reported as `copilot not run: <reason>`, never counted as a round or read as clean, and FO's next step when the second reviewer cannot run, consistent with the README's `## Extensions` rule and the Captain's rulings in the task
Acceptance criteria with reproducible evidence clauses and falsifiers, including one that runs `copilot_review.py`'s reading logic on the recorded refusal bodies of iamcxa/kc-claude-plugins #627 (review:5499757433) and #628 (review:5499757731) and fails if they read as answered
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Captain's words are in the task under `## Captain's words`; scheduling ruling recorded in the backlog gate resolution: 「Copilot 的 task是否可以先排？因為顯然會接下來一直遇到此問題」, then 「是」.

The code under design is `<package>/extensions/copilot/` (EXTENSION.md and copilot_review.py); its canonical source is `kc-dev-flow-2/extensions/copilot/` in iamcxa/kc-claude-plugins at origin/main 133f1315. Read the reviews with `gh api repos/iamcxa/kc-claude-plugins/pulls/627/reviews` and `.../628/reviews` (read only). Check upstream first: whether `codex_review.py` or kc-pr-flow already recognise a non-review answer, and say what you found.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or request any review.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
