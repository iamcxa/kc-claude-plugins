# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5
Model: sonnet

## Checklist

One Draft PR (feat(scripts): ...) from a branch off origin/main (7244594bef4e1c9c42db0ed8ff42509ba6d48dd3) implementing the cycle-2 design with Captain Amendment 1: a new AGENTS.md holding the ## Decisions pointer (where ADRs live and when to look; no ADR text), one added @AGENTS.md line in CLAUDE.md, scripts/adr-path-check.py and scripts/adr-path-check.test.py (a trunk path is checked for existence; any branch or ref form is refused with a reason pointing at the trunk file; no ref is fetched or resolved), and .github/workflows/adr-path-check.yml (path-filtered, not required); only those five files
Every acceptance criterion still declared (AC-4 is superseded by AC-8) green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including AC-3's probes that the pointer reaches claude -p, an ensign and codex exec, and AC-5's red run on the PR
roborev evidence= line; push without force and without -u; CI green on the PR head; the new job's cost per PR measured from its run or stated as not measured; the PR body lists the unmeasured read effect under without-it unanswered (the Captain's D2)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Profile: pilot. Approved design: `## Design`, `## Acceptance criteria` and `## Captain amendments` in the task file; ideation gate approved 2026-10-22. No title hook (reopen: dev2-poc moment-of-use-rules-long-session-poc). qnow is its own task, not here. agents-md-holds-instructions edits the same two instruction files later; this task lands first. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run probes with time caps and an isolated config where a probe could write host settings.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
