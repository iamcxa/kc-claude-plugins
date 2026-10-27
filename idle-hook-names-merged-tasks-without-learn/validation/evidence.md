# Independent validation of PR #737

Candidate: 207c0a7eb51d08c00e68dbe52e9b364793750484
Base: 8bf4f3582411e8e4238f19fbadda8ddeca6767be
Verdict: REJECTED pending disposition of F1 (Needs decision).

## Finding F1: contradictory accepted behavior

Amendment 1 records Captain 「其他全照建議」 accepting an Asked row that says:
「閒置檢查提醒還沒跑的 learn ｜ 照設計做，加一條驗收 ｜ 要確認 learn 判為「不適用」的任務，不會每次都被重複點名」.

AC-8 instead requires the next idle pass to repeat the name, and calls that approved full-history repetition. The candidate implements AC-8 exactly. The validator cannot replace either the recorded Captain wording or the criterion with a new eligibility/suppression policy.

- Released user and normal workflow: an FO with learn listed scans a committed archived merged task; learn rejects its legacy profile.
- Observable harm: every later idle pass repeats the same unactionable learn instruction because no job exists.
- Affected boundary: captain-ruling[2026-10-27] no repeated naming after ineligibility conflicts with value-ac[AC-8] explicit repeated naming and the original full-history design.
- Trigger evidence: acceptance.sh step 3 uses the real learning recorder and a subprocess of the candidate watcher CLI. Both idle passes emit exactly `next: run kc-dev-flow-2:learn for old-profile.`; claim returns ineligible/profile; notices stays empty; archived task bytes stay unchanged.
- Disposition: Needs decision. FO must reconcile the accepted wording and criterion before a delivery recommendation; no repair or suppression rule has been invented here. The green AC-8 test proves the repeated behavior, not that the contradictory Captain wording was satisfied.

## Five-step acceptance script

Run in a fresh shell:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/idle-hook-names-merged-tasks-without-learn/validation/acceptance.sh
```

The script includes all five exact steps, expected observations, a pinned disposable checkout, cleanup, and no secret or network dependency. It requires the named local repository, Git, Python 3, Bash, and the dispatched installed Codex package. It was executed unchanged in a fresh Bash shell; observed stdout/stderr is in acceptance.log (exit 0, approximately 11 seconds). Its success reproduces F1; it is not a delivery approval.

Coverage: archive shapes, all-notices state subtraction, frozen historical replay, provider failure/uncertain data, ineligible next-idle behavior, and ADR lint. It does not cover a live GitHub read, real FO invocation/decision-making, all suites, hosted CI, merge, or plugin installation. Disposable fixture scheduler/provider interfaces are stubbed; the recorder, filesystem, Git snapshots and step 3 watcher CLI execute for real.

## Commands and primary evidence

All candidate code commands were run from the detached candidate checkout. No product bytes were changed.

- `python3 -B kc-dev-flow-2/scripts/test_pr_watch.py`: exit 0; 122 tests; watch.log.
- `python3 -B kc-dev-flow-2/scripts/test_observer_check.py`: exit 0; 19 tests; observer.log.
- `python3 -B kc-dev-flow-2/scripts/test_learning.py`: exit 0; 47 tests; learning.log.
- `python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3`: exit 0; dispatch.log; CLI 0.27.2 with plugin 0.27.3.
- To reproduce mutation/recount evidence, put the retained mutate.py and recount.py in a fresh candidate checkout at `.context/idle-evidence/`, then run `PYTHONDONTWRITEBYTECODE=1 python3 -B .context/idle-evidence/mutate.py` and `PYTHONDONTWRITEBYTECODE=1 python3 -B .context/idle-evidence/recount.py` from that checkout. Both were run with exit 0; all 14 mutant subprocesses exit 1 with assertion failures. The mutation script alters only its disposable package copy and restores its source between cases.
- Independent manifest verification read state commit 1158adc584637bdbf1b2f347b91a4c63844d6c00 with Git and compared every path/PR pair: 88/88 exact matches. Frozen 53 notice keys remain a sanitized reconstruction, not recovered historical store bytes.
- A second whitespace recount independently extracted the two workflow sections line by line, counted full files, and recounted retained actual stdout. Before/after: startup 1344/1342, idle OPEN 1039/1037, idle MERGED 572/570, after archive 358/356, merge ask 680/680, empty recovery 552/550. Each missing name adds 5 words per pass; uncertain/malformed fixtures add 11 each. The learn/framework load is 2918 + 3067 = 5985 words, plus evidence.
- Added comment review: one comment identifies the immutable sanitized manifest provenance; it does not narrate the code or cite a task/PR/line number. Three changed paths map to archive recovery, its falsifiers, and the retained reader pointer; no CI trigger/version/ADR/scaffold change.
- Caller search found the existing package mod as the runtime instructions consumer, plus extension documentation and tests; no extra package machine parser requires adjustment.
- Implementer's snapshot, real recorder, frozen history, count and mutation claims reproduced. Its provider/history/hosted evidence limits remain valid. The claim that AC-8 reflects approved repetition is not cleared: F1.
- FO-supplied external evidence only: RoboRev clean on this head, evidence=roborev:1264; CI 4/4 pass (2026-10-28). Neither was independently queried. CI cost per PR was not measured.

## Falsifier mapping

| Criterion | Behavior checked | Deliberate error detected |
| --- | --- | --- |
| AC-1 | sorted flat/folder discovery, folder preference, learn guard | archive exclusion; folder omission; removed guard |
| AC-2 | one code-root notices --all read; workflow-qualified key; all job states | unread-only list; wrong workflow; state-root store; uncertain key requiring input |
| AC-3 | all 11 absent keys named and restored keys suppressed, including folder task | live-only archive exclusion |
| AC-4 | state-only qualified provider reads; failure exit 2; live output survives malformed notices | full review query; treating malformed data as empty |
| AC-5 | repeated scans preserve state/store bytes and create no watch/store; pending claim suppresses | injected archive watch-cache write |
| AC-6 | observer pointer and existing hook/live behavior | removed observer script pointer |
| AC-7 | exact five-word reminder and complete reading ledger | longer reminder |
| AC-8 | actual ineligible/profile hold, empty notices, repeated next-idle line | silently suppressing old-profile; this mutation validates AC-8's text, while F1 remains unresolved |

