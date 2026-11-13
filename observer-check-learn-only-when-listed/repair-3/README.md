# Parser repair before validation — trial round 3

Product branch: `spacedock-ensign/observer-check-learn-only-when-listed`. Integration base: `c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694`; reviewed candidate: `17eccdda05fde54e6dff66f4989787864219ef43`; repaired candidate: `97fe3d6ff9f9afe220b463c71ac428e380fc4dc5`. Only four files changed in this repair, all inside the approved six-file design; the combined feature diff still contains those six files.

## Finding verified before mutation

The finding is correct. `before-reproducer.json` records the unrepaired native fixture: the quoted/commented block list enables learn in observer_check.py (exit 1, learn steps present), but laws_check.py exits 0 and says L1 judged no events because the README lists no learn. The fixture has real committed task/sentinel/archive history, not just a parser call. `before-laws.log` and `before-observer.log` preserve the synthetic outputs; they contain no private adopter data.

`red-laws.log` and `red-watcher.log` show the two new tests failing on unrepaired production code. L1 skips the quoted block form and refuses valid inline lists with trailing comments; the watcher skips the block form and falsely enables learn when the word appears only in a trailing comment. Their hand-written expected booleans do not call the parser under test.

The repair removes L1's separate list parser, delegates through the existing shared reader with its diagnostic/dependency guards, and replaces the watcher's tokenization with the same reader. The new tests then pass (`green-laws.log`, `green-watcher.log`). `after-reproducer.json` records L1 exit 1 with a violation, no skip, and observer exit 1 with learn steps for the same quoted block form.

## Scoped reader inventory

`scope-and-readers.json` lists each of the six files. Production extension decisions are:
- `observer_check.py:learn_enabled`: already used workflow_extensions.readme_extensions; unchanged by the repair.
- `laws_check.py:readme_extensions`: now delegates to that reader, preserving Cannot diagnostics and dependency guards.
- `pr_watch.py:tasks`: now uses that reader instead of a tokenized raw frontmatter value.
The watcher's generic front_text helper still copies the raw field alongside other metadata, but the raw extension field no longer controls any extension choice. The three test files construct fixtures and assert behavior; they do not implement another activation parser. No replacement parser or external dependency was added.

## Reproduction commands

```sh
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-check-learn-only-when-listed
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
TASK="$WORKFLOW/.spacedock-state/observer-check-learn-only-when-listed.md"
E="$WORKFLOW/.spacedock-state/observer-check-learn-only-when-listed/repair-3"
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1
SCRATCH="$WT/.context/observer-learn-repair3-scratch"
BASE=c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694
CANDIDATE=97fe3d6ff9f9afe220b463c71ac428e380fc4dc5
```

The following positive commands were run from WT and exited 0; the expected failing mutation children are recorded separately with exit 1. Helpers compare against the original integration base as in round 2; the prior candidate was also exercised directly by the two red tests before the repair. Private corpus commands remain read-only and emit counts only.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/reproduce.py" --code "$WT" > "$E/after-reproducer.json"
python3 -B "$E/probe.py" fixtures --code "$WT" --scratch "$SCRATCH" > "$E/fixtures.json"
python3 -B "$E/probe.py" mutation --code "$WT" --scratch "$SCRATCH" > "$E/mutation.json"
cd "$WT" && PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_observer_check.py > "$E/focused.log" 2>&1
cd "$WT" && PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_pr_watch.py > "$E/pr-watch.log" 2>&1
cd "$WT" && PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_laws_check.py > "$E/laws.log" 2>&1
cd "$WT" && SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_observer_recovery.py > "$E/recovery.log" 2>&1
python3 -B "$E/probe.py" real --code "$WT" --scratch "$SCRATCH" --workflow /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2 --workflow /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2 --workflow /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2 > "$E/real-counts.json"
python3 -B "$E/probe.py" historical --code "$WT" --scratch "$SCRATCH" --workflow /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2 --readme-before 2026-10-10T00:00:00+08:00 > "$E/historical-counts.json"
PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/mutations.py" --code "$WT" --scratch "$SCRATCH" > "$E/mutations-run.log" 2>&1
python3 -B "$E/words.py" "$WT" > "$E/words.json"
python3 -B "$E/unreadable.py" --code "$WT" --scratch "$SCRATCH/unreadable" > "$E/unreadable.json"
cd "$WT" && python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$E/lint.log" 2>&1
cd "$WT" && python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" > "$E/adr-lint.log" 2>&1
python3 -B "$PKG/scripts/number_guards.py" check --repo "$WT" --workflow-dir "$WORKFLOW" --task "$TASK" --base "$BASE" --head "$CANDIDATE" > "$E/number-guards.log" 2>&1
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" "$CANDIDATE" --repo "$WT" --workflow-dir "$WORKFLOW" > "$E/comment-ratio.log" 2>&1
cd "$WT" && python3 -B "$PKG/scripts/doc_impact.py" "$BASE" "$CANDIDATE" > "$E/doc-impact.log" 2>&1
python3 -B "$PKG/scripts/design_surfaces.py" check "$TASK" > "$E/design-check.log" 2>&1
git -C "$WT" diff --check 8125e6d516d32abbf79c6772de10cde2c20900a8 HEAD > "$E/diff-check-probe-base.log" 2>&1
```

## Per-criterion results

- AC-1: `fixtures.json` has all 12 unselected cases passing; unconditional learn is detected by `mutation.json` and the named negative matrix.
- AC-2: all 12 enabled matrix cases match base stdout/exit; 23 observer tests pass. Deleting/reordering steps, reading a report from disk and printing learn live each fail the intended oracle.
- AC-3: 137 watcher tests pass; detached-state generated commands execute correctly; omitting the printed README causes real exit 2 after archive. `unreadable.json` proves permission-denied selection returns 2, a cause and no next actions.
- AC-4: three enabled corpora retain all 237 output/verdict pairs; historical unlisted configuration gives 82 intended deletions and zero unexpected changes. Unexpected output mutation is detected with counts only.
- AC-5: 85 laws tests (84 passed, one optional source replay skipped), 137 watcher tests and native recovery pass. Isolated dependency omission fails the expected law assertion. The new two parser-regression tests fail on prior code, pass after repair, and fail again when each legacy parser is restored in a disposable mirror.
- AC-6: only the approved six combined files differ; the repair changes four of them. Lint, ADRs, number guards, comments, design and diff checks pass. Added comments 0.0%, maximum 5%; no version, new dependency or CI-trigger change. `words.json` retains the approved footprint comparison (-22 words for unlisted archive output, +2 for the printed merged command, zero other changed-path moments); a copied governing-document edit fails its identity assertion.

`focused-summary.json` accounts for the three focused suites. `mutations.json` records 11 detected falsifiers, each negative child exiting 1 with Python -B, bytecode disabled and caches cleared. Inspection found the intended failures rather than SyntaxError substitutes. The initial mutation preparation omitted one source dictionary entry; the helper-only error is retained and all eleven were rerun. The initial words check raced fixture completion; its error is retained and the dependent check was rerun after the fixture file completed. Neither orchestration correction changed candidate bytes.

## Full local unit command and limits

`full-suite-command.txt` is the repository's exact merge-test command, run unchanged from the assigned worktree with bytecode disabled. `full-suite-files.json` lists all 25 participating scripts with no duplicates; `full-suite.log`, `full-suite-exit.json` and `full-suite-summary.json` carry completion and counts. The command excludes three pinned-Spacedock integration scripts by design; native observer recovery was also run separately. This is local unit evidence, not hosted CI or an independent verdict.

`doc-impact.log` names learning.md: **unaffected**. Its shared-parser/laws practices remain correct and no learning entry is changed. No new ADR or scope/criterion decision is introduced. RoboRev job 1809 is FO-reported evidence that was independently reproduced, not a fresh clean review; FO reruns RoboRev and independent validation on the repaired head. No product push, review request, PR comment, ready or merge action was performed. CI cost per PR remains not measured, with CI unchanged. The accepted exact-old-incident and optional source-replay limits remain.

Scratch and retained PR text are listed in `cleanup.json` after the evidence commit. This is build round 3 of at most 3; another build round requires the Captain's decision.
