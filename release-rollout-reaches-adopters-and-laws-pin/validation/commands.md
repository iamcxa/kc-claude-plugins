# Commands executed

Candidate sources came from `git -C "$rollout_repo" archive 61529999eb4184b44328fe2fbad545b1b0b0ed92`, extracted to `/tmp/rollout-validation-838/candidate`; base was exported similarly. No git worktree was created. For read-only checks needing revision metadata, the environment was:

```sh
rollout_repo=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-rollout-reaches-adopters-and-laws-pin
rollout_package=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1
rollout_workflow=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
rollout_task="$rollout_workflow/.spacedock-state/release-rollout-reaches-adopters-and-laws-pin"
export GIT_DIR=/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/spacedock-ensign-release-rollout-reaches-adopters-and-laws-pin
export GIT_WORK_TREE=/tmp/rollout-validation-838/candidate
cd /tmp/rollout-validation-838/candidate
python3 -B kc-dev-flow-2/scripts/test_package_version.py
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 "$rollout_package/scripts/adr_lint.py" docs/adr --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0075
python3 "$rollout_package/scripts/number_guards.py" check --workflow-dir "$rollout_workflow" --task "$rollout_task.md"
python3 "$rollout_package/scripts/comment_ratio.py" e8664a72b0f904e5dda3c391d52ab3abaca876b4 61529999eb4184b44328fe2fbad545b1b0b0ed92 --workflow-dir "$rollout_workflow"
python3 "$rollout_package/scripts/doc_impact.py" e8664a72b0f904e5dda3c391d52ab3abaca876b4 61529999eb4184b44328fe2fbad545b1b0b0ed92
python3 "$rollout_package/scripts/design_surfaces.py" check "$rollout_task.md"
python3 "$rollout_package/scripts/dispatch_records.py" "$rollout_task"
```

Number guards were rerun with remote access after the first sandbox run warned that its state fetch failed; `number-refreshed.log` is authoritative. The git environment above is restricted to the archive's read-only revision checks and proof runners, never used for disposable-repository commits.

The original, order and integrity proof runners were copied from this task's implementation evidence, inspected and run in `/tmp/rollout-validation-838/evidence/{original,order,integrity}/prove.py`, each with `/tmp/rollout-validation-838/candidate` as its argument and `python3 -B`. They write logs beside themselves and mutate only disposable copies. Their source is retained here. The integrity runner's descriptive byte count now reads the fresh provider response rather than the implementation's old literal. `pin-skew/probe.py` was similarly reused, with only its read-only git source path pinned to the assigned repository; it ran without GIT_DIR/GIT_WORK_TREE and created its own disposable repository.

The state checks ran without the archive git environment:

```sh
python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/role_triggers.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state release-rollout-reaches-adopters-and-laws-pin
python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/dispatch_records.py --names --strict /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-rollout-reaches-adopters-and-laws-pin/dispatch/validation-1.md
```

`live.py` records the exact candidate rollout command, the pre-network local-list check, the two independent `gh api` reads and the altered-release/pin falsifiers. `provider-probes.py` records all matching-ref and omitted-content API requests. `recount.py` records the independent document spans and `wc -w` comparisons. All use the declared `/tmp` export/evidence location; the only standalone Captain entry is `acceptance.sh` documented in README, which creates its own export.
