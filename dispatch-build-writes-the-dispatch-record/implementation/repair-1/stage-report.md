
## Stage Report: implementation

- SKIPPED: One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (334d91e3165953b2ca7191e3308d80b6c02c4a99) implementing the approved design and acceptance criteria in the task file; D1 as recommended (build dispatches through a package script and land the ADR, reserved as ADR 0070), D2 as recommended (keep --model and --roster as FO-supplied flags) and D3 as recommended (leave /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/package_version.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/workflow_checkout.py out of the script), per the Captain's batch 17 ideation approval 「核准（建議）」 (host question dialog, 2026-11-07); only the files the design names
  PR #812 exists on the earlier head; repaired candidate 0d84d5d1b96fd674dba3a442d69c2e7898cceccd is committed locally on spacedock-ensign/dispatch-build-writes-the-dispatch-record, parent afa4523468a2e86e6c6e0467591df00bf8e51d35, base 334d91e3165953b2ca7191e3308d80b6c02c4a99. FO owns pushing the new head and the review reply; no product push or PR write performed.
- DONE: ADR 0070 records the ruling the design names, quoting the Captain's words from the task file and its gate records
  ADR 0070 and its protected pointer are unchanged; the candidate's ADR linter passes. The repair changes the writer and its seam test only; follow-up 1's observer correction and follow-up 2's linter substitution remain intact.
- SKIPPED: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  All local acceptance checks and original thirteen falsifiers pass at the new head; three preservation falsifiers also fail as intended. Hosted AC-8 and independent validation on this repaired head are not run; the earlier validation/CI evidence applies to afa4523468a2e86e6c6e0467591df00bf8e51d35 only.
- SKIPPED: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> --require 0070 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured
  Installed 0.35.0 ADR lint retains the known pre-#806 false positive; the previously authorized candidate linter passes. New-head publication, RoboRev and hosted CI remain FO-owned; CI cost per PR is not measured, and its configuration/triggers did not change.
- DONE: Repair the Codex P2 finding on PR #812 (review comment 4505536959 at afa4523468a2e86e6c6e0467591df00bf8e51d35, "Preserve existing uncommitted dispatch records"): kc-dev-flow-2/scripts/dispatch_stage.py numbers the next record from HEAD only, so it overwrites a record that already exists untracked or staged, and its cleanup then deletes that file and its index entry. FO dispositions it Material and authorizes the fix in this task.
  Reproduced all three data-loss cases against the reviewed writer (repair-1/regressions-before.log), then committed 0d84d5d1b96fd674dba3a442d69c2e7898cceccd; repair-1/preservation-falsifiers-committed restores that old writer and rejects it separately for each regression.
- DONE: Refuse, before writing, when the target record path already exists in the worktree or index and is not the identical committed record the retry rule reuses; name the path and leave its bytes and staging untouched. Cleanup removes only a file this invocation created.
  select_record checks the index, then opens the target with exclusive creation; main reports FileExistsError and the path before checking/building. The existing wrote flag now marks a newly created file, so cleanup does not own a pre-existing file; committed identical retry reuse remains unchanged.
- DONE: Add a test with a falsifier for each: a pre-existing untracked record and a pre-existing staged record both survive a refused run byte for byte with their staging state. Rerun the existing acceptance runner and package tests, commit locally on the same branch, and append an implementation stage report with the new candidate SHA. Reply on nothing in the PR; FO pushes and answers the review.
  repair-1/fresh/dispatch-stage.json: 12 passes, including different staged/worktree bytes and an index-only path. All 28 checked-in CI Python commands exit 0 (1215 tests reported, 11 skipped); repair-1/package-tests/results.json and per-command logs. The final seam file also passes dispatch-stage-final.log. Original acceptance.sh rerun in a fresh bash shell exits 0 at 0d84d5d1b96fd674dba3a442d69c2e7898cceccd; no PR reply or product push.
- DONE: AC-1 through AC-4: complete committed records still carry received input, and malformed dispatches still hold before build.
  repair-1/fresh/dispatch-stage.json and original no-stamp/no-model/dropped-line/no-cleanup/build-before-check/ignored-checker mutants pass their rejection controls; pre-existing records now hold before the checker too.
- DONE: AC-5 and AC-6: owned failure cleanup, committed retry numbering, later rounds and advance envelope/commit boundaries remain covered.
  The seam suite and original failure/reuse/commit mutants pass. Per follow-up 3, a pending record after advance commit failure is now preserved and refused; the test commits it via real spacedock state commit, then verifies identical committed reuse succeeds.
- DONE: AC-7: approved README passages, delta=-2 budget and existing dispatch consumers remain valid.
  repair-1/fresh/: lint-skills.log 5931/5931; 47 lint tests and 115 record tests pass without skips; test_sd_dispatch.py exits 0; restored-base-passages falsifier still fails. Workflow prose is unchanged by this repair.
- DONE: AC-8 local wiring: real-binary step and missing-binary hold are preserved.
  repair-1/fresh/falsifiers retains CI-step deletion and unset-SPACEDOCK_BIN controls; real 0.27.2 seam/integration tests pass locally. The new head's hosted CI is not run by this worker.
- DONE: Required local gates, candidate preservation and document dispositions.
  repair-1/fresh/: candidate ADR lint, number guards and diff check exit 0; comment ratio: code lines 379, comment lines 3, 0.8%, below 5%. Design surfaces are presentable (scope scan not run at validation); doc_impact exits 0. repair-1/doc-impact-verdicts.json covers every listed document against the original base; this repair edits no document, ADR or version and changes no diagram.
- SKIPPED: RoboRev and new-head external review/CI/independent validation.
  roborev not run: FO owns the review and publication handoff. This worker leaves the product branch local and posts nothing to PR #812; prior-head validation is not claimed for the repaired head.

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

Repaired the existing-record data-loss finding at 0d84d5d1b96fd674dba3a442d69c2e7898cceccd; untracked, staged and index-only records are refused without changing file bytes, index entries, task bytes or state HEAD. This complete implementation report supersedes the earlier implementation report, including its automatic retry over a pending uncommitted record; new-head CI, review response and independent validation remain FO-owned.
