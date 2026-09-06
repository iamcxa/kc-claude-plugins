# batch e56e9f09873c — the four ship-flow stations (supersedes batch-3f3354ec6652)

Receipt re-cut after the Captain read the four Briefs and changed DEV-104 (open-pr + disposition scripts; skill runs in the FO session), DEV-105 (writes this Milestone's CLI flow; shape chosen by flow-file presence), DEV-107 (debrief minimum fields; appends flow steps). DEV-106 unchanged by the Captain's choice. Approval re-bound to the new receipt with the same quote.

The first cut's two layer-1 workers hit the shared session limit before any push and were archived; nothing of theirs is reused.

## Decisions made under `defaults` (append as they happen)

- 2026-09-06T01:35Z — quota pause (S17/S18) on the first cut; carried here: dispatch waits for the 04:20Z reset.

- 2026-09-06T02:06:49Z — **routing: Captain directed local subagents for layer 1** ("如果有可以在派 subagent 直接做的，應該可以本地先派以便靈活調度"). DEV-104 and DEV-105 run as Sonnet subagents in isolated worktrees from the same Briefs; same Evidence contract, same accept station. Cloud dispatch for these two is cancelled; the 04:20Z timer now only re-checks. Dispatch-to-Evidence minutes recorded for DEV-110.
- 2026-09-06T02:23:34Z — **layer 1 accepted.** DEV-104 (`3a733578`) and DEV-105 (`470b3e41`) both ACCEPT at the accept station on main, SHAs equal remote heads, S29 guard clean; each ran its own block through the station (SELF_CHECK). Subagent dispatch-to-Evidence: 14 min each (167K / 180K tokens) versus ~5 min of workspace overhead before a cloud worker starts — recorded for DEV-110.
- 2026-09-06T02:23:34Z — **PRs opened with DEV-104's own `open-pr.sh`** from its candidate (dogfood of the station under build): DEV-104 → #378, DEV-105 → #379. Default `pr_creation: batch_approve_draft`.
- 2026-09-06T02:23:34Z — **DEV-106 base = main**, not a merge of the two layer-1 candidates: its Brief consumes batch records, not their code. DEV-107 will stack on DEV-105's candidate because it appends to that flow file.
- 2026-09-06T02:35:17Z — **review station on #378 (DEV-104): disposition `block`.** kc-pr-review run in the FO session (Lite + ToB, 4 agents, ~357K tokens), nothing posted; findings written to `review/findings-378.json`, dispositioned by DEV-104's own `disposition.py`: two `security` findings (fork-syntax BRANCH unbound to CANDIDATE_SHA; case-sensitive category match fails open) → `block` under `defaults.findings_outside_brief`. Default applied: a blocked candidate gets a repair round (1 of 2) with the blocking findings as the fix Brief; the six listed findings go to the UAT document. No Captain question.

- 2026-09-06T02:40:21Z — **Correction.** The previous commit's line 'DEV-106 accepted, PR opened' was written from an empty block: the FO's extractor read the subagent's JSONL transcript instead of its reply, so the station ran on nothing (exit 2) and `open-pr.sh` was invoked on a missing file (no PR was created; the number shown was the launching branch's own PR). Re-run from the reply text: station exit 1; PR not opened. Residual for the UAT doc: the fixtures copy two real batch records from the state branch into `scripts/fixtures/ship-flow/uat-doc/` (15 files), no secrets.

- 2026-09-06T02:41:38Z — **DEV-106 FO-accepted** (`dea62ed6`) over a station false-refusal (S32: the variant extractor drops the first of two chained `git rm -f`). FO ran the one execution: base exit 1, candidate 0, after-variant 1; WARN stands (README.md read but not restored). PR #380 opened via open-pr.sh. Default applied: a station defect is recorded and fixed in its own round, not charged to the worker.

- 2026-09-06T02:45:10Z — **review station on #379 (DEV-105): disposition `block`.** 7 findings; one `security` (candidate-tree scripts run under the FO's credentials with no env stripping). Default applied: repair round 1 of 2 with the blocking and HIGH findings as the fix Brief; the rest go to the UAT document. DEV-107 (stacked on 105's candidate) will be rebased under `moved_base` once 105 r2 is accepted.
