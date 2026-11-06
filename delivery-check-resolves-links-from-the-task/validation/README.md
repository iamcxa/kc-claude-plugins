# Independent validation: delivery links

Candidate: `97dceebedd68108ef8e67fa5455f1e578c910ad6` (PR #799).
Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (origin/main resolved at start).
Product was read and run from Git archive exports in `/tmp`; the assigned worktree remained unchanged. No worktree metadata, configuration, branch, PR or remote was mutated.

## Captain acceptance

No graphical surface changes. Run this exact four-step script in a fresh Bash shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-check-resolves-links-from-the-task/validation/acceptance.sh
```

Prerequisites: this repository's local object database containing the candidate, Bash, Git, tar, Python 3 and the repository's existing lint dependencies. The default repository is `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-check-resolves-links-from-the-task`; an equivalent clone can be supplied as the script's first argument. The script and adjacent `mutations.py` must stay together. All generated product copies and mutation evidence go to new directories under `/tmp`.

1. Export the exact candidate; expect `Step 1 PASS: exported 97dceebedd68108ef8e67fa5455f1e578c910ad6`.
2. Run seven existing command-line entrance tests; expect `Ran 7 tests`, `OK`, and `Step 2 PASS: seven entrance tests`.
3. Reintroduce six defects in temporary copies; expect all six falsifiers `passed` and `Step 3 PASS: six assertion-killed mutations`.
4. Run workflow lint; expect `references/sd/workflow.md: 5939 of 5939 words` and `Step 4 PASS: workflow lint`.

Run unchanged by this validator; exit 0. Actual output is [fresh-shell.log](fresh-shell.log). This short script covers the path/prose/fence boundary and workflow budget, not historical archived tasks, hosted CI, model execution, installation, human approval or delivery.

## Acceptance evidence and falsifiers

- AC-1: `TaskFolderCaptainTests.test_question_reads_task_card_from_repository_state_and_task_directories` covers recorded and unrecorded task fences from repository, state and task directories. The cwd mutation fails four assertions, including the wrong-directory fence and a missed unrecorded fence: [mutation-1.log](mutation-1.log).
- AC-2: `test_question_reads_slug_prefixed_markdown_from_task_folder` holds on the task's unrecorded fence. Removing the own-slug branch incorrectly passes: [mutation-2.log](mutation-2.log).
- AC-3: the real `steps` CLI test locates card.md from the record's task folder while cwd is elsewhere. Using cwd incorrectly passes: [mutation-3.log](mutation-3.log).
- AC-4: `test_report_routes_do_not_hide_missing_message_or_asked_paths` permits report-only /api/office/me but refuses missing FO-message and Asked paths. Restoring report paths to the missing-file loop creates the historical hold: [mutation-4.log](mutation-4.log).
- AC-5: ran the existing ideation/replay.sh for both candidate and base, then separately captured each underlying command's exit code and unfiltered output. Candidate: six exits 0. Base: #793 repository exits 1 on the root README's plugin command (state/task pass); #1338 all three directories exit 1 on /api/office/me. Exact commands, cwd and exits: [replay-exits.json](replay-exits.json); original replay outputs: [replay-candidate.log](replay-candidate.log), [replay-base.log](replay-base.log).
- AC-6: [scope.json](scope.json) confirms all emit calls and out-of-scope functions unchanged, with only inspect_steps, steps, captain_step_problems changed and named_file added. An emitted-string mutation is caught by both the AST comparison and an existing exact-output test: [mutation-6.log](mutation-6.log). Workflow bytes and 5939-word budget are unchanged. [ci.json](ci.json) records the successful full hosted package suite at this exact head.
- AC-7: report-only cards retain fences and fenced URLs while excluding prose links; FO-named cards also require prose links, including aliases. Restoring prose links from report-only cards incorrectly holds: [mutation-5.log](mutation-5.log).

The approval's two attached changes are covered: repository-relative documents are not read as task cards, and report-only absolute paths no longer cause missing-file holds. Relative record names, absolute record names, slug-prefixed names and relative task/index inputs are also covered.

## Full package rerun

All 26 CI-listed commands exited 0: 1162 unittest cases were discovered, 1151 executed successfully and 11 were explicitly skipped. Model-free dispatch and recovery probes also passed. See [suite.json](suite.json) and [suite-summary.json](suite-summary.json). The local Spacedock CLI is 0.27.2 with the declared plugin root 0.27.3; hosted CI uses its workflow-pinned 0.27.2 runtime/plugin. No native worker-model invocation is claimed.

## Other checks and necessity

All package-helper commands and actual results are in [checks.json](checks.json). Both the loaded Codex package and dispatch-named Claude package ran adr_lint.py docs/adr --since the exact base; each returned 0 (61 records, 0 legacy). Archive checks that need Git use read-only GIT_DIR/GIT_WORK_TREE and GIT_OPTIONAL_LOCKS=0 for this invocation only. No ADR is added, changed or reserved.

The added module docstring contributes 28 words (1068 to 1096); rendered --help is 1085 to 1113 because argparse adds its own text. These are different measurement surfaces, not a budget discrepancy. No code comments were added: 125 code lines, zero comment lines, within the 5% maximum. doc_impact's three documents each have a checked unaffected disposition in [doc-dispositions.json](doc-dispositions.json).

Goal sufficiency: the two original supported failures are resolved across all three cwd choices while unrecorded fences and missing asked paths still refuse. Minimal necessity: the six mutation failures plus the historical base replay establish the need for the retained resolver, own-slug branch, steps base, report separation and prose-link boundary. The existing functions for check, reviewer facts, round counts and merge authority are unchanged. No extra capabilities or CI changes were introduced.

## Limits and disposition

F1 — Polish (nonblocking evidence-summary correction): implementation says one skipped test, but its original logs and this independent run both record eleven. See [skip-evidence.json](skip-evidence.json). The four design skips require optional frozen/historical amendment corpora; four release-acceptance skips require Journey Map Node dependencies; one dispatch skip requires an explicitly supplied SD_PLUGIN_ROOT; one delivery skip requires GATE_PRESENTATION_STATE; and one laws replay requires DEV2_OBLIGATION_SOURCES. These are pre-existing optional cases, not the seven affected entrance tests, which all ran. The corrected count supersedes the implementation aggregate for this validation; no product repair is requested. No Material, Deferred risk or Needs decision finding was established. The accepted prose-link tradeoff remains: a link in a report-only card is not forced into an Asked line unless FO names that card; its fenced commands remain covered. This is the Captain-approved design, not a newly introduced scope decision.

Historical replays depend on this machine's two archived state checkouts. The removed qnow worktree is represented by an empty temporary stand-in, with only historical path relocation and the post-failure waiver removed, exactly as the approved replay specifies. This is bounded local evidence, not a live qnow run. The replay shell intentionally filters output and suppresses its child failures; therefore replay-exits.json separately records the actual child exit codes.

Implementation's publication/hosted-CI limit is now partially closed: PR #799 exists as Draft and the exact-head package CI succeeded. RoboRev was not run by this validator and remains FO-owned; no conclusion about its findings is claimed. Native worker/model execution, installation, credentials, human approval, merge and delivery remain outside this validation. CI cost was not measured; no CI workflow or trigger changed.
