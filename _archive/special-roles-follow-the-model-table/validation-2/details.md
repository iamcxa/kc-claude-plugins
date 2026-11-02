# Validation of PR #764 at 8eed70b2

Verdict: **PASSED for this task's pre-merge scope**, candidate `8eed70b260346811a1f2aa035ca1354a2d735576`. No new Material, Deferred risk, Polish or Needs decision findings. This is a bounded merge recheck, as the dispatch's second checklist item permits; carried evidence below is not represented as freshly executed native work.

The merge parents are the previously validated `562b1a87198d97bb2ae1d87b72884e390b20e146` and PR #763 repair `fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf`. The complete diff from the former is byte-for-byte the same as PR #763's diff from `c129cb215c2630d08853eeffae0fd5a2ee7e40c6`: only dispatch_records.py and test_dispatch_records.py changed. [carry-forward-inputs.json](carry-forward-inputs.json) identifies 159 unchanged package, decision-record, CI and learning inputs by Git blob; [merge-only.diff](merge-only.diff) contains the two-file delta. All four role definitions, model table, role trigger, workflow, lint, POC derivation and release-walk inputs remain unchanged.

The dispatch asks for origin/main: it resolved to `146727ded0d4ce8014ea0b41a45dc3409d6b269b` and is pinned in the acceptance and required ADR commands. Task-only number/comment/document checks use the actual stacked base `fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf`, excluding the separately owned ADR 0048. This does not certify the sibling's full outcome.

## Checks and criterion decisions

| Criterion | This recheck | Falsifier and evidence boundary |
| --- | --- | --- |
| AC-1 | 27 role tests pass, including the specified pilot/prod model cases. | Removing Astra gives 2 failures; restoring leading-word recognition gives 4. Fresh mutation logs. |
| AC-2 | The same suite checks both chief-engineer events, dates and waivers. | Removing the floor gives 4 failures. Fresh. |
| AC-3 | Fresh replay at state `0c56419a56c6c5ff078f17b4e112222ca8c03910`: 184 task files, 0 changed exit results. Real archived peer-policy task without waiver: base 1, candidate 0. | Changing Astra to Sol returns 1. The prior 16 expected wording changes remain supported by unchanged trigger code and the pinned validation-1 replay; no claim of a new full message comparison. |
| AC-4 | Role suite and 248 PR-watch/delivery-gate tests pass, invoking the real script. | Restoring one-family wording gives 6 failures. Fresh. |
| AC-5 | Carry validation-1's four native role runs: engineer/reviewer Opus xhigh; director/observer Sonnet high; no model arguments, zero warnings. Nine original candidate/base/mutant transcript SHA256 hashes independently rechecked. | Carry the reasoning-field mutation: medium and one warning, versus four warnings at base. Agent/package/native probe inputs unchanged. No new native agent launched. |
| AC-6 | Lint and 47 lint tests pass, including changed-cell/effort refusal and seven exact rows. | Removing table comparison gives 1 failure. Carry explicit max/ultra resolver success because model_roster.py and its inputs are unchanged. |
| AC-7 | Fresh lint counts 5781/5781; unchanged budget steps; family phrase counts 1/0; reviewer-record fixture passes. | Fresh controls: removing director yields a missing phrase; restoring all-workers yields count 0. |
| AC-8 | Carry six real stamped dispatch builds: Claude Opus for ideation/validation, Sonnet for implementation; Codex null for each. | Carry both removed-model controls, which return Sonnet/from defaults. Workflow, stage-dispatch fixture and external integration inputs unchanged; these are prior builds, not new builds on this head. |
| AC-9 | Candidate/all, loaded-package/changed and dispatch-requested-package/changed ADR commands pass: 48 files, 0 legacy. ADR 0026 amendment and ADR 0049 remain identical to the approved record. | Fresh empty-folder --require 0049: exit 1, only “required ADR 0049 does not exist”. |
| AC-10 | Required origin/main release-walk diff is empty. PR #764 remains OPEN/Draft; old director seed is still backlog. | Retirement and its after-merge falsifier are not due until merge and remain with FO. No future pass claimed. |

The inherited repair is independently exercised. Listed, quoted, absent, suffix and comment-only extension cases behave as expected. Restoring the old parser produces exactly three assertion failures: two comments containing paseo and the distinct quoted item 'paseo disabled'. The five built-in completion mutations are detected without cached Python files.

Fresh test command results:
- Acceptance: 27 role tests, 3 completion tests (including the five mutations), 47 lint tests, 9 POC derivation tests, lint/ADRs/word count/exact rows/clean checkout all pass.
- `TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py`: 100 tests, 99 pass, 1 existing optional real-builder skip (SPACEDOCK_BIN/SD_PLUGIN_ROOT absent).
- Same environment, `python3 -B kc-dev-flow-2/scripts/test_laws_check.py`: 63 tests, 62 pass, 1 existing DEV2_OBLIGATION_SOURCES corpus skip.
- From kc-dev-flow-2/scripts, same environment, `python3 -B -m unittest test_pr_watch test_delivery_gate`: 248 pass.
- Five model-code mutants: all detected. Workflow/ADR controls pass. Product bytes were never edited.
- No new complete 26-command CI replay: carry validation-1's reconciled 1009-test local evidence where inputs are unchanged, and separately refresh the changed and consuming suites above. Hosted CI is independently green on the new exact head.

## Captain acceptance

The final [acceptance.sh](acceptance.sh) has six steps and declares its prerequisites and limits. Executed exactly as written in a fresh shell:

```bash
/bin/bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence-8eed70b2/acceptance.sh'
```

Exit 0; [acceptance-output.log](acceptance-output.log) is the complete observed output. The initial sandbox attempt could not create shared Git worktree metadata; the authorized native rerun succeeded. The final script additionally includes the repair tests and was rerun unchanged. It has no graphical surface, takes under five minutes, and does not rerun native settings, the historical corpus, all CI commands or post-merge retirement.

The separate dispatch-requested command ran from the detached checkout:

```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 146727ded0d4ce8014ea0b41a45dc3409d6b269b --require 0049
```

Exit 0, 48 ADR files, 0 legacy; [guards.json](guards.json). The loaded Codex package path also passes through the acceptance script. Probe scripts retain their executed absolute paths; recreate the named detached checkout at this exact head to replay them. The Captain script creates/removes its own checkout and is independently runnable from its state-folder copy.

## Limits, documents and remaining ownership

- The installed 0.34.0 dispatch checker still rejects four preserved final-reply records; the candidate checker accepts all six, and the current record passes --names --strict. This known version prerequisite requires the inherited #763 checker, not a repair of historical records.
- Native perTurnEffort proves recorded settings, not reasoning quality. Explicit Agent model arguments can override agent files. Codex special roles still receive settings manually; stage-worker effort remains the separately owned follow-up. Astra/Fable equivalence and stage costs are unmeasured.
- The previous RoboRev 1400 default-roster discrepancy remains owned by PR #765. Its latest observed head is `3c49c24a3eba3d90093f330c051b682a3335ae23`, OPEN/Draft; its prior validation rejected the old head. No sibling acceptance, clean integrated review, release or merge is claimed.
- PR #763's repair has a scoped PASSED report with its existing compatibility/deferred findings. Only its changed extension-parser behavior is re-judged here; no new native completion transport claim.
- Hosted observation saved at this recheck: PR #764 OPEN/Draft at the exact candidate, all five checks SUCCESS; #763 OPEN at the parent. Initial sandbox refresh failed; native read-only refresh succeeded. No product push or PR mutation.
- Number guard PASS; comments 2/63 = 3.2%, maximum 5%; design surfaces presentable. New merge delta adds no comments. No CI trigger changed; CI cost per PR unmeasured.
- Document dispositions remain verified: updated ADR 0049 and package README; ADR 0026 amendment retained. Unaffected ADR 0020 (budget unchanged), ADR 0037 (shared-work rule unchanged), adoption.md (integration/proof scope unchanged), maintain-flow/SKILL.md (same commands/budget), learning.md (historical evidence unchanged).
- Goal sufficiency and minimal necessity carry from validation-1 for the 15 task files. The only new two-file delta is necessary to prevent comment text enabling an extension; its old-parser counterexample demonstrates that need.
- FO retains integration/review of #765, the delivery decision, and post-merge seed retirement. Task frontmatter remains unchanged. Detached checkouts are removed before handback; report/evidence are the only committed changes.
