# Independent validation — skipped workflow runs

Candidate: `1ca2625de0706e5494f73e010a394f8e5194b2a1` (PR #797).
Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (origin/main resolved at entry).
Verdict: **PASSED** against all eight acceptance criteria. Five suites ran 637 cases with zero failures and six existing skips; all required guard checks exited 0.

Profile: Pilot. Source code was exported with git archive into /tmp; the assigned worktree was not edited. Shared-state files alone are committed.

## Five-step acceptance

No graphical interface changes. This script exercises the command-line behavior.
Prerequisites: bash, git, tar, Python 3, the two pinned commits available in the named
repository, this task's committed ideation/implementation evidence, and the declared
installed kc-dev-flow-2 0.35.0 package. It makes no network calls.

Run this exact command in a fresh shell (the validation worker ran it unchanged):

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-check-passes-a-skipped-by-design-run/validation/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-check-passes-a-skipped-by-design-run /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-check-passes-a-skipped-by-design-run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
```

The script contains exactly five steps:
1. Export the pinned candidate and base. Expect PASS 1 and both full commit hashes.
2. Replay the six scenarios. Expect PASS 2: intended skip 1 -> 0; five failing cases remain held; word counts match.
3. Exercise required-check and settled-check boundaries. Expect PASS 3.
4. Run the ten behavioral mutants and product-scope assertion. Expect PASS 4.
5. Run the declared package's architecture-decision-record linter against the pinned base. Expect PASS 5 and an evidence directory under /tmp.

All steps must complete with exit 0. The random output directory is printed, so a
later run preserves this run's evidence. This local acceptance does not refresh
GitHub, run the full package suite, check a live merge ask, or grant publication,
merge or worktree-removal authority. Absolute repository/package paths are declared
host prerequisites and need adjustment on another machine.

## Evidence and falsifiers

- `checks/base-replay.log` and `checks/candidate-replay.log`: the actual reduced
  historical #1338 fixture, not a claim of a new live merge. Base exit/word pairs:
  (1,56), (1,87), (1,87), (1,58), (1,58), (1,56). Candidate:
  (0,84), (1,85), (1,85), (1,49), (1,58), (1,56).
- AC-1: the first replay row and sole-skipped-run test pass; removing skipped
  settlement fails assertions.
- AC-2: failed/pending checks and failure/cancelled/neutral/in-progress runs hold;
  allowing failure or every bucket fails assertions.
- AC-3: only-skipped required names hold; removing required_problem or treating
  skipping as pass fails assertions.
- AC-4: empty/no-required results retain the old skipped-run hold; unconditional
  settlement fails the unchanged original test.
- AC-5: unreadable/unparseable/wrong-shape responses exit 2 without an ask record;
  swallowing read/JSON errors fails assertions.
- AC-6: the call-list test pins exactly four gh calls; dropping or duplicating the
  added call fails assertions.
- AC-7: `live-contract.json`, read on 2026-11-06 UTC / 2026-11-07 Asia/Taipei,
  gh 2.103.0; Relay #477 exits 1 with empty stdout and no-required stderr;
  QNow #1338 exits 0 with pass/skipping/pass JSON; QNow #1316 exits 0 with
  fail/skipping/fail JSON. The existing empty-stdout exit-8 test is the falsifier:
  it exits 2 rather than interpreting missing JSON as a usable required list.
- AC-8: only the two approved script files differ and the FO-read diff is empty;
  replay words match. In addition to the implementation comparator, validation
  changed the workflow bytes in a disposable export and ran the actual
  `scope-proof.py`: its workflow-byte assertion rejected the change
  (`checks/AC-8-real-scope-falsifier.log`).

`checks/results.json` records exact executed commands, return codes and suite
case counts. `run_validation.py` is the preserved orchestration used to run them;
its host-specific paths are explicit. Tests run from the exported candidate,
using Python -B. Git-dependent read-only checks use the assigned worktree's
GIT_DIR and the export as GIT_WORK_TREE, without config writes or worktree creation.
The original implementation acceptance.sh requires a Git worktree; validation
uses this five-step export adaptation to honor the dispatch's stronger archive rule.

## Goal sufficiency and minimal necessity

The six-row replay demonstrates the accepted fix and the retained failure
boundaries. The ten mutations show why the required read, name grouping,
conditional skipped settlement and failure handling are needed. The new shape
checks implement the unreadable-response boundary; no file outside the two
approved scripts changes. The affected ADRs 0044, 0051 and 0062 remain accurate:
summary review facts, round-count enforcement, and approval-question binding
are unchanged. `checks/doc-verdicts.json` records those unchanged documents.

## Limits and dispositions

- F1 Deferred risk: GitHub may omit a required check it never created.
  Released user/workflow: FO checking a PR with a path-filtered required workflow.
  Observable harm: no such live omission was observed here; a missing obligation
  could remain invisible. Protected contract: the design explicitly leaves this
  existing blind spot unverified, so it does not establish an AC failure.
  Trigger that would make it material: a supported live PR showing the required
  obligation omitted, no pass, and an otherwise passing gate. No repair authorized.
- The non-empty required list and at-least-one-pass-per-name rule are the accepted
  definition; this validation does not infer which workflow condition was intended.
  Changed no-required stderr wording holds with exit 2; this is accepted fail-closed
  behavior and was tested with other error text.
- The historical replay monkeypatches required_checks to focus on behavior.
  Separate required-reader unit tests execute the gh subprocess stub; the live
  read proves current real CLI response shapes. These are distinct evidence types.
- The five reported local suites are rerun; the entire local package suite is not.
  Hosted PR #797 results were read at the exact head, not rerun by this worker:
  five SUCCESS entries and one intentionally SKIPPED deploy; PR remains Draft.
- Implementation's lack of hosted CI/PR evidence was accurate for its local stage;
  the current read confirms FO subsequently published #797. RoboRev was not run
  by this validator and no clean local-review verdict is inferred.
- Same-file sibling changes are outside this candidate. Integration after any
  rebase/head change requires renewed evidence; this verdict binds only the hash above.
- CI cost per PR remains unmeasured; no CI trigger changes. The approved change
  adds exactly one gh request per delivery check; latency/billing are unmeasured.
- There are no Material, Needs decision or Polish findings. FO retains gate,
  publication, review, delivery and cleanup decisions.

The explicit guard limits were also retained: number_guards skips migration checks because no migrations-path is declared; design_surfaces skips its ideation-only scope check at validation; lint-skills does not claim full Agent Skills conformance or native host behavior. These are appropriate to this script-only Pilot task. ADR lint checked 61 records, exit 0; no number is reserved or added by this candidate. Comment ratio is 0/100 = 0.0% within 5%, and workflow text remains 5939/5939 words. Dispatch validation found all 3 records complete.
