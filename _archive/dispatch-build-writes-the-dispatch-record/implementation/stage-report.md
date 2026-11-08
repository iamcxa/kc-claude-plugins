
## Stage Report: implementation

- DONE: Bounded integrated implementation committed locally on the assigned branch, based on origin/main.
  Candidate afa4523468a2e86e6c6e0467591df00bf8e51d35; base 334d91e3165953b2ca7191e3308d80b6c02c4a99; branch spacedock-ensign/dispatch-build-writes-the-dispatch-record; nine authorized files; clean code worktree; implementation/candidate-tree.txt.
- SKIPPED: One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (334d91e3165953b2ca7191e3308d80b6c02c4a99) implementing the approved design and acceptance criteria in the task file; D1 as recommended (build dispatches through a package script and land the ADR, reserved as ADR 0070), D2 as recommended (keep --model and --roster as FO-supplied flags) and D3 as recommended (leave /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/package_version.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/workflow_checkout.py out of the script), per the Captain's batch 17 ideation approval 「核准（建議）」 (host question dialog, 2026-11-07); only the files the design names
  No PR opened: no push grant. Product push and Draft PR are FO-owned; /tmp/impl-dispatch-build-writes-the-dispatch-record-pr.md is ready, also saved as implementation/prepared-pr.md; no version edits.
- DONE: ADR 0070 records the ruling the design names, quoting the Captain's words from the task file and its gate records
  ADR 0070 quotes 「核准（建議）」 and the task gate's D1/D2/D3 question excerpt, recorded 2026-11-07T15:37:23.875685Z; it protects dispatch_stage.py main with its ADR pointer.
- SKIPPED: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  AC-1 through AC-7 and AC-8 local wiring/binary checks pass; hosted AC-8 PR run is not run, delegated to FO. All thirteen local counterexamples are caught; implementation/fresh/falsifiers/results.json and adjacent mutation patches/logs.
- DONE: AC-1 through AC-4: stamp commits a complete record with received inputs; incomplete records and invalid/missing candidates hold before building.
  implementation/fresh/dispatch-stage.json: real 0.27.2 split-root seam tests; no-stamp, no-model, dropped-scope-line, skipped-removal, build-before-check and ignored-checker mutants fail their corresponding assertions.
- DONE: AC-5 and AC-6: failed/repeated builds and reuse-advance dispatches preserve the intended record/commit boundary.
  The same real-binary suite checks immediate reuse, changed checklist, intervening state commit, staged-record cleanup, advance commit and withheld envelope on commit failure; no-removal, no-reuse, bytes-only reuse and no-state-commit mutants fail.
- DONE: AC-7: three README passages match the approved text, delta=-2, and the updated consumers pass.
  implementation/fresh/: lint-skills.log 5931/5931, test-lint-skills.json 47 passes, dispatch-records.json 115 passes, sd-dispatch.log exit 0; restored-base-passages mutant fails at 5933 versus 5931. lifecycle-words.json: startup 5933→5931, fresh dispatch 116→101, follow-up 147→87.
- DONE: AC-8 local source and binary checks: CI runs the real seam test after installing the pinned binary and an unset SPACEDOCK_BIN fails.
  implementation/fresh/falsifiers/: deleting the step removes the seam command; missing-binary log exits 1 naming SPACEDOCK_BIN. Existing package/workflow path triggers retained; CI cost per PR not measured; hosted run not run.
- SKIPPED: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> --require 0070 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured
  The installed 0.35.0 ADR command exits 1 on the base's known pre-#806 historical-assertion false positive (adr-lint.log, base-adr-lint.log). Follow-up 2 substitutes the candidate's corrected ADR linter; product publication, RoboRev and hosted CI remain FO-owned.
- DONE: Required local gates and fresh-shell exact-candidate acceptance.
  SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/tmp/spacedock-0272-source bash --noprofile --norc implementation/acceptance.sh <code-root> <candidate> <output> exited 0; fresh/adr-lint.log, number-guards.log and diff-check.log pass; comment-ratio.log 0.9% ≤ 5%. The runner uses git archive, python3 -B and no exported caches; goal-without-change.log shows the missing base writer.
- DONE: Implementation follow-up 1: change only the observer chat-only command entry forced by the shortened README command.
  Extra file kc-dev-flow-2/skills/observer/SKILL.md authorized in dispatch/implementation-1-message-1.md; lint-skills.log exit 1 before, lint-skills-after-observer.log exit 0 after. No additional observer test pin names that entry.
- DONE: Implementation follow-up 2: keep the historical ADR 0047 assertion unchanged and use the candidate ADR linter.
  dispatch/implementation-1-message-2.md names merged #806 and its linter correction; `python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 0070` exits 0; the installed command's exit 1 is retained, not called clean.
- SKIPPED: RoboRev review before publication.
  roborev not run: FO runs RoboRev after this report because the worker sandbox cannot reach the local daemon; no review, PR comment, ready action or merge performed.
- DONE: Affected documents checked with doc_impact.py <base> <candidate> --repo <code-root> --json.
  implementation/doc-impact.json and doc-impact-verdicts.json cover every listed document; dispositions follow. Workflow prose and the observer entry are updated; no affected diagram changes.

### Document dispositions

- `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` — unaffected: The recorded -2 step follows the existing exact-count rule; no ruling changes.
- `docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md` — unaffected: The protected +144 step, its quote and loaded moments are unchanged.
- `docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md` — unaffected: Agent effort and model-table comparison are unchanged.
- `docs/adr/0052-fo-answers-its-own-paseo-workers-permission-requests.md` — unaffected: The extension's normalized_words measurement and permission ownership are unchanged.
- `docs/adr/0064-a-round-three-declined-finding-becomes-a-backlog-task-only-with-a-bite.md` — unaffected: ROUND_RULE and follow-up-reason pins are unchanged.
- `docs/adr/0070-stage-worker-dispatches-are-built-by-a-package-script-that-writes-their-record.md` — updated: New accepted ruling and protected writer pointer.
- `docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py` — unaffected: parse_args is this historical artifact's argparse method, unrelated to the new wrapper.
- `docs/dev/artifacts/skill-ablation-harness/span-match-demo.py` — unaffected: parse_args is this historical artifact's argparse method, unrelated to the new wrapper.
- `docs/ship-flow/tools/validate-tdd-ledger.py` — unaffected: parse_args is this separate ledger tool's argparse method, unrelated to the wrapper.
- `kc-dev-flow-2/README.md` — unaffected: Its complete test inventory points to the CI workflow, which now lists the new seam test.
- `kc-dev-flow-2/references/sd/adoption.md` — unaffected: test_sd_dispatch still checks both adapted graphs and split-root transport; invocation unchanged.
- `kc-dev-flow-2/skills/maintain-flow/SKILL.md` — unaffected: The exact-count lint command and separate review obligation remain accurate.
- `learning.md` — unaffected: Per-moment recount and retained follow-up wording pins are exercised, with their obligations unchanged.

### Summary

Implemented and locally committed afa4523468a2e86e6c6e0467591df00bf8e51d35, with a fresh export acceptance run and thirteen caught falsifiers. The approved package wrapper owns record writing/checking/build order; model/roster flags and the two preflights retain their existing ownership. Prepared PR text and all local evidence are ready for FO; product publication, hosted CI, RoboRev and independent validation are not run by this worker.
