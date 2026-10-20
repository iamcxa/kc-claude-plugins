# implementation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3, added before release
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main (891a9a24b51e5e9fda02a992c6a27910a216787d, which carries #679's kc-dev-flow-2/scripts/delivery_gate.py) implementing D1 as the Captain approved at the ideation gate (「批准」): ci_problem settles a CheckRun that finished SKIPPED or NEUTRAL; a head on which no check finished SUCCESS is still held; runs_problem unchanged; the module docstring states the rule (AC-6); tests in kc-dev-flow-2/scripts/test_delivery_gate.py for AC-1 to AC-5 placed as the design's Batch overlap says, rebased on #679's test helpers
Every acceptance criterion green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including AC-3's SUCCESS-beside-FAILURE row and AC-5's replay of the stored gh output for subspace-relay #398, #399, #401, #402 and subspace-web #150 through the stub harness; AC-7's words table recomputed on the candidate
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> exits 0; no change under docs/dev2, kc-dev-flow-2/references, kc-dev-flow-2/skills or kc-dev-flow-2/extensions; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-20, accepting D1 as recommended, which reverses the SKIPPED or NEUTRAL clause of merge-gatekeeper AC-1. The design's scratch prototype under /tmp/skipgate may be gone; rebuild what you need. Stored adopter gh output: re-read it read-only with `gh pr view <n> --repo spacedock-dev/subspace-relay|subspace-web --json statusCheckRollup,headRefOid` and save it under the task folder in the state checkout. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
