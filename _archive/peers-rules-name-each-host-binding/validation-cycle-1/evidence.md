# Cycle 1 independent revalidation

Candidate: dc3916fbb4ce9655dc37c5e4185653694e029de4, PR #730.
Base: c70f1b22cb1e4a66fd15c617647c778d54c59ec9.
Prior candidate: bff1d8147b626ae91c6ca431f7dde459a63f254d.
Detached validation checkout: /tmp/peers-validation-730-cycle1.
Verdict: **PASSED within the accepted prose/manual-replay and local-check boundary.**
Prior F1 (redundant dependency automation) is resolved. No product-code repair finding remains.

## Repair proof

The candidate changes only lint-skills.py and test_lint_skills.py since the prior head: 23 deleted lines, zero added lines.
The dependency helper, its call, and its two dedicated tests are absent. Every other file is unchanged.
The tier-enforcement source bytes match the base exactly after excluding the retained document-presence block; no optional-extension tier behavior was changed.
The document-presence guard and its remaining test still detect a missing EXTENSION.md.
The installation refusal remains an FO-followed instruction; this repair does not introduce automated adopter-list enforcement.

repair-proof.txt records executed controls: default template passes; a template listing optional paseo is refused; three adopted README lists do not affect the package-template result; default/custom/opt-in lists survive git merge-file byte-for-byte.
Removing the retained document guard makes its named test fail (exit 1). Marking paseo required makes the tier check refuse the unchanged default.
This closes F1's necessity gap: the unused dependency mechanism is gone and the surviving presence guard catches an actual missing-document case.

## Acceptance criteria and falsifiers

| Criterion | Fresh evidence | Executed falsifier | Limit |
| --- | --- | --- | --- |
| AC-1: transport routing | Re-ran the existing 37-trace auditor and compared unchanged policy bytes with the previously inspected host scenarios. Native Claude retains probing; incoming Paseo answers do not load unlisted paseo for either model provider; unsupported and ambiguous transport fall back. | Vendor-selected route, unlisted extension read, missing Claude probe/opening rejected. | Manually selected event traces, not a policy executor. |
| AC-2: bounded sends | Fake clock at 0, 299, 300, 301; busy new questions do not send, 299 idle can send, expiry/no independent work/still-busy recheck stop waiting. Explicit reply steer/no callback, new-ask steer/callback, worker exception and unknown/racy interrupt fallback remain. Current Paseo CLI help/tool schema match. | Missing behavior, explicit interrupt, busy new send, polling, reset deadline, expired send, blocked worker, queue-as-answer and duplicate action/send rejected. | No live exchange or prevention of host interruption proved. |
| AC-3: records and authority | All eight rows in each interview round remain in the replay; taskless notices use notes, bound briefings stay unchanged, existing backlog is reused, original-unavailable authority remains unverified. Real SD discovery/pr_watch again omit a task-shaped .notes entry. | Duplicate task, lost record, briefing mutation and relayed-authority acceptance rejected. | Prose compliance is not mechanically enforced; notes do not authenticate Captain words. |
| AC-7: optional activation | Default [learn, peers], unchanged installation policy, three preserved adopter lists and package-template controls. | Mandatory-paseo tier mutant refused; unlisted-read trace rejected. | Optional activation and refusal of paseo without peers are installation instructions, not an adopter config validator. Removed helper tests are intentionally not rerun. |
| AC-6: complete reading bundles | Fresh output/manifest and independent recount: peers 805, paseo 290, upstream skill 1380, proactive 2475, inbound/gate 2185. Unaffected moments 5631/1045/1318/3276/742 unchanged; native/unsupported/task-opening 805, warm exchange and withdrawn source repair 0. | Omitting upstream or inbound bundle is rejected by the independent sum check; missing document guard fails its test. | Counts measure words, not attention; current identical SD passages charged to both arms. |

replay.txt: 37 manual traces, 17 bad-event mutants rejected. As in the first validation, the scratch auditor does not consume the policy text, so its failures prove audit predicates only. Earlier base/initial/final model-reader transcripts were inspected in the first validation and remain applicable to byte-identical policy; they were not rerun or recast as fresh live-agent evidence. AC-4 and source migration remain withdrawn by amendment 1.

## Regression and retained checks

All 25 remaining test files ran on this head and exited 0. Their manifests record commands, elapsed times and raw logs.
876 unittest cases: **875 passed, 1 skipped**, plus SD dispatch and observer-recovery assertion runners.
The skipped release-acceptance integration reports: “node or journey-accept.mjs missing, or its yaml dependency is not installed.” The test does not distinguish which dependency failed; this unchanged optional seam is not claimed verified.
Lint suite now has 44 cases. Whole-package lint prints 5421/5421 workflow words.
ADR lint with --since base --require 0038: 37 records, 0 legacy, exit 0.
Number guards: PASS; migration guard skipped because this workflow/task has no migration path.
Comment ratio: 6 added code lines, 0 comment lines, 0%; the maximum is **not enforced** below 20 code lines.
Dispatch records: 7 complete. Design surfaces presentable; scope checking is not applicable at validation.
doc_impact for the repair lists ADR 0020, package README, maintain-flow and learning.md; all four are unaffected for the implementation's recorded reasons: budget, template-tier contract, maintenance/replay instructions and learned practice are unchanged.
No CI workflow or trigger changed; cost per PR not measured.

## Review/provider evidence and finding

FO supplied clean RoboRev evidence roborev:1230 and CI 5/5 on dc3916fb, dated 2026-10-27. These are attributed receipts, not checks rerun by the validator.
The first API read this cycle confirmed the exact head, OPEN/Draft state and a stale PR body. A final API re-read failed with “error connecting to api.github.com”; no retry or remote mutation followed.
The earlier successful body still said “Add extension dependency/document checks”, “46 lint tests”, 0/25 comments and roborev:1229. Those describe the previous candidate.

- F2 Polish: refresh the PR description for the repaired candidate. User/normal workflow: a reviewer reads PR #730. Observable issue: the successful API snapshot describes a removed dependency guard and old test/comment/review evidence. Affected protected criterion: none; this is review clarity, not a product regression. Trigger: head dc3916fb alongside those old claims. FO should replace them with the current implementation/validation results and limits before presenting delivery; current remote text could not be reverified after the API failure.

Sufficiency: the accepted local/paper policy boundary remains supported at the new head.
Necessity: removing the unused dependency mechanism resolves the earlier objection; retained policy, adoption text, decision record and document guard each map to accepted outcomes or observed negative cases.
No new Material, Deferred risk or Needs decision finding was established.

## Five-step acceptance

Run the complete script in fresh Bash:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/peers-rules-name-each-host-binding/validation-cycle-1/acceptance.sh
```

The script contains five exact steps and expected outputs. It ran unchanged, exit 0; full observed output is acceptance-output.txt.
1. Create a detached checkout and print dc3916fbb4ce9655dc37c5e4185653694e029de4.
2. Package lint PASS and 44 lint tests OK.
3. 37 ADR file(s) checked, 0 legacy.
4. Helper/call/two tests absent; original tier bytes and policy unchanged.
5. 805/290/1380 words; proactive 2475, inbound 2185; no candidate diff.
The script removes its own checkout. Installed package/tool paths are declared prerequisites. No UI changed.
It does not prove live delivery, adopted workflow enforcement, human authority, hosted CI, merge permission or release/adoption completion.

This evidence supersedes the previous candidate's validation conclusion. The previous files remain historical; the new head and current checks above govern.
