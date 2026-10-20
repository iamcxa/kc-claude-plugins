# implementation-1

Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5 (workflow checkout, kc-dev-flow-2 0.26.0 README); batch 4
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (ad44f0cbf42274ff65802cabc52ebe919f159fd5) implementing the design as the Captain ruled at the ideation gate and in Amendments 1 to 3: rule 3 in kc-dev-flow-2/scripts/design_surfaces.py (D1), rule 2's parse fix and F-id join in kc-dev-flow-2/scripts/delivery_gate.py with the one validator sentence in kc-dev-flow-2/skills/validation/principles.md (D5), the named-carry sentence and the (verdict ask) tag on the kc-dev-flow-2/scripts/delivery_gate.py ASK and class lines (D2 narrowed per Amendment 1, D3, D6), the README phrase "between gates" in kc-dev-flow-2/references/sd/workflow.md, their tests, and docs/adr/0027 with the short title Amendment 2 names; no rule-1 check (Amendment 2) and nothing from `### Deferred to the D7 guard task`
Every acceptance criterion still declared in the task file (AC-7 is superseded with no replacement) green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including the replays over the four repositories' committed records the design measured; the shipped kc-dev-flow-2/scripts/test_delivery_gate.py expectations updated for the tag and sentence (the design counts 62 assertions) as a mechanical edit
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 27 exits 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0

Number guards: ADR: 0027

Profile: pilot. Approved design: `## Design`, `## Acceptance criteria` and `## Captain amendments` in the task file; ideation gate approved 2026-10-20 (D1 「要」, D2 「Ａ」, D3 「第九題要」, D4 「那就不做」, D5 「好」, D6 「可以」, D7 「好」). The ADR's Words line quotes those replies verbatim. The prototypes and saved outputs under fo-write-rules-checked/measure/ are inputs; rebuild what you need. State checkouts to read, read-only: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state, /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state. If a change needs a file the design does not list, stop and return to FO. comment-check-reaches-delivery-gate was closed without building, so nothing orders this task after it. Open PRs #685 (workflow.md line 2) and #686 (kc-dev-flow-2/scripts/number_guards.py and one workflow.md bullet) touch workflow.md on other lines; whichever merges later reruns kc-dev-flow-2/scripts/lint-skills.py.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
