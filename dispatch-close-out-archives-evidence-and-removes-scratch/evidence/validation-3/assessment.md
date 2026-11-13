# Independent validation, cycle 3

Verdict: PASSED for this pre-release candidate. No new unwaived Material finding. Gate, merge, release and post-release real-task acceptance remain with FO/Captain.

Candidate: c429ab1815a5fc5507056ee54f8005be024e1e69; base: abe8c08ea2716e5f1c046823082e122759703b87; PR: https://github.com/iamcxa/kc-claude-plugins/pull/854.
Started 2026-11-13 11:46:23 Asia/Taipei from clock.curr_time UTC plus eight hours. This worker did not implement the candidate or run its earlier validations.

## Authority and identity
- The live PR read confirms the same head/base, OPEN and not merged (pr-live.json). It is no longer Draft; this worker changed no PR metadata.
- Pilot scope, Captain amendments 1-3 and the named waiver apply. The task remains in validation; this is the third and last allowed validation cycle. role-triggers.log exits 0.
- Read the five implementation dispatch records and their checklists (dispatch-inputs.json). Their requirements trace to the accepted design and amendments.
- Exactly the six designed scripts/tests and authorized ADR 0079 differ from the merged main. The source version 0.40.0 came from main; assigned policy scripts remain 0.39.1.
- The candidate ran from a git archive export with its own fixture Git metadata, never a new registered worktree of the product repository. candidate-files.json binds the seven changed files; source-binding.json binds all package files and the CI workflow. Product bytes are unchanged.
- The export is under macOS system temporary storage, outside /tmp, because the real dispatch scope check rejects a Package root under /tmp. identity.json records its exact path; no package-path test input was rewritten.

## Accepted criteria and actual evidence
- AC-1: the exact grep count on a real native validation-2 dispatch record is 1; its native dispatch artifact also has one Scratch line. The private-repository exclusion is present, caller notes and validation-1 bytes remain unchanged, and an identical retry does not create validation-3. actual-cli-probe/probe.json and implementation-acceptance-rerun.log. Removing notes_for's paragraph makes count 0 and fails (ac-mutations/AC1-paragraph-removed.log).
- AC-2: the exact s4_repro.py command passes: a report citing removed scratch exits 0, the Captain message citing that same missing path exits 1. captain-run.log and implementation-acceptance-rerun.log. Making delivery_gate scan reports again fails the report assertion (ac-mutations/AC2-reports-scanned.log). No delivery_gate product change was necessary.
- AC-4: the exact named unittest and the actual close CLI pass. Own registered worktrees count 0, peer count 1 and its uncommitted file survives; actual-cli-probe/probe.json and captain-run.log. Skipping own worktree removal leaves registration and fails; deleting the peer loses its file and fails (ac-mutations/AC4-*). Superseded global AC-3 is not claimed or enforced.

## Repairs and sibling sites
- Later-dispatch selection: independent native stage and special-role regression tests accept their own second roots and reuse identical retries. Restoring d4fe39e54's selector makes both fail before dispatch. The incoming chosen-root scope and ownership checks still run before creation; rejecting a previous-number render only makes that record ineligible for reuse. repair-mutations/validation-next-root.log and role-next-root.log.
- Evidence retry: actual CLI collision refusal changes no evidence bytes, preserves scratch, then after removing the occupied destination it closes and restores both original payloads/names/digests from committed gzip. Restoring the old evidence implementation fails; saved bad gzip/digest siblings also fail before the ordering repair. actual-cli-probe/ and repair-mutations/collision-partial-write.log, gzip-validation-after-write.log.
- Later write error: candidate saves original digests before compression. A later destination-open error preserves a previously compressed file's original identity on retry; restoring pre-I/O-repair evidence code loses that identity. repair-mutations/later-write-loses-digest.log and captain-run.log. This does not claim a transaction against arbitrary concurrent edits or automatic repair of a partial destination.
- Independent sibling audit agrees with implementation: record_text/notes_for/claim_root have no second number selector; stage and special-role calls share select_record; idle readers do not build records. All evidence validation precedes the compressor; close invokes it before deletion. Scope-note/record writes and watcher-cache writes are separate operations, not original-digest writers.
- The collision-isolation, foreign-owner, symlink, missing-record, root-mismatch and follow-up-root cases run in the candidate suite. The symlink mutant is rejected by the still-present owner check as well as the expected refusal mismatch; it is not isolated proof that removing one defense alone deletes a sentinel.

## Main merge
- merge-identity.log confirms two-parent 2f454b7bd with main abe8c08ea as second parent; watcher-merge-delta.patch shows the retained delta.
- The import keeps both scratch and readme_extensions. Merged cleanup runs before the learn condition, including learn disabled. Both the internal observer call and printed post-merge command retain --readme.
- Existing main tests exercise YAML extension-list forms/comment handling, a missing worktree as a fact, and the printed observer command before and after archive in a detached state checkout with learn enabled/disabled. New combined tests also exercise owned cleanup ordering. Removing merged cleanup or the printed README argument fails (repair-mutations/).
- One supplementary falsifier removing only the internal active-task observer README argument survives. observer_check consults README only for archived tasks; the candidate retains the argument. This is a limit of that extra probe, not observed harm, and it is not included among the twenty rejected mutations (additional-probe-disposition.json).

## Design checks formerly marked not provable
- Dispatch refusal: arbitrary /tmp paths and traversal outside the selected root refuse before record/build; removing the refusal fails.
- Close refusals: missing records, symlink roots/parents, mismatched derived roots and foreign/missing ownership preserve scratch/sentinels.
- Close behavior: actual fixture worktrees are deregistered; dirty-file count is recorded; threshold remains strictly over 256 KiB; retained size over 1 MiB refuses before scratch deletion.
- Restoration: the native close probe commits and restores its gzip through git show with matching original SHA-256. Independently restored all 261 implementation manifest entries from committed state (implementation-restore.json), including compressed originals.
- Post-archive record: the candidate test commits scratch-removed.txt after archive and compares watcher/observer results before and after; no change.
- Idle sweep: older, merged and archived roots prompt close; latest live and unknown roots remain. The newest root can remain during a gate/merge wait until worker close, another dispatch, merge or archive, as explicitly accepted.
- Instruction words: candidate worker paragraph is 52 words against ceiling 66 (words.json); README remains unchanged, and the idle instruction remains one bounded line per ended root.
- Stop condition: still unproven. No real task dispatched after release has completed its full cleanup/restore/delivery journey. Synthetic fixtures and this validation do not replace that obligation.

## Retained documents, necessity and limits
- ADR 0070 unaffected: record/check precedes native builder and committed prompt handoff.
- ADR 0074 unaffected: role floor, checked record and commit-before-prompt remain.
- ADR 0077 unaffected: budget/routing still runs; native tests and role_triggers cover it.
- ADR 0079 updated in this PR, unchanged by repair: it records only approved decisions. Restored privacy wording, original digests, scoped force removal, threshold and cap match it.
- doc-impact.log names exactly these four documents. All added comments were read; they point to binding ADRs. comment-ratio.log is 0.7%, below 5%, against merged main.
- Goal sufficiency: the accepted pre-release limited-use journey works through native dispatch, refusal/retry, real fixture close, committed restore and watcher guidance.
- Minimal necessity: mutations demonstrate each retained dispatch/close/watch behavior, failure boundary or lifecycle obligation; the unchanged AC-2 behavior needs no extra delivery-gate edit. No new policy or publication mechanism was introduced.
- Captain's public-evidence-check waiver remains a Deferred risk accepted for this PR: a worker could put private content into evidence, but no actual private input/exposure was used or observed here. No automated classification or new automatic publication route is claimed. Trigger for material reassessment: observed private publication or a new automatic publication path beyond the waived design.
- Evidence here uses this public repository and synthetic fixtures only; no private-repository task names, rulings or logs are added.
- Required checks: source skill lint, assigned ADR lint with --since merged main --require 0079, design surfaces, dispatch records, role triggers, comment ratio and fresh-reference number guards all exit 0 (required-checks.json). The initial number guard had a sandbox fetch warning; the exact network-enabled rerun has none (number-guards-fresh.log).
- CI: five exact-head workflow runs report success (ci-live.json); this is not a required-check-policy audit or merge authority. CI triggers were not changed; cost per PR was not measured.
- Full-suite skip counts, source binding and selected raw/alias results are recorded in test-counts.json and tests.json. Historical/private corpus and optional journey cases are not counted as passes.
- Existing unchanged replay test normalizes /private on only one side. Its original canonical-path failure is retained; a rerun with the same owned directory's /var alias passes with all source/assertions unchanged (alias-setup.json, replay-alias.log).

## Rerun commands
The exact full invocation arguments are retained in required-checks.json and module-results.json. No command below is a step assigned to the Captain; his sole command is in acceptance.md.
- `bash --noprofile --norc evidence/implementation-1/repair-3/acceptance.sh <archive> /Users/kent/.local/bin/spacedock <evidence>/s4_repro.py <owned-output>`
- `python3 -B full_package_final.py <archive> <owned-output> <pinned-public-Spacedock-root>`
- `python3 -B mutate-acceptance.py <archive>/kc-dev-flow-2/scripts <owned-output> s4_repro.py`
- `python3 -B repair_mutations_final.py <archive>/kc-dev-flow-2/scripts <owned-output>`
- `python3 -B internal_readme_falsifier.py <archive>/kc-dev-flow-2/scripts <evidence>`
- `bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-3/acceptance.sh`
- `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since abe8c08ea2716e5f1c046823082e122759703b87 --require 0079` — exit 0.

## Complete-suite result

All 28 CI Python entries were run. Selected results: 1,438 unittest passes plus two passing native integration programs, ten explicit skips, zero failures (test-counts.json, tests.json, module-results.json). The raw full run exited 1 for the single alias assertion; all eight tests in that module then passed under the same directory alias, with no changed product/test bytes. The selected set replaces only those eight identical test IDs, with uniqueness and completeness checked. Twenty acceptance/repair mutations were rejected; the separately disclosed active-observer mutation survived and is not counted as rejected.
