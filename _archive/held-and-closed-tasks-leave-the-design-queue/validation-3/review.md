# Independent validation, cycle 3

Artifact: PR #856, candidate `5859c3ccd25a86c79df3b36cafdda9762bd8142e`, main parent `46e9d0ed4bb86889022457adcdf656965dc97e73`. Profile: Pilot. Captain amendments 1–5 apply. This validator neither implemented this candidate nor performed earlier validations. Verdict: PASSED recommendation for this exact artifact, with the limits below. This is not gate or delivery approval.

## Identity, scope and necessity

`source-identity.json`, `parents.txt` and `source-diff.patch` independently establish the two merge parents, exactly three changed paths, and the original ordered added/removed lines: 210 additions and four deletions. The four dispatch/scratch files owned by PR #854 equal main byte-for-byte. `main-regressions.json` joins the five watcher cases added by PRs #858, #861 and #854 to the passing `watcher.xml`: absent-worktree facts, extension selection, scratch reminders and post-archive behavior remain covered.

`pr-856.json` confirms the public PR is OPEN, targets main and names this candidate. Its observed hosted checks succeeded except the non-executed docs deployment; this worker does not assert required-check completeness or delivery approval. The PR is already non-draft; no PR mutation was performed. `public-source-proof.json` confirms the entry state revision is in the public remote, and no private repository was read. Only this task's report/evidence is staged.

The changed fact line addresses held tasks being presented as waiting. The quote diagnostic addresses missing recorded reopen/close wording. Removing the change fails the held tests (`mutation-candidate-removed.log`); disabling each behavior separately also fails (`mutation-*.log`). The decision record is specifically authorized by amendment 1. No retained surface is unrelated to the accepted goal. Live Held edits remain an explicit First Officer step after merge, so package validation does not claim the whole operational outcome has already landed.

## Acceptance and falsifiers

- AC-1, existing held selection: the frozen public state returns exactly the original ten ideation holds; deleting one returned row fails the set comparison (`recheck-results.json`). Current state has an additional ideation hold; this does not rewrite the frozen baseline criterion.
- AC-2, scheduler exclusion: no original held task is ready or dispatchable; injecting one held row makes the oracle reject (`recheck-results.json`, `ac2-next.log`).
- AC-3, original startup gap: the unchanged legacy script exits 0 and names none of the original ten; inserting one held name is rejected in a fresh process (`legacy-tasks-network.log`, `AC-3-output.log`, `AC-3-mutated-output.log`).
- AC-4, native held dispatch: Spacedock 0.27.2 builds the held dispatch, exit 0, in the independent fixture (`ac4-outside-worktrees.log`). The first attempt failed because its path contained `.worktrees`; `native-recheck-resolution.json` retains that setup failure and equal candidate bytes. A refusal exit rejects the evidence oracle; this does not claim a mutation of the upstream executable.
- AC-5, no unforced close: all three native commands exit 1. Merge and status cite `not-applicable`; archive refuses the unrun merge hook (`ac5-*.log`). An observed success exit is the rejecting oracle counterexample. No forced archive is attempted.
- AC-6, reopening: the historical public record has a successor after a hold; removing that successor rejects (`recheck-results.json`). This reads an actual history, rather than claiming a fresh gate operation was performed.
- AC-7, quoted text: all seven proposed quotes occur verbatim in their hold reasons; adding one character to each quote rejects (`recheck-results.json`). Verbatim comparison does not decide the semantic labels or make new Captain rulings.
- NP-1, held output: the actual public workflow command exits 0 and its single fact line names all fifteen current holds exactly once (`candidate-live-network.log`, `NP-1-current-output.log`). Missing/duplicate names and the removed implementation reject; empty input prints nothing (`output-falsifiers.json`, `recheck-results.json`, `captain-results-rerun/held-tests.xml`).
- NP-2, quote diagnostics and failure exit: missing/unverified/fenced/duplicate/stale quotes and query errors are exercised. Deleting quote comparison, newest-hold selection, empty suppression, task wiring or exit 2 each fails (`mutation-*.log`). Candidate bytes are restored after every mutation; the product worktree was never mutated for a test.
- NP-3, amendment 4: the actual word-counter commands pass for one, current fifteen and fabricated hundred tasks at 17/21, 33/35 and 120/120 (`words/measurements.json`). The independent acceptance counter uses 125 fabricated tasks across all five stages at 145/145 (`captain-results-rerun/measurements.json`). One-word-over-bound cases reject in both sets. Terminal `done` rows are formatter input only. The replacement criterion matches the Captain's one-word-per-task plus twenty wording; amendments 2 and 4 supersede the old numbers, not the listing behavior.
- NP-4, state projection: fourteen frozen task copies have valid Held text with unchanged frontmatter; the fresh acceptance copies fifteen current holds with the same preservation check (`recheck-results.json`, `captain-results-rerun/measurements.json`). A frontmatter mutation rejects. Live Held sections are deliberately not edited; the live count of valid sections is zero, recorded by the replay.
- NP-5, plain upstream status: outside this package's accepted implementation; unchanged, not claimed passed. The approved design leaves closed tasks at their existing stage and uses readiness/held output to distinguish them.

## Checks rerun

All commands below ran with Python 3.11.14, PyYAML 6.0.1 and pytest 8.4.2; exact argument vectors and paths are saved in the cited JSON records. The required installed package is retained alongside the currently loaded 0.40.0 skill's package checks.

- `python3 -B validation-2/recheck.py --scratch … --evidence … --state …` — native criteria and candidate mutation checks; `resolved-recheck-results.json` joins the independent path correction without overwriting the original failure.
- `python3 -B implementation/amendment-4/count-held-words.py --candidate … --state … --scratch … --output … --spacedock … --case one|current|larger` — `word-commands.json`.
- `python3 -B validation-3/output-falsifiers.py --output … --scratch … --task …` — `output-falsifiers.json` contains each full command and expected exit.
- `python3 -B -m pytest -q kc-dev-flow-2/scripts/test_pr_watch.py --junitxml=…` — 163 passed, zero skipped (`watcher.xml`).
- `python3 -B implementation/merge-main-resolved/run-full-suite.py --candidate … --scratch … --output …` — complete CI Python command list plus the additional scratch test file; original and environment-corrected results are retained separately.
- `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since 46e9d0ed4bb86889022457adcdf656965dc97e73 --require 0081` — exit 0 (`dispatch-installed-adr-lint.log`).
- `python3 <loaded-package>/scripts/number_guards.py check --workflow-dir … --task …` — exit 0 after public-ref refresh (`number-guards.log`).
- `python3 <loaded-package>/scripts/{adr_lint,comment_ratio,doc_impact,design_surfaces,dispatch_records}.py …` — every exact command exits 0 (`package-checks.json`). Comment ratio is 1/144 = 0.7%, maximum 5%; the sole added comment cites the governing decision. `doc-impact.log` lists only ADR 0081, updated with the accepted quote. No retained diagram changes.

## Minimal Captain acceptance

Run this one command in a fresh shell. It derives its state-checkout location from the script, exports the exact candidate using retained Git objects, exports the public state pinned in `context.json`, runs eleven held-behavior tests and installed ADR lint, then measures one/current/larger cases and rejects over-bound output. It needs no product worktree, removed scratch, network, private repository or credential. The dependencies and machine-specific installed Python/Spacedock paths are declared in the script; there is no changed graphical surface.

```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation-3/captain-acceptance.sh
```

Expected observations: the full candidate SHA; `NATIVE INPUTS 15`; eleven tests pass; ADR lint exits 0; ONE 17/21, CURRENT 33/35 and LARGER 145/145 pass with three rejected counterexamples; final `PASS: exact candidate held behavior, ADR and amendment-4 counts`. `captain-acceptance-exact.log` records the exact command above, run successfully from /tmp after the primary evidence commit, with no retention overrides. The earlier retained run is also preserved in `captain-acceptance-rerun.log`. Ordinary execution cleans its own temporary directory. This small script does not run the complete package suite, edit live Held tasks, decide labels, validate all hosted required checks or approve delivery.

## Limits and dispositions

No new Material, Needs decision or Polish finding is established by the accepted package behavior. The known origin-less fixture limitation is reproduced on both main and candidate (exit 2, same scratch-close-out diagnostic); the real public workflow entrance exits 0 (`originless-comparison.json`). It remains a Deferred risk for this task unless a supported origin-configured workflow reproduces attributable harm to the held-task criterion. Identical baseline behavior is used only to scope attribution, not to label the failing command a pass.

The native-command exit falsifiers are evidence-oracle checks, not upstream binary mutations. Synthetic Held projections and large formatter inputs prove their stated mechanical properties only. Optional external corpus/dependency skips are not passes. Hosted CI, local review, gate approval, post-merge Held edits, release and adoption remain First Officer/Captain responsibilities. No CI configuration changed, and cost per PR was not measured.

Initial failures are retained: missing PyYAML in the default interpreter; native entity paths containing `.worktrees`; plain temporary fixtures inheriting an enclosing Git checkout; and the first acceptance export lacking a populated index/full source. All corrections change execution setup only, retaining candidate bytes and assertions. Plain-copy fixtures must be outside any repository: a Git discovery ceiling alone does not alter the Python ancestor scan in `dispatch_records.py`.

## Full package coverage

`full-suite-summary.json` and `full-suite-resolved.json` account for all 30 declared commands, including all 29 test files: 1,471 unittest cases comprise 1,461 passes and ten optional skips; both custom native integration commands pass. The ten skips are four design-history cases, four release-acceptance dependency cases, one delivery-history case and one laws corpus case. No private corpus was acquired.

The initial runner completed 26 commands with six failing modules in the unsuitable nested fixture environment. Each affected assertion has passing unchanged-source rerun evidence; the dispatch-record module also has its native case rerun separately so that optional skip is filled. The already-covered duplicate native suffix of the original runner was terminated, exit 143, rather than waited out; the four suffix commands are covered by independent successful runs. This is complete, non-duplicated command/case coverage, not a claim that one unmodified full-suite invocation exited 0. The coverage manifest retains both original exits and replacement evidence.

## Committed evidence and cleanup

Primary evidence was committed and pushed as `4321a2630eeac3457666b4c2c459ab44a5f0049c` before cleanup. `cleanup.json` verifies the following exact owned paths absent:

- `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-held-and-closed-tasks-leave-the-design-queue/.validation3-scratch`
- `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/validation3-held-20261113-1306`
- `/tmp/validation3-fixtures-20261113-1259`
- `/tmp/spacedock-dispatch/spacedock-ensign-adoption-asks-which-extensions-ideation.md`
- `/tmp/captain-acceptance-v3.jZUdLP`

The product worktree is clean at the candidate; only this task report/evidence remains for the final state commit. No held-task body or frontmatter changed.
