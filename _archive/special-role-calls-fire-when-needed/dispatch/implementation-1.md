# implementation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3, added before release
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (891a9a24b51e5e9fda02a992c6a27910a216787d) implementing the design as the Captain accepted D1 to D5 at the ideation gate: kc-dev-flow-2/scripts/role_triggers.py and kc-dev-flow-2/scripts/test_role_triggers.py per the design's "Keep, change, drop" table (chief-engineer owed at four repair passes read from stage-report headings, D2; engineering-reviewer one line per task cleared by date, with the model chosen by profile: prod or a db surface for Fable, otherwise Opus, D4); the review-round count as the last, separately droppable slice (D1, AC-6); docs/adr/0026 with the design's ADR draft; every other file the design names
Every acceptance criterion AC-1 to AC-9 green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including the replay over the four repositories' committed records the design measured (38 window tasks, 287 overall) reproducing the fire counts it states
D5 stage 1 only, as a committed report under the task folder in the state checkout, not in the PR: for the 10 saved prod validation reports, each later inline finding and roborev High on the same PR, classified as an escape or not, with no model run
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 26 exits 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Number guards: ADR: 0026

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-20 (D1 「同意」, D2 「第四輪」, D3 「Ａ」, D4 「Ａ」, D5 「同意」), each as recommended. The ideation's measuring scripts under /tmp/ideation-rc may be gone; rebuild what you need and save replay inputs under the task folder. State checkouts to read, read-only: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state, /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state. If a change needs a file the design does not list, stop and return to FO. PR #680 (delivery-gate-settles-skipped-checks) is open and shares no file with this task.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
