# implementation-1

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); batch 1
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main implementing D1 to D4 as recommended with FO's change: the package laws file, kc-dev-flow-2/scripts/laws_check.py and its template workflow; v1 is wired on no state branch by this PR; every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
No FO-read word added beyond the design; the candidate's own kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-16 in batch 1, accepting each decision as the gate question states. AC-8 may push a throwaway branch `spacedock-state/laws-probe` to origin and must delete it when done; do not commit to `spacedock-state/dev2` or any other existing state branch; installing the workflow on a real state branch is a later Captain decision per adopter.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's 「准」 (chat, 2026-10-16) to a gate question that says approval "is the grant for the implementation worker to push a branch and open a Draft PR". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. Other batch-1 tasks are in flight in other worktrees; change only the files your design lists, and stop and return to FO if the change needs another.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
