# implementation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (5a951034f270efe967f56d1d3c3c69436d37b8ad, which carries captain-question-load #675, fo-write-checks #671 and number-guards-readme-shrink #670) implementing the five items of "What changes" in the task design as the Captain accepted D1, D2 and D3 at the ideation gate: the three passages and the chat-only-rules list in kc-dev-flow-2/skills/observer/SKILL.md; unstated_confirmations and the two record fields in kc-dev-flow-2/scripts/delivery_gate.py with kc-dev-flow-2/scripts/test_delivery_gate.py; the list lint in kc-dev-flow-2/scripts/lint-skills.py with kc-dev-flow-2/scripts/test_lint_skills.py; docs/adr/0024-chat-only-fo-rules-are-listed-not-judged.md
Re-baseline on origin/main 5a951034f270efe967f56d1d3c3c69436d37b8ad before building: #675 rewrote the Delivery authority paragraph and the merge-ask step ("Before merging or asking, FO runs"), so check each chat-only-rules phrase still occurs in kc-dev-flow-2/references/sd/workflow.md and rerun the AC-5 word counts there (README 5374, not 0.25.0's 5429); rebase on #675's kc-dev-flow-2/scripts/delivery_gate.py ASK line and test literals rather than reverting them; every acceptance criterion green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 24 exits 0; no word added to kc-dev-flow-2/references/sd/workflow.md; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Number guards: ADR: 0024

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved in batch 3 (「照建議」), accepting D1, D2 and D3 as recommended. AC-7 is the validator's observer run, not yours. The prototype and measurement files the design cites are under the task folder's `measure/` in the state checkout. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
