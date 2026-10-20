# implementation-1

Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5 (workflow checkout, kc-dev-flow-2 0.26.0 README); batch 4
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (ad44f0cbf42274ff65802cabc52ebe919f159fd5) implementing the design as the Captain accepted D1 and D2 at the ideation gate (migrations-path: none, and R7 fails an added NNNN_name.sql under it): every file the design's Batch overlap list names (kc-dev-flow-2/scripts/number_guards.py, kc-dev-flow-2/scripts/test_number_guards.py, the one workflow.md bullet, the ADR 0002 Amended paragraph, and the rest of that list)
Every acceptance criterion AC-1 to AC-9 green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including AC-8's replay on the real relay record; AC-7's paragraph quotes the Captain's gate words verbatim (D1 「可以」, D2 「要」); AC-9's order sentence in the PR body
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr exits 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-20 (D1 「可以」, D2 「要」, each as recommended). No new ADR number is reserved; ADR 0002 gains an Amended paragraph only. Adopter state to read, read-only: /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state, /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state. If a change needs a file the design does not list, stop and return to FO. commissioned-by-names-spacedock is in implementation and edits line 2 of workflow.md, a different line from yours; whichever merges second reruns kc-dev-flow-2/scripts/lint-skills.py.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
