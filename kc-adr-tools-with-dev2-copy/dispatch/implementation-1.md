# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5 addition
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (fd630b2a20d53cc3482159857c1143f34f70dd8f) implementing the approved cycle-2 design with the Captain rulings D1 to D5: the sync script and its test, the byte-identical copies of kc-adr/references/adr-template.md, kc-adr/scripts/adr_lint.py and the kc-adr/skills/read-adr skill folder in kc-dev-flow-2, the kc-dev-flow-2/scripts/lint-skills.py exemption for the copied folder, the parity-job steps in marketplace-parity.yml (byte compare, its test, kc-adr/scripts/test_adr_lint.py), the design-director skill naming the dev2 copy, the D5 pointer folded into the existing ADR sentence of kc-dev-flow-2/skills/implementation/principles.md, and the three kc-adr writing.md edits in intake/kc-adr-fo-writing-md-edits-2026-10-23.md applied to kc-adr and carried by the sync; the PR body names the D4 two-plugin exception
Every acceptance criterion green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including the install probe that kc-dev-flow-2:read-adr resolves on Claude Code and Codex in isolated configs, and a grep of <kc-adr> in the copied writing.md and SKILL.md returning nothing
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base>, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file, cycle 2; ideation gate approved 2026-10-23 (Captain 「可以」); Captain Amendments 1 and 2 and rulings D1 to D5 under ## Captain amendments and ## FO alignment. The kc-adr FO agreed the writing.md edits ride this PR (intake). This PR touches kc-adr/ and kc-dev-flow-2/ by the Captain's D4; name that exception in the PR body. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
