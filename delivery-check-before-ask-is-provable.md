---
title: The merge-ask record proves the delivery check ran before the question was presented
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:delivery-check-before-ask-is-provable:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-check-before-ask-is-provable-backlog-1
              briefing:
                id: briefing:delivery-check-before-ask-is-provable:backlog:attempt-1:revision-1
                digest: sha256:973beb8a677426dcd56bd3e3df4910207d10319e6d04dd19ac1fc708fb8c933a
                room-ref: ./delivery-check-before-ask-is-provable/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-check-before-ask-is-provable:backlog:1
                briefing: briefing:delivery-check-before-ask-is-provable:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T04:57:45.448796Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-09), answering 「決定：第 18 批這四張（驗證回答 Captain 能不能合併並因此主動讀完審查意見、合併檢查不再把網址和資料區塊當成檔案和指令、合併提問紀錄能證明檢查在提問前跑、數字寫明是哪次執行算出來的並涵蓋 learn 證據）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。核准即接受四張任務檔現在寫下的內容；要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:delivery-check-before-ask-is-provable:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:delivery-check-before-ask-is-provable-ideation-1
              briefing:
                id: briefing:delivery-check-before-ask-is-provable:ideation:attempt-1:revision-1
                digest: sha256:0eed174540720412e22a499e87d330d04f72b9f7697aff640fc6a321dceb2268
                room-ref: ./delivery-check-before-ask-is-provable/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-check-before-ask-is-provable:ideation:1
                briefing: briefing:delivery-check-before-ask-is-provable:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T06:49:16.951329Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-09), answering 「決定：第 18 批四張設計照下列建議進實作嗎？建議核准。(1) 驗證回答能不能合併：Claude 和 Codex 兩邊都要跑，Codex 跑不了就停下來回報，不接受只有 Claude 的結果；這次不寫決策紀錄，等第 19 批觀察者的數字出來再定。(2) 合併檢查誤判：只在引用的文件裡，把 shell 或沒標語言的程式區塊算成你要跑的步驟；問題和報告裡的區塊照舊全算。(3) 檢查跑在提問前：沒有對應的檢查紀錄就不讓準備問題，所以 PR 要先 ready、CI 綠才能開驗證關卡。(4) 數字寫明出處：learn 提案完成時，證據裡的數字在它引用的資料找不到就擋下；摘要裡的「未查核的數字：N」改由工具自己寫進去，不擋、也不用我抄（工人原案是擋到我抄上那一行）。核准即接受上列每一項建議，包括 (4) 改成工具自己寫；要改哪項直接說。」. Recommendation: followed; approving accepts each listed recommendation, including (4) written by the tool.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-09T04:59:10Z
---

## Scope

- Source: the Captain 「驗證不讀 PR 審查意見（建議）, 特別角色派工紀錄手寫（建議）, 改驗收條件沒當下檢查（建議）, 合併檢查時間點看不出（建議）」 (host question dialog, 2026-11-08), answering 「批次 17 觀察者找到的問題，哪些要開成 kc-dev-flow-2 套件問題單（排進下一批的待辦）？建議四張都開，每張都真的發生過。」
- Bite: all five batch 17 observers reported can't tell for 'delivery_gate.py check before the merge ask': each merge/ask-N.json postdates its briefing commit, so state cannot show the order.
- Non-goals: changing Spacedock; adopter AGENTS.md files.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- An observer can tell from state alone whether the delivery check ran before the question was presented, with a falsifier.

## FO alignment

Alignment: not needed; the Captain chose to file it from the batch 17 observer findings.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

### PRFAQ

**From the release that ships this, the validation briefing that asks the Captain to merge carries the delivery check's own record, fingerprinted by Spacedock, so anyone reading state can tell that `delivery_gate.py check` passed on that head and that text before the question was prepared.** Today the check saves `<task>/merge/ask-N.json` with a `time`, and the observer compares that time with the commit that added the briefing. In batch 17 every such file came 7 s to 2 m 56 s after its briefing commit, so five observers wrote `can't tell`. Under this change FO runs `check` first, then `delivery_gate.py question` refuses a merge-naming question unless the newest record matches the dispatched head and the question's own Sufficiency and Necessity text, and prints the record path. FO state-commits and passes that path to `spacedock gate prepare --reference`. Spacedock already refuses a `--reference` file that is not committed byte-for-byte (`gitsource.Inspect`, Spacedock 0.27.3) and writes its commit and sha256 into the briefing's `context`. The briefing is prepared before it is presented, so the record is shown to exist before the question.

- **Who uses it?** The observer at archive (kc-dev-flow-2 `observer` skill), and FO, whose preparation is held when the check has not run.
- **Why not a new written rule?** The record is written by `check` and fingerprinted by Spacedock; `question` refuses its absence. The one added FO step, passing `--reference`, is printed by `question` at the moment it is due, and a briefing without it reads as `violation`.
- **Why not compare timestamps better?** A record's `time` is self-reported, and the record is committed at FO's next state commit, which can come after the briefing. Only a content fingerprint inside the briefing orders the two.
- **Does this repeat ADR 0051's rejected "receipt that `question` ran"?** No. 0051 rejected it because a receipt "proves execution, not the bound text". Here the record is `check`'s own output, `question` compares its `sufficiency` and `necessity` with the text about to be bound, and the briefing pins the record by digest.
- **What about the run just before merging?** Unchanged. FO still runs `check` after approval; that writes ask-(N+1).json, which `merge_audit.py` and the merge-guard design already read.

### Flow

```mermaid
sequenceDiagram
  participant FO as First Officer
  participant DG as delivery_gate.py
  participant SC as state checkout
  participant SD as spacedock gate prepare
  participant C as Captain
  FO->>DG: check task --pr --text-file question+summary
  alt exit 1 or 2
    DG-->>FO: problems; hold the ask
  else exit 0
    DG->>SC: write merge/ask-N.json (head, sufficiency, necessity, time)
    FO->>DG: question task --text-file --summary-file
    alt text names --match-head-commit and newest ask-N.json missing, head differs from Candidate or match-head sha, or clauses differ
      DG-->>FO: exit 1; hold preparation; run check on this text first
    else passes
      DG-->>FO: exit 0; next: state commit, then --reference merge/ask-N.json
      FO->>SC: spacedock state commit slug
      FO->>SD: gate prepare --question --artifact --summary --reference merge/ask-N.json
      alt record not committed or changed since commit
        SD-->>FO: refused: selected source is not the exact committed file
      else committed
        SD->>SC: briefing index.json context: Reference uri git-root://state/sha/.../merge/ask-N.json, rev sha256
        FO->>C: present the briefing
      end
    end
  end
```

A question that does not name `--match-head-commit` is not changed: it carries no merge, so no record is required (limit below).

### Chain checked

- **Spacedock 0.27.3** (installed binary 0.27.2, source at the plugin cache): `gate prepare --reference FILE` resolves a state-checkout file, refuses one that is untracked or differs from its committed object, and records `git-root://state/<sha>/<path>` with `rev: sha256:` in `context` (`internal/gitsource/source.go` `Inspect`; `internal/gates/prepare.go`; `.json` gets its own media type in `mediaType`). `spacedock state commit <slug>` includes the task's companion folder (`TestStateCommitFlatIncludesExactCompanionDirectoryAndTrackedDeletions`). No Spacedock change is needed.
- **kc-dev-flow-2 at origin/main (0.36.0):** `check` writes the record (`write_record`); `question` reads no `merge/` file (only `write_record` names that folder). `question` already requires a passing Captain steps record at the latest dispatched Candidate (`captain_step_problems`, ADR 0054), the precedent for requiring a record before preparation. The observer skill's paragraph beginning "Where `<TASK>/merge/ask-<N>.json` files exist" carries the time comparison. No validation skill file (SKILL.md, principles.md, profiles) names `delivery_gate.py`, but a validator may run `check` ad hoc (one batch observer row: "The `delivery_gate.py` run in state is the validator's"), so the newest record can be a validator's; `question`'s clause and head comparison holds it unless it was run on the same text and head.
- **Adopters (read-only, `spacedock-state/dev2`):** subspace-web has 41 ask records; one briefing summary cites "delivery_gate check exit 0 (merge/ask-1.json)" in prose with no digest, so it cannot order the two. subspace-relay has 3 records, qnow none. Their briefings use `--reference` only for question files and the README. No adopter binds the record.
- **ADRs:** 0051's Consequences say the check "forces neither its own execution nor its order: skipping it or binding first is not refused" and "Reopen when … this nearest-moment check no longer covers the observed sequence"; the five batch 17 rows are that sequence. 0023 (merge carried by the delivery question) and 0062 (grant follows the quoted bound question) are unchanged. `git grep -n 'Override:'` in state shows no ruling in this area.

### What changes

One package PR:
- `kc-dev-flow-2/scripts/delivery_gate.py` `question()` plus one helper: when `GRANT` matches the gate text, read the highest-numbered `<task folder>/merge/ask-N.json` and hold (exit 1, one problem line and `next: hold preparation; run delivery_gate.py check on this question and summary, then this check again.`) when it is missing or unreadable, when its `head` prefix-matches no latest dispatched `Candidate:` or does not start with the sha after `--match-head-commit`, or when its `sufficiency` or `necessity` differs from `clean(clause(text))[:200]` of the question plus summary. On exit 0 add one last line: ``next: run `spacedock state commit <slug> --workflow-dir <dir>`, then `gate prepare` with `--reference <task folder>/merge/ask-N.json`.`` The docstring's `question` usage paragraph gains one sentence saying this. No record field changes.
- `kc-dev-flow-2/scripts/test_delivery_gate.py`: new cases for each hold and the pass line; existing `question` fixtures whose text names `--match-head-commit` gain an ask record.
- `kc-dev-flow-2/references/sd/workflow.md` § Delivery authority: the `check` paragraph moves above the `question` paragraph unchanged, and the `question` paragraph becomes: "FO runs `python3 <package>/scripts/delivery_gate.py question <task> --text-file <question file> --summary-file <summary file>`; nonzero holds `gate prepare`, which takes `--reference <check record>`. The summary declares `External rounds: N` and the configured second-reviewer outcome. Use it unchanged; callers omitting `--summary-file` retain combined-text checks." 80 words before and after (`str.split`), so `WORKFLOW_BUDGET_STEPS` does not move.
- `kc-dev-flow-2/skills/observer/SKILL.md`: the paragraph from "Where `<TASK>/merge/ask-<N>.json` files exist" through "…before presenting. When no file exists the task may predate the record, so report `can't tell`." becomes: for each validation briefing whose question names `--match-head-commit <sha>`, find a `context` Reference whose `uri` ends `/merge/ask-<N>.json`; `ok` when `git -C STATE show <uri sha>:<path> | shasum -a 256` equals its `rev`, the file's `head` starts with `<sha>`, and its `sufficiency` and `necessity` equal the first 200 characters of the briefing's clauses, quoting the Reference id, `time` and `head`; `violation` when a comparison fails, or when no such Reference exists and RULES in force at the briefing commit say `gate prepare` takes `--reference <check record>`; otherwise the existing time comparison stays as the fallback for a briefing with no Reference under the older README (`ok` when a file at that head has a `time` not after the briefing commit, else `can't tell`). Layered, not replaced: the time comparison produced a real `ok` (agent-reads-governing-adr ask-1, 07:29:32Z, before briefing commit dae03dc3), and tasks still in flight will archive with pre-rule briefings. The sufficiency and necessity row after it stays.
- A new ADR (FO reserves the number at dispatch), short title `the-merge-question-carries-its-delivery-check-record`. Draft: **Decision:** `question` refuses a merge-naming question without a matching `check` record, and `gate prepare` takes it as `--reference`. **Context:** the five batch 17 `can't tell` rows and ADR 0051's reopen clause. **Consequences:** amends 0051's consequence sentence above, so preparing before the check is now refused at `question` and visible in the briefing; 0051's decision (round count at `check`) stands. **Words:** the Captain's answer at this ideation gate.

Not changed: Spacedock, `merge_audit.py`, the record shape, adopter AGENTS.md files.

Second reviewer: this changes merge-ask and approval rules, so the workflow's second-reviewer trigger "the change touches authority, approval, merge or review rules" holds.

### Words FO reads at each moment

Counted with `str.split`, base origin/main 0.36.0, candidate as drafted above (`python3` over `/tmp/wf.md` and the module constants, 2026-11-09).

| Moment | Base | Candidate |
| --- | --- | --- |
| Startup and resume (README § Delivery authority, the two paragraphs) | 80 | 80 |
| Validation gate preparation, `question` exit 0 (claim-source line, `gate text complete`, `ASK_FORM`) | 92 | 107 (+15, the `--reference` line) |
| Validation gate preparation, `question` held | its problem lines | plus one problem line and one `next:` line, only when the record does not match |
| Merge ask and merge, `check` output | unchanged | unchanged |
| Idle on an open or merged PR, after the archive | unchanged | unchanged |

The +15 is the one rise, at the one moment the step is due; putting it in the README instead would add it to every startup. The observer paragraph (126 to about 132 words) is read by the observer, not FO.

### Existing-code check

Use what exists: `check` already writes the record and Spacedock already fingerprints a committed `--reference`. The gap is in `question`: it reads no `merge/` file, so a briefing can be prepared with no record. Observation: the five batch 17 observer rows quoted in Scope's bite, and `grep` over `delivery_gate.py` at origin/main showing only `write_record` names the `merge` folder.

### Limits

- A validation question that does not name `--match-head-commit` (the Captain merges himself) is not covered; its briefing carries no merge for the check to precede.
- If FO skips `--reference`, nothing refuses at preparation; the observer reports `violation` at archive, after the merge.
- Equal clauses show `check` read the same Sufficiency and Necessity text, cut at 200 characters, not the whole briefing.

### Needs decision

- **D1. Hold `question` when no matching record exists (recommended).** Alternative: print a warning only. Under the hold, the PR must be ready, green and mergeable before the validation gate can be prepared, so a late CI job delays the sitting; batch 17's 7 s to 2 m 56 s gaps suggest CI was already green at preparation. Under a warning, a skipped check is found only at archive.

### Batch overlap

| Task | Shared file or check | Overlap |
| --- | --- | --- |
| merge-guard-stops-unasked-merges (validation, #794) | `delivery_gate.py`, `test_delivery_gate.py`; reads `merge/ask-N.json` | edits the `ASK`/`ASK_UNQUOTED` sentence and its test literals; this task edits `question()` and adds pre-ask records, which its guard already treats as records (it reads PR and head only) |
| delivery-gate-ignores-url-paths-and-data-fences (ideation) | `delivery_gate.py`, `test_delivery_gate.py` | edits `absolute_paths` and `inspect_steps`; no shared function, same files |
| counts-name-the-run-that-produced-them (ideation) | possibly `delivery_gate.py` `CLAIM_SOURCE`, which `question` prints first | no design yet; this task appends a last line and does not touch `CLAIM_SOURCE` |
| validation-reads-pr-review-comments (ideation) | none found: the validation skill | none |
| adr-required-statement (closed by the Captain 「那就關掉」) | `workflow.md` § Decision records | different section; none |
| journey-server-host-pilot | kc-journey-map server | none |
| domain-note-reaches-worker-poc | no package change | none |
| ADR index | a new ADR number | FO reserves it at dispatch, beside any sibling's |

Recommended order: after #794 merges; then in any order with the other batch 18 `delivery_gate.py` tasks, the later one rebasing over the shared test file.

## Acceptance criteria

**AC-1** `question` holds a merge-naming question that has no check record. Verified by: a `test_delivery_gate.py` fixture (dispatched `Candidate:`, text naming `--match-head-commit <that head>`, complete clauses, no `merge/` folder) exits 1 with a line naming the missing delivery check record; the same fixture exits 0 at origin/main. Falsifier: removing the new hold makes the test pass at exit 0 and fail.

**AC-2** `question` holds when the newest record does not match. Verified by fixtures each exiting 1: newest `ask-2.json` head differs from the Candidate while `ask-1.json` matches; head matches the Candidate but not the `--match-head-commit` sha; `sufficiency` or `necessity` differs from the text's clause; the record is not valid JSON; the newest record was written on another text (a validator's ad-hoc run at the same head with different clauses). Falsifier: reading the lowest instead of the highest N, or skipping either comparison, turns one case to exit 0.

**AC-3** On a match, `question` exits 0 and its last line names the exact record path for `--reference`. Verified by a fixture asserting the line ends with `merge/ask-N.json` of the newest record. A question without `--match-head-commit` behaves as at origin/main: the existing tests pass unchanged except the fixtures that name it.

**AC-4** Spacedock binds the record into the briefing. Verified by a transcript in a throwaway split-root workflow (temporary directory, Spacedock 0.27.x): `gate prepare --reference <task>/merge/ask-1.json` is refused while the file is uncommitted; after `spacedock state commit <slug>` it succeeds, and the briefing `context` holds a Reference whose `uri` ends `/merge/ask-1.json` and whose `rev` equals `shasum -a 256` of the file. Falsifier: editing the file after the commit makes prepare refuse.

**AC-5** README word count is unchanged. Verified by `python3 kc-dev-flow-2/scripts/lint-skills.py` passing with `WORKFLOW_BUDGET_STEPS` unchanged and the § Delivery authority text as drafted above.

**AC-6** The observer can tell from state alone. Verified by a scripted replay of the observer's three comparisons (digest, head prefix, clauses) on the AC-4 briefing giving `ok`; on a copy whose record head differs giving `violation`; on a copy with no Reference under the new README giving `violation`; and on the five batch 17 briefings named in Scope (no Reference, older README) giving `can't tell`; and on agent-reads-governing-adr validation briefing-1 (no Reference, older README, ask-1.json 07:29:32Z before commit dae03dc3) still giving `ok` through the time fallback. Falsifier: deleting the fallback turns that last case to `can't tell`. Limit: an observer agent run on the first dev2 task delivered after release is post-merge evidence, not part of this PR.

**AC-7** The words FO reads move only as the table says. Verified by an independent recount script, base origin/main and candidate head, of the README passage, `question` exit-0 output and `check` exit-0 output: 80 to 80, 92 to 107, unchanged.

**AC-8** The ADR lands with the Captain's words from this gate and states that it amends ADR 0051's consequence and leaves its decision. Verified by `adr_lint.py docs/adr --require <reserved number>` exiting 0.

## Number guards

ADR: 0071

## Stage Report: ideation

- DONE: Design how the merge-ask record shows, from state alone, that kc-dev-flow-2/scripts/delivery_gate.py check ran before the question was presented; prefer the tool writing that fact over a new written rule. Batch overlap: name each file your design changes; siblings validation-reads-pr-review-comments, delivery-gate-ignores-url-paths-and-data-fences, delivery-check-before-ask-is-provable and counts-name-the-run-that-produced-them may touch kc-dev-flow-2/scripts/delivery_gate.py, so say the order you need relative to them.
  `question` holds a merge-naming question without a matching `check` record and prints the path; Spacedock's existing `gate prepare --reference` fingerprints the committed record into the briefing (## Design, PRFAQ and Flow). Files: delivery_gate.py, test_delivery_gate.py, workflow.md, observer SKILL.md, one ADR. Order: after #794.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task and live task of other sessions that changes the same file or check, so FO can order implementation
  `### Batch overlap` table covers the five batch 18 tasks, the three live tasks and the ADR index; Recommended order: after #794, then any order.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Table under `### Words FO reads at each moment`: README passage 80 to 80, `question` exit 0 92 to 107, `check` and idle unchanged (`str.split`, origin/main 0.36.0).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-8 below, each with a falsifier; one decision, D1 (hold, recommended; worse: CI must be green before the validation gate is prepared).
- DONE: AC-1 missing record holds `question`: not yet verified; future test in test_delivery_gate.py. Current fact: `question` at origin/main reads no `merge/` file (grep).
- DONE: AC-2 newest record mismatch holds: not yet verified; future fixtures.
- DONE: AC-3 pass line names the record path: not yet verified; future fixture.
- DONE: AC-4 Spacedock binds the record: not yet verified at runtime; source read only (`gitsource.Inspect` refuses an uncommitted or changed file; `.json` media type; state commit includes the companion folder per its test).
- DONE: AC-5 README count unchanged: drafted passage counts 80 against base 80 (`str.split`); lint not yet run on a candidate.
- DONE: AC-6 observer tells from state: not yet verified; replay planned on the AC-4 briefing, two falsifier copies, the five batch 17 briefings and the agent-reads-governing-adr fallback `ok`.
- DONE: AC-7 per-moment recount: drafted counts above; independent recount not yet run.
- DONE: AC-8 ADR lands: not yet verified; draft in ## Design.
- DONE: `python3 <package>/scripts/design_surfaces.py check <task>` before reporting
  Output: "delivery-check-before-ask-is-provable.md: design surfaces presentable", exit 0 (package 0.36.0).

### Summary

Design: `check` runs first, `question` refuses a merge question unless the newest `merge/ask-N.json` matches the dispatched head and the text's Sufficiency and Necessity, and FO passes that record to `gate prepare --reference`, where Spacedock 0.27.3 already refuses an uncommitted file and records its sha256 in the briefing. The observer gains a digest comparison, keeping the time comparison as the fallback for older briefings. The README stays at 80 words; FO reads 15 more words only at validation preparation. The change amends ADR 0051's consequence ("binding first is not refused") through its own reopen clause; one Captain decision, D1. Chain: Spacedock needs no change; kc-dev-flow-2 has the record and the Captain-steps precedent; subspace-web cites the record in prose without a digest.
