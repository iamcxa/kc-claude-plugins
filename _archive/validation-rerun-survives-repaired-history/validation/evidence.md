# Independent validation evidence

Candidate: `0a5c37f091daec6909a76d443219c655b17d534e` (PR #844).
Task base and current merge base: `546a136386c94c58e430c91a6f3457b38bd73880`.
The three changed files match implementation's SHA-256 values in `candidate.json`.
Candidate behavior was executed from a `git archive` export; the product worktree
was read-only. Mutations ran on separate disposable copies, with Python bytecode
disabled. Git-metadata-dependent lint read the verified exact product checkout.

## Acceptance and falsifiers

- AC-1: `replay.json`, `recorded`: all nine recorded task revisions exercise the
  actual ruling predicate. Five repaired versions change 2 to 0; the two missing-
  ruling versions remain 1, and two unrepaired controls remain 2. The removed-catch
  mutant returns 2 at all five repaired versions (`extra-mutations.json`).
- AC-2: the two task controls and two web controls preserve exit 2 and their full
  diagnostic. Swallowing current/pinned parsing errors fails the strict control
  (`mutation-swallow-current-and-pinned-errors.log`).
- AC-3: both amendment and gate identities in broken pre-report text are held.
  `mutation-identity-always-absent.log` shows both assertions detect the unsafe
  clear. The independent real web control also exposes this mutation.
- AC-4: post-report malformed placement and a later repaired heading typo clear;
  removing the after-report exemption makes both fail
  (`mutation-drop-after-report-filter.log`).
- AC-5: pre-report broken text without the ruling identity clears for amendments
  and gates; invalid quoted gate text is included. Overblocking and narrowing the
  caught exception each fail (`mutation-every-pre-report-break-blocks.log`,
  `mutation-catch-only-ruling-history-error.log`).
- AC-6: `corpus-verification.log` and `replay.json` bind the exact six state tips,
  the aggregate comparison, and each public event. Private adopter task names,
  paths and text are omitted; only aggregate outcomes remain. The raw comparison
  was checked before redaction. The absent-identity mutant wrongly clears the
  real unruled web history at `fda02ff5` (`extra-mutations.json`).
- AC-7: repaired history without a later ruling returns 1 and the needs-later-
  ruling line. Unconditionally raising a saved parse error fails this assertion
  (`mutation-raise-any-stored-error.log`).
- AC-8: duplicate historical task paths, a fence hiding the report and undecodable
  bytes retain exit 2 at the released baseline and candidate. Removing each
  boundary fails its matching test (`mutation-accept-two-task-paths.log`,
  `mutation-ignore-hidden-report-gap.log`,
  `mutation-replace-undecodable-bytes.log`).
- AC-9: `suite.log` passes the full dispatch-record suite. The optional native
  builder test passes separately in `native-builder-corrected.log`. Weakening the
  same-commit ruling rule fails an existing test (`mutation-existing-suite.log`).
- AC-10: the diff adds one paragraph to ADR 0045 with the exact alignment and
  ideation-approval words. `adr-lint-dispatch-package.log` records the specifically
  assigned lint command, exit 0; omitting its required recommendation returns 1
  (`mutation-adr-lint-only.log`).

The released baseline fails six new assertions; all ten behavioral mutations are
killed (`mutation-baseline.log`, `mutations.json`). The report-rewrite test also
retains the existing refusal when its identity comparison cannot be made.

## Captain acceptance: four steps in a fresh shell

Prerequisites: Bash, Git, Python 3; the exact product checkout with its released
tag/base objects; a read-only local source containing the named task's state
commits; and the installed package. The existing sibling `implementation/replay.py`
is a declared dependency. No credentials or network are needed by these steps.

Run this exact command; `acceptance.log` is this validator's observed output:

```bash
TMPDIR=/tmp /bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-survives-repaired-history/validation/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-rerun-survives-repaired-history /Users/kent/conductor/repos/qnow-adopt-dev2 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1
```

The script's four steps print: exact export PASS; 12 tests OK; nine PASS revision
comparisons (five 2/0, two 1/1, two 2/2); and ADR lint PASS. It deletes its temporary
export and clone on exit. There is no changed graphical interface. This quick
script covers the real repaired task and safety controls, not the full six-branch
corpus, all tests, hosted CI, worker execution or delivery.

## Implementation limits adjudicated

- Accepted design limitation: two historical task paths, a fence hiding a report,
  and undecodable bytes remain held; acceptance explicitly incorporates the
  Captain's ideation decision. This is not a new repair finding.
- Historical replay is bounded to the six named `spacedock-state/dev2` tips.
  The other workflow branches and future states are not established.
- The predicate proves structural identity/order only. FO retains verification of
  the original reply, its semantic coverage and permission for the particular rerun.
- The implementation acceptance wrapper was only syntax-checked by its author.
  This validation supplies and actually runs the four-step replacement above.
- The full record suite's optional native test was separately run. The laws suite's
  optional external-source corpus remains skipped; the required six-branch replay
  is a separate exercised corpus, not evidence for that optional obligation check.
- Initial supplemental dispatch-stage discovery omitted `SPACEDOCK_BIN` and failed
  because it tried to execute `None`; `dispatch-stage.log` retains that setup error.
  The corrected run supplies the declared installed binary without changing tests.
- The first native-test invocation named a nonexistent test class;
  `native-builder.log` retains it and the corrected exact class passes separately.
- Loaded Codex and assigned Claude helper hashes agree except `design_surfaces.py`:
  the Codex installation also has a later story-record check. Its diff does not
  change the amendment parser. Both installations' design/dispatch guards were run;
  both pass. Candidate and released-baseline replays load exported package bytes,
  not either installed parser. See `package-hashes.json` and `package-design-diff.log`.
- RoboRev was not run by this validator; FO owns its review. The PR remains a
  delivery decision. CI cost per PR was not measured; no CI configuration changed.

## Scope and document review

The retained changes are necessary: historical parse recovery enables the repaired
task; raw identity and ancestry checks prevent the demonstrated unsafe clear;
strict current/pinned parsing and the rewrite guard retain the safety boundary.
The named mutation failures show each distinction matters. The test fixtures
exercise real Git history and the command entrance, not a mocked positive result.

`doc-impact.json`: ADR 0045 updated; ADR 0048 unaffected because completion and
publication authority do not change; `learning.md` unaffected because no adopted
practice changes. Existing output grammar is retained; `laws.log` exercises its
consumer. Workflow text, release versions, other product files and CI are unchanged.
`comment-ratio.log` has no added comment lines; the new module-docstring sentence
describes the rule rather than implementation history. No new finding is identified.
