# Validation evidence for PR #793

Candidate: 5b3e290a7eaceb0fe70f489d25d622314598b9f0
Base: b804d81d3abc94c9c321326dc75e7cac927c5252 (origin/main at validation)
Date: 2026-11-06

## Captain acceptance

Run this exact command in a fresh Bash shell:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-question-requires-worktree-clause/validation/acceptance.sh
```

The script has five numbered steps, their exact commands and expected observations, and declared local prerequisites. It exports both pinned revisions under /tmp without creating or removing a Git worktree. Observed output is acceptance.log: all commands exited 0, 12 question tests OK; historical candidate exits 1/1/0 versus base 0/0/0; merge-time output and workflow bytes identical; 61 ADR records checked, zero legacy; lint PASS, 5939 of 5939 words; version parity consistent; acceptance PASS.

The gate fixtures supply valid task, summary, step and GitHub facts, isolating real recorded question strings. No graphical surface changes. This is not a live merge, native approval, provider authorization, real worktree-cleanliness check or proof that the Captain saw the question.

## Independent reruns

checks.json records commands, working directories and exit codes. The installed package is /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0, resolved from the loaded validation skill. Candidate and baseline exports used /tmp/opencode/validation-delivery-worktree-clause/{candidate,base}. The historical state is pinned to 846c4202b2a7e70bd08eee1d31406502f350aa0d.

- prove.py is the implementation proof runner reused independently, with arguments for export and output paths. Run `python3 -B prove.py <candidate export> <shared state checkout> <base export> <output directory>`. proof-summary.json, mutations.json, mutation-1.log through mutation-5.log and check-parity.json are the observed results. Five deliberate defects cause assertion failures without runtime errors. corpus-verdicts.json preserves all 131 historical decisions with outputs omitted; each of the 24 changes is intended, and the runner regenerates full output.
- run_suite.py reads test commands from the candidate CI workflow plus its native recovery command. Run `python3 -B run_suite.py <candidate export>`. It declares the native binary and plugin paths in source. suite.xml, suite.json and the per-command logs record 25 passing commands, 1156 unittest cases including 11 skips. Local native CLI 0.27.2 uses plugin root 0.27.3; this does not claim parity with every host or CI environment.
- The unmodified parity script first exited 128 in a pure export because it calls git ls-files. parity-with-readonly-git.log records exit 0 after setting GIT_DIR to the assigned worktree metadata and GIT_WORK_TREE to the export. ADR lint uses the same read-only environment; no Git config/index write or new Git worktree was needed. acceptance.sh contains the exact commands.
- dispatch.log records the initial exit 1 for the missing review-delegation annotation. FO corrected only its record in e0b47efc0d7bf7acd6e0878f6b0ae9196545ab35; dispatch-corrected.log records exit 0, four complete records. The FO message named c8bb8e07b, which changed the sibling task; git log for this task establishes the correction commit above.
- pr.json is a read-only GitHub metadata observation: PR #793 OPEN, Draft, assigned head/base, five SUCCESS checks and one skipped deployment. RoboRev job 1544 is FO-reported, not rerun here. No PR writes, merge, product push or review request was made by this validator.

## Limits reviewed

The 11 optional skips match the implementation report: four design historical/native checks lack their DEV2_AMENDMENT inputs; four release checks lack node/journey-map/yaml prerequisites; dispatch builder lacks SD_PLUGIN_ROOT; historical delivery replay lacks GATE_PRESENTATION_STATE; laws replay lacks DEV2_OBLIGATION_SOURCES. They remain unverified rather than counted as passing evidence. All five task criteria have independently run checks.

limits.json observes the accepted presence-only behavior (negated removal passes), the English-only clause requirement (Chinese-only removal is held), and the lack of real worktree state inspection. Bypassing question still bypasses this new clause check, as approved decision D1 requires. D2 deliberately refuses removal wording missing clean/pushed. Corpus replay uses valid fixtures because archived Captain-step paths are obsolete. These known limits do not expand the accepted claim.

The three affected ADR documents (0044, 0051, 0062) preserve their protected behavior: optional summary reviewer facts, merge-time round count, and quoted-question authority. doc impact and tests agree with implementation's unaffected assessments. No new ADR, workflow text, version or CI configuration changed; CI cost per PR was not measured. PR #794 edits the same script later and needs its own integration checks after #793; this verdict covers only #793.

A portability recheck of prove.py first rejected bytecode caches left by a separate limit probe in the reused export (cached-proof-attempt.log). It was rerun unchanged with python3 -B on the fresh exports from acceptance.sh: fresh-proof.log reports five caught mutants, zero errors and zero caches. The initial independent mutation run also had zero caches.
