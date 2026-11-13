# Independent validation evidence

Candidate: `97fe3d6ff9f9afe220b463c71ac428e380fc4dc5`, PR #861.
Integration base: `c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694`.
Repair parent: `17eccdda05fde54e6dff66f4989787864219ef43`.
Profile: pilot. The validator did not implement either candidate.

## Captain acceptance

Prerequisites: bash, Python 3, Git, curl, tar, shasum, and HTTPS access to the public source repository. No product checkout, installed plugin, private adopter, credential, or retained temporary directory is required. Keep this committed validation folder: the script uses its adjacent parity probe and hash manifest.

Run from any directory, unchanged in a fresh shell:

```sh
env -u PYTHONPATH -u PYTHONHOME bash --noprofile --norc "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/observer-check-learn-only-when-listed/validation/acceptance.sh"
```

The script has four steps:
1. Download the public archive at the exact candidate; expect seven file hashes to print OK.
2. Exercise observer, history laws and the watcher with eight independently chosen forms; expect `passed: 8, total: 8`.
3. Exercise committed observer reports, historical revisions and bad selection; expect 23 tests, OK.
4. Exercise both callers and the generated detached-state command; expect 85 laws tests (one optional replay skipped), 137 watcher tests, and the final PASS line.

`acceptance.log` is the observed fresh-shell output, exit 0. `acceptance-summary.json` records duration and totals. The first attempt could not resolve the public download host inside the sandbox; `acceptance-sandbox-network.log` retains exit 6. The identical command passed with the authorized network allowance. Both runs removed their own exact temporary paths, printed in their logs.

This is command-line behavior, with no changed visual screen. The small acceptance script does not replay private corpora, run the full package suite, repeat native Spacedock recovery, establish hosted CI completeness, or authorize merge/release/adoption.

## Commands actually rerun

All candidate execution used a `git archive` export. Its independent fixture metadata under the owned /tmp directory received the three public source commits for read-only history queries; no shared repository worktree was created or removed. `identity.json` and `code-files.sha256` bind the input. The temporary execution copies matched the repair report's helpers byte-for-byte; helper-sources.json records their retained originals and hashes. Those duplicate copies were removed before publication to avoid republishing a private incident name embedded in an old helper; only `cross-reader-probe.py` and this acceptance wrapper are new evidence code.

For the following recorded commands, CODE is the exported candidate, E is this validation folder, and SCRATCH is CODE/.proof-scratch. Those historical commands used temporary execution copies at E, whose original sources and hashes remain in helper-sources.json; the Captain command above creates fresh paths itself.

- `python3 -B "$E/probe.py" fixtures --code "$CODE" --scratch "$SCRATCH"`
- `python3 -B "$E/probe.py" mutation --code "$CODE" --scratch "$SCRATCH"`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/mutations.py" --code "$CODE" --scratch "$SCRATCH"`
- `python3 -B "$E/words.py" "$CODE"`
- `python3 -B "$E/unreadable.py" --code "$CODE" --scratch "$SCRATCH/unreadable"`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/reproduce.py" --code "$CODE"`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B "$E/cross-reader-probe.py" --code "$CODE"`
- `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_observer_recovery.py`
- `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694`

The real and historical probe invocations used the same three read-only workflow inputs and historical cutoff recorded in AC-4, replacing only CODE/SCRATCH/output paths with this independent export. Public results contain counts only: `real-counts.json`, `historical-counts.json`, and `AC4-unexpected-verdict-output.json`. No private task bodies, names, titles, rulings or raw outputs were retained. `guards.json` records each exact guard command and exit; both selected-host and explicitly dispatched ADR-lint paths passed, with identical ADR-lint bytes.

## Acceptance and falsifiability

- AC-1: `fixtures.json` passes all 12 unselected cases; `baseline-goal.json` passes only the 12 selected cases and exits 1. `AC1-unconditional-learn.json` detects the unconditional-output reversal.
- AC-2: all 12 selected cases match the original base stdout/exit exactly. Focused tests in `acceptance.log` preserve live/committed/--rev behavior. Delete-notice, reorder-steps, disk-report and live-learn mutations fail their intended assertions.
- AC-3: missing, malformed and permission-denied selection holds; `unreadable.json` records exit 2, cause and zero next actions. `AC3-omit-printed-readme.log` reaches real detached post-archive execution and gets the expected wrong exit 2.
- AC-4: `real-counts.json` retains 237/237 output/verdict pairs across three corpora. `historical-counts.json` records 82 intended two-line deletions and zero other changes. The output-drift mutation is detected with counts only.
- AC-5: native recovery passes in `recovery.log`; actual invoked CLI version is Spacedock 0.27.2, not inferred from the plugin directory. Parser omission and each legacy-parser reversal fail. All three production readers use the same shared parser; every `listed` membership branch in watcher tasks inherits it. The three changed test files contain fixtures/assertions rather than independent activation readers.
- AC-6: `scope.json` records exactly six changed files, with no CI/config/dependency/adopter edit. `words.json` preserves the approved -22-word unlisted archive change, +2-word merged command change, and unchanged governing passages. Copied governing-document edits fail identity. CI cost per PR was not measured; CI was not changed.

`cross-reader-candidate.json` and `cross-reader-prior.json` are the validator's own falsifier, beyond the implementation tests: eight forms include commented empty lists, comment-only learn decoys, a trailing comma, blank/comment lines inside a block, and similarly named unselected items. The candidate passes 8/8; the repair parent passes 1/8 (exit 1). Each run exercises the real observer CLI, laws CLI and watcher main; no parser is mocked.

`mutations.json` records 11/11 detected falsifiers, with bytecode disabled. Inspection of the saved failures confirmed intended behavioral/identity assertion failures, not syntax errors. `comparison-summary.json` holds derived totals and source files remain the primary evidence.

## Limits and disposition

No new Material, Polish or Needs decision finding was established. The reported High parser mismatch is resolved at this exact head: its supported quoted block-list trigger now engages both laws and watcher checks.

The accepted historical limitation remains: the original archived incident was absent (presence count 0), and pairing a historical README with current tasks does not prove those bytes coexisted. Optional external-source replays remain unconfigured; the full local command excludes three pinned-Spacedock integration scripts, with native observer recovery exercised separately. These are bounded evidence gaps, not claims of end-to-end historical or delivery acceptance. A supported real input with extra output/verdict drift would reopen a Material finding against the corresponding accepted criterion.

`doc-impact.log` names learning.md: unaffected because its shared-parser and caller-audit practices remain true. Governing ADRs 0035, 0048, 0072 and 0083 were read; no new decision or ADR is needed. Package identity is recorded in `package-identity.json`: the host cache has an existing explicit-task-path handling overlay in design_surfaces.py; both installed versions pass this exact .md input, while all other invoked guard scripts match the dispatched cache. No cached package was changed.

The full local command passed: 25 scripts, 1377 tests total, 1366 passed and 11 skipped, with no duplicate script (full-suite-summary.json). The command, file enumeration and log are retained separately. Hosted status is only the timestamped `pr.json` observation; FO owns fresh review, gate disposition and delivery. Product files, branch and task frontmatter are unchanged.

