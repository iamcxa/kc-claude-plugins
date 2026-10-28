# Independent validation evidence

Candidate: e4bd4d06a1538ed166205609002e5eef1ebf0983 (PR 744).
Stacked base: ea84b08d4c726e33460609b2247599afb2d54c2b (PR 743).
Date: 2026-10-28. Code was checked out detached in the assigned worktree's .validation-pr744 directory; candidate bytes were preserved. State evidence is separate from code.
Dependencies: Python 3, git, the declared Codex kc-dev-flow-2 0.32.1 package, /Users/kent/.local/bin/spacedock (reports 0.27.2), and the Spacedock 0.27.3 skill/mod package. This is the actual tested combination, not a claim that the CLI is 0.27.3.

## Acceptance script

Run exactly:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/batch-reaches-each-gate-together/validation-evidence/acceptance.sh
```

The script contains four steps with exact commands, checkout/install paths and an exact-head refusal. It was run unchanged in a fresh Bash shell and exited 0. Full stdout/stderr is in acceptance-output.txt.

1. Verify the pinned checkout and lint: expected head e4bd4d06a1538ed166205609002e5eef1ebf0983, PASS, and 5754 of 5754 words.
2. Lint architecture decisions against the stacked base, requiring 0043: expected “41 ADR file(s) checked, 0 legacy”, exit 0.
3. Derive the proof-of-concept workflow: expected 8 tests, OK, and no ideation. The printed trunk next/main diff is its intentional drift test, not a candidate failure.
4. Exercise local dispatch/gate commands: expected PASS lines for worker-context invariance and distinct approve/revise/hold/unanswered outcomes, with stale-binding refusal and no duplicate consumption.

There is no user-visible application screen. This script exercises local instruction transport and gate authority. It does not prove model obedience, a live optional reviewer, full chat history, hosted Review, deployment, merge or adoption.

## Additional commands independently run

All commands ran from the detached candidate, with Python -B. Package commands used /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1, never a different install. All listed positive checks exited 0.

| Command | Observed result / claim and falsifier |
| --- | --- |
| python3 -B kc-dev-flow-2/scripts/test_lint_skills.py | 45 tests pass; removes quotes/loaded moments or changes budget arithmetic and the corresponding negative tests reject. |
| python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py | 113 tests pass; holds draft, wrong head, inadequate question/review and other delivery conditions. |
| python3 -B PACKAGE/scripts/number_guards.py check --workflow-dir WORKFLOW --task TASK | PASS: no findings; no migrations-path; locally known trunk e57feb6eec95, head e4bd4d06a153. This checker deliberately uses configured trunk, while the review diff/ADR lint use the stacked base. No fresh remote fetch is claimed. |
| python3 -B PACKAGE/scripts/comment_ratio.py ea84b08d4c726e33460609b2247599afb2d54c2b HEAD --workflow-dir WORKFLOW | 68 code lines, zero added comments, 0.0%, maximum 5% met. |
| python3 -B PACKAGE/scripts/dispatch_records.py TASK_FOLDER | 5 dispatch records complete; both implementation records read and mapped to accepted criteria/amendment. |
| python3 -B PACKAGE/scripts/design_surfaces.py check TASK | design surfaces presentable; seed scope check correctly not run at validation. |
| python3 -B PACKAGE/scripts/doc_impact.py ea84b08d4c726e33460609b2247599afb2d54c2b HEAD | Six affected documents, each accounted for below. |
| python3 -B recheck.py CODE STATE PACKAGE SD | Re-executes existing lifecycle/ledger fixtures; output in recheck-output.txt, positive claims and negative controls. |

For the table, WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2, TASK=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/batch-reaches-each-gate-together.md, TASK_FOLDER=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/batch-reaches-each-gate-together, CODE is a clean checkout at the candidate, STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state, PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1, SD=/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3. Replace table placeholders with these named paths; the acceptance script itself needs no replacements.

## Direct controls and evidence

- AC-2 and AC-4: the existing real-command suite prepares and commits four independent briefing bindings, maps approval/revision/hold/no-answer separately, rejects nonapproval consumption, rejects a changed binding and consumes the restored approval once. In the throwaway mutation, all four decisions are copied to approve. The second task then advances incorrectly, causing the existing nonapproval assertion to fail (exit 1). bulk-answer-output.txt captures that failure; bulk-answer-commands.jsonl contains exact commands and output. Eight structured checklist/AC reads (two per task) all exited 0 before the synthetic presentation.
- AC-5: the declared package's decision ledger re-read all four historical exact heads/questions, including the later PR 732 incorporation. A four-member barrier emits one sitting; eager policy emits four; membership omission/unrelated joining are rejected. This remains a counterfactual using recorded answer times as availability proxies, not observed completion time or a runtime scheduler.
- AC-6: lifecycle counts independently reproduce startup 6810→6959, idle open 1089→1238, idle merged 1060→1209, archive 333→333, merge sitting 2635→2784; fixture outputs remain 29/29/0/5/90 words. The instruction paths and fixture implementation other than workflow.md are byte-unchanged by the five-file diff. Worker definitions are byte-invariant on Pilot/POC, and intentional inlining reaches both. Missing quoted approval, missing load moment, and an omitted budget word reject. In-memory replacement of “present the batch in one sitting” with “present each ready task immediately” fails the existing test_poc_readme assertion.
- AC-7: the diff contains exactly the five authorized files. A changed director file is rejected by that scope check; this detects scope drift, not model behavior. Roles, pr_watch, decision_ledger, upstream commands, manifests and CI are byte-unchanged. No added comments require repair. Mermaid CLI 11.17.0 rendered flow.mmd to flow.png; visually inspected the all-members barrier, exception/split, review-before-binding, stale stop and separate outcomes. The local cached renderer initially hit the sandbox browser-launch restriction; the approved renderer retry passed. The image/source are retained so the cache is not an artifact dependency.
- AC-8: independently verified all ten backlog/ideation bindings against committed raw artifact hashes, ancestor history, the joint quoted questions/answers and the latest ideation report in each bound artifact. Five backlog approvals; four ideation approvals and one hold. Changed artifact bytes and an omitted member reject. Adjacent timestamps do not establish a sitting; the joint quote is the evidence. Full chat and absence of intervening ordinary asks remain FO-attested as the replacement criterion expressly allows.
- AC-9: fresh-reader scenario inputs/actions are retained separately. They exercise requested/no-request advice, neutrality, family mismatch, unsupported director access and advisory authority; these are simulated decisions, not actual reviewer launches.

## Amendment, budget and necessity

AC-1 and AC-3 are withdrawn under amendment 1; AC-8 and AC-9 replace them with fresh IDs. AC-5's reference to the withdrawn AC-1 is read with the expressly substituted batch-9 live sitting, not as a second requirement to run the three cancelled model replays. The fifth restating paragraph and the new director pass are absent from code. The joint gate question at cdbd5e8f36f3181bbd41d22135dc65b9909bdb38 explicitly accepts about 180 workflow words with the preceding task. The exact total is 29 + 149 = 178; the budget uses one step, not two duplicate raises.

The 149-word rule supplies a named-cohort barrier that the unchanged stage-only sitting hint lacks. The budget edit is required by the equality invariant; ADR 0043 is required by the Captain's amendment and records the supersession of ADR 0028's as-ready policy. The two test changes protect derived profile/context behavior and distinct gate authority. These five surfaces map to accepted criteria or lifecycle obligations; no new membership store, ledger counter, role or provider operation is introduced.

## Affected document judgments

- docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md — unaffected: exact equality, quoted authority and load accounting are retained.
- docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md — unaffected: Team and worker context are byte-unchanged.
- kc-dev-flow-2/README.md — unaffected: advertised commands, profile routes and bounded local-proof claims remain true.
- kc-dev-flow-2/references/sd/adoption.md — unaffected: derivation, separate profiles, manual adoption and worker-context selection remain true.
- kc-dev-flow-2/skills/maintain-flow/SKILL.md — unaffected: budget and replay duties remain; cancelled fresh batch-7 runs follow the Captain's specific amendment.
- learning.md — unaffected: historical evidence is preserved; complete lifecycle differential was applied.

## Implementation limits judged

- Draft PR creation, RoboRev and hosted checks were delegated: resolved only by the dispatch's FO-supplied evidence for PR 744 at this exact head (RoboRev 1298 clean; five checks pass). The validator did not query GitHub, run RoboRev, or claim independent provider verification.
- The implementation's optional reviewer templates did not execute a reviewer. The fresh-reader exercise strengthens scenario evidence; amended AC-9 does not demand a live reviewer launch. No cross-provider execution guarantee is inferred.
- Its restart scenario alone did not prove runtime recovery. The independently rerun existing local command test proves single consumption and separate durable states; full FO restart behavior remains simulated.
- The batch-9 chat presentation and no-between-asks statement remain attestations, allowed explicitly by AC-8; committed quotes/hashes and sufficient latest reports are verified independently.
- Open-PR overlap uses the FO's dated follow-up: PR 743 is the only identified shared workflow/budget change. Local five-file diff and ADR guard pass; current remote overlap is not independently known, and FO must recheck at delivery if other work changes.
- CLI 0.27.2 with 0.27.3 skill/mod package is the actual local test surface. Hosted Review, multipart answers, human decision capture and deployed behavior are out of this task's delivered scope.
- CI cost per PR was not measured; no CI trigger or workflow changed.

