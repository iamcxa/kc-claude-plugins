# implementation-4

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #647 36ffa7a1 (local, unpushed)
Model: sonnet
Fresh worker: the live worker was unreachable when FO sent the AC-4 ruling, so this record replaces the follow-up FO first wrote here.

## Checklist

Recovery first: the previous worker is unreachable; its two unpushed commits 747d0fc9 and 36ffa7a1 (anchor plus template skip, and the SHA window ending at the next Verdict form) sit on the task branch in the existing worktree of PR iamcxa/kc-claude-plugins#647; check git status and git log, and keep them
Move AC-4 verbatim under Captain amendment 1 (task file) as Superseded text and write its replacement as a new AC id saying "Amended by Captain, amendment 1": the latest validation section that carries a counting Verdict form decides, and a latest REJECTED holds even when an older section PASSED; run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/design_surfaces.py check on the task file until it exits 0, and commit the state
Build that rule in kc-dev-flow-2/scripts/delivery_gate.py (walk sections from the latest; the first section with a counting form decides), flip the base test that pins an older candidate under a later REJECTED section, add the same-head case (PASSED, then a cycle-2 REJECTED on that head, exit 2) and a mutation restoring the fall-through, shown red; re-run the corpus count and report any section whose result changes
Suite, mutations, the roborev gate, one push of all commits without force, CI green, stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree. FO authorized the Codex round-1 P1 anchor and the validation F1 template skip (records implementation-2 and -3); the Captain ruled AC-4 on 2026-10-15 (amendment 1). Inside kc-dev-flow-2/scripts/delivery_gate.py and kc-dev-flow-2/scripts/test_delivery_gate.py, plus the task file for the criterion move. Push under the Captain's standing grant for repositories he owns ("No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar"). Roborev: `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base c545b896`; on exit 1 fix inside scope at most twice and report the rest. Run each suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. No comments, review requests, ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
