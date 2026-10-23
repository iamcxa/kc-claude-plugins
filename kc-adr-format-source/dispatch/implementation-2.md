Dispatched: from 57b86de4805e32d2910348482e1c33089a6d8004
Model: sonnet

## Checklist

Apply Captain amendment 1: in kc-adr/skills/read-adr/SKILL.md, change only the sentence "To write the ADR read `writing.md` in this folder; no words from the person, or no reserved number, means do not write one: ask the coordinator." so that a missing person's words means do not write one and ask the coordinator, and numbering points to writing.md. Keep the frontmatter and every other line unchanged. Commit on the worktree branch.
Re-run the AC-3 text check so it covers SKILL.md and writing.md agreeing on numbering, plus the closing checks (version-parity-check.sh, skill-frontmatter-lint.sh, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py on the diff, sanitize-check, and the roborev step) on the new head. Update the stage report: every line DONE or SKIPPED, and state that no agent scenario was re-run for this sentence. Then commit and push the state branch.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
This is a follow-up message to the live implementation worker for kc-adr-format-source. Read `### Amendment 1` in the task's `## Captain amendments`.
Before reporting, run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base c3514876339cb732d0bea8b2d2dd45c234bcdeaf` on the new head and put its evidence line in the report.
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2.
