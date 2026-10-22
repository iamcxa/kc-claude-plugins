Dispatched: from cebd0ab93c7f9b681d55434cfc99c19b2d9dd8ba
Model: sonnet

## Checklist

Apply the approved SKILL.md change to kc-adr/skills/read-adr/SKILL.md exactly as shown in the task's Design (frontmatter unchanged). Apply the harness schema change (ruling_check gains status; nullable in_force_record; S9 alt removed) in this task's copied harness, with expectations already committed before the first run.
Run the declared 8 runs (B1 x S6, S7, S9, S11 x Claude and Codex; hard stop 10, retries for no answer only), installing the candidate kc-adr as a user would on both hosts, and report AC-1 and AC-2 per cell with the falsifiers. Report honestly any criterion not met.
Closing checks: version-parity-check.sh, skill-frontmatter-lint.sh, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/comment_ratio.py on the diff, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/design_surfaces.py check, and the roborev step in the scope notes. Commit in the worktree; FO handles push, PR and release.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Before your first change: `git -C <worktree> fetch origin main && git -C <worktree> merge --ff-only origin/main`. The shared checkout it was cut from is behind origin/main. Base for review: cebd0ab93c7f9b681d55434cfc99c19b2d9dd8ba.
Before reporting, commit your changes and run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base cebd0ab93c7f9b681d55434cfc99c19b2d9dd8ba`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
Do not bump kc-adr's version by hand; release-please owns it. Do not change kc-adr's writing.md or prefix.md (writing-tool ownership is dev2 task kc-adr-tools-with-dev2-copy).
Install for runs: Claude in an isolated HOME cannot log in. Use the real HOME with the candidate installed through a local marketplace pointing at your worktree, then restore the user's kc-adr 0.1.0 install (claude plugin marketplace update kc-claude-plugins; claude plugin install kc-adr@kc-claude-plugins) and say so in the report. Codex can use a per-run CODEX_HOME install. Model pins: claude --model sonnet; codex -m gpt-6.1-sol -c model_reasoning_effort="high". Check flags with --help first. Fictional data only.
