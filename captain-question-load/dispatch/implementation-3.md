# implementation-3

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); resumed worker (SendMessage) after the Captain had the refused hunks applied in its worktree
Model: sonnet

## Checklist

Under Captain amendment 1, continue from the uncommitted hunks now in your worktree (applied at the Captain's request, 2026-10-19, 「幫我跑看看……我暫時給你 bypass」): the three Delivery authority hunks in kc-dev-flow-2/references/sd/workflow.md, the ASK constant in kc-dev-flow-2/scripts/delivery_gate.py and its four literals in kc-dev-flow-2/scripts/test_delivery_gate.py. Read `git diff` first; keep their words, and rewrap the edited paragraph to the README's existing line width
Do the rest of the design: the docstring clause of kc-dev-flow-2/scripts/delivery_gate.py ("one last `next:` line, which is always the ask line") reworded; the pin delivery-question-carries-merge in kc-dev-flow-2/scripts/test_sd_dispatch.py with the two need strings of AC-3; docs/adr/0023-a-delivery-gate-question-may-carry-the-merge-of-the-validated-head.md; find and fix whatever kc-dev-flow-2/scripts/lint-skills.py and kc-dev-flow-2/scripts/test_delivery_gate.py now fail on (both exit 1 after the hunks)
Every acceptance criterion green, AC-2 and AC-4 measured on base 18dbf490 (README 5374 to 5374 measured after the hunks), each falsifier shown failing by a mutation you run (python3 -B, caches cleared); kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 23 exits 0; roborev evidence= line; push without force; one Draft PR (feat(kc-dev-flow-2): ...); CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Number guards: ADR: 0023

Profile: pilot. Captain authorization, verbatim (Captain amendment 1, 2026-10-19, chat): 「授權修改 Delivery authority 合併措辭，照 D1 設計。」 If the permission check refuses one of the remaining edits, stop and report which; do not retry or route around it. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved in batch 3 (「照建議」), accepting D1 and D2 as recommended and FO's order (number-guards-readme-shrink, then this task, then chat-only-evidence-observer-blind). AC-5 is measured by FO at batch close, not by you. The ADR Words line quotes the Captain's answer at the ideation gate as the briefing records it (review/ideation/briefing-1/index.json and the gate record reason), never FO's paraphrase. chat-only-evidence-observer-blind starts after this PR merges and will rebase on your Delivery authority hunk; change only the files your design lists, and stop and return to FO if the change needs another.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
