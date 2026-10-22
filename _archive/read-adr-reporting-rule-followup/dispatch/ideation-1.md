Dispatched: from 8bf7b9e4f63257f5b55edd97ff3c957a09e58019
Model: sonnet

## Checklist

Design the fix for read-adr's Accepted branch to the Captain's wording: the worker reports the cited commit, its verified digest and its Status; if a different record is in force at head, it also reports that record's commit and digest; it takes no action on either until a person decides. Align the chain-end line with the same rule. Show the exact new SKILL.md text against the shipped text at origin/main.
Design the harness answer-schema change so it holds both the cited record and an in-force record. Write the S6, S7, S9 and S11 expectations under the new rule before any run, and declare the run count (both hosts, these four scenarios only).
Give AC-1 and AC-2 reproducible evidence clauses and list any decision for the Captain. Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/design_surfaces.py check <task>`. Write no repository file, branch or commit.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Shipped skill: kc-adr/skills/read-adr/SKILL.md on origin/main (8bf7b9e4f63257f5b55edd97ff3c957a09e58019), released as kc-adr v0.1.0.
Harness to reuse, read only: the archived task folder _archive/kc-decision-log-cli/ in the state checkout (harness/, results/, expectations). Copy what you need into this task's folder; do not edit the archive.
Known from kc-decision-log-cli's engineering review: in S11, ADR 0014 is Accepted at the cited commit, so the Accepted branch applies (not the chain-end rule); the harness answer has a single ruling_check slot.
Fictional data only. Model pins for any run (implementation stage, not now): claude --model sonnet; codex -m gpt-6.1-sol -c model_reasoning_effort="high".
