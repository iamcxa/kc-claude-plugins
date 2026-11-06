# Independent validation — PR #794, second validation

Verdict: PASSED for b82f20de6c8e5b868695d03aa4bbcb97e77dd877 against the accepted Pilot scope. Base: b804d81d3abc94c9c321326dc75e7cac927c5252. Date: 2026-11-06.

## Identity and execution boundary

Product checkout: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges. Product programs ran from a git archive export at /tmp/merge-guard-validation-b82f20de/export. source-sha256.json verifies every changed file against the candidate blob. No product bytes, shared Git configuration, repository worktree metadata, operator hook settings or rules were changed by this validation.

GitHub readback at the start and end confirmed PR #794 OPEN and non-draft at the exact candidate. PR #793 remained OPEN/non-draft at 5b3e290a7eaceb0fe70f489d25d622314598b9f0; its prescribed first-merge ordering and later-head integration remain FO-owned. origin/main moved concurrently from the assigned base to 6dab84e2acab5e8e55c9a8d3bc07ce223c7f4ed2; candidate HEAD stayed unchanged. The number check used that updated trunk and reported merge-base b804d81d3abc; all direct comparisons and the ADR acceptance check remain pinned to the assigned base.

The validation skill resolves its package to /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0; package audits used that root. The dispatch's explicit /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py command was also run against the same base with --require 0063 and exited 0.

## Acceptance evidence and falsifiers

- AC-1: `python3 -B kc-dev-flow-2/scripts/test_merge_guard.py` from the export: 45 tests, all pass. Full and seven-character heads, newest-only task/archive/_merges records, identity, flag/URL/origin forms, non-merges and host decisions are exercised. Restoring oldest-record selection, removing _merges discovery or emitting Codex ask fails its designated assertion.
- AC-2: the same suite creates a separate temporary Git repository and linked spacedock-state/x worktree: an uncommitted record carries, changing the fixture branch stops. Replacing disk reads with git show HEAD fails that test. These fixtures do not modify the product repository's worktree metadata.
- AC-3: current-source native tests cover missing script, injected exception and unreadable record on both hosts. Missing/exception hooks exit 2 via the documented wrapper; unreadable records ask/deny. Every one has zero fake-gh executions. Removing `|| exit 2` gives a Claude hook exit 1 and one fake execution, demonstrating that the wrapper is necessary.
- AC-4: Claude 2.1.318 auto headless stops an uncarried global-repository-flag command with permission_denials and zero fake executions; the carried command executes once. Interactive auto shows the global-repository command, the newest-record failure reason and “Do you want to proceed?”. FO message 8b42b6b3-2223-4d88-8421-d347e6000219 authorized trust of this throwaway folder and Esc cancellation. Down, cursor readback and Enter selected folder trust; Esc canceled the merge request, the UI showed Interrupted, and ran.log remained empty. The session exited 0 before FO's subsequent no-more-keys message; no keys were sent afterward. The no-wrapper native counterexample removes this stop.
- AC-5: Codex 0.162.1 stops the uncarried command with rules ignored and with the operator rules loaded. The latter hook payload is plain `gh pr merge`, login=false, with fake gh on PATH; both fake logs stay empty. A carried command executes once. An additional native mutation changing deny to ask executes the fake command once, independently reproducing why Codex must deny.
- AC-6: current package replay over the saved 84 PRs gives 54 pass / 30 stop; synthetic ancillary-question recount gives 74 pass / 10 stop. No differences from ideation. #672 is refused for missing head 6c972e7. Removing record's question-head check gives 75 pass / 9 stop and #672 passes. Recount approvals are synthetic, not proof of historical grants.
- AC-7: current adoption instructions contain both registration bodies, `|| exit 2`, Codex deny-only, Paseo user-setting loading, record route and stop-count assumptions. The stale no-equivalent-hook sentence is absent. `lint-skills.py` passes with WORKFLOW_WORD_BUDGET and workflow text unchanged at 5939 words. Removing the documented Codex wrapper fails the document counterexample; AC-3 supplies its behavioral necessity.
- AC-8: ADR 0063 retains the Captain's exact revision/approval words and full D1–D4 approval question. Seven approved files changed; no workflow.md, _mods, version or shipped-hook registration changes. delivery_gate.py changes only ASK and ASK_UNQUOTED's closing sentence. `test_delivery_gate.py` runs 157 tests: 156 pass, one pre-existing skip for an unconfigured committed gate-presentation corpus. Reverting the record reminder makes the existing FoWriteRuleTests pass-line assertion fail.
- AC-9: the guard suite verifies highest-plus-one numbering, URL/#number input, valid full head and nonempty answer, per-problem errors and no writes on refusal. Removing the digit boundary fails #6720 rejection. A copy of the adopted workflow with a disposable task gives byte-identical `spacedock status` before/after the _merges folder, both exits 0 (status.json).
- AC-10: captain-steps/1.md records 「看得到，也答了」, FO's no-pending-request observation and one fake execution after the Captain's Yes. Removing that answer fails an evidence-integrity control. This is the criterion's existing Captain-only phone observation, not a new device run or a claim that this package head was exercised on the phone.

## Both repair classes

`merge-guard-repair-mutations.py`: 22 assertion-based falsifiers rejected (16 tests against the first candidate, six focused mutations), covering global/attached/interleaved repository flags, literal wrappers, executable paths, quoted spelling, REST/GraphQL, shell context and inherited GH_REPO/GH_HOST. `merge-guard-deferred-mutations.py`: 17 assertion-based falsifiers rejected, covering bare/equals/wrapped --auto, encoded asynchronous REST, GraphQL auto/enqueue/opaque bodies, unknown flags, safe subject text and no live query. The original six record/discovery/decision mutations also fail. All used fresh modules and python3 -B; candidate bytes were untouched.

The 20-form deferred matrix was rerun. In native hosts, matching-record --auto and encoded REST merge-async each stop, as do direct REST and opaque GraphQL commands. These runs complement the static matrix and unit-level host output checks. native-results.json verifies 21 headless cases including the two intentionally weakened negative controls; interactive-observation.json is the additional interactive case.

## Limits judged

- The hook deliberately makes no live merge-queue lookup. FO's four-repository no-main-queue observation remains attributed to FO, not independently rerun. Plain gh pr merge can enqueue or enable auto-merge when the target branch requires a queue; adoption.md and ADR 0063 explicitly require revisiting the guard before relying on it after enabling a queue. This is the accepted scope premise, not a repaired guarantee. [GitHub CLI manual](https://cli.github.com/manual/gh_pr_merge) independently confirms that behavior.
- Explicit deferred routes are stopped even with a matching record. --disable-auto is cancellation; subject/body text containing --auto remains allowed. Unknown flags/aliases, GraphQL reads and opaque commands may be stopped conservatively. [GitHub REST documentation](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#merge-a-pull-request-asynchronously) confirms the asynchronous route; no live merge endpoint was called.
- Script bodies, generated executable names, direct curl/SDK calls and non-PR branch writes remain outside this gh command-text guard. This protects ordinary mistaken requests, not a hostile actor with the same filesystem access.
- A record does not authenticate the Captain or interpret approval intent; task records and chat records retain their different origins. Paseo agents can answer another agent's permission request. These were explicitly accepted design limits, unchanged by the repairs.
- Registration is manual and each unregistered machine remains unguarded. Persistent hook registration and hook-trust installation on the Captain's machines were not exercised. Native tests used temporary settings with normal existing login, as authorized; Codex used ignore-user-config/ephemeral, with rules read only in the rules case.
- Historical replay stop counts depend on the sample and synthetic ancillary questions. Foreign repository records outside this clone are unavailable; head prefixes and conservative text-mention stops are retained as designed. No new phone delivery observation is claimed.
- Repair-2's skipped native proof was correctly labeled as belonging to the previous head. This validation supplies current-head native evidence instead of treating that prior proof as current. No new review agents were started.

## Other required checks

ADR lint: 62 records, zero legacy, exit 0. Number guard, design-surfaces check, dispatch-record check (seven records), document impact and diff whitespace check exit 0. The implementation dispatch and two follow-up records trace to accepted criteria and the recorded FO repair rulings.

All three added code-comment lines were read: purpose docstrings and the ADR enforcement pointer, with no narrative or review provenance. comment_ratio.py reports 581 added code lines / 3 comments = 0.5%, below maximum 5%.

Document dispositions: ADR 0044 unaffected (summary/legacy-call behavior unchanged); ADR 0051 unaffected (round-count rule unchanged); ADR 0062 unaffected (quoted-question grant unchanged); ADR 0063 updated (user-hook ruling and offline/queue boundary); kc-dev-flow-2/README.md unaffected (no automatic installation, existing CI test-discovery direction remains accurate). These match the implementation report.

Reading cost independently reproduced: ASK 40→57 words; ASK_UNQUOTED 39→56; adoption 2347→2760; workflow 5939→5939. CI cost per PR was not measured. The existing package-path triggers are unchanged; only a guard-test step was added. Final GitHub metadata reports applicable checks successful and deployment skipped, a provider readback rather than a local CI rerun. RoboRev and external review remain FO-owned; this worker did not run them.

## Minimal acceptance script

Run exactly in a fresh shell:

```sh
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-guard-stops-unasked-merges/validation-2/acceptance.sh
```

The script declares the required local clone and installed package paths. Five steps: export the exact clean candidate; run 45 guard tests; observe stop → record → pass → moved-head stop and deferred-route stops without executing gh; run delivery tests/lint; check the reserved ADR against the pinned base. Expected final line: `Acceptance passed; no hook installed and no merge executed.` The script was run as written in a fresh bash shell; acceptance.log is the observed output. It completes in under five minutes and exits 0.

The command interface is the product surface. This short script does not repeat the native-host, interactive or phone observations, install persistent hooks, merge a PR or prove release/adoption.

## Verdict, necessity and cleanup

No new Material, Deferred risk, Polish or Needs decision finding was established beyond the accepted limitations above. The candidate satisfies the mistaken-merge journey at its stated Pilot depth: stop, identify a missing record, save an approved PR/head and retry. The base has no guard; removing newest/head/discovery checks breaks their probes; the earlier parser allows the global-flag forms; removing deferred checks allows the reproduced --auto/encoded route. The script, tests, CI step, record reminder, registration guide and ADR each serve an accepted behavior or lifecycle obligation.

All owned native processes exited. Interactive session 32659 exited 0 before FO's stop-message 125a51d2-0219-4473-bb0d-6fdfab894d7e, and received no keys afterward. Its fake log is empty. The interactive CLI wrote its own trust/session metadata for the temporary fixture under FO authorization; no operator hook settings or rules were edited. Exports/fixtures remain under /tmp for inspection.

The initial sandbox Claude attempt failed before inference with “Not logged in”; the authorized outside-sandbox runner passed. Early evidence-helper path/test-name mistakes were corrected before producing the cited results and are not candidate failures. Product worktree is clean at the exact SHA. The state helper owns the report's task-scoped commit/synchronization; no product push, PR comment, review request, ready action or merge was performed. FO owns the sibling-first integration, gate, merge and post-release registration.

