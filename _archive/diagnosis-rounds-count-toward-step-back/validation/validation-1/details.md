# Independent validation of PR #771

## Verdict and identity

**REJECTED** at candidate **97cf87965ec052a1c9f2d40a1a1d0ca83e8d2244**, base **713d4e6ed6381e65fa6d8305e08b282ceb56a8fb** (local origin/main and the live PR base agree). The nine explicitly enumerated acceptance fixtures pass, but the accepted Design includes follow-up message records and the candidate excludes them. That scope conflict requires disposition before repair or delivery.

Code was inspected and executed in the detached temporary worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back/.validation-771`. All seven changed-file hashes match the implementation evidence; see candidate.json. No product bytes or candidate revision were changed.

Live GitHub read: https://github.com/iamcxa/kc-claude-plugins/pull/771 is open, Draft, and names this exact head and main base. All four returned hosted runs succeeded, including package tests run 41626726024; pr.json and ci.json retain the provider responses. These reads are not delivery approval.

## Findings under Review-finding disposition

- F1 Needs decision: Follow-up message records are excluded despite the approved round definition.
  - Released user and normal workflow: an adopter First Officer sends further diagnosis instructions to an existing implementation or validation worker, recording them as the already-supported `stage-N-message-M.md` form.
  - Observable harm: three records with the same symptom (one plain implementation record plus two message continuations) count as one. Folder and strict named-record checks return 0 without a reminder, and the committed-state role checker returns 0 without an owed call.
  - Affected value: `value-ac[AC-1]` requires the second same-stage dispatch on one symptom to remind; the approved Design's PRFAQ defines the round as including “a follow-up message record”. The latter wording is present at the consumed ideation-gate state commit `f9a78202d`, not merely a later report.
  - Trigger evidence: additional-probes.py and message-records.json execute real dispatch and role checkers against valid fixtures. The new matcher at kc-dev-flow-2/scripts/role_triggers.py:66 only accepts plain stage-N.md, and both readers use it. The candidate ADR amendment explicitly excludes message continuations, and its tests assert that exclusion.
  - Why this class: the precise AC fixtures use plain numbered files, while the approved round definition includes messages. A validator cannot choose which accepted scope to discard. FO must disposition this mismatch; repairing it requires authorization, and intentionally narrowing the approved outcome requires a Captain amendment. No product repair was attempted.

No other Material, Deferred risk, or Polish finding was identified. F1 is separate from the settled nested-directory finding.

## Acceptance criteria and falsifiers

### AC-1 — second same-stage symptom dispatch

PASS for the criterion's literal numbered-record fixture. SymptomDispatchTests run the real CLI and assert a single stderr reminder, the three questions, unchanged stdout/exit, and no reminder for the first named round. Mutants adding record 1 to every group and moving stderr to stdout fail their target assertion (mutation-0.log, mutation-1.log). F1 prevents extending this pass to follow-up message records.

### AC-2 — separation and normalization

PASS. The dispatch and role tests exercise distinct symptoms, separate stages, none prefixes, whitespace/case folding, fenced/body/duplicate headers and numeric ordering. Removing stage from the group key fails the role grouping assertion (mutation-2.log).

### AC-3 — named cutoff and strict-only missing-header hold

PASS for the criterion's numbered-record fixture. Named record 3 counts no later record; only strict names mode holds a missing header, record 1 is exempt, and none passes. Requiring the first header and holding folder mode both fail assertions (mutation-3.log, mutation-4.log).

### AC-4 — committed records and dated clearing

PASS. The role tests exercise uncommitted/deleted disk records, --rev, nested and archived layouts, old/low-model calls, qualifying calls/waivers, no-date fallback, the fourth-round clear, and independent event reminders. Reading disk or skipping the date condition fails assertions (mutation-5.log, mutation-6.log); removing cwd-relative revision syntax separately fails the unchanged nested test (reproduction.log).

### AC-5 — historical qnow replay

PASS. The validator reran proof.py replay on the task-declared qnow state revision 290b47a39 (full revision and original SHA-256 hashes retained in replay.json). Fourteen candidate/base runs, k=14..27: first reminder at 16; none through 15; no reminder for the distinct symptoms at 22, 23, 27. Candidate stdout and exit equal base for every run; base never reminds. Thus removing the change falsifies the selected stop condition. This is a historical-shape replay with inserted headers, not proof the historic FO saw or followed a reminder.

### AC-6 — unchanged L2 parser

PASS. Unchanged test_laws_check.py ran separately: 63 tests, 1 skip, exit 0. proof.py laws executes the real checker with repeated and missing headers and without the headers; both runs retain equal semantic L2 violations and exit 1, never Cannot. Moving the new stderr lines to stdout fails this probe (mutation-7.log). laws_check.py and its test file are byte-identical to base.

### AC-7 — idle and merge forwarding

PASS. Existing integration helpers run real committed-state role_triggers. The added idle test forwards exactly one round-two advisory; the merge test holds at round three and writes no ask. Removing next: fails the idle test (mutation-8.log). pr_watch.py and delivery_gate.py production bytes are unchanged.

### AC-8 — lifecycle reading cost

PASS within the designed symptom-name fixture. Fresh base/candidate CLI outputs were counted by the existing proof and independently by wc -w (words.json and words-independent.json). Added words: clean dispatch 0; repeating dispatch 48; missing-header hint 21 (limit 26); idle/merge advisory 47; owed line 74. Extra STEP_BACK words fail the count check (mutation-9.log).

Workflow text is 5781 words on both revisions, and workflow.md and lint-skills.py are byte-identical to base; lint exits 0. Startup adds no words because its entry/workflow paths are unchanged. A separate real pr_watch fixture emits the symptom owed line while active and zero lines after archive (archive-moment.json). These are per-case output counts, not an operator-time saving or a bound for arbitrarily long symptom names.

### AC-9 — ADR amendment and checks

PASS for the listed contents. ADR 0026 carries the dated Captain words, thresholds, clearing date, stderr placement citing ADR 0027 and measured word counts. Its message-exclusion clause causes F1 above. The exact dispatch-named command ran from the detached candidate:

```sh
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb --require 26
```

Exit 0: 50 ADR files checked, 0 legacy. The resolved Codex skill package's identical command also exits 0. Required-statement deletion in a disposable ADR copy exits 1; the independent content check rejects the base without the amendment (adr-falsifiers.json). ADR documentation tests are included in full package discovery.

## RoboRev 1418 decline

The decline is supported on the observed local runtime. The unchanged nested-checkout regression passes. Re-executed direct Git show, cat-file, ls-tree and per-record show commands succeed after moving the archive under nested/. The actual role checker then exits 1 and prints the three-round owed line. Removing ./ from all three revision expressions produces the reported lookup failure and makes that existing test fail with 2 != 1. Full commands, stdout/stderr and exit codes are retained in reproduction.log and review-1418/reproduction.json.

The PR body records FO's exact-head review 1418 and its decline. The worker's separate local review daemon failure is an environment limitation; this validator did not start a daemon, request a new review or claim a new clean review. The reproduction establishes local Git behavior, not an unknown reviewer's environment. No new evidence makes the declined allegation Material.

## Package test execution

Full discovery ran exactly as specified: `python3 -B -m unittest discover -s kc-dev-flow-2/scripts` from the detached candidate. Result: 879 tests, 6 skips, zero failures, exit 0. tests.json and full-suite.log retain the result. Standalone role tests (41) and unchanged laws tests (63, one skip) also pass.

## Other checks and retained-document judgments

All structural checks exit 0: skill lint, number guards, comment ratio, doc impact, design surfaces, dispatch records, and diff --check. Exact commands and output are in checks.json. Comments: zero added comment lines / 262 code lines; 0%, below 5%. There is no added explanatory comment needing repair.

The doc-impact list was read against each protected clause:

- ADR 0045: unaffected; later Captain-ruling predicate, its history semantics and names-only call stay unchanged.
- ADR 0048: unaffected; Paseo completion line and publication owner remain unchanged.
- ADR 0049: unaffected; model rank table and required floor are unchanged and reused for this new event.
- learning.md: unaffected; existing lessons remain accurate; lifecycle reading cost was independently recounted as required.
- ADR 0026: updated; all requested contents checked, but message exclusion still needs disposition under F1.

Corpus rerun: 101 task folders, 445 folder/plain/strict comparisons at state 5f536bb6d5a1334497a815a57413d5f9292ea435, zero stdout changes and zero unexpected verdict changes; 66 intended new strict holds. The implementation used 443 comparisons at an older state; two additional comparisons are from the later corpus, not extra product behavior. corpus.json retains every row.

## Judgment of stated implementation limits

- Renaming a symptom, using none, historical records without headers, and multiple browser attempts within one dispatch do not count: accepted design limits, exercised by normal/none/missing/separate-group controls. No backfill was promised.
- An FO that runs neither check sees no reminder: accepted reach limit. Actual user compliance or reduced diagnosis time was not measured.
- Message continuations do not count: not a safely accepted limit; the accepted round definition says they do. This is F1.
- Local package discovery skips integration-dependent tests: preserve the actual skips; hosted run 41626726024 supplies the separate pinned Spacedock CI evidence. No local test result is relabeled hosted/native evidence.
- Worker could not run local RoboRev: reproduced nested behavior adjudicates the named allegation; FO's PR record supplies the review/disposition claim, not a new validator review.
- Worker left publication and hosted CI to FO: live GitHub now verifies a Draft PR on the exact head and all returned hosted checks green. Merge, ready, release and adopter installation remain outside this validation.
- CI cost per PR was not measured. No CI configuration or trigger changed, so this validation claims no cost reduction.
- Version/workflow budget/dependency scope: no version bump, no workflow text or budget change, no new dependency; verified against the seven-file diff.

## Goal sufficiency and minimal necessity

The selected historical stop-condition replay works, and removing the change restores silence. Shared grouping, committed-state reads, dispatch diagnostics, the existing idle/merge paths, their regression cases and ADR amendment each map to an accepted criterion or lifecycle obligation; no new runtime framework was introduced. Overall goal sufficiency remains unresolved because F1 excludes a supported continuation route the accepted Design includes.

## Minimal acceptance script and state handoff

acceptance.md contains all five exact steps, expected observations and the full output of the unchanged acceptance.sh run in a fresh /bin/bash --noprofile --norc shell. It exits 0 and visibly reproduces F1; that diagnostic success is not acceptance of the product. The temporary acceptance checkout was removed.

The dispatch both requires spacedock state commit and says not to push. Read-only inspection of installed Spacedock 0.27.3 internal/cli/state_sync.go confirms this helper automatically publishes split-root state and offers no no-push flag. To preserve the explicit no-push boundary, the report and named evidence are committed locally with a path-scoped Git commit; the helper and state push are not run. No remote/config change is made. FO owns any later sync.
