# Independent validation evidence — PR #763

Observed 2026-11-02. Candidate c129cb215c2630d08853eeffae0fd5a2ee7e40c6; base origin/main resolved to 146727ded0d4ce8014ea0b41a45dc3409d6b269b. Product branch spacedock-ensign/worker-completion-reaches-fo-on-paseo was clean before and after; all six changed files are the design's named files. Pilot scope; no product repair, push, PR comment/review request, merge, permission response or new agent.

## Executed checks

These bindings describe the exact execution environment. The detached directory was removed after checks; recreate it with the first command to repeat this sequence.

```bash
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-completion-reaches-fo-on-paseo'
V="$WT/.validation-c129cb21"
PK='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
WF='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2'
TASK="$WF/.spacedock-state/worker-completion-reaches-fo-on-paseo"
BASE=146727ded0d4ce8014ea0b41a45dc3409d6b269b
git -C "$WT" worktree add --detach "$V" c129cb215c2630d08853eeffae0fd5a2ee7e40c6
```

Each check below ran at that detached HEAD, except the minimal acceptance script and final dispatch reproduction, which ran at the same clean candidate in WT.

```bash
cd "$V" && python3 -B kc-dev-flow-2/scripts/lint-skills.py
cd "$V/kc-dev-flow-2/scripts" && PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 python3 -B -m unittest test_dispatch_records
cd "$V" && SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3
cd "$V" && python3 -B "$PK/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0048
cd "$V" && python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since "$BASE" --require 0048
cd "$V" && python3 -B "$PK/scripts/number_guards.py" check --repo "$V" --workflow-dir "$WF" --task "$TASK.md" --base "$BASE"
cd "$V" && python3 -B "$PK/scripts/comment_ratio.py" "$BASE" HEAD --workflow-dir "$WF"
cd "$V" && python3 -B "$PK/scripts/doc_impact.py" "$BASE" HEAD
cd "$V" && python3 -B "$PK/scripts/design_surfaces.py" check "$TASK.md"
cd "$V" && python3 -B "$PK/scripts/dispatch_records.py" "$TASK"
cd "$V" && python3 -B kc-dev-flow-2/scripts/dispatch_records.py "$TASK"
cd "$V" && python3 -B /tmp/impl-worker-completion-proof.py "$V" "$PK"
git -C "$WT" worktree remove "$V"
```

| Check | Observed result and falsifiability |
| --- | --- |
| Skill lint | Exit 0; basic frontmatter/routes/roles/paths pass; workflow 5781 of 5781 words. No claim of host obedience. |
| Dispatch unit suite | Exit 0; 100 tests in 141.826s, no skips. Environment enables the real builder test omitted in the earlier implementation run. |
| Spacedock fixtures | Exit 0; 10 fresh/reused route/stage/host handoffs; both main-line pins fail when reverted individually; actual non-Paseo dispatch contains main. Complete log: sd-dispatch-1.log. No model spawned by this harness. |
| ADR lint, both cache paths | Exit 0; 47 ADR file(s) checked, 0 legacy; --require 0048. |
| Number guards | Exit 0, PASS: no findings; migrations skipped because no migrations-path is declared. |
| Comment ratio | Exit 0; code 75, comments 1, 1.3%, maximum 5%. The sole new comment is the required ADR link; it does not narrate implementation. |
| Document impact | Exit 0; lists ADR 0045 (review), ADR 0048 (updated), learning.md (review). Checked implementation dispositions: ADR 0045's names-only ruling predicate unchanged; learning practices retained; ADR 0048 updated. README and adoption entry now include both providers. No changed retained diagram. |
| Design surfaces | Exit 0, design surfaces presentable; scope check correctly not run outside ideation; task has Surfaces: none. |
| Actual dispatch records | Exit 1 for both script versions: validation-1.md: needs a scope-notes line naming main as the completion recipient. Candidate correctly rejects the paraphrase; installed package predates the new exception. |
| Existing implementation archive proof | Exit 0; 25 tests in 37.021s; four completion mutations rejected with AssertionError and no pyc; extension 820 >819 refused; missing Words label returns 1. Existing proof copied to implementation-proof-1.py for retention, unchanged. |
| Independent recount | Extension 713 ->819; workflow 5781 ->5781; workflow.md, lint-skills.py and test_sd_dispatch.py byte-identical to base. |

## Native record assessment

Primary excerpts: native-record-1.json; existing native-runs/README.md and f33b5aa3.log/e48b1442.log. The new excerpt names source paths, line numbers and timestamps so FO can compare them with its full transcript.

- AC-1 is NOT MET: calls at FO lines 75360–75361 ask Haiku and Sol only to read CLAUDE.md. Both omit workspaceId and any real stage bootstrap. Line 75395 contains the two matched finished notifications with Done replies. Worker logs show no send tool attempt. These demonstrate callback transport, but do not exercise the generated stage completion block (which still says SendMessage) or fetched Signal fact; the candidate's real Claude stage behavior therefore remains unproven. The cheap probes are explicitly disclaimed as stage dispatches in FO's README. Worker bc46043b is a real Codex stage worker but was still running when inspected; this validator's eventual callback cannot prove both models.
- AC-2 is met within FO-record evidence: line 75388 has errored/canceled; line 75402 has finished/no Done; line 75436 has permission-required. FO killed the permission probe, did not grant it. Failed permission attempts are excluded. A finished event on a background-job pause is accurately listed as a limitation; the extension requires report verification and does not treat finish alone as completion.
- AC-5 is met within FO-record evidence: the README's 04:40:24Z summary was written after a failed first shell attempt. The successful command is line 75487, 04:40:35Z, and result 75488, 04:40:47Z. Its next host tool action is create_agent at line 75490, 04:40:51Z, with explicit workspaceId wks_00a7078b0a0e1dc6, mode and notifyOnFinish true. Result 75491 places worker bc46043b-44e9-4677-8b7f-420858e17733 in the assigned worktree. The worker session's first pwd and later git root match; live worktree listing contains one such worktree. The successful retry, not the stale summary timestamp, is the supporting record.
- Native falsifiers were assessed rather than repeated, as the assignment forbids new agents. For AC-1/2 the task's historical command-line arm records main refusal and no finish/permission/cancel callback; this validator did not independently rerun it. AC-5's concrete no-workspaceId results are FO lines 75370–75371: both use /Users/kent/conductor/workspaces/kc-claude-plugins/colombo, not the task worktree. These probes cannot also serve as compliant AC-1 stage spawns.
- Codex FO receiver and cross-host transport were not proven. They are not silently generalized from this Claude FO's same-host evidence. No demonstrated candidate callback loss is reported.

## Dispatch finding reproduction

Candidate checker run on the actual task returns exit 1. A disposable copy of its four dispatch records, checked with --readme pointing to the real workflow README, gives the same failure. Replacing only the current paraphrased completion line with PASEO_COMPLETION_LINE and placing the task's Done line on the following line gives exit 0: `4 dispatch record(s) complete`. The saved record was not edited.

FO can correct its record with the already-approved literal; product code does not need loosening. Protected rule is kc-dev-flow-2/references/sd/workflow.md, Stages, lines 115–120: check saved records before committing/dispatching and hold on failed coverage.

## Hosted and local review limits

```bash
gh pr view 763 --repo iamcxa/kc-claude-plugins --json number,state,isDraft,headRefOid,baseRefName,url,statusCheckRollup,reviewDecision
roborev show --job 1396 --json
```

Live GitHub lookup succeeded: OPEN/DRAFT, main base, exact head; all five checks SUCCESS (unit tests, ADR path, route gate, version parity, GitGuardian). This resolves the implementation worker's earlier network/CI uncertainty. No CI trigger changed; cost per PR was not measured.

Read existing RoboRev job 1396 only; no review agent launched. Job is done, branch matches, git_ref exactly 146727ded0d4ce8014ea0b41a45dc3409d6b269b..c129cb215c2630d08853eeffae0fd5a2ee7e40c6, verdict P, verdict_bool 1, output SEVERITY_THRESHOLD_MET. Its prompt filters to High and Critical findings; that is the scope of its clean result, not proof of zero lower-severity issues. FO transcript line 75473 also records the same evidence identifier.

## Goal sufficiency and minimal necessity

Goal sufficiency is not established until actual stage completion is shown for both providers. The callback, exact-sentence acceptance and workspace route are locally/recordedly supported, with the missing real-stage layer identified rather than repaired by assertion. All six retained files are necessary for the accepted extension boundary, entry wording, checker/falsifiers or required decision record; no broad workflow, host, version or CI change was introduced.

Implementation's local-only and no-native-spawn limits were authorized by its follow-up dispatch. Its prepared PR and delegated review were subsequently supplied by FO and verified here. The 99-tests/one-skip observation was historical; this run with both required environment bindings passes 100 without skips. Candidate and accepted criteria were not changed.
