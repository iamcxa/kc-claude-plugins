# Independent validation 2 — PR #868

Verdict: PASSED at `a4f2fc41413866f0148e1f176f447e81216ca6cf`, against base `bfc53d82510006b52baf41569c1e25176e99d87a`. Previous candidate: `2661da44a77c2b2f93991a3968fb1515bb4e7132`. Start: 2026-11-14 00:34:18 Asia/Taipei; clock__curr_time UTC +08:00. Fresh validator, not an author or validation-1 worker. Pilot scope: counts and recorded times; no product edits, publication or delivery authority.

## Repair and Captain amendment 1

The entire repair is three replaced lines in `kc-dev-flow-2/references/sd/workflow.md`; the derivation, POC test, budget reader, dispatch code, timeline and every other file are byte-identical to the prior candidate (`provenance.json`). The Captain's stated outcome holds: deriving the POC workflow omits the ideation budget count, with the unchanged POC suite passing all nine tests (`poc.log`). The shared Budget paragraph explicitly says “See stage prefixes”; the ideation section supplies `Prefix N ideation,` and its round/default meaning. A five-stage reader is therefore told an extra form exists and can find it. This was a textual discovery check, not a user study.

The author tried the Captain-named derivation edit and FO chose placement instead; this validator accepts the expressly dispatched outcome/smaller repair, and does not claim the derivation script was edited. Both unchanged POC assertions matter: only removing the stage/section and carrying no stray ideation wording. Restoring the previous shared placement reproduces the prohibited line (`placement-falsifier.json`). This resolves validation-1 F1, previously Needs decision; no new Material, Deferred risk, Polish or Needs decision finding. The ten-file original scope remains the ten-file PR; no version or CI file changed.

## Evidence boundary and all criteria

`acceptance.json` maps every criterion to fresh outputs and explicitly reused validation-1 evidence/falsifiers. Fresh local direct test entry points from the clean product worktree: POC 9/9, role 63/63, dispatch 56/56, all exit 0; no skips (`poc.log`, `role.log`, `dispatch.log`). Runtime: `/Users/kent/.local/bin/spacedock`, 0.27.2. Owned TMPDIR kept suite fixtures under this dispatch scratch. `product-status-after.txt` is empty; before status is in `provenance.json`.

AC-1/2/4/5: fresh budget grammar/replays and real dispatch suite prove the same count text, explicit bound, Pilot default, Prod exemption, builder-not-run/record-removal on hold, and budget-only special-role behavior. Their code and prior mutation-tested tests are unchanged. AC-3: the fresh acceptance script checks six replay exits 0/1/0/0/1/1 and three recorded round results 43.6 withdrawn, 562.2 revise, 97.0 approve (`acceptance-final.log`). The three-versus-two bound is the fresh counterexample.

AC-6/7: intentionally reuse validation-1's frozen-state comparison and census, not the author's counts: 249 tasks, 24 text differences, zero exit changes; 192 rounds over 170 archived tasks, zero mismatches/missing ends, three zero-minute rounds (`../validation-1/logs/base-comparison.log`, `../validation-1/logs/rounds-census.log`). Workflow text placement cannot affect these unchanged scripts on the same frozen corpus. Their falsifiers remain `../validation-1/mutations.json` (over-holding and removing rounds).

AC-8: fresh lint is 6097/6097; restoring the prose hold yields 6101/6097 and exit 1 (`lint.log`, `lint-falsifier.log`). Whitespace delta stays -2; normalized startup delta is -1, not -2 (`word-counts.json`). AC-9: role/dispatch rerun; unchanged timeline 13 and design-check 234 suites, including four optional corpus skips, are explicitly inherited from validation-1, not claimed rerun. AC-10: required installed-package ADR lint exits 0, 78 records; ADR 0085 and pointer bytes unchanged, so reuse prior pointer-removal falsifier (`adr.log`, `../validation-1/mutations.json`).

All ten prior per-criterion falsifiers were read and reused where unaffected; they were not rerun wholesale. Only affected prose falsifiers were rerun, as the supplemental dispatch requires. The old export-harness failures in validation-1 do not support this verdict; authoritative current suites ran directly from the clean product worktree. No export adaptation was needed.

Hosted CI was read on this exact SHA: all five returned pull-request workflows completed successfully (`ci-final.json`); the package test job completed every step, including unchanged POC and real SD consumer tests (`ci-jobs.json`). Run: https://github.com/iamcxa/kc-claude-plugins/actions/runs/43463783071. This is observed hosted success, not a branch-protection completeness or merge claim. PR remains OPEN/Draft (`pr.json`).

## Commands rerun

`WT` is the assigned product worktree named in the dispatch; all commands below ran there unless an absolute script says otherwise. `P` is `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts`; `STATE` is the shared state checkout; `TASK` is this task folder. Full argv/exits are in `commands.json`.

- `python3 -B kc-dev-flow-2/scripts/test_poc_readme.py` — exit 0, 9 tests; unchanged test.
- `python3 -B kc-dev-flow-2/scripts/test_role_triggers.py` — exit 0, 63 tests.
- `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py` — exit 0, 56 tests; no test or path adaptation.
- `python3 -B kc-dev-flow-2/scripts/lint-skills.py` — exit 0; 6097/6097.
- `python3 "$P/adr_lint.py" docs/adr --since bfc53d82510006b52baf41569c1e25176e99d87a --require 0085` — exit 0.
- `python3 "$P/number_guards.py" check --repo "$WT" --workflow-dir "$STATE/.." --task "$STATE/budget-form-counts-ideation-rounds-and-times-each-round.md" --head a4f2fc41413866f0148e1f176f447e81216ca6cf` — exit 0; final live fetch has no stale-ref warning (`numbers-live.log`); initial sandbox fetch warning retained in `numbers.log`.
- `python3 "$P/comment_ratio.py" bfc53d82510006b52baf41569c1e25176e99d87a a4f2fc41413866f0148e1f176f447e81216ca6cf --workflow-dir "$STATE/.."` — exit 0; 3/117, 2.6%, maximum 5%; unchanged ADR-pointer comments.
- `python3 "$P/doc_impact.py" bfc53d82510006b52baf41569c1e25176e99d87a a4f2fc41413866f0148e1f176f447e81216ca6cf --json` — exit 0; all 18 documents carry a checked implementation disposition (`document-check.json`).
- `python3 "$P/dispatch_records.py" "$TASK"` — exit 0; six complete records. The repair record plus supplemental validation dispatch establish the authorized placement outcome; accepted criteria and amendment explain the scope.
- `python3 -B kc-dev-flow-2/scripts/poc_readme.py check docs/dev2-poc/README.md docs/dev2/README.md` — exit 0 (`adopted.log`); no adopted README edit needed.
- The exact five-step Bash command below — exit 0 (`acceptance-final.log`, `acceptance-result.json`); it also reruns legacy grammar, six archived-task replays and the recorded three-round timeline.

## Captain steps

No user-visible screen changes. Requires Git, Python 3, and this public state checkout's existing candidate/base/frozen-state Git objects. The command runs from any directory, creates and removes temporary files, and does not depend on the product worktree or validator scratch. The validation run changed only TMPDIR to keep temporary files in its owned scratch; an ordinary shell uses its normal temporary directory.

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/validation-2/acceptance.sh
```

Step 1 exports and prints the pinned candidate. Step 2 checks unchanged legacy forms and six replay exits 0/1/0/0/1/1. Step 3 prints the three expected timed outcomes. Step 4 checks the 6097-word cap and ADR 0085. Step 5 derives four POC stages with no ideation budget and confirms five-stage prefix discovery. Expected and observed final line: `PASS: five acceptance checks`, exit 0. It exercises direct behavior, not the full suites from an export. It does not cover corpus-wide comparison, real dispatch suite, hosted CI or released-live behavior; those proof boundaries remain separate.

## Implementation limits judged

The reported whole-package local run was not independently rerun here; the changed-surface suites were, and hosted full-package success was independently observed. Validation-1's optional historical-corpus skips remain limits; they are unrelated to moving prose. Minutes include waiting, late commits can yield zero-minute rounds, and gate/boundary results are not worker success reports. Released-live third-dispatch behavior, actual RoboRev review of this head, merge, release and adoption are not claimed. UI screenshots are inapplicable; no diagram changed. External dynamic adopters are outside the in-package consumer claim; the unchanged derivation entry point and hosted SD test cover the identified package consumer. CI cost per PR was not measured; CI configuration is unchanged. Original failed attempts remain in earlier reports and are not relabelled as passes. PR description/review freshness and the delivery decision remain with FO.
