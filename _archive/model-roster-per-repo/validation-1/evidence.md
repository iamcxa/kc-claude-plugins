# Independent validation of PR #759

Verdict: **REJECTED** for candidate `a8536dc5239edc3db6c1b76cb3bb7e1ce0433088`, against stacked base `9f065b01f1c6d6561793a168f584075edb85bf1f` (PR #758). No product repair was made. The source implementation passes the model-free checks; the accepted real-use journey remains incomplete.

## Evidence boundary

- The validator used a detached checkout of the exact candidate, then removed it. The Captain script created and removed its own detached checkout.
- FO's `../adoption-trial/question-receipts.jsonl`, `fo-commands.jsonl`, README and saved roster files are **FO-record evidence**. The validator read them and independently replayed the saved data; it did not observe or repeat the human dialog. The original scratch repositories were deleted by FO.
- Live Paseo status independently confirmed Astra/high and Astra/xhigh, the assigned worker roots and auto-review mode. See `runtime.json`. This proves those two runtime settings, not the complete dispatch protocol or a Sol launch.
- `pr759.json` confirms the open Draft, exact head, stacked base and five successful hosted checks. `pr674.json` confirms the older native-transport draft remains open at `0ced054c1c927c5836c4e28a7f62d02f254c979f`. FO retains deferred-scope closure authority.
- RoboRev clean `roborev:1348` is FO-supplied in the dispatch, not a validator rerun. No model agents, PR comments, reviews, readiness changes or product pushes were created by this validator.

## Acceptance criteria and counterexamples

| Criterion | Result and primary evidence | Counterexample and limit |
| --- | --- | --- |
| AC-1 explicit shared adoption | PARTIAL: seven FO question dialogs record Accept, Customize and three stage answers, Cancel and dismissal; saved accept/customize bytes replay all four stage/repair results correctly (`fo-data-replay.json`). FO records unchanged cancel/dismissal manifests. | Removing either eligibility instruction is detected by its existing pin. This is an instruction test, not the owed live consent/sync falsifier. A real sync over a committed choice was explicitly not run. No Codex-host dialog parity claimed. |
| AC-2 resolver and absence | PASS: 100 retained subprocess commands exercise explicit roots, state-versus-code distinction, linked checkouts, repeatability, precise invalid-data errors, committed edit/deletion and read-only behavior. | Wrong-cwd, fabricated-absence and write-on-read resolver mutations each produce an assertion failure. See `mutations.json` and `resolver-commands.jsonl`. |
| AC-3 historical stage replay | PASS: real CLI returns Astra/high, Sol/high, Astra/high and implementation for repair. Rehashed all three source dispatches; digests exactly match the accepted criterion. | Swapped-stage selection and removed effort each fail the ideation historical assertion. Fixture replay is not child-runtime evidence. |
| AC-4 real dispatch and continuation | NOT MET: Astra/high and Astra/xhigh reached real workers; source-root binding and immediate build/spawn order fail the required evidence shape. Sol and both continuation cases were not run. | The retained real command itself contains the post-build check forbidden by AC-4. The validator also resolved the actual code root and observed `readme-default`, unlike the scratch-source Roster header. No agent was started to manufacture further evidence. |
| AC-5 family evidence and records | COMPUTATION PASS; REAL RECORD FAIL: all three actual author records replay as Sol/high and yield `same-family: openai` for both saved validator rosters. Legacy, augmented, missing and unknown author controls run. | Hiding the warning and refusing same-family each fail. Existing record checks remain green on the actual record while its author references and family are missing; their green result does not prove roster consumption. |
| AC-6 scope, reading and regressions | Model-free checks PASS: exact eight-file allowlist; no CI, role, law/checker, native adapter or private-store change. All 26 CI command entries exit 0; existing fixture-dependent skips are reported below. | Unknown role/private-layer schema inputs fail; write-on-read and prerequisite-removal mutations fail. Scope and preserved role bytes were independently compared. Human output is counted only from retained FO receipts, not assumed host behavior. |

Historical source digests: ideation `18eeff12f0ad4f662ce5889bc6e78bf36223cf4b9282beed86506245bbd5d331`; implementation `e65a8911f7d741ba78aa6b98bdae59de3d9753b7c72d95ec31ae42e73b04a833`; validation `2f33b40eba6c9a881e9070199857843351c746e8408ba37195b630eb169d0bff`.

## Findings and workflow disposition

- **F1 Material — lost family evidence.** Released user/normal workflow: FO preparing validation of the actual Sol-authored candidate. Observable harm: the real dispatch record omits the authors and same-family information the reviewer must see. Boundary: `value-ac[AC-5]` requires source references and the informational flag in the record and existing report/gate. Trigger: `../dispatch/validation-1.md` has a Roster tuple but no authors/family; FO acknowledges its dispatch script dropped them; the validator's replay with all three contributing records yields `same-family: openai`. This is a real record/integration failure; it is not a request for a new refusal or law.
- **F2 Needs decision — repository-bound dispatch proof absent.** FO's real call resolves `/tmp/roster-real-customize`, then launches in the task's different code worktree. Resolving that actual worktree at the exact candidate returns `source=readme-default, tuple=null`. These calls prove transport of a chosen tuple, but do not prove AC-4's bound repository choice. FO must provide compliant evidence or return an amendment to the Captain; no resolver defect is asserted.
- **F3 Needs decision — immediate-spawn evidence fails its counterexample.** The 02:33:03 retained `spawnv` command runs `grep -q FAIL /tmp/v-$v.out` after the build wrapper returns and before `paseo agent run`. AC-4 explicitly disallows a post-build check. Both child metadata receipts remain valid setting evidence; the ordered launch acceptance is not passed.
- **F4 Needs decision — Sol/high real launch missing.** AC-4 requires both recommended models; only Astra was launched through this resolver. FO explicitly confirms Sol/high was not run.
- **F5 Needs decision — unchanged continuation missing.** No real same-tuple continuation was exercised, so AC-4's reuse behavior is unverified.
- **F6 Needs decision — changed continuation missing.** No real changed-tuple continuation returned for a fresh handoff, so AC-4's failure/recovery boundary is unverified.
- **F7 Needs decision — sync preservation missing.** FO explicitly records no real sync over a committed roster. AC-1 requires startup/sync to preserve that choice, and its overwrite falsifier was not exercised. Read-only resolver repeatability cannot substitute for that host journey.

F2–F7 are incomplete/invalid acceptance evidence, not newly demonstrated package-code defects. They cannot be silently waived by the validator. The implementation's delegated/not-run labels were accurate; later FO evidence fills only the bounded portions above. Goal sufficiency is not established at Pilot depth. Each retained product surface has a necessary role: recommendation, adoption entry, stage entry, Paseo handoff, resolver, behavior tests, runtime instructions or required decision record; no extraneous surface was found.

## Checks, reading and cost

All 26 command entries and their log paths are in `final-regressions.json`. Seven individual tests remain skipped by their existing conditions: four design-history/corpus fixtures, one release-acceptance Node/module fixture, one dispatch-record real-builder fixture lacking SD_PLUGIN_ROOT in that unit invocation, and one historical obligation corpus. The separately run full SD suite exercises real Spacedock 0.27.2 dispatch using activated plugin root 0.27.3, without spawning models.

Six initial suites failed because the validator initially placed disposable no-Git fixtures beneath a Git checkout. Each unchanged suite passed when rerun with `TMPDIR=/tmp`; the original failures and corrected logs are retained. The first mutation harness attempt lacked the scripts import path; that harness setup error was corrected before the nine reported assertion/pin results. Neither setup error was treated as a product defect.

- Assigned package ADR lint, both `--since BASE` and `--since BASE --require 0047`: exit 0, `45 ADR file(s) checked, 0 legacy`.
- Number guard: exit 0, `PASS: no findings`; adopted trunk remains `a6612948936a`, migration check skipped because no migrations-path exists. This does not replace the stacked delivery base.
- Added comments: `318` code lines, `3` comment lines, `0.9%` against `5%`; read and acceptable. Design check: presentable, with scope replay not run because this task is in validation. Dispatch folder: seven complete records; names check exit 0 despite F1.
- Document impact: ADR 0047 and adoption reference updated; package README unaffected because its generic suite/handoff claims remain true; root learning.md unaffected because historical learning records are not changed. The single authority for new runtime behavior is the linked model-roster reference. No retained diagram changed.
- Existing ADRs 0020, 0035, 0037 and 0042 are byte-preserved; role declarations, special-role instructions, CI YAML/triggers, record/law scripts and startup entry remain unchanged (`scope.json`, `prior-decisions.json`).
- Independent count (`words.json`): startup 9710; idle/open 1821; merged/archive 328; merge ask 2258; workflow 5781, all unchanged. Dispatch static corpus 2444 → 3154 configured / 3110 absent; adoption 2182 → 2914 including the 634-word runtime reference and 44-word settings. This is word accounting, not token usage.
- Fresh CLI outputs (`resolver-output-ledger.json`): repository output 1–2 words / 292–713 bytes, absence 1 word / 164 bytes, errors 4–14 words / 41–143 bytes. Seven serialized FO question payloads total 289 words; seven timed answer/error strings total 246 words, with the duplicated untimed dismissal omitted. Per-payload counts and raw FO receipts remain available; unretained host output and upstream context are unmeasured.
- One sequential local wall-time sample: baseline SD suite 35.37 s, candidate SD suite 42.26 s, delta +6.89 s. Other model-free regression activity was present, so this is a noisy local observation, not an isolated performance claim or billed CI estimate. CI cost per PR was **not measured**. CI configuration and model calls are unchanged.

## Captain acceptance script

Prerequisites: this local repository contains the two pinned commits; Python 3, Git, Spacedock 0.27.2 at the exact path below, the activated Spacedock 0.27.3 plugin, and the assigned dev2 0.33.1 package are installed. These machine-specific paths are explicit; no secrets or provider calls are used.

Run the following six steps together in a fresh Bash shell. The validator saved exactly this body as `acceptance.sh` and ran `bash --noprofile --norc acceptance.sh`; exit 0. It took under five minutes. This script verifies the observable CLI/package boundary only; it does not pass AC-1's human/sync journey, AC-4's live calls, or repair F1.

```bash
#!/bin/bash
set -euo pipefail
# 1. Create an isolated checkout and verify the exact candidate.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo'
ROSTER_HEAD='a8536dc5239edc3db6c1b76cb3bb7e1ce0433088'
ROSTER_BASE='9f065b01f1c6d6561793a168f584075edb85bf1f'
ROSTER_CHECK="$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance.XXXXXX")/candidate"
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
cd "$ROSTER_CHECK"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
# 2. Check the shipped package and its fixed workflow reading budget.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Exercise the real resolver and existing dispatch transport without models.
TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock time -p python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep
# 4. Check the added decision record against the stacked base.
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since "$ROSTER_BASE" --require 0047
# 5. Observe absence at this exact code checkout.
python3 -B kc-dev-flow-2/scripts/model_roster.py resolve --code-root "$ROSTER_CHECK" --stage validation
# 6. Confirm no product edits and remove only this disposable checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
cd /tmp
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
rmdir "${ROSTER_CHECK%/candidate}"
```

Expected and observed, in order (`acceptance.log` retains full output):

1. Detached HEAD `a8536dc52`; full-SHA assertion passed.
2. `PASS: basic frontmatter, declared profile routes, role bindings and package script paths`; `5781 of 5781 words`. Host behavior explicitly not checked by lint.
3. `PASS: roster subprocess replay...`, then all existing real-SD dispatch checks passed. `real 42.26`; no model worker execution, human gate or remote merge is claimed.
4. `45 ADR file(s) checked, 0 legacy`.
5. `{"commit":"a8536dc5239edc3db6c1b76cb3bb7e1ce0433088","digest":null,"path":".dev2/model-roster.json","role":"validation","source":"readme-default","tuple":null}`.
6. Clean status assertion and checkout removal exited 0, silently.

Raw subprocess fixture commands are retained in `resolver-commands.jsonl`; model-free test logs and the FO data replay are separate from runtime receipts. All candidate/head claims refer to the original product SHA above, not the later state-report commit.
