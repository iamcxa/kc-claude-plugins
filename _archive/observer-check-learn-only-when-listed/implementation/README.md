# Implementation evidence — trial round 2

Base: `c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694`; candidate: `17eccdda05fde54e6dff66f4989787864219ef43`; branch: `spacedock-ensign/observer-check-learn-only-when-listed`.
The branch was fast-forwarded to fetched origin/main before the six-file probe patch was applied. The two watcher hunks reconcile cleanly with PR 858; `scope.json` checks its retained absent-worktree fact behavior. Neither open PR 854 nor 856 was used as a base.

The approved acceptance criteria are unchanged. For this rerun, WT is the assigned implementation worktree, E is this implementation evidence directory, and the copied evidence helpers compare against the dispatch-required integration base rather than the old probe base. The original ideation evidence remains untouched. Installed operational checks use the dispatch-selected 0.39.1 package; the lint command uses the repository copy CI runs.

## Reproduction commands and recorded exits

```sh
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-check-learn-only-when-listed
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
TASK="$WORKFLOW/.spacedock-state/observer-check-learn-only-when-listed.md"
E="$WORKFLOW/.spacedock-state/observer-check-learn-only-when-listed/implementation"
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1
BASE=c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694
CANDIDATE=17eccdda05fde54e6dff66f4989787864219ef43
SCRATCH="$WT/.context/observer-learn-proof-scratch"
```

All positive commands below exited 0; `receipt.json` records their saved output. Run source commands from WT, and keep the explicit git -C paths. Real-adopter commands need the named read-only local clones; their output is counts only. A machine lacking those inputs must report that limit rather than invent a pass.

```sh
python3 -B "$E/probe.py" fixtures --code "$WT" --scratch "$SCRATCH" > "$E/fixtures.json"
python3 -B "$E/probe.py" mutation --code "$WT" --scratch "$SCRATCH" > "$E/mutation.json"
cd "$WT" && python3 -B kc-dev-flow-2/scripts/test_observer_check.py > "$E/focused.log" 2>&1
cd "$WT" && python3 -B kc-dev-flow-2/scripts/test_pr_watch.py > "$E/pr-watch.log" 2>&1
cd "$WT" && python3 -B kc-dev-flow-2/scripts/test_laws_check.py > "$E/laws.log" 2>&1
cd "$WT" && SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_observer_recovery.py > "$E/recovery.log" 2>&1
python3 -B "$E/probe.py" real --code "$WT" --scratch "$SCRATCH" --workflow /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2 --workflow /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2 --workflow /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2 > "$E/real-counts.json"
python3 -B "$E/probe.py" historical --code "$WT" --scratch "$SCRATCH" --workflow /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2 --readme-before 2026-10-10T00:00:00+08:00 > "$E/historical-counts.json"
PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/mutations.py" --code "$WT" --scratch "$SCRATCH" > "$E/mutations-run.log" 2>&1
python3 -B "$E/words.py" "$WT" > "$E/words.json"
cd "$WT" && python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$E/lint.log" 2>&1
cd "$WT" && python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" > "$E/adr-lint.log" 2>&1
python3 -B "$PKG/scripts/number_guards.py" check --repo "$WT" --workflow-dir "$WORKFLOW" --task "$TASK" --base "$BASE" --head "$CANDIDATE" > "$E/number-guards-fresh.log" 2>&1
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" "$CANDIDATE" --repo "$WT" --workflow-dir "$WORKFLOW" > "$E/comment-ratio.log" 2>&1
cd "$WT" && python3 -B "$PKG/scripts/doc_impact.py" "$BASE" "$CANDIDATE" > "$E/doc-impact.log" 2>&1
python3 -B "$PKG/scripts/design_surfaces.py" check "$TASK" > "$E/design-check.log" 2>&1
git -C "$WT" diff --check "$BASE" HEAD > "$E/diff-check.log" 2>&1
git -C "$WT" diff --check 8125e6d516d32abbf79c6772de10cde2c20900a8 HEAD > "$E/diff-check-probe-base.log" 2>&1
```

## Per-criterion result and falsifier

- AC-1: 12 unselected archive cases pass within the 24-case matrix. `mutation.json` detects unconditional learn. The corresponding matrix mutation exits 1 with 12/24 cases passing, not a syntax/import failure.
- AC-2: all 12 enabled cases match the integration base's bytes/exit. The 23 observer tests pass. Deleting the notice, reordering the steps, reading a report from disk, and printing learn on a live task each exit 1 under their named oracle; see the four AC2 outputs in `mutations.json`.
- AC-3: `python3 -B "$E/unreadable.py" --code "$WT" --scratch "$SCRATCH" > "$E/unreadable.json"` also exits 0 after observing a real permission-denied README: checker exit 2, cause present, zero next actions. The detached-state command actually runs before and after archive with enabled and unselected README settings. All 136 watcher tests pass. The omitted-README mutation exits 1 because the generated command returns 2 after archive. Its mutation runner bypasses the old command-string regex assertion to reach that runtime failure; the candidate tests themselves are unchanged and their assertions remain enabled.
- AC-4: all 237 enabled corpus output/verdict pairs match (82, 86, 69). The historical unlisted configuration gives 82 intended changes, zero unexpected. An unexpected committed-report prefix mutation changes 12 of the first corpus's 82 outputs, so the comparison exits 1. Private repository task data is neither saved nor printed in these artifacts.
- AC-5: native Spacedock recovery passes. Laws: 84 total, 83 passed, 1 optional external-source replay skipped; watcher: 136 passed. Omitting the parser from the isolated laws fixture makes the expected L1 violation disappear into a missing-module diagnostic and the test exits 1. The first mutation run exposed an import-path escape in the harness (8/9 detected); `mutations-before-env-fix.json` retains it. Removing inherited PYTHONPATH and rerunning all nine gives 9/9 detected; source candidate bytes never changed.
- AC-6: only six approved files differ; no version, dependency or CI file changes. Lint, ADR lint, number guards, comments, design and both diff checks pass. Comment ratio is 0.0%, maximum 5%. `words.json` retains unchanged governing passages as a common term: no-learn archived output loses 22 words; the printed merged-PR command adds 2 words; other changed-path moments add 0. A copied governing-document edit fails the identity assertion with exit 1, without editing a protected product document.

`mutations.json` records every negative child command, exit and saved output. Every mutation subprocess uses python3 -B with bytecode disabled, caches are cleared first, and disposable copies stay under the assigned worktree. Inspection confirmed each failure corresponds to its intended falsifier, not a SyntaxError substitute. `baseline-goal.json` runs the unchanged integration-base checker through the same matrix: exit 1, 12/24 pass, identifying the missing selection behavior.

## Documents, authority and limits

`doc_impact.py` lists `learning.md`: **unaffected**. Its existing laws-checking and shared-parser practices remain correct; this repair changes a caller argument and fixture dependency, not the practice or learning entry. No retained document outside the six-file scope needs an edit; the observer docstring inside the approved file was updated.

The existing-chain audit is reused from the approved design under Accepted ADR 0083. Changed facts were rechecked: origin/main, PR 858 watcher behavior, and current source/tests. Accepted ADR 0035 still governs listed/default extensions; no new ADR is required. ADR 0078's later moved-trunk check remains FO-owned.

The initial number-guard run warned that state fetch was sandbox-blocked; the exact check was rerun with narrow filesystem/network access and `number-guards-fresh.log` passes without that warning. It explicitly skips migration guarding because no migrations-path is declared; this task changes no migrations or ADRs.

No product push or PR was performed. RoboRev, product publication, hosted CI and independent validation are delegated to FO, not reported green. CI triggers are unchanged and CI cost per PR was not measured. The exact original historical task remains unavailable, as accepted at design; cross-snapshot evidence does not reconstruct that incident. The optional laws source replay remains unconfigured. No full package-suite claim is made.

PR title/body: `/tmp/impl-observer-check-learn-only-when-listed-pr.md`, also saved as `pr-text.md`; `pr-text-sha256.txt` pins its bytes. Keep this required handoff file. Cleanup of the disposable worktree proof root is recorded after the evidence commit in `cleanup.json`.
