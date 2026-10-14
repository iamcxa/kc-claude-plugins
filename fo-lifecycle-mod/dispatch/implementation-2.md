# implementation-2

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet
Follow-up message to the live implementation worker after its stop report: the Captain chose option 1 (Captain amendment 1); ADR 0015 reserved.

## Checklist

Apply Captain amendment 1 (task file, ## Captain amendments): delete the ## Hook: merge section from watch-and-learn.md, start the PR watch at startup and idle only, and add an idle (and startup) step that records the task's pr field as owner/repo#N when its PR is open and pr is empty; drop watch-and-learn from AC-1's merge line accordingly and adjust the flow
Change the references/sd/workflow.md sentence "Use SD's pending terminal approval and existing merge hook; do not invent another PR stage" to match the amendment (the implementation stage opens the Draft PR and FO records pr when it opens), counted against the budget
Draft ADR 0015 (reserved, recorded under ## Number guards) in docs/adr recording the ruling that the implementation worker opens the Draft PR before validation so external review runs before the delivery gate, with the Captain's words and the rejected alternative
Then the original implementation checklist (mod files, README edits R1 to R3, budget, adoption.md, package README row, tests), AC-1 to AC-3 and AC-7 green with each falsifier shown failing by a mutation run, roborev evidence= line, CI green, CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Follow-up to your stop report: the Captain chose option 1 (Captain amendment 1 in the task file). Your merge-guard finding stands as recorded; the merge hook is not used in this workflow. Run the ADR check `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base>` and `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task <task file>` before reporting. All other scope notes of implementation-1 apply unchanged (one Draft PR off origin/main, roborev with `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`, no replay launches, no adopter copies, PR #642 touches the same workflow.md and budget line).

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
