# Validation 2: merged-head evidence

Verdict: PASSED for b61a708dadf9cbd9ac1e6d727720c67cf9f06076, base origin/main at bfa5354b40ba99e297e7cb2d3e70b41f7d0fece9. This is the amended Pilot instruction change, not a runtime scheduling barrier.
The detached candidate was checked under the assigned worktree in .validation-pr744-round2, remained clean, and was removed after checks. The original branch remains clean at the candidate. No product repair, Git configuration change, PR mutation or code push was made.

## Merge and scope
merge-proof.txt records the two exact parents and equal candidate/first-parent tree IDs. Independent three-way file merging found only lint-skills.py conflicted; merge-conflict.txt shows its single budget-step conflict. The retained resolution is the prior candidate's joint +178 step, with quote/load accounting; +29 is the prior task's share and +149 is this task's share. Compared with main there are exactly five files, 135 insertions and 2 deletions: workflow.md, lint-skills.py, test_poc_readme.py, test_sd_dispatch.py and ADR 0043. No role, ledger, provider, CI, version or gate-command implementation changes.

## Four-step acceptance
Run unchanged in a fresh shell:
```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/batch-reaches-each-gate-together/validation-2-evidence/acceptance.sh
```
The exact four steps are in acceptance.sh. Observed stdout/stderr is in acceptance-output.txt; exit 0.
1. Pin the assigned checkout to b61a708dadf9cbd9ac1e6d727720c67cf9f06076 and run repository lint: expected/observed exact head, PASS and 5754 of 5754 words.
2. Run the declared Codex package's adr_lint.py docs/adr --since bfa5354b40ba99e297e7cb2d3e70b41f7d0fece9 --require 0043: expected/observed 41 ADR files, 0 legacy, exit 0.
3. Run test_poc_readme.py: expected/observed 8 tests, OK; the printed trunk diff belongs to its deliberate drift test.
4. Run actual local test_sd_dispatch.py with /Users/kent/.local/bin/spacedock and the declared 0.27.3 plugin root: expected/observed worker-context invariance, separate decisions, stale-binding refusal and single consumption.
There is no application-screen change. The script proves local instruction transport and gate boundaries; it does not prove a live reviewer, model compliance, hosted Review, full chat, merge, adoption or release.

## Repeated checks and falsifiers
All positive commands in checks.txt exited 0. They were executed with python3 -B in the detached candidate; it began without Python caches. The declared Codex package was /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1.
- Lint: 5754/5754. Lint mutation suite: 45 tests. Delivery gate: 113 tests. Number guard: no findings, base bfa5354b40ba/head b61a708dadf9. Comment ratio: 0/68, 0.0% <= 5%; no newly added comment needs repair.
- Dispatch records: 7 complete; implementation-1, its message, and implementation-2 match accepted criteria and the merge ruling. Design surfaces: presentable.
- AC-2: current-context scenario actions continue authorized repair, hold uncertain membership, preserve unanswered status, and refuse synthetic hold/drop and unrelated joining. recheck.py rejects removal/join mutations; real gate replay covers interrupted one-use consumption. Full FO restart remains simulated.
- AC-4: dispatch-output.txt is the unmodified suite. structured-replay-output.txt and route-commands.jsonl repeat the same fixture with eight checklist/AC reads inserted before presentation. Four prepared/committed bindings retain approve/revise/hold/unanswered; stale binding refuses. The bulk mutation replaced zip(members, ("approve", "revise", "hold")) with four approvals in memory; exit 1 at the unchanged nonapproval assertion because the revise task advanced. bulk-answer-output.txt and bulk-answer-commands.jsonl retain the failure and actual commands.
- AC-5: recheck.py re-reads all four historical exact heads/questions and later #732 inclusion from the declared ledger; barrier gives one four-task sitting, eager-policy mutation four. It rejects omitted members and unrelated joining. Counterfactual only; the cancelled AC-1 fresh replays are replaced by amended AC-8.
- AC-6: workflow 5605→5754 (+149 over main), joint step +178. Startup 6810→6959; open idle 1089→1238; merged idle 1060→1209; archive 333→333; merge sitting 2635→2784. Output words 29/29/0/5/90 unchanged. Missing approval quote, missing loaded moment and unbudgeted word reject. Pilot/POC worker output stays byte-identical; inlining controls reach both. In-memory early-presentation wording fails the existing POC test (early-ask-output.txt, exit 1).
- AC-7: five-file-set assertion passes; adding a director file to that set rejects. Existing role inputs, decline/release-walk authority, ledger, provider and gate commands remain unchanged. The committed Mermaid source equals the prior rendered source byte-for-byte; its saved flow.png was visually inspected again for barrier, reviewer-before-binding, exception/split, stale stop and separate outcomes. Rendering itself is reused from validation 1, not freshly rerun; no diagram or code-tree bytes changed.
- AC-8: recheck.py independently verifies all ten committed backlog/ideation artifact hashes, ancestor snapshots, joint quoted questions/answers and sufficient latest reports: five backlog approvals, four ideation approvals and one hold. Changed artifacts and omitted member reject. Full chat and no-intervening-decision-ask remain explicitly FO-attested, as the criterion permits.
- AC-9: scenario-replay.md captures this validator's nine input/action variants and unsent neutral prompts. Anchored inputs, silent family substitution, invented director access and reviewer approval authority are refused. No-request adds no gate. This round is current-context tabletop evidence, not a fresh-model or native reviewer execution.

## Affected documents
The six doc_impact.py results were reviewed against the current diff:
- docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md — unaffected: exact equality, actual quoted authority and load accounting retained.
- docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md — unaffected: Team and worker context unchanged.
- kc-dev-flow-2/README.md — unaffected: profile routes, commands and bounded local-proof claims remain true.
- kc-dev-flow-2/references/sd/adoption.md — unaffected: manual adoption/derivation and worker-context selection retained.
- kc-dev-flow-2/skills/maintain-flow/SKILL.md — unaffected: budget and replay duties retained; the Captain's task-specific amendment replaces the fresh batch-7 replays.
- learning.md — unaffected: historical evidence retained; complete lifecycle differential repeated.

## Limits and disposition
- FO supplied PR #744 base main, merge state CLEAN, all five hosted checks passing and RoboRev roborev:1307 clean on this exact head. These were not independently queried; no GitHub API access or RoboRev run is claimed. The prior head's validation passed, and equality of trees was independently verified.
- Native optional-reviewer execution is still unverified. Amended AC-9 requests scenario variants; no live pass was requested. Preserve F1 Deferred risk: released workflow is optional advice on a complete process batch; possible harm is anchored/wrong-family advice or mistaken approval; boundary value-ac[AC-9] requires neutral eligible advice; trigger evidence is passing scenarios without an actual invocation, so harm is not observed. A supported live invocation violating these boundaries makes it Material.
- Full FO restart is scenario-level; real command recovery checks only separate persistent records, stale refusal and one-use consumption. Batch-9 full-chat/no-early-ask claims remain FO attestations.
- Current remote overlap is FO-sourced. The latest supplied provider result is CLEAN on main; locally the exact five-file set and number guard pass. FO retains final delivery reconciliation.
- Actual CLI reports 0.27.2 with skill/mod package 0.27.3. No hosted Review, multipart-answer, deployment or human-capture guarantee.
- CI cost per PR was not measured; CI triggers and workflows are unchanged.
- A read-only git --remerge-diff attempt could not create its temporary object directory under the sandbox. Independent git merge-file three-way reconstruction then proved the sole content conflict without changing repository configuration or candidate bytes. Process listing was unavailable and was unnecessary; all test process handles were observed complete.

## Sufficiency and necessity
The named-cohort barrier fills the gap in existing stage-only hints without new runtime storage. The budget and ADR are required lifecycle obligations; the two tests protect derived contexts and separate decision authority. No additional store, role or provider surface was retained. No Material, Polish or Needs decision finding; the existing Deferred risk remains. FO owns gate presentation and delivery.
