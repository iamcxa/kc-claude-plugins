Dispatched: from c3514876339cb732d0bea8b2d2dd45c234bcdeaf
Model: sonnet

## Checklist

Build the approved design exactly: add kc-adr/references/adr-template.md (dev2's template with "the worker or FO" -> "the recommender"), kc-adr/scripts/adr_lint.py (byte-identical to kc-dev-flow-2/scripts/adr_lint.py at the PR base) and kc-adr/scripts/test_adr_lint.py (AdrLintTests only); apply the approved writing.md replacement text; and the two approved scope additions: D1 (writing.md items 2 and 5 aligned with the single-writer numbering rule) and D2 (the README kc-adr paragraph and docs/journey/kc-decision-log/boundary-contract.md claims this change makes false). No dev2 file changes.
Verify AC-1..AC-3 per their evidence clauses: cmp on the linter and diff on the template against the base's dev2 files; kc-adr's test_adr_lint.py passes; the overlay run of dev2's suites with kc-adr's template and linter placed on dev2's paths in a scratch copy is green; the single-writer dry run passes the kc-adr linter; a text check of writing.md. Include the two template falsifiers.
Closing checks: version-parity-check.sh, skill-frontmatter-lint.sh, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py on the diff, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/design_surfaces.py check, the kc-plugin-forge sanitize-check for kc-adr, and the roborev step in the scope notes. Commit in the worktree; FO handles push, PR and release.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Before your first change: `git -C <worktree> fetch origin main && git -C <worktree> merge --ff-only origin/main`. Base for review: c3514876339cb732d0bea8b2d2dd45c234bcdeaf.
Before reporting, commit your changes and run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base c3514876339cb732d0bea8b2d2dd45c234bcdeaf`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
Do not bump kc-adr's version by hand; release-please owns it. Do not touch any kc-dev-flow-2 file or CI workflow: dev2's copies, the sync script, the byte compare and the CI trigger belong to the dev2 FO's task kc-adr-tools-with-dev2-copy.
No agent scenario runs are part of this task.
