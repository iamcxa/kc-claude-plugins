# implementation-4

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #642 12670427
Model: sonnet

Follow-up message to the live implementation worker: FO fix authorization after its phase-1 reproduction confirmed the Codex round-1 P2.

## Checklist

Apply the allowlist pointer rule (helper is_pointer and constant POINTER_WORDS in kc-dev-flow-2/scripts/dispatch_records.py), stating its known limit with the design's Limits
Tests for the P2 line, the two-line action checklist and the paraphrase pointers, each shown red under the three named mutations; the AC-1/AC-2 replays unchanged
Keep the budget comment in kc-dev-flow-2/scripts/lint-skills.py unchanged (it follows that block's one-reason-per-raise rule)
Commit with named files only, the roborev gate with base 12670427, push without force, CI green, stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Roborev: `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base 12670427`. Inside the files the PR already changes. No comments, review requests, ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
