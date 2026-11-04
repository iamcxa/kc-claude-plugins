# Independent validation, cycle 2

Candidate: PR #771, 7aad891353a973c7fbda2ad4214a3aadea71d2a6.
Assigned source worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back.
Detached checkout used: .validation-771 under that worktree.
Fetched origin/main: e1bee223c47a1cd534a665a47776b683375b34fc.
Merge base and original implementation comparison: 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb.
All seven changed product hashes equal implementation-3/product-hashes.json. No product bytes or candidate ref were changed.

**Verdict: PASSED.** Full scripts-directory discovery: 882 tests, 6 skips, zero failures, exit 0.

## Authority and prior finding

The task is Pilot, Surfaces: none, in validation. Captain amendment 1 quotes 「照你建議」 in reply to 「決定：B 照原設計修，讓追加指示紀錄也算進同症狀的輪數嗎？」 and supersedes no criterion.
The earlier validation's F1 Needs decision is resolved at this head: one plain implementation-2 record plus message-1 and message-2 counts three rounds in both readers. The folder and named CLI print the three-round reminder, while the committed-state CLI exits 1 and owes chief-engineer. Removing message support separately from the shared counter, disk reader or committed reader makes an assertion fail; ignoring message order in the named cutoff fails too. The same three new tests reject the pre-repair parent with three assertion failures (repair-parent-red.log). Numeric message 2/10 order also determines the third-round clearing date correctly.
The prior RoboRev 1418 nested-path decline is settled; repair changes no cited relative-Git-path behavior. The unchanged nested/archive test was rerun and passes. No review was requested.

## Acceptance and failure controls

- AC-1: acceptance step 2 exercises the actual dispatch CLI, stderr-only reminder and unchanged stdout/exit at the second round. Adding a fictional first round or moving output to stdout fails mutation-0/1.
- AC-2: stage/symptom separation, first header, whitespace/case normalization, none, fences and body exclusions pass. Removing stage from grouping fails mutation-2.
- AC-3: numeric named cutoff excludes later plain/messages; folder selects numeric latest. Missing header holds only named strict mode, while record one and none pass. Broadening first-record or folder-mode refusal fails mutation-3/4; ignoring message number fails message-mutation-3.
- AC-4: committed records, --rev, deletion/uncommitted exclusion, archived/nested layout, model/date/waiver rules and other event-family independence pass. Reading the disk or removing the date check fails mutation-5/6; follow-up reader and counter deletions fail their dedicated controls.
- AC-5: the original pinned qnow state 290b47a39 replay, with retained full revision and SHA-256 per record, first reminds at k=16, never k=14/15 or for distinct symptoms 22/23/27. All 14 original-base runs are silent, with identical stdout/exits. The same replay also passes against fetched origin/main.
- AC-6: the existing laws tests run in full discovery. The explicit real L2 probe gives equal violation verdicts with/without the new symptom lines, never Cannot. Moving stderr to stdout makes mutation-7 fail.
- AC-7: the actual role checker feeds pr_watch's next line, and three committed rounds hold delivery_gate without saving an ask. Dropping next: fails mutation-8. The production forwarding files are unchanged.
- AC-8: independent wc -w recount agrees: dispatch +0 clean / +48 repeated / +21 missing-header hint; idle/merge +47 advisory / +74 owed. Startup +0 by unchanged lifecycle/template; actual pr_watch after-archive probe emits no line. Workflow 5781 -> 5781, lint/budget byte-identical. Extra question words fail mutation-9. Fetched-origin/main comparison agrees.
- AC-9: ADR 0026 retains the dated Captain approval, round count, dated clearing, stderr/ADR 0027 placement and measured words, and now carries the follow-up clarification. The original base lacking the amendment fails the content check; deleting Recommended fails required-record lint. Both dispatch-named Claude package and resolved Codex package adr_lint commands with --since origin/main --require 26 exit 0, reporting 50 ADRs and zero legacy.

## Other checks and retained documents

lint-skills, number guards, design surfaces, dispatch record completeness, diff whitespace, comment ratio and doc impact pass; the exact commands and exits are in checks.json and supplemental.json. The requested origin/main comparison and original implementation-base comparison both pass.
Comment ratio is 0 comment lines / 311 code lines = 0.0%, below 5%. All added documentation strings and the two changed historical test-output helpers were read: the latter preserve stdout assertions and explicitly constrain stderr to the new hint.
Document dispositions:
- ADR 0026: updated, including Captain amendment 1.
- ADR 0045: unaffected; later-Captain-ruling eligibility is unchanged and its existing tests remain.
- ADR 0048: unaffected; worker completion/publication authority is unchanged.
- ADR 0049: unaffected; opus/Astra rank and floor are unchanged and the model/date controls exercise them.
- learning.md: unaffected; historical examples stay historical. Applied its configuration-write prohibition, per-moment word recount, output-consumer check and historical-corpus comparison.
No workflow or CI configuration changed. CI cost per PR was not measured.

The committed-state corpus at 3f2da193a3035e78148ce6edf3c0af0561fc9364 includes 102 task folders. All 460 folder/plain/strict comparisons preserve stdout and have zero unexpected verdict changes; 71 intended strict-only holds add the missing-header requirement. The increased hold count versus implementation-3 is from a newer state snapshot, not an unexplained product change.

## Goal sufficiency and minimal necessity

The accepted stop condition is observed at the dispatch moment that the source history shows the First Officer actually used. Both disk and committed readers count the Captain-approved message form; the next two moments forward the existing lines and dated clearing without changing their production callers. The seven-file delta consists only of the shared counting/readers, their dispatch entry points, four relevant test files and ADR 0026. The original-base counterexample is silent, and the mutation controls fail at each added behavioral boundary. No new stage, tool, workflow-budget rise, backfill, CI trigger or product scaffolding was retained.

## Limits judged

- Renaming a symptom or using none prevents grouping. This is an accepted limit, exercised by the separation tests; no semantic inference or backfill is claimed.
- Multiple browser runs within one dispatch do not count. This is the recorded non-goal; only persisted dispatch records are inputs.
- Skipping both dispatch check and idle hook bypasses the reminder. The feature adds no interception hook. The replay establishes output when the supported command runs, not universal enforcement.
- Old records with no header count zero; named strict mode now refuses a later record without one. The corpus measures this intended compatibility cost.
- Idle and merge read committed state; uncommitted changes cannot add/clear rounds. The corresponding negative controls pass.
- Full discovery is a scripts-directory unit suite, not proof of every live integration; six pre-existing skips remain. The hosted PR checks were read at the exact head separately (six success, one deploy skipped).
- implementation-3's one-shot RoboRev attempt was incomplete because its daemon was unavailable. A usable exact-head external review remains FO-owned; this validation makes no clean-review claim and did not start reviewers.
- Publication already reaches the assigned PR head, with hosted checks observed. Merge, release, adoption and Captain delivery approval remain outside this worker's authority.
- The five-step fresh-shell acceptance script is unchanged between writing and execution, exit 0, with commands and full output in acceptance.md. It does not replace the longer replay/corpus/mutation evidence.

## Evidence handling

The existing implementation proof scripts were rerun, not treated as asserted results. Their paths were adapted for the detached checkout and scratch outputs. An initial scratch-path relocation left the baseline extractor pointing elsewhere; the harness path was corrected and replay/word/corpus/mutation comparisons rerun successfully. Candidate bytes were never repaired.
The installed spacedock state commit helper calls publication for split-root state, and its parser offers no no-push option (installed internal/cli/state_sync.go). The dispatch explicitly prohibits push. Therefore the report and evidence use a local path-scoped Git commit; FO owns synchronization. No remote URL or Git configuration write was performed.
