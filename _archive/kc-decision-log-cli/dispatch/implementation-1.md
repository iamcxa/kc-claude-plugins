Dispatched: from c27e76590c1d2dc910e7fa2d332242a7534df0b0
Model: sonnet

## Checklist

Build the kc-adr plugin as Captain amendment 1, Captain amendment 2, Captain amendment 3 and Captain amendment 4 and the approved cycle-2 design define it, skill-only: `kc-adr/` with Claude and Codex manifests, `skills/read-adr/SKILL.md`, `writing.md`, `prefix.md`; a marketplace entry at 0.1.0 marked experimental; release-please wiring; marketplace README row. `scripts/version-parity-check.sh` and the repo's plugin checks pass, and no dev2 script or template is copied.
Run the approved evidence plan (28 runs, hard stop 34, dated CHANGES.md before the first changed-scenario run) and record per-criterion evidence for AC-4 to AC-9, with AC-9's real dev2 dispatch transcript as the main proof. Report honestly any criterion not met.
Closing checks: `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/design_surfaces.py check <task>`, `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/comment_ratio.py` on the diff, and the roborev step in the scope notes. Leave the commits in the worktree; FO handles push and PR at delivery.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Before your first change, bring the fresh worktree branch up to origin/main: `git -C <worktree> fetch origin main && git -C <worktree> merge --ff-only origin/main`. The shared checkout it was cut from is behind origin/main. Base for review: c27e76590c1d2dc910e7fa2d332242a7534df0b0.
Before reporting, commit your changes and run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base c27e76590c1d2dc910e7fa2d332242a7534df0b0`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
Read the task's `## Captain amendments` 1-4 and the cycle-2 `## Design`. Plugin name kc-adr, skill read-adr. Writing tools are named by role and resolved in one paragraph that points at dev2's installed tools; ownership is undecided (dev2-poc kc-adr-dependency-poc). Do not copy dev2 scripts.
Evidence harness: copy the archived adr-read-and-route-poc harness from /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state/_archive/adr-read-and-route-poc/ into this task's state folder. Do not edit the archive. Fictional data only. Pin models: claude --model sonnet; codex -m gpt-6.1-sol -c model_reasoning_effort="high". Check flags with --help first and tell FO before passing 34 runs.
Plugin conventions: the repo CLAUDE.md (two-phase sync, version parity across plugin.json, .codex-plugin and marketplace.json, README sync rule). No tag, no local install sync, no push.
