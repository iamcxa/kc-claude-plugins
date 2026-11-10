# Independent validation: counts name the producing run

Candidate: 90f43f801be3d03ebd7d98d1a41ad78801aea54d (PR #822).
Implementation base: 82c9e67ae892b80647c3f6a8b6929f993e42dbc2.
Fetched origin/main: f980a097bf15d8d1382c039949c6b9aefc5439c8.
Run date: 2026-11-10 UTC. `identity.json` records the export and conflict-free merge tree.
The candidate and merged tree were exported under /tmp, without creating a repository worktree or changing the product branch. `source-integrity.json` binds inspected candidate files to Git blob IDs. The throwaway bare object database used by merge-tree is not delivery evidence.

Each `NAME.json` records the command, cwd, UTC start/end, process PID, exit and SHA-256 of `NAME.log`. Numbers below come from those named commands/runs, not from the earlier implementation report. Reused replay/mutation/word drivers were inspected and copied from implementation-3; only archive-root and immutable revision lookup were adapted. `extra-falsifiers.py` and `probes.py` add the small missing boundary checks. No models or external provider mutations were run.

## Acceptance evidence

| Criterion | Independent observation | Falsifier |
| --- | --- | --- |
| AC-1 | `acceptance.sh` step 2 and full suite exercise complete's 18-versus-15 reference join, pending state, usable token, successful correction and historical read compatibility. | `mutations.py` learn-join removes the check; the named acceptance test fails with exit 1 and no import error. |
| AC-4 | `replay.py` gate-replay reads the four pinned ideation state revisions: 24 of 30 recent summaries need nonzero disclosure (gate-replay.log). learn-replay reads 28 add entries in five stores and reproduces exactly the implementation's three refused records: 441fe280, d829872c and ed2d3ee1 (learn-replay.log). Original records remain unmodified; snapshots match implementation-3 byte digests. | `extra-falsifiers-corrected.log` restores the old comma-swallowing regex: `cycle 2, round 2` again matches `2, round`, whereas the candidate does not. `probes.log` also demonstrates identifier P1/S1 does not supply standalone 1. |
| AC-5 | `words.py` / words.log independently executes base/candidate fixture outputs: startup 5931+48 unchanged; validation 826 to 848; evaluator 877 to 896; question zero-count stdout 92 to 97; check 84 to 89. The bounded diagnostics test covers at most eight twelve-word cuts. | `extra-falsifiers-corrected.log` adds one startup word in a disposable copy: the recount becomes 5932 and the native lint refuses the unchanged 5931 budget. |
| AC-6 | See suite-candidate.json and suite-merged.json for the exact full-suite producer results; lint.json, adr.json, comments.json, numbers-refreshed.json and source-integrity.json for the required bounds. Both exported trees are exercised, including merged role_triggers.py from current main. | The native lint mutation exits 1; the POC writer mutation retains both route failures, wrong-summary and previous hold assertions. Product diff has only the nine authorized files; no version, CI, workflow.md or mod change. |
| AC-7 | `acceptance.sh` step 3 checks K-shaped missing/wrong/duplicate disclosures, a cited 3, derived 3 of 6, legacy input, fences, containment, other holds, automatic persistence and idempotence. | `mutations.log` number-in-file and writer removals each make the named tests fail. |
| AC-8 | `acceptance.sh` step 3 exercises the real check function with the repository's gh stub: the PR-body count enters the saved ask, missing/wrong input is rewritten, and write errors create no merge-ask record. | `mutations.log` pr-body and writer removals each fail the relevant test. |

The old AC-2/AC-3 disclosure holds are superseded by Captain amendment 1; they were not restored as requirements. Current AC-7/AC-8 wording was checked with design_surfaces.py, exit 0. Dispatch records all trace to accepted criteria or the explicit POC fixture authorization, and dispatch_records.py exits 0.

## Extra ordinal-reference refusal

`probes.py` reads the actual completed ed2d3ee1 record and copies its add decision and evidence strings into a fresh disposable claim. The original `Cycle 1 FO line` wording makes complete exit 1 and leaves the claim pending. Replacing just that phrase with `first-cycle FO line`, while preserving the evidence and token, completes. The error's twelve-word cut does not include the actual matching phrase in this long historical sentence; probes.log retains the full observation. Existing completed records still read normally; the script never revises the historical record.

This is observed friction in the supported learn completion route, not a hypothetical malformed input. The approved integer/optional-word/unit grammar deliberately covers this text, and AC-4 explicitly permits explained replay differences; therefore it is a **Needs decision** compatibility finding rather than a claim that implementation violated that grammar. Recommendation: do not silently accept it as harmless; narrow ordinal-reference recognition within authorized scope, or obtain an explicit disposition accepting the pending correction cost. The validator does not rewrite the accepted grammar or edit product bytes. The warning does not establish any loss of completed data or token usability.

## Limits judged

- The external issue #811's original adopter record is unavailable. The 18/15 CLI test reproduces its reported failure shape, not the adopter incident itself.
- A matching numeric token in a cited task file or referenced pack item proves presence only. Stale or unrelated numbers can pass, and no new recorder binds the actual producing command. This is an explicitly accepted design limit, not count-truth proof.
- Correct derived gate counts remain unchecked without a hold; derived learn counts need numbers stated in references. Both are the selected two-seam treatment.
- The comma defect is absent; extra recognition changes are explained by the approved unit list, fence exclusion and standalone-number normalization. The additional ordinal-reference refusal is the unresolved decision above.
- Chat, spelled-out/implicit lists, stage-report text not carried into a summary and PR readers who never see the ask remain outside the scanner, as the approved design states. No UI screenshot or diagram-render requirement applies to this Surfaces: none task.
- Existing completed-record reads do not retroactively apply the new check. Pending bad completions remain repairable. Local runtime fixtures and corpus replays do not prove host-wide adoption or model writing behavior.
- GitHub PR/CI observations are read-only and retained in github-pr-refreshed.log; review comments in github-comments-refreshed.log. These are separate from independent local test evidence and grant no merge authority.
- CI topology is unchanged. CI cost per PR was not measured.

## Retained documents and necessity

The independent doc-impact.log lists ADR 0044, 0051, 0062, 0071 and 0072, matching implementation's coverage. 0044 is unaffected: split and legacy reviewer routing remains. 0051 is unaffected: External rounds holds remain. 0062 is unaffected: bound-question authority remains. 0071 is unaffected: matching delivery-record checks remain. 0072 is updated with the amended automatic-write contract. The added skill sentences describe actual behavior. Added comments are only the three ADR links; comment_ratio.py reports 1.3% against maximum 5% (comments.log).

Goal sufficiency is bounded by the unresolved ordinal-reference disposition. Necessity of the shared recognition, source comparison, PR-body scan, automatic write and learn join is shown by the matching mutations; POC expected-byte adjustment is necessary for the approved automatic write, while retaining its other holds. The shared module avoids separate gate/learn grammars, and skipping retrospective content checking prevents corruption of readable legacy records.

## Captain acceptance script

Run exactly:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/counts-name-the-run-that-produced-them/validation/validation-1/acceptance.sh
```

Prerequisites: this repository contains the pinned candidate, Python 3, Git and tar. The script creates only a fresh /tmp export, and does not need the validation evidence folder as an input. Its four exact steps and expected observations are:

1. Export pinned head: prints `Exported 90f43f801be3d03ebd7d98d1a41ad78801aea54d`.
2. Execute learn refusal/correction and legacy-read tests: `Ran 2 tests`, `OK`.
3. Execute gate disclosures and both POC routes: `Ran 8 tests`, `OK`.
4. Exercise an ordinal citation via complete: prints `KNOWN LIMIT: Cycle 1 FO line refused; claim remains pending`, then `SAME EVIDENCE: wording change completes`.

`acceptance-published-path.json` / acceptance-published-path.log record the validator's exact published-path fresh-bash run; acceptance.json / acceptance.log retain the preceding identical-script run from /tmp. This script confirms the selected behavior and exposes the unresolved limit; passing it does not authorize that limit, prove the whole corpus, repeat the full suite or validate a merge. No user-visible graphical surface exists in this task.

## Environmental and probe notes

The first number-guard read could not fetch state inside the sandbox and was not accepted as fresh reservation evidence; numbers-refreshed.log records the authorized rerun without that warning. The initial wrapped GitHub calls hit a sandbox network failure and were superseded by github-*-refreshed. The first extra-falsifiers assertion expected the wrong wording for the native lint error; the tool correctly refused the mutation. The corrected probe checks the observed diagnostic, preserving both original and corrected logs. The mid-run clarification transport to FO returned `user rejected MCP tool call`; it was not retried through another channel. This report/final reply is the handback.

## Final suite and verdict

2026-11-10 UTC: SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py' exits 0 on both exports: candidate Ran 1050 tests, OK (skipped=7); merged Ran 1053 tests, OK (skipped=7) (suite-candidate.json/.log, suite-merged.json/.log). merge-tree of current main f980a097bf15d8d1382c039949c6b9aefc5439c8 and the candidate exits 0, tree f9ce811f8bd3b80bd8fbfa4b3e69cf072351ba66; no merge-main repair is needed on these bytes.

REJECTED pending F1 compatibility disposition. All current mechanical acceptance checks pass; the formal verdict holds the unaccepted ordinal-reference compatibility cost. verification.json checks every accepted producer exit and output hash, the unchanged product branch and exported source bytes.
