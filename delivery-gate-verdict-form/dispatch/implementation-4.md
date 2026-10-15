# implementation-4

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #647 36ffa7a1 (local)
Model: sonnet

Follow-up message to the live implementation worker: the Captain's AC-4 ruling (amendment 1) and the push.

## Checklist

Move AC-4 under amendment 1 and write the replacement AC; design_surfaces.py check exits 0
Build the latest-verdict-decides rule in kc-dev-flow-2/scripts/delivery_gate.py, flip the base test, add the same-head REJECTED case and its mutation, re-run the corpus count
Suite, mutations, roborev gate, one push without force, CI green, stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

> 1. Move AC-4's block verbatim from `## Acceptance criteria` into the amendment entry under a `Superseded text:` line, and write its replacement as a new AC id saying "Amended by Captain, amendment 1": the latest validation section that carries a counting Verdict form decides; a latest REJECTED holds even when an older section PASSED; the quoting, template and window rules stay. Then run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/design_surfaces.py check on the task file until it exits 0, and commit the state with `spacedock state commit`.
> 2. Build (3) in kc-dev-flow-2/scripts/delivery_gate.py: walk the validation sections from the latest; the first section with a counting form decides; a REJECTED there holds. Flip the base test that pins an older candidate under a later REJECTED section, naming the amendment in the test's name or docstring. Add the validator's rej2.md case (PASSED then a cycle-2 REJECTED on the same head, exit 2) and a mutation that restores the fall-through, shown red. Re-run the corpus count and report any section whose result changes.
> 3. Suite, mutations, the roborev gate (/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base c545b896), then one push of all commits without force, CI green, stage report appended, completion to `main`. No comments, review requests, ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
