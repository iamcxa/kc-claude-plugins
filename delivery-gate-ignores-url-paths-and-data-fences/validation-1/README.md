# Independent validation: PR #818

Candidate: `6f2fe8f33de15cf4e9283bf9dfed185a5691ed57`
Base: `e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e` (origin/main and live main at review).
Profile: pilot. Product source read and executed from fresh git archives in `/tmp/pr818-validation-pP1gbX`; no product edits or worktree creation/removal.

## Acceptance

Run these four numbered steps together with this exact command (Python 3, Git, tar, and the existing assigned checkout are prerequisites):

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-gate-ignores-url-paths-and-data-fences/validation-1/acceptance.sh
```

The script documents each step and expected observation. It exports the named candidate; runs the five recorded inputs through the real `question` CLI; exercises the retained holds and all seven reverse mutations through the candidate's own fixture tests; and checks the two-file scope and identical workflow bytes. Observed output is in `acceptance-published-path.log`, exit 0. There is no graphical surface change. This small check does not cover hosted CI, review completeness, real gate submission, approval, merge, publication, or other machines' top-level directories.

## Evidence by acceptance criterion

- AC-1: `fixtures-candidate.log`, `question-replay.json`, and `mutation-observations.json`: site paths and the elided path pass; a generated absent root and Asked /llms.txt pass. Removing the existing-root predicate returns S4. The exported base is byte-identical to installed 0.36.0 (`identity.json`).
- AC-2: the braced namespace passes in both message and validation report through the real CLI. Removing the preceding-brace exclusion returns S5; unbraced HTTP/HTTPS links remain held, and removing all links breaks that control.
- AC-3: both original named YAML card strings pass the real CLI; the design card includes the accepted ADR filename and the chief-engineer card uses the full recorded outcome string. Replacing shell-only card scanning with all-fence scanning returns S5.
- AC-4: sh, sh run, bash, zsh, shell, console and untagged card fences hold; YAML message/report fences still hold; existing files pass and missing files under the real temporary directory hold in both message and Asked. Four weakening mutations break their corresponding controls. `mutations.log` and its JSON retain 43 observed calls, including 20 mutant calls across seven distinct source mutations.
- AC-5: `question-replay.log/json` compare all five exact inputs at both revisions: candidate exit 0 / gate text complete, base exit 1 / Captain steps record fails. Real sh-card and missing-file question controls hold. `base-regression.log` additionally runs the new CLI regression tests against the base script: 3 tests produce 4 expected assertion failures, proving the tests can reject the original implementation.
- AC-6: `candidate.diff` names only delivery_gate.py and test_delivery_gate.py; workflow content is byte-identical and 5931 words at each revision. Full discovery used Python 3.15.0 resolved from the assigned-worktree launch; the focused checks and fresh-shell acceptance used Python 3.11.14. Full discovery completed with 1032 tests, 7 opt-in skips, exit 0. Full discovery and lint results are recorded in `checks-reconciled.json` and their logs. The base negative control also falsifies regression-suite acceptance of the old behavior.

## Required checks and commands

`run_checks.py` records each command, direct subprocess exit and log; `checks-reconciled.json` incorporates the explained reruns. `run_extra_checks.py` is the existing implementation evidence runner, reused against the fresh export.

Commands already executed from the exported candidate (exact argv also retained in the JSON evidence):

- `cd /tmp/pr818-validation-pP1gbX/candidate`
- `env TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'`
- `python3 kc-dev-flow-2/scripts/lint-skills.py`
- `env GIT_DIR=/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/spacedock-ensign-delivery-gate-ignores-url-paths-and-data-fences GIT_WORK_TREE=/tmp/pr818-validation-pP1gbX/candidate python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/adr_lint.py docs/adr --since e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e`


ADR lint exits 0 (63 records, no new/modified/reserved ADR); the additional --require 0044 0051 0062 run also exits 0 (adr-lint-required.log). Three affected ADRs (0044 separate-summary compatibility, 0051 round-count rule, 0062 bound-question authority) retain correct unchanged contracts; each has the implementation's explicit unaffected disposition and the independent doc-impact result agrees.
Comment ratio exits 0 (127 added code lines, no added comment lines, 5% maximum). Design check and three dispatch records exit 0. Number guards exit 0 after an authorized refresh, with no stale-fetch warning; migrations are inapplicable.
Five extension suites and the real model-free dispatch/recovery runs exit 0. The release-acceptance suite has 122 tests with four optional Node/journey dependency skips; those runtime paths are not proven here. Spacedock is local 0.27.2 with the declared 0.27.3 plugin/mod root; this is not hosted execution or worker-model evidence.

The first version-parity run exited 128 because an archive has no .git. The same script with read-only GIT_DIR/GIT_WORK_TREE exits 0 (`version-parity-with-metadata.log`). No Git configuration was changed. The initial number-guard sandbox fetch warning was resolved by rerunning its exact narrow command with authorized access; both observations are preserved. CI configuration is unchanged; CI cost per PR was not measured.

## Review and merge readiness

The complete GitHub PR response and paginated review/comment responses were read at the named head. There are three conversation comments (request, completed status, clean review receipt), zero review submissions and zero inline review comments. The Codex status binds the full candidate SHA and reports completed with no findings; the receipt names 6f2fe8f33d. No published review finding stands unaddressed. Sources:
- https://github.com/iamcxa/kc-claude-plugins/pull/818#issuecomment-6734589760
- https://github.com/iamcxa/kc-claude-plugins/pull/818#issuecomment-6734657705

At the final 2026-11-09 07:54:44 UTC snapshot, the candidate is OPEN/DRAFT and GitHub reports BLOCKED; the unit-test check has since passed on rerun, while version parity still fails. Initially both checks failed at installation with `curl: (22) ... 504` while fetching the pinned Spacedock 0.27.2 release asset:
- https://github.com/iamcxa/kc-claude-plugins/actions/runs/42579057011/job/129033231764 (unit tests)
- https://github.com/iamcxa/kc-claude-plugins/actions/runs/42579057014/job/129033231551 (version parity)

The initial logs establish external download failures, not demonstrated code failures. The final snapshot supersedes the earlier unit-test failure; version-parity attempt 2 also failed on the same 504 download, confirmed from its current failed log (version-ci-rerun-failure.log). Current job: https://github.com/iamcxa/kc-claude-plugins/actions/runs/42579057014/job/129037914107 . It remains a failed check and does not count as a green run. FO owns rerun/reconciliation, exact-head local RoboRev evidence, ready state, the Captain gate and any later merge. This validation makes no local RoboRev-clean claim. No CI rerun, PR mutation, comment or review request was issued. Raw remote snapshots/downloaded logs stay under `/tmp/pr818-validation-pP1gbX`, outside task state.

## Limits and disposition

No new Material, Deferred risk, Polish or Needs decision product finding was established.
The accepted design deliberately misses absent/misspelled top-level roots and non-shell command fences inside named cards; changing those policies would reverse the accepted ruling. Python-card acceptance is exercised in `question-replay.json`. Detection of site-path tokens depends on the runner's real roots, so a machine actually containing /web would still treat /web/... as a file path by design.
FO-named card links remain checked: the PR attribution URL still holds in the independent replay. This is the existing separately filed delivery-gate-pr-body-attribution-link task, not new scope.
PR #794 remains Captain-held and is neither included nor required. The overlaps with PR #817 and the other batch tasks do not authorize combining their candidates.

Goal sufficiency: the five original inputs now reach the real question CLI without scratch rewriting, while the named true positives remain enforced.
Minimal necessity: each of the three production narrowings has an observed base/mutation failure; the added tests prove those transitions and no unrelated file or workflow text changed.

