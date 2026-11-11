# ideation-1
Dispatched: 44f11855264bde64da284ffa9c1fef70e8ac38dd (workflow checkout, kc-dev-flow-2 0.39.0 README; batch 18)
Model: claude-opus-5-5 (Claude via Paseo, thinking high; repo roster .dev2/model-roster.json ideation row)
Budget: 1 cycle per stage, in one package PR to `kc-dev-flow-2/scripts/design_surfaces.py`, its tests and, if the design shows ADR 0077's words exclude the outcome, that ADR.
Roster: source=repository; role=ideation; provider=claude; model=claude-opus-5-5; effort=high; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=44f11855264bde64da284ffa9c1fef70e8ac38dd

## Checklist
Decide what 'passed its ideation gate' is read from (the task's stage through the native reader, its gate records, or its first dispatch record as the Budget exemption does) and what the check does when that cannot be read; show the choice by replaying this workflow's in-flight tasks and one adopter's at pinned commits, read-only, with counts of tasks released and tasks still refused; name every caller that runs the full check after ideation; keep the refusal for a task still in ideation
A `### Batch overlap` section naming each file the design would change and each other batch task (none: this task runs alone as a Captain-approved priority exception) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.0

Start in the assigned worktree; verify pwd and git root before edits.

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of priority exception after batch 21; read the other task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read the released version from kc-dev-flow-2/.claude-plugin/plugin.json there) (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for a third-party mechanism read its own docs or source, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, web, qnow) only through read-only commands.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: worth-questions-asked-only-before-the-design-gate completed ideation
