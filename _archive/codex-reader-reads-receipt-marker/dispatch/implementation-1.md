# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5, first to implement
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (c27e76590c1d2dc910e7fa2d332242a7534df0b0) implementing the cycle-3 design and Captain Amendments 1 to 3: kc-dev-flow-2/extensions/codex/codex_review.py and its tests (v1 receipt marker read as clean; exit 5 with unrecognized=comment:<id> for an unread Codex comment naming the head), kc-dev-flow-2/scripts/pr_watch.py and kc-dev-flow-2/scripts/test_pr_watch.py (give up after two consecutive unrecognized reads at least 180 s apart, three lines, the upstream line with its three branches per Amendments 2 and 3), and the one EXTENSION.md sentence; every file the design names and no other
Every acceptance criterion green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including AC-1's live read of iamcxa/kc-paseo-plugins#8 and the 22-PR base-versus-candidate replay; the upstream line's third branch (package repository files a backlog task) carries its own test
kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Profile: pilot. Approved design: `## Design`, `## Acceptance criteria` and `## Captain amendments` in the task file; ideation gate approved 2026-10-21. No ADR number is reserved. codex-reader-counts-code-review-only edits the same reader and lands after this task; idle-names-failing-seeds and new-work-starts-from-a-story-map edit other functions of kc-dev-flow-2/scripts/pr_watch.py. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
