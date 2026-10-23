Dispatched: from 0701aa8debd45b3fe7eab7e930141319d52f3aa2
Model: sonnet

## Checklist

Build the approved design in the task's `## Design` (### Exact text) on a branch based on origin/main 0701aa8debd45b3fe7eab7e930141319d52f3aa2: the `**Protects:** none` label in `kc-adr/references/adr-template.md`; steps 4-6 in `kc-adr/skills/read-adr/writing.md`; checks 1 and 2 in `kc-adr/scripts/adr_lint.py` with the `docs/adr/NNNN` prefix match and the listed-files-only scan; tests in `kc-adr/scripts/test_adr_lint.py`. Use a `feat(kc-adr):` commit. Change no kc-dev-flow-2 file.
AC-1 and AC-2: run the linter tests (new and existing), the old-vs-new linter output comparison over this repository's ADRs, and the falsifier that removes the superseded scan and sees its test fail; record commands and exit codes.
AC-3: the `writing.md` text check, then one recorded agent run per host (claude, codex) using the harness at `_archive/adr-code-pointer-poc/harness/` in the spacedock-state/dev2-poc checkout (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state): copy it into this task's state folder, add scenario S15 per the design, commit the pass rule and grader before the first run, run with KC_ADR_ROOT at your candidate commit; include the design's falsifier worlds. Keep run records in this task's state folder.
Closing checks on the head: `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py` on the diff, `scripts/version-parity-check.sh`, `scripts/skill-frontmatter-lint.sh`, the sanitize rules, and `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since 0701aa8debd45b3fe7eab7e930141319d52f3aa2`. Write the stage report, every line DONE or SKIPPED, then commit and push the state branch path-scoped.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Worktree base: FO reset the fresh worktree to origin/main 0701aa8debd45b3fe7eab7e930141319d52f3aa2 before dispatch (the workspace HEAD is older and lacks kc-adr's tools).
Roborev: before reporting, run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 0701aa8debd45b3fe7eab7e930141319d52f3aa2` on the head and put its evidence line in the report.
Fictional data only for agent runs; nothing from a private decision repository. Agent-run budget: 2 counted runs plus falsifier worlds; an infrastructure failure gets one retry per cell.
