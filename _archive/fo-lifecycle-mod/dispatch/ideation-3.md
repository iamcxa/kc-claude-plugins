# ideation-3

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: opus
Redo after Captain amendment 3 (task sent back from validation) with amendment 4 constraints. dispatch build reported effective_model=sonnet; FO launched the worker with model=opus.

## Checklist

A redone design (PRFAQ and Mermaid) under Captain amendments 3 and 4: for each FO step tied to a lifecycle moment, exactly one home (the mod for moment-bound steps, the README for authority rules) with the README keeping at most a one-line pointer; where a package script already runs at that moment (/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/observer_check.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/pr_watch.py), the next action carried in the script's own output instead of prose, naming each script change; the mod text written to the four STE rules (numbered steps, one action per step, condition first, at most 20 words per sentence); keep the observe-merged step validation already showed works; carry the two open Codex round-2 items (the Draft-PR authority handshake, as a Captain decision with a recommendation; the stale closed PR re-recorded after merge guard --rework)
A measured word table per moment (startup, idle on an open PR, idle on a merged PR, after the archive, the merge ask): the words FO must read at that moment today on origin/main and under the design (README passages plus mod plus script output), with the design lower at every moment and in total; acceptance criteria with reproducible evidence clauses and falsifiers, and a replay plan whose cue is a Captain utterance (not an FO label) with its run count stated for the Captain to approve
For every review finding the old design absorbed (Codex rounds 1 and 2, roborev, validation cycles 1 and 2 under ### Feedback Cycles), the disposition under amendment 4's three rules: a script check or test instead of prose where one can, otherwise prose with an equal number of words removed, and any new condition as its own step
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. This is ideation cycle 3, a redo: the Captain sent the task back (amendment 3) because the old design put each step in both the README and a mod, so FO's total reading grew by about 507 words while the README shrank by 80, and every review round added prose. Read the whole task file first: `## Captain amendments` (1 to 4), `### Feedback Cycles` (cycles 1 and 2) and the earlier stage reports are evidence, and the old `## Design` is superseded. Replace it rather than editing around it, and keep the old acceptance criteria only where amendment 3 leaves them standing; supersede the rest in the amendment entries the way the workflow's Captain amendments rules say. Evidence on disk (read only): the old candidate is PR iamcxa/kc-claude-plugins#643 (Draft, head d6a427aa); validation replays and harness under the task's `validation/` folder and /tmp/replay-s2 and /tmp/replay-c2; Spacedock's mod convention in /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0/skills/first-officer/references/first-officer-shared-core.md and its source. Spacedock is not changed. Related tasks you must not absorb: dev2-laws-check (a laws file checked over state history), names-check-before-dispatch, pr-watch-state-per-session, extension-instruction-reaches-dispatch; name any file you expect to share with them.

Dispatched on the stronger model because the design sets what FO loads at every lifecycle point in every adopter and the previous design's premise failed.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, do not launch any replay, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
