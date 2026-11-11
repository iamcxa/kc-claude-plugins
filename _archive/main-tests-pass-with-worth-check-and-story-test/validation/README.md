# Independent validation evidence for PR #846

Verdict: **PASSED** at `9b9be172c7cb2453ae74a79f10322344bf9ab32f`, with FO-owned delivery obligations still due. The fetched main parent is `571a7bd8a24ce08fac149fbcc91c4561610834c7`; `git merge-tree --write-tree` yields `67b75a024aa3c39ef0e6bec8f2db764cf51ad584`, identical to the candidate tree. This is candidate validation, not a gate, merge, release or installation result.

- `summary.json`, `acceptance-results.json`, `findings.json`: verdict and exact evidence boundary.
- `candidate.diff`, `scope.json`, `provenance.json`, `merge-tree.log`: one-file fixture diff, assertion/byte preservation, tested parents/tree and final freshness/integrity checks.
- `candidate-workflow.json`, `merged-workflow.json`: every unchanged workflow test command and its log/exit; both runs complete 28 commands with exit 0. Each JSON row links its raw log. `run-workflow.py` records how local Python and the pinned native installation are supplied.
- `probes.json`, `probes-run.log`, `probe.py`: original failure, both PATH variants, candidate/merge Story/full suites, direct checks and reverse controls. `swallowed-exception-refusal-assertion.*` records the direct refusal assertion rejecting the bad checker; `freshness-controls.json` and `stale-main-acceptance.log` record stale-main acceptance refusal and identity controls.
- `reading-base.json`, `reading-candidate.json`, `recount.py`, `direct-counts.json`: independent lifecycle measurements and per-input hashes, using the task's declared synthetic scenarios.
- `guards.json` and its named logs: ADR lint, comments, affected docs, design, dispatch-record and fresh number-guard checks. `adr-lint-dispatch-command.log` is the dispatch's exact Claude-package ADR command. `role-triggers.log` records the active entry check.
- `ci.json`, `pr-final.json`: successful hosted workflow and final exact-head PR readback. `spacedock-provenance.json`, `spacedock-release.json`, `package-provenance.json` and the package diffs bind the native sources/binary and distinguish installed package bytes.
- `acceptance.md`, `acceptance.sh`, `acceptance.log`: the five-step Captain script, exact fresh-shell invocation and observed passing output. `acceptance-sandbox.log` retains the first environment-denied attempt; `number-guards.log` likewise retains the initial stale-fetch warning instead of erasing it.
- `limits.md`: judgment of every material implementation caveat, default skips, platform adaptation, installed-package identity, FO ownership and unchanged CI cost scope.
- `cleanup.json`: exact owned scratch directories and their removal status. Raw logs can name removed scratch files; the evidence itself is committed here, never retained only under `/tmp`.

The task entity contains the authoritative validation Stage Report. The workflow's Review-finding disposition produced no new finding in any class. FO must run the committed Captain script and confirm then-current main before the merge ask; advancing main invalidates this merge-result snapshot.
