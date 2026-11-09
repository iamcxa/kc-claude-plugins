# Independent validation of the merge in PR #818

Candidate: `b8362fb901cd27bd367be1cd5b826f21fefad70e`.
Base/second parent: `8c8313823f353f631e2b7cca4559dd3e643f30a5`.
Previously validated first parent: `6f2fe8f33de15cf4e9283bf9dfed185a5691ed57`.
Observed on 2026-11-09. This is Pilot validation of the bounded gate-input change, not delivery authority.

## Captain acceptance

Run this exact command in a fresh shell after the state report is committed:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-gate-ignores-url-paths-and-data-fences/validation-2/acceptance.sh
```

The script contains five steps with exact commands and expected observations: export the pinned candidate; replay the five original inputs as real merge questions with matching delivery records; run seven focused controls including the seven reverse source mutations; run the eight missing/mismatching delivery-record tests; assert the two-file boundary and unchanged workflow. Expected final output: `scope and workflow unchanged`, then `PASS`.
Prerequisites are Python 3, Git, tar, and the existing assigned checkout retaining both pinned commits. No graphical surface changes. It does not prove hosted CI, review completeness, actual gate submission/reference binding, approval, merge, publication, or behavior on other machines' top-level directories.

The implementation's current-head acceptance script was also run unchanged (`acceptance-original.log`). `acceptance.log` records the five-step script in a fresh Bash shell before publication; `acceptance-published-path.log` records the identical bytes from the final state path.

## Accepted criteria and falsifiers

- AC-1: `fixtures-candidate.log`, `combined-observations.json` and `mutation-observations.json` show site paths, the elided package path and a generated absent top-level path pass. Removing the existing-root predicate restores S4. Asked-line paths are covered by the original focused test.
- AC-2: the namespace URI in both message and validation report passes. Removing the preceding-brace exclusion restores S5; ordinary HTTP/HTTPS links still hold, and disabling links breaks that control.
- AC-3: both named YAML cards pass. Scanning every card fence restores S5. `acceptance.sh` preserves the recorded full chief-engineer outcome string.
- AC-4: shell/untagged card fences and YAML message/report fences hold; missing files under the real temporary root hold in both message and Asked, while existing files pass. Suppressing message data fences, paths, links or card fences each defeats a required hold. All seven reverse mutations were rerun with Python -B after removing export-only bytecode caches.
- AC-5: `combined_probe.py` uses the real question CLI, with a merge grant and a matching record, for all five original inputs. Each passes and prints its --reference path. The same five inputs fail against the exported main parent in `base-observations.json`. Shell-card and missing-file controls hold through question. This is observed necessity of each narrowing, not only inspection.
- AC-6: `scope.json` and `candidate.diff` show only delivery_gate.py and test_delivery_gate.py differ from main. Workflow bytes/count are identical. An injected unexpected path fails the file-boundary assertion. Regression/lint results and direct exits are in `checks.json`, `extra-checks.json` and `verification.json`.

## Merge preservation and the adjacent check

`source-preservation.json` compares exact AST-extracted source text, not only normalized syntax. absolute_paths, fenced_steps, links and inspect_steps equal the first parent; matching_delivery_record and question equal the second parent. `merge.diff` shows the matching-record fixture was preserved before the real CLI branch in QuestionTests.ask.

The eight DeliveryCheckBeforeQuestionTests pass. The combined real-CLI probe adds the original URL/namespace inputs and observes missing/matching/newest-mismatched records returning 1/0/1; a missing record never prints gate text complete. This preserves #817's approved hold. The test fixture fabricates records to isolate the check; it does not claim to run FO's real hosted delivery check.

## Checks, configuration and scope

`run_checks.py` records exact commands and direct subprocess exits; `run_extra_checks.py` reuses the implementation runner with read-only GIT_DIR/GIT_WORK_TREE only for version parity because an archive has no .git. Package helpers use the loaded Codex 0.36.0 package root; the dispatch's explicitly requested Claude-cache adr_lint.py command was additionally run and its exact command/exit saved in `adr-dispatch-command.json`.

ADR lint and --require 0044 0051 0062 0071 pass. All four affected documents have the implementation's unaffected dispositions, independently checked: 0044 optional summary and legacy compatibility, 0051 review-round enforcement, 0062 quoted-question authority, and 0071 matching delivery-record hold/reference output. Their bytes and governing functions outside the approved narrowing are unchanged from main.

The first number-guard run could not fetch state refs in the sandbox. The same command with authorized network access passes without that warning (`number-guards-refreshed.log`); the initial warning remains recorded.
The first full discovery launch omitted SPACEDOCK_BIN. A one-test reproduction fails because --spacedock receives None (`missing-binary-probe.log`), while the identical test with the declared binary passes (`configured-binary-probe.log`). The corrected full command and direct exit are retained in verification.json; this is already-run evidence, separate from the five-step Captain script.

The optional corpus/runtime skips are not claimed as coverage. Five extension suites and native model-free Spacedock dispatch/recovery pass; release-acceptance has four optional dependency skips. Local Spacedock binary 0.27.2 and plugin/mod root 0.27.3 are the implementation's declared prerequisites, not worker-model execution proof. CI configuration is unchanged and cost per PR was not measured.

## Review and delivery readiness

All five PR conversation comments, zero inline comments, and the one submitted review were read. Pagination was independently checked. Codex's completion marker binds the full candidate head and reports no findings; its current receipt is:
https://github.com/iamcxa/kc-claude-plugins/pull/818#issuecomment-6738566177 .
The submitted Copilot review is a quota refusal on the prior head:
https://github.com/iamcxa/kc-claude-plugins/pull/818#pullrequestreview-5823039113 .
It is not a review round or a clean result. ADR 0013 requires reporting it and no retry until the Captain confirms quota is back. No published review finding stands unaddressed. The old security marker and old receipt were not counted as current-head reviews.

The PR is OPEN, ready, CLEAN/MERGEABLE at the candidate head. Both required check names pass; all four workflow runs at this head are successful. The docs deploy job is skipped inside a successful workflow, not a failing or absent required check. Primary hosted evidence is linked in `review-summary.json`. Raw downloads remain only under /tmp/validate-pr818-merge-15Eaje, never in the state folder.

Product/hosted checks support proceeding to FO's delivery gate, not immediate merge. Current-head local RoboRev evidence was not supplied in the artifacts read: the PR body and prior briefing still name roborev:1625 on 6f2fe8f33. FO owns that evidence, the new-head Captain-step record, delivery check, --reference briefing, Captain decision and merge. The PR body's explicitly old-head validation paragraph is not used as this head's proof.

## Limits and finding disposition

No new Material, Deferred risk, Polish or Needs decision product finding was established.
The accepted policy still ignores missing/nonexistent top-level roots and non-shell named-card fences. Python, Node and YAML card behavior is reproduced in `limits.log`; message/report data fences still hold. If a runner actually has /web, /web/... remains a filesystem candidate by design. Ordinary links in FO-named cards still hold, including the PR attribution URL; that already belongs to delivery-gate-pr-body-attribution-link, not this task.
The merged record helper still checks truncated clauses and only merge-naming questions, as ADR 0071 states and its eight tests cover. It does not prove the supplied observations are true or that FO later binds the reference.

Goal sufficiency: five recorded false positives now reach the real merge-question CLI without scratch rewrites while required true positives and the matching-record hold remain enforced.
Minimal necessity: the main-parent controls fail all five inputs and seven reverse mutations expose each narrowing or retained boundary; no unrelated production surface or workflow bytes changed.

