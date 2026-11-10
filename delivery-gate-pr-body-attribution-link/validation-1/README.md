# Independent validation of PR #825

Verdict: PASSED at `2a72c89b9aa9d114e45aeb16b746b8ca9f747bb8` against `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1` (origin/main at validation entry, also hosted PR base). Profile: pilot. Review-finding disposition: no new Material, Deferred risk, Polish or Needs decision findings. This is a fresh validator of the same OpenAI model family; it is not a cross-family review.

## Captain acceptance

No graphical screen changes. The following command runs four numbered steps in a fresh bash shell, with a temporary archive export and no worktree/config writes:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-gate-pr-body-attribution-link/validation-1/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-pr-body-attribution-link
```

Prerequisites: git, tar, Python 3.10+, this evidence directory and the assigned repository containing both pinned commits. No network, credential, installed plugin or hidden environment variable is required. The exact step commands and expected observations are in `acceptance.sh`; its observed output is `acceptance.log` (exit 0). It exports both commits, exercises both command routes and counterexamples, runs nine regression/boundary tests, then checks scope/startup/help. This local script does not establish hosted merge, release, installation or review independence.

## Evidence and falsifiers

- AC-1: `routes/cli-matrix.json` pairs actual base/candidate CLI subprocesses for both `question` and `steps`. Exact, surrounding-space and internal-whitespace attribution lines change exit 1 to 0; `routes/question-removed-exemption.log` and `no-line-exemption.log` catch removal of the filter.
- AC-2: named Captain links hold on both CLI routes and pass once recorded. Their unrecorded hold output is byte-identical at base/candidate. `routes/captain-link-mutation.log` shows the existing assertion failing when link coverage is removed; both named existing tests also run unchanged in the complete suite and acceptance script.
- AC-3: the same URL in a card's instruction, FO's message, a prefix/suffix, or a line with an additional link still holds. `url-wide-exemption.log` and `substring-exemption.log` show overbroad variants caught by the regression tests. `steps` reports both links; `question` retains its existing first-failure presentation.
- AC-4: a separate real link beside attribution holds only on the real link. Real CLI output is in `routes/other-url-*-candidate.log`; `routes/baseline-regressions.log` and `no-line-exemption.log` detect missing exclusion.
- AC-5: `suite.log` / `tests.json`: 206 run, 205 passed, one pre-existing optional historical-replay skip, exit 0. `candidate.diff` contains only the two approved Python files. Acceptance step 4 rejects an extra-file counterexample; the new bounded help clause and exact set membership agree.
- AC-6: `words.json` / paired logs: question 60-word hold to 97-word pass; Captain-link hold 60/60 and byte-identical; help 1214 to 1225; README/workflow bytes identical. `routes/output-drift-mutation.log` adds one output word, producing 98 and failing the pinned 97-word expectation. `prove.py` also compares unchanged check() source/output with the existing provider fixture.

`route-probes.py` reuses repository fixtures and adds real CLI paired observations. `run-suite.py` is copied unchanged from the implementation evidence. `prove.py` preserves the implementation checks with only Git show reads replaced by the actual base archive, keeping tests away from shared Git metadata. Both proof scripts run with `python3 -B`. The first supplemental probe selected one test from the wrong class; correcting that validator-only test selection made the probes pass and changed no candidate bytes.

## Other rerun checks

`checks.json` records the exact commands and exit codes for repository lint-skills, ADR lint, comment ratio, document impact, design surfaces, dispatch records, role triggers and diff whitespace. The loaded validation skill resolves its package to `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0`; role_triggers uses the dispatch's explicitly prescribed Claude cache path. Git-aware read checks use the assigned checkout's GIT_DIR with GIT_WORK_TREE bound to the candidate archive, never exported into tests.

ADR command: `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py docs/adr --since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`, exit 0 (`adr-lint.log`); repeated with `--require 0044 0051 0054 0062 0071 0072`, exit 0 (`adr-lint-required.log`). No new ADR or number reservation is owed by this bounded repair inside ADR 0054.

Number guards initially returned exit 0 with a sandbox-blocked state-ref refresh; the exact same check was rerun with permitted metadata/network access and returned exit 0 without the warning (`number-guards-refreshed.log`). Migration checking is inapplicable: no migrations path or migration changes. Comment ratio is 93 code lines, zero comment lines, 0.0%, maximum 5%; no new comments to disposition. Workflow 5931/5931 words. No CI workflow changed; cost per PR was not measured.

The first sandboxed GitHub refresh failed to connect; it is preserved in `checks.json`. The authorized read-only retry succeeded: `pr.json`, `required-checks.json`, and `hosted-summary.json` bind the open Draft PR to the exact candidate. The required list is nonempty and every listed check passes. The full rollup's docs deploy job is skipped; this does not substitute for the checked required list. No PR write, product push, ready request, review request or merge was performed.

## Affected documents

Every document returned by doc_impact.py has a matching implementation disposition, independently confirmed against the two-file diff and complete suite:

- ADR 0044: unaffected; optional summary input, reviewer placement and legacy calls stay unchanged.
- ADR 0051: unaffected; external-round count and merge-check hold stay unchanged.
- ADR 0062: unaffected; bound-question/approval comparison and merge authority stay unchanged.
- ADR 0071: unaffected; matching delivery record and merge-naming question hold stay unchanged.
- ADR 0072: unaffected; count disclosure, count token scanning and learning evidence references stay unchanged.

## Sufficiency, necessity and limits

The real CLI pair exercises the accepted local journey and protects both failure and recorded-step recovery. Removing the new line filter restores the reported false hold, while broad URL/substring exemptions lose the protected Captain-link check. The constant encodes the exact accepted form, the usage clause describes it, and the tests enforce the accepted boundary. No other product change is retained.

The optional historical test requires five older committed gate snapshots and its original historical baseline; its skip is inherited and unrelated to the changed attribution logic. The implementation's stubbed merge-check evidence proves local behavior only; this validator does not promote it into hosted merge or adoption proof. Hosted CI is freshly observed, but RoboRev remains FO-reported rather than independently rerun. Same-family author/validator lineage and these delivery limits remain explicit. Gate, ready/merge, publication, installation and worktree cleanup belong to FO/Captain after this validation.
