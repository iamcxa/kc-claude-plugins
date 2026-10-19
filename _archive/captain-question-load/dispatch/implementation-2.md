# implementation-2

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); resumed worker (SendMessage) after the permission check refused the Delivery authority edit; the Captain re-authorized it
Model: sonnet

## Checklist

Under Captain amendment 1, one Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (18dbf490b399ecaa8ec288188bd1cf25e5c9d3ab, which already carries fo-write-checks #671 and number-guards-readme-shrink #670) implementing D1 and D2 as recommended: the two edits of "Mechanism: the sentence and the line the implementation lands" (kc-dev-flow-2/references/sd/workflow.md Delivery authority; the ASK constant and one docstring clause of kc-dev-flow-2/scripts/delivery_gate.py with the literals of kc-dev-flow-2/scripts/test_delivery_gate.py (four literals on origin/main, not three)), the pin delivery-question-carries-merge in kc-dev-flow-2/scripts/test_sd_dispatch.py, and the ADR at docs/adr/0023-a-delivery-gate-question-may-carry-the-merge-of-the-validated-head.md; every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
AC-2 and AC-4 re-baselined on origin/main 18dbf490b399ecaa8ec288188bd1cf25e5c9d3ab: README and Delivery authority word counts at base and candidate measured there (the design's 5429 and 447 were drafted on c60e89e1), no moment above its base, no raise step; the AC-4 diff check also allows the test-literal changes #671 made to kc-dev-flow-2/scripts/test_delivery_gate.py to stand
kc-dev-flow-2/scripts/lint-skills.py exits 0 on the candidate; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 23 exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Number guards: ADR: 0023

Profile: pilot. Captain authorization for this edit, verbatim (Captain amendment 1 in the task file, 2026-10-19, chat): 「授權修改 Delivery authority 合併措辭，照 D1 設計。」 His precondition that the PR be ready before FO merges is already a hold in kc-dev-flow-2/scripts/delivery_gate.py (a draft PR exits 1), so it adds no README word. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved in batch 3 (「照建議」), accepting D1 and D2 as recommended and FO's order (number-guards-readme-shrink, then this task, then chat-only-evidence-observer-blind). AC-5 is measured by FO at batch close, not by you. The ADR Words line quotes the Captain's answer at the ideation gate as the briefing records it (review/ideation/briefing-1/index.json and the gate record reason), never FO's paraphrase. chat-only-evidence-observer-blind starts after this PR merges and will rebase on your Delivery authority hunk; change only the files your design lists, and stop and return to FO if the change needs another.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
