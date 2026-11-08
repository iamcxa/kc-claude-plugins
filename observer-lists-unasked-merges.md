---
title: The observer lists each merge in its window that no task's saved merge ask carries
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:observer-lists-unasked-merges:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:observer-lists-unasked-merges-backlog-1
              briefing:
                id: briefing:observer-lists-unasked-merges:backlog:attempt-1:revision-1
                digest: sha256:b2ad9cdc9bcf9da7256f7fca7df2c3bc48c1fea883b4a455111ee7047d5de06a
                room-ref: ./observer-lists-unasked-merges/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:observer-lists-unasked-merges:backlog:1
                briefing: briefing:observer-lists-unasked-merges:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T08:09:36.024308Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:observer-lists-unasked-merges:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:observer-lists-unasked-merges-ideation-1
              briefing:
                id: briefing:observer-lists-unasked-merges:ideation:attempt-1:revision-1
                digest: sha256:06a6e8cfd7df4e08a4d747d0b16d5c6d71318e5eef755cb08b38f70b9805377a
                room-ref: ./observer-lists-unasked-merges/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:observer-lists-unasked-merges:ideation:1
                briefing: briefing:observer-lists-unasked-merges:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T15:37:36.847222Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批五張設計都照各自寫下的建議進實作嗎？要你決定的有：Paseo 瀏覽器 D1 那句指示不強制成派工紀錄必填、D2 在 kc-claude-plugins 用 journey-map 畫面驗證；設計檢查 D1 綁的不是任務檔就印「沒跑」、D2 不做開關卡時的提醒；未經提問的合併 D1 讀本 repo 所有狀態分支、D2 用分支前綴和同步 PR 標題認發版／同步／學習類；派工紀錄 D1 用套件裡的派工腳本並新增一份決策紀錄（ADR）、D2 模型與名冊仍由我手填、D3 版本與工作流程檢查這次不併進腳本；決策紀錄檢查沒有要你決定的事。核准即接受每張設計對其決定寫下的建議。要改哪件直接說。」. Recommendation: followed.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-07T15:40:18Z
worktree: .worktrees/spacedock-ensign-observer-lists-unasked-merges
pr: iamcxa/kc-claude-plugins#809
---

At archive, the observer reports every PR merged in its window whose number and merged head match no saved `merge/ask-N.json` in any state checkout it can read, so an unasked merge is found after the fact without a pre-tool hook.

## Scope

- Source: the Captain 「可以」 (chat, 2026-11-06), answering FO's 「要照這樣做嗎？」, which proposed keeping merge-guard-stops-unasked-merges held and doing first the cheaper after-the-fact check and a look at whether #785 and #727 were asked.
- Bite: fo-feedback round 005 (2026-11-06): journey-map PR #785 merged 2026-11-05 while its task still reads `status: backlog` with no gate decision (FO read of that state file); ops-inbox PR #727 merged 2026-10-27 with the Captain's 「准」 recorded (FO read of its archived gate, 2026-11-06) but with Codex's code review only on an earlier commit. The held merge-guard replay counts (54/30, then 74/10) stay in its task file.
- Added 2026-11-06 (journey-map FO reply, Paseo 7b9a9beb, operator statement): #785 was asked; the Captain answered 「Ａ可以，我覺得配對流程不是很順，應該參考 relay 的做法，但可以先合併再重構」 to a question ending 「要合 #785 就說合併」 in the journey-map FO's session on 2026-11-05, and the FO then ran `gh stack merge 785 --squash`. The wording is in that session's transcript only, not in task state. So neither #785 nor #727 was an unasked merge; both are record gaps (no gate record; no code review on the merged head). An audit that flags "no ask record" would list #785 although the Captain approved it, so the design must say how a chat-only approval is told apart from an unasked merge, or the task's value is in surfacing record gaps.
- Upstream first: the merge-guard task's record discovery (state worktrees on `spacedock-state/*`, `*/merge/ask-*.json`); the observer skill; delivery_gate.py's saved ask records.
- Non-goals: blocking any merge; Release, workflow-sync and learning PRs, which carry no task ask (the observer names them as such instead of as violations).

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay over the window that holds #785 lists #785 as merged with no ask record, lists a task PR with a matching record as carried, and names Release and sync PRs separately.

## FO alignment

Alignment: needed at ideation; which state checkouts the observer reads and how a Release PR is named are his to accept.
Result: aligned at backlog: Batch 17 backlog sitting, the Captain 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」, approved the outcome and bounds in this file; the design choice the Alignment line names stays his at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

### Chain check

Read 2026-11-07, kc-dev-flow-2 at origin/main (released 0.35.0):
- **Spacedock 0.27.3.** `spacedock merge guard` runs after a merge, for a task that owns the PR. It never sees a PR with no task, and it never compares the merged head with an ask.
- **kc-dev-flow-2.** `delivery_gate.py check` saves `<task>/merge/ask-N.json` (`write_record`) with `pr` as `owner/repo#N`, the full 40-hex `head` and `time`; 126 records sit on `spacedock-state/dev2`, none on the other six `spacedock-state/*` branches. The observer skill already reads a task's own ask records (the "FO runs `delivery_gate.py check` before the merge ask" paragraph), but only for its own PR. `number_guards.py` already reads every `origin/spacedock-state/*` branch after `git fetch origin +refs/heads/spacedock-state/*:refs/remotes/origin/spacedock-state/*`, falling back to local refs with a warning. `pr_watch.py` already calls `gh pr list`. No script lists merged PRs against ask records. ADR 0023 Consequences name the gap: "Nothing checks that a merged PR's approved question named the merge".
- **Held sibling.** merge-guard-stops-unasked-merges (validation, held by the Captain) designs `merge_guard.py record`, which saves a chat approval of a Release, sync or learning PR as `_merges/<owner>-<repo>-<N>/merge/ask-K.json`. It reads worktrees on disk, before a merge; this design reads committed refs, after.
- **Third-party names, read at their source.** release-please 17.11.1 `build/src/util/branch-name.js` builds `release-please--branches--<target>` (with `--components--` or `--groups--` suffixes). `learning.py` requires `branch == "learning/" + key` (64 hex). Sync PRs follow no enforced name: 19 of 19 merged sync PRs are titled `chore(dev2): sync workflow to kc-dev-flow-2 v<version>`, but their branches drift (`iamcxa/dev2-sync-0.22.1` #641, `chore/dev2-sync-kc-dev-flow-2-0.23.0` #648).
- **Siblings.** No adopter lists merges against records.

**Existing-code check.** Reuse the patterns and leave the scripts alone. `observer_check.py`'s exit codes drive the package mod's archive step, so a merge finding there would block archives. `number_guards.py` reserves numbers, a different job. A new read-only script reuses `number_guards.py`'s fetch-and-read pattern and `delivery_gate.py`'s record shape. The observation that shows the change is needed: `poc/replay-output.txt` (below).

### What state can and cannot tell

State cannot tell a chat-only approval from an unasked merge. #785 shows it: the Captain approved it in the journey-map FO's chat (operator statement, Scope), and no record anywhere this repository holds says so. Its task file is on no `spacedock-state/*` ref of this repository and was not found on this machine's disk, so the replay prints "no task in readable state" for it and for the 9 other journey-map PRs. Round 005 read `status: backlog, pr: pr-merge:785` in a state file outside these refs.

So the audit reports what state can show, in the observer's existing verdict words:
- **carried** (`ok`): a saved `merge/ask-N.json` anywhere in readable state has this `owner/repo#N` and a `head` the merged head starts with (at least 7 hex). This includes `_merges/` records once merge-guard lands.
- **head differs** (`violation`): records exist for the PR, but none at the merged head. Quoted rule: workflow.md § Delivery authority, "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it".
- **no ask record** (`can't tell`): no record for the PR. The evidence outside state is the Captain's chat, or a state checkout this run cannot read. The line names the task that owns the PR (`pr:` frontmatter) or says "no task in readable state".
- **release**, **sync**, **learning** (`observed`, one line per kind listing the numbers): PRs that carry no task ask, named as such and not as findings (Scope non-goals). These are checked after carried, so a recorded Release PR reads carried.

Until a chat approval can be recorded (merge-guard's `record` route), the value of this task is surfacing record gaps, the Scope's stated fallback. This is not ADR 0024's case: that ADR lists rules whose only witness is chat. Here state is the witness for 60 of 92 merges in the replay, and `can't tell` is the gap that remains.

### Window, inputs, repeats

Only the observer's declared inputs (STATE, TASK, FROM, TO) are used:
- **Repository and base.** `git -C STATE remote get-url origin` (state branches live in the code repository), and `trunk:` from the workflow README above STATE.
- **Window.** PRs merged into the base whose `mergedAt` lies after FROM's committer time and at or before TO's: `gh pr list --state merged --base <trunk> --search "merged:<from date>..<to date>" --limit 1000`, filtered exactly in the script. A result of 1000 holds, as exit 2.
- **Records.** After the `number_guards.py` refspec fetch, the script reads every `merge/ask-<N>.json` at any depth on each `refs/remotes/origin/spacedock-state/*` and `refs/heads/spacedock-state/*` tip. The tip is used, not TO, because other tasks commit their records later. The `read:` line names each ref and its commit time, so a stale ref shows.
- **Repeats.** A finding line already quoted in another committed `observer.md` in STATE (`git grep -F "no ask record: #<N> head <12 hex>"`) collapses into one `observed | already in an earlier observer report` line. If an earlier report paraphrased the line, it repeats; nothing is lost.

### PRFAQ

**Press release.** At a task's archive, the observer report now lists each PR merged during the task's life that no saved merge ask carries. A Release, sync or learning PR is named as that kind, a merge whose ask record has another head is a violation, and a merge with no record says plainly that its approval, if any, is outside state.

- *Does it stop a merge?* No. It reports after the fact; merge-guard-stops-unasked-merges is the before-the-fact task, and it stays held.
- *Will #785 read as a violation?* No. It reads `can't tell`, naming the chat, because the Captain approved it there.
- *Why not read the chat?* No record of it exists in a place the observer can read; that is what merge-guard's `record` route would add.
- *What does it not prove?* That a carried merge's question named the merge (the observer's own `answering 「…」` row checks the task's question). It also cannot see records in a state checkout outside this repository's refs, or a merge approved in words.

### Mermaid

```mermaid
flowchart TD
  FO[FO: merged task, before archive] -->|dispatch STATE, TASK, RULES| O[observer]
  O --> A["merge_audit.py STATE TASK --rev TO"]
  A --> F[fetch origin spacedock-state/*; on failure warn, read local refs]
  F --> L["gh pr list merged into trunk, FROM..TO"]
  L -->|1000 results, gh or git fails| X[exit 2: observer reports can't tell with the cause]
  L --> C{for each merged PR}
  C -->|a record has PR and merged head| OK[carried: counted in one ok line]
  C -->|release-please branch / sync title / learning branch| OB[observed: one line per kind]
  C -->|records for PR, none at merged head| V[violation: head differs]
  C -->|no record| CT[can't tell: no ask record, owning task or none]
  V --> R{quoted in an earlier observer.md?}
  CT --> R
  R -->|yes| RP[observed: already reported, one line]
  R -->|no| W[finding line]
  OK --> REP[observer report lines plus Coverage caveat]
  OB --> REP
  RP --> REP
  W --> REP
  REP -->|saved unedited as observer.md| FO2[FO sends it to the Captain with learn's notice]
```

### What changes

One package PR:
- `kc-dev-flow-2/scripts/merge_audit.py` (new, read-only apart from the state-ref fetch): `merge_audit.py <state checkout> <task slug> [--from FROM] [--rev TO]`, FROM and TO as the observer skill defines them. It prints `window:`, `read:`, one `carried: <n> of <m>` line, one line each for `release:`, `sync:` and `learning:`, and one line per `head differs:` / `no ask record:` PR in the fixed form `<kind>: #<N> head <12 hex> merged <time> (<owner or note>)`, then `already reported:`. Exit 0 when every merge is carried or named, 1 when any finding line prints, 2 when it cannot tell (usage, no origin, gh or git failure, 1000 results).
- `kc-dev-flow-2/scripts/test_merge_audit.py` (new), plus one step in `.github/workflows/kc-dev-flow-2-tests.yml`, which runs each test file by name. It covers fixture state refs and a stubbed `gh` (each verdict, the head prefix, release before no-record, repeats, exit 2).
- `kc-dev-flow-2/skills/observer/SKILL.md`: one paragraph after the ask-record paragraph. It says to run the script and map its lines to `ok` / `observed` / `violation` / `can't tell` as above, quoting the Delivery authority sentence, with the caveat once under `Coverage:`. It also says to quote each finding line's `<kind>: #<N> head <12 hex>` verbatim, which is what lets the next report collapse a repeat.

Not changed: `references/sd/workflow.md`, `_mods/`, `observer_check.py`, `delivery_gate.py`, `agents/observer.md`, `extensions/learn/EXTENSION.md`. No ADR: this fills the check ADR 0023 says is missing and decides nothing new about authority.

### Words FO reads at each moment

Counted 2026-11-07 with `str.split()` (`poc/render.py`, over the 54 dev2 archives since 2026-10-24 and merges since 2026-10-23):

| Moment | Before | After |
| --- | --- | --- |
| startup / idle (`_mods/kc-dev-flow-2.md`, README) | unchanged | unchanged |
| idle on a merged PR (`observer_check.py` exit 1 `next:` lines) | unchanged | unchanged |
| merge ask (`delivery_gate.py check` output, § Delivery authority) | unchanged | unchanged |
| after the archive (the observer report FO relays; today 442 to 1087 words in the last 8 reports) | 0 merge lines | median +60, max +320 (override-recorded-when-captain-departs: 77 merges, 5 new findings, 2 collapsed); +422 at that max without collapse |

The observer agent, not FO, reads the new SKILL.md paragraph (about 110 words on 1105). `WORKFLOW_WORD_BUDGET` covers `workflow.md` only and does not move; the design asks for no raise.

### Non-goals

Blocking or delaying any merge; recording a chat approval (merge-guard's `record`); reading state outside this repository's `spacedock-state/*` refs; judging whether a carried question named the merge.

### Needs decision

- **D1: which state checkouts the observer reads.** Recommended: every `origin/spacedock-state/*` and local `spacedock-state/*` ref of the code repository, after the `number_guards.py` refspec fetch, at each tip. Worse under it: a workflow whose state is not in this repository (journey-map's private tasks today) shows each of its merges as `can't tell … no task in readable state`, 10 of the 12 gaps in the replay, until that state is pushed here. The other option was local worktrees on disk only (merge-guard's discovery); it was not chosen because it misses a peer machine's pushed records and reads uncommitted files the observer cannot quote.
- **D2: how Release, sync and learning PRs are named.** Recommended: Release by release-please's branch prefix `release-please--branches--`, learning by `learning/<64 hex>` (both enforced by their producers), and sync by the title form `chore(<scope>): sync workflow to kc-dev-flow-2 v`, which nothing enforces. Worse under it: a sync PR titled differently falls into `can't tell`, as the renamed-branch falsifier shows for a Release PR, and an adopter whose sync titles differ sees its sync PRs as gaps.

Past rulings: `git -C <state> grep -n 'Override:'` finds none on merge listing or observer inputs; ADR 0023 and ADR 0024 are followed as described above.

### Batch overlap

| Task | Shared file or check | Overlap |
| --- | --- | --- |
| worker-browser-checks-use-paseo-browser (batch 17) | the paseo extension and worker browser text | none |
| adr-lint-tells-supersession-assertion-from-pointer (batch 17) | `adr_lint.py`, `test_adr_doc_checks.py`, `test_sd_dispatch.py` | none |
| dispatch-build-writes-the-dispatch-record (batch 17) | `spacedock dispatch build`, `dispatch_records.py` | none |
| design-check-says-not-run-without-a-scope (batch 17) | `design_surfaces.py check` output, which the observer skill's design-check replay paragraph maps by exit code | same file (`skills/observer/SKILL.md`), different paragraph, and only if that task edits the replay mapping; no rule overlap |
| merge-guard-stops-unasked-merges (held, read only) | `.github/workflows/kc-dev-flow-2-tests.yml` (each adds a step); its `_merges/*/merge/ask-K.json` records, which this audit reads as carried | adjacent lines in one file; producer and reader of one record shape. This design does not depend on it landing |
| gate-summary-names-each-decline (held, read only) | `delivery_gate.py`, `workflow.md`, `lint-skills.py` | none |
| archive-waits-for-observer-report (implementation) | `observer_check.py`, the package mod, learn `EXTENSION.md`; it moves the observer run before the archive | no shared file; the window uses TO, never the archive commit, so either order works |
| adoption-asks-which-extensions, step-back-answer-has-a-record-line (ideation) | both state they leave `skills/observer/SKILL.md` unchanged | none |
| journey-map tasks (journey-map FO, read only): journey-canvas-hosted-poc, journey-map-progress-and-provenance, journey-server-host-pilot | `kc-journey-map/**` | none; their merged PRs are among the audited merges |

Recommended order: independent of every batch-17 task. If merge-guard-stops-unasked-merges is released from hold, land this first, then rebase its `kc-dev-flow-2-tests.yml` step on this one.

## Acceptance criteria

**AC-1** — Replay over the window that holds #785. Evidence: at the candidate, `python3 -B kc-dev-flow-2/scripts/merge_audit.py <dev2 state> merge-check-reads-two-pr-tasks --rev 8ffd6dfa3e021c1967aeaeabd7cf0cb61db48aae` (its archive commit; FROM defaults to 70b0f2f66, the commit that added the task file, 2026-10-23T10:17:22+08:00) prints `carried: 54 of 82`, which counts #727 (record `_archive/ops-metric-event-protocol/merge/ask-1.json`, head 5dee91fb7fbf); `no ask record:` lines for #704 #762 #774 #776 #778 #784 #785 #789, #785 as `no ask record: #785 head 0c38dd60b562`; `release:` #707 #717 #723 #731 #739 #746 #752 #760 #768; `sync:` #715 #718 #725 #733 #741 #747 #753 #761 #781; and `learning:` #726 #782. It exits 1. These sets match `poc/replay-output.txt` restricted to that window. Falsifier: removing the release check makes #707 print `no ask record`.
**AC-2** — Head differs is a violation line. Evidence: `test_merge_audit.py` with a fixture record for `o/r#7` at head A and a merged #7 at head B prints `head differs: #7 head <B12>` and exits 1, as `poc/falsifier-output.txt` shows for #727 with its head zeroed. Falsifier: matching on PR number alone makes the test pass a carried line and fail.
**AC-3** — Named kinds come from their producers. Evidence: tests feed a `release-please--branches--main--components--x` branch (release), a `learning/<64 hex>` branch (learning), the sync title form (sync), and a branch `chore/release-main` with no record (`no ask record`, per `poc/falsifier-output.txt` #707). A recorded Release PR reads carried. Falsifier: checking kinds before records turns the recorded Release PR into `release`.
**AC-4** — Inputs and holds. Evidence: tests show that a failed fetch prints a warning and reads local refs; that `gh` failing, 1000 results or no origin exit 2 with the cause; that `read:` names each ref with its commit time; and that records are read at ref tips, so a record committed after TO is carried. Falsifier: reading at TO makes the last case print `no ask record`.
**AC-5** — Repeats collapse. Evidence: a test with a committed `_archive/x/observer.md` quoting `no ask record: #9 head <12 hex>` prints `already reported: #9` and no #9 finding line. Falsifier: deleting that file brings the finding line back.
**AC-6** — The observer reports it. Evidence: `skills/observer/SKILL.md` holds the new paragraph, and one observer run over an archived dev2 task on the candidate package produces the `ok` / `observed` / `can't tell` lines in the form of `poc/rendered-lines.txt`, with the caveat once under Coverage. Falsifier: an observer dispatched on base 0.35.0 prints no merge lines.
**AC-7** — Words and scope. Evidence: `git diff --name-only origin/main...HEAD` lists only `merge_audit.py`, `test_merge_audit.py`, `skills/observer/SKILL.md` and `kc-dev-flow-2-tests.yml`; `python3 kc-dev-flow-2/scripts/lint-skills.py` passes with `WORKFLOW_WORD_BUDGET` unchanged; the after-archive count is recounted on the landed line forms with an independent copy of `poc/render.py` (per learning.md) and stays at or below a median of +60 and a max of +320 words over the same 54 windows.

## Stage Report: ideation

- DONE: Design how the observer lists each PR merged in its window that no saved merge/ask-N.json carries, with a replay over the window holding #785, telling a chat-only approval from an unasked merge and naming Release and sync PRs separately
  `## Design`: new read-only `merge_audit.py` plus one observer SKILL.md paragraph. `poc/replay-output.txt` covers 92 merges (2026-10-23..11-07): 60 carried (#727, #788 included), 12 no ask record (#785 included), 9 release, 9 sync, 2 learning. Chat-only and unasked read the same in state, so a missing record is `can't tell`, not `violation`.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (worker-browser-checks-use-paseo-browser, adr-lint-tells-supersession-assertion-from-pointer, dispatch-build-writes-the-dispatch-record, design-check-says-not-run-without-a-scope) and live task of other sessions (merge-guard-stops-unasked-merges and gate-summary-names-each-decline (held by the Captain; read only), and journey-map tasks driven by the journey-map FO (read only)) that changes the same file or check, so FO can order implementation
  Every named task is a table row; shared surfaces: observer SKILL.md (design-check-says-not-run, other paragraph) and kc-dev-flow-2-tests.yml plus `_merges/` records (merge-guard). Ends with a `Recommended order:` line.
- DONE: The words FO reads at each moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: only after-the-archive moves, median +60, max +320 words over 54 archives (`poc/render.py`, `poc/rendered-lines.txt`); without collapse the max is +422.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1..AC-7, each with a command and a falsifier; D1 (which state refs) and D2 (how release, sync and learning are named) under `### Needs decision`.
- DONE: AC-1 replay over the window holding #785: shown by the ideation replay (`poc/replay-output.txt`, the sets restricted to merge-check-reads-two-pr-tasks' window); not yet verified on the candidate script.
- DONE: AC-2 head differs: shown by the ideation falsifier (`poc/falsifier-output.txt`, #727 with zeroed head prints `head differs`); the candidate test is not yet verified.
- DONE: AC-3 named kinds: the renamed-branch falsifier (#707 to `no ask record`) is shown; component and group branches and the recorded-Release case are not yet verified.
- DONE: AC-4 inputs and holds: committed-refs reading gives the same counts as the on-disk reading at ideation; fetch fallback, exit 2 and tip-not-TO are not yet verified.
- DONE: AC-5 repeats collapse: simulated in `poc/window-simulation.txt` (finding lines over 54 archives fall from 57 to 12, assuming verbatim quotes); not yet verified on a script.
- DONE: AC-6 observer reports it: line forms rendered in `poc/rendered-lines.txt`; an observer run is not yet verified.
- DONE: AC-7 words and scope: the base counts are measured; the diff file list and recount are not yet verified.

### Summary

The observer gets a merge listing from a new read-only `merge_audit.py`. It fetches every `spacedock-state/*` ref (the `number_guards.py` pattern), lists PRs merged into trunk between FROM and TO, and sorts each one: carried (`ok`), head differs (`violation`), no ask record (`can't tell`, approval may be in chat), or release/sync/learning (`observed`). Repeats already quoted in earlier reports collapse to one line. Replayed on real data, #785 lists as no ask record (its journey-map state is not in this repository's refs), #727 lists as carried, and Release and sync PRs are named separately. `design_surfaces.py check` printed "design surfaces presentable", exit 0. D1 and D2 are the Captain's; no ADR and no word-budget raise.

## Stage Report: implementation

- DONE: Implement the approved design and acceptance criteria; D1 reads every local and fetched spacedock-state/* branch, D2 uses the approved producer names, only the files the design names.
  Candidate b36fbeeec3a6699c0a82a021dc4ee0142410f6c8, base origin/main 139feeaee7ce037a0c6535568cd6bd103155cbae, branch spacedock-ensign/observer-lists-unasked-merges; four product files in implementation/identity.json; no version bump.
- SKIPPED: One Draft PR in iamcxa/kc-claude-plugins.
  no PR opened: no push grant; the dispatch gives FO publication. Conventional Commit title and body are prepared at /tmp/impl-observer-lists-unasked-merges-pr.md and mirrored in this task's implementation/pr.md.
- DONE: AC-1 — Replay over the window that holds #785.
  implementation/replay-live.log: actual GitHub read, exit 1, carried 54 of 82 and all eight expected gaps; snapshot.py checks every named set and #727 carried; release-removal mutation exposes no ask record #707.
- DONE: AC-2 — Head differs is a violation line.
  test_merge_audit.py's PR-7 fixture prints head differs and exits 1; the PR-number-only mutation fails that test; acceptance/snapshot/727-wrong-head.log separately proves the real #727 head boundary.
- DONE: AC-3 — Named kinds come from their producers.
  Producer-prefix, learning-length, sync-title, renamed-release and recorded-Release cases pass; the kind-before-record mutation fails the recorded-Release test.
- DONE: AC-4 — Inputs and holds.
  Fixtures exercise remote-only fetched refs, fetch warning/local fallback, read ref/sha/time, exact time bounds, late records, gh failure, 1000 results, no origin and invalid evidence; reading records at TO fails the late-record test.
- DONE: AC-5 — Repeats collapse.
  A committed earlier report suppresses #9, deleting it restores the finding, uncommitted and self reports do not hide it; disabling collapse fails the repeat test.
- DONE: AC-6 — The observer reports it.
  implementation/observer-candidate-final.md is the native Sonnet observer report at b36fbeeec3a6699c0a82a021dc4ee0142410f6c8; observer-base.md has no merge lines; base-control.json binds the control skill to published 0.35.0.
- DONE: AC-7 — Words and scope.
  Four-file product diff; workflow.md and WORKFLOW_WORD_BUDGET unchanged; independent recount.py over the pinned original 54 revisions gives median +60, max +320 (uncollapsed +422), as the approved chronological verbatim-report simulation.
- DONE: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared).
  implementation/acceptance.log: fresh-shell PASS; mutate.py uses new empty directories and bytecode-disabled processes for 17 baseline tests and five rejected mutations; the native base observer supplies the sixth control.
- DONE: Repository lint-skills.py, package adr_lint.py docs/adr --since base, number_guards.py check, and comment_ratio.py within its maximum.
  acceptance/ logs: exit 0 at candidate; lint 5933/5933 workflow words, 62 ADR files checked, number guards no findings, comments 2/431 lines = 0.5% below 5%; no new ADR or migration.
- DONE: Run the local package consumer checks and affected-document review.
  implementation/suite-summary.json and suite/: 27 commands succeeded, 1199 unittest cases including 11 skips; doc-impact.json lists README.md, unaffected because its named-CI-command entry remains accurate.
- DONE: Commit locally, no push; PR text written for FO.
  Product worktree is clean at b36fbeeec3a6699c0a82a021dc4ee0142410f6c8; implementation/README.md maps durable proofs and the fresh-shell acceptance command.
- SKIPPED: FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured.
  roborev not run: dispatch assigns the local daemon review to FO; hosted CI not run and cost per PR not measured. Existing CI path triggers/job are unchanged; local dispatch used CLI 0.27.2 with plugin files 0.27.3, not the hosted pinned install.

### Summary

Delivered the Pilot slice as one local product commit: saved asks carry matching PR heads, differing heads are violations, and missing records stay inconclusive; release, sync, learning and repeated findings are named separately. The live replay, behavioral mutations, native observer controls, word recount, package guards and local suite passed within their recorded limits; the fresh-shell harness pins the original archive corpus so midnight does not change its 54 windows. FO retains publication, review, independent validation and delivery authority.

## Stage Report: validation

- DONE: Independent verdict on PR #809 head b36fbeee against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at b36fbeeec3a6699c0a82a021dc4ee0142410f6c8 (base 139feeaee7ce037a0c6535568cd6bd103155cbae): AC-1..5 and AC-7 pass; AC-6's fresh native report contains false execution evidence. Full matrix and limits: validation/README.md.
- DONE: Rerun the merge audit over the window holding #785 read-only and judge the one CI test step added to .github/workflows/kc-dev-flow-2-tests.yml, stating its cost as measured or not measured
  validation/replay-live-network.log: new actual GitHub read, exit 1, carried 54/82, exact eight gaps and all named-kind sets; only intended state-ref fetch writes. One stdlib test step, existing narrow path triggers/job/setup unchanged; hosted CI cost per PR not measured.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Five-step validation/acceptance.sh, fresh bash exit 0, observed output in validation/acceptance.log; installed-package adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae exits 0 (62 records). The script explicitly excludes native prose and cannot close AC-6.
- DONE: AC-1 — Replay over the window that holds #785.
  Live and saved replay agree on all sets and #727 carried; removing release recognition exposes #707 as no ask record (validation/mutations/release-removed-snapshot-replay.log).
- DONE: AC-2 — Head differs is a violation line.
  PR-7 A/B fixture and changed real #727 head exit 1; PR-number-only mutation fails the head-boundary test (validation/mutations/pr-number-only.log).
- DONE: AC-3 — Named kinds come from their producers.
  Producer names, renamed release, learning length and matching recorded release pass; kind-before-record mutation fails the recorded-release test (validation/mutations/kind-before-record.log).
- DONE: AC-4 — Inputs and holds.
  Fetch fallback, remote refs, timestamps, exact bounds, late committed asks, gh/no-origin/1000/malformed holds pass; reading records at TO fails the late-record fixture (validation/mutations/records-at-to.log).
- DONE: AC-5 — Repeats collapse.
  Committed sibling report hides #9, deleting it restores the line; uncommitted/self reports cannot hide it, and removing collapse fails (validation/mutations/collapse-removed.log).
- FAILED: AC-6 — The observer reports it.
  Fresh candidate Sonnet report emits all merge rows but falsely says audit exit 0; its follow-up confirms that was cut's pipeline status, not the audit's. Fresh base 0.35.0 emits no new merge rows. Both raw reports and the unchanged-report clarification are preserved under validation/.
- DONE: AC-7 — Words and scope.
  Exactly four product paths, unchanged workflow/budget, lint green; independent rendering of candidate outputs gives 54 windows, median 60/max 320 (without collapse 422). Adding one word per report violates both limits (validation/independent-words.json).
- DONE: Local package checks and affected-document review.
  27 commands succeeded; 1199 unittest cases, 11 skips. ADR/number/design/comment/dispatch/diff checks exit 0; comment ratio 0.5%. README is unaffected because its named-CI-command guidance remains accurate (validation/checks.json, suite-summary.json, doc-impact.json).
- SKIPPED: Independently reproduce FO-owned RoboRev and hosted CI.
  roborev not run: FO owns the local daemon review; no hosted CI invocation/cost measurement. Local Spacedock CLI 0.27.2 plus plugin files 0.27.3 do not establish hosted pinned-install behavior.
- DONE: Commit the stage report and evidence with the dispatched Spacedock state helper; preserve the no-product-push boundary.
  validation-1-message-1.md authorizes the helper's state-only push. Evidence lives only in this entity's validation/ folder; product branch and PR readiness remain unchanged.
- F1 Material: Native observer records pipeline success as audit success.
  Normal archive observer/unedited FO relay; observable false exit 0 versus direct exit 1; value-ac[AC-6] faithful audit evidence and contract[kc-dev-flow-2/skills/observer/SKILL.md#prove-each-finding]; trigger: validation/observer-candidate.md and observer-exit-clarification.md. No product repair made; FO disposition required.
- F2 Polish: Native observer abbreviates the specified per-row rule/evidence/source format.
  All eight exact finding tokens and all kind lists survive, with the shared rule above; no additional classification or repeat-collapse harm shown. Trigger and future Material threshold are in validation/README.md.

### Summary

Independent validation recommends REJECTED for b36fbeeec3a6699c0a82a021dc4ee0142410f6c8: deterministic behavior, historical replay, mutations and package checks passed, but the fresh native observer report did not faithfully record the audit's execution status. The word counts establish the accepted pinned simulation, not arbitrary model prose; no reported check proves authorization for missing-record merges. FO retains findings disposition, any repair/revalidation authorization, gate and delivery.

## Stage Report: implementation

- DONE: Dated addendum — 2026-11-08, implementation-1-message-1 and implementation-1-message-2.
  Local product head a43b537cd12d69a5ccfde38bf964c6ea35cb0de0, parent b36fbeeec3a6699c0a82a021dc4ee0142410f6c8, base 139feeaee7ce037a0c6535568cd6bd103155cbae; only observer/SKILL.md changed in this repair.
- DONE: Repair validation-1 F1 by recording the audit's own exit status before presentation.
  implementation/repair-2026-11-08/direct-execution.json records an unpiped exit 1; observer-report-1.md records own exit 1, carried 54/82 and the same eight tokens. observer-report-2.md retains the second attempt, also with own exit 1 but abbreviated/missing row fields.
- DONE: Keep the current observer SKILL.md wording if the existing tests and repository lint pass.
  Repository lint passes at 5933/5933 workflow words; test_merge_audit.py 17/17 and test_lint_skills.py 47/47 pass; the final row templates are retained under FO's message-2 instruction.
- DONE: Record both format runs as retained evidence and stop observer reruns.
  Both unedited reports, activity transcripts and tested skill snapshots are in implementation/repair-2026-11-08/; identity.json binds their shared exit-capture instructions to the committed skill. A third create call was rejected before an agent started and was not retried.
- SKIPPED: Claim a native pass for validation-1 F2 (row format, Polish).
  FO declines F2 at the gate per dispatch/implementation-1-message-2.md, committed in state 03db43d8600146efba9b6d4ec59f72425e8a138e. Both format results remain false in the retained comparisons; the final template has test/lint coverage without another native format run.
- DONE: Check the new report against a direct audit and retain a failing control.
  compare.py rejects validation-1's original exit-0 claim and accepts exit 1 for both repair samples; it still rejects their abbreviated rows. The negated phrase "not exit 2" is excluded after manual inspection, rather than treated as a second claimed status.
- DONE: Run the existing local package suite and required package guards.
  implementation/repair-2026-11-08/suite-summary.json: 27 commands succeeded, 1199 unittest cases including 11 skips; ADR lint checks 62 files, number guards report no findings, design check passes, comment ratio 2/431 = 0.5% below 5%, and diff check passes.
- DONE: Preserve approved scope and affected documents.
  Audit script, tests, CI, workflow and version files are byte-unchanged from b36fbeeec; the full PR still has only its four approved paths. doc-impact.json lists README.md, unaffected because its named-CI-command entry remains accurate.
- DONE: Commit locally and append this dated implementation addendum naming the new head.
  Product worktree is clean at a43b537cd12d69a5ccfde38bf964c6ea35cb0de0; original validation-1 REJECTED evidence and earlier implementation reports are preserved.
- SKIPPED: Push, PR edits, RoboRev, hosted CI and independent revalidation.
  No product or state push was run during this repair. roborev not run: FO owns the daemon review; hosted CI and its cost per PR were not measured. FO retains publication, revalidation and gate ownership.

### Summary

This dated addendum supersedes the earlier implementation report for the repaired head: F1 is proven by the direct run and the first fresh native observer, while F2 is a declined Polish item with both failed format samples retained. The current wording is kept under FO's test/lint condition; no additional observer rerun or push follows message-2, and the historical validation-1 verdict at b36fbeeec remains unchanged.

## Stage Report: validation

- DONE: Independent verdict on PR #809 head a43b537c against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Cycle 2, 2026-11-08: PASSED at a43b537cd12d69a5ccfde38bf964c6ea35cb0de0, base 139feeaee7ce037a0c6535568cd6bd103155cbae; full matrix, falsifiers and limits in validation-2/README.md; no new Material finding.
- DONE: Re-validate at the repair head: judge validation-1 F1's repair (the observer records merge_audit's own exit status) against the retained repair runs and one fresh observer run of your own, carry forward validation-1 evidence only where the diff from b36fbeeec leaves it unchanged, and treat F2 (row format) as declined by FO
  validation-2/native-execution.json proves the fresh observer ran unpiped and printed the immediate audit status 1 before cat; report and direct run agree. Both retained repair samples pass exit capture; original exit-0 report fails. Only the unchanged 0.35.0 native base control is carried forward; F2 remains declined.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Five-step validation-2/acceptance.sh ran in fresh bash, exit 0; acceptance.log holds observed output. Installed-package adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae exits 0, 62 records, no legacy; F3 below is Polish.
- DONE: AC-1 — Replay over the window that holds #785.
  New live GitHub run exits 1, carried 54/82, all eight specified gaps and exact named-kind sets; snapshot proves #727 carried. Removing release recognition exposes #707 (validation-2/replay-live.log, snapshot/, mutations/release-removed-snapshot-replay.log).
- DONE: AC-2 — Head differs is a violation line.
  A/B fixture and changed #727 head report a mismatch; PR-number-only mutation fails the head-boundary test (validation-2/mutations/pr-number-only.log).
- DONE: AC-3 — Named kinds come from their producers.
  Producer-prefix, learning-length, sync-title, renamed-release and recorded-Release cases pass; kind-before-record mutation fails (validation-2/mutations/kind-before-record.log).
- DONE: AC-4 — Inputs and holds.
  Fetch fallback/remote refs, timestamps, exact bounds, late committed asks and missing/malformed/network holds pass; records-at-TO mutation fails. Initial sandbox exit 2 remains separate from the approved live exit 1 (validation-2/mutations/records-at-to.log, replay-live-sandbox.log).
- DONE: AC-5 — Repeats collapse.
  Committed sibling report suppresses #9; deleting it restores the line; self/uncommitted reports cannot suppress it. Removing collapse fails (validation-2/mutations/collapse-removed.log).
- DONE: AC-6 — The observer reports it.
  One fresh Sonnet observer a45b399f-c67f-489c-9298-bd6dd9029a15 read the exact export: carried/kinds/eight no-ask tokens and one caveat survive; 13 comparisons pass. Original candidate fails the exit comparison; unchanged native base has no merge rows (validation-2/comparison-fresh.json, comparison-original-control.json, identity.json).
- DONE: AC-7 — Words and scope.
  Four product paths; only observer SKILL.md changed since b36fbeeec; workflow/budget unchanged. Independent 54-window simulation repeats median 60/max 320, uncollapsed 422; extra-word control exceeds both bounds. Final shorter templates fit this conservative rendering; no total model-prose guarantee (validation-2/independent-words.json).
- DONE: Local package checks and affected-document review.
  27 commands succeeded, 1199 unittest cases including 11 skips; lint/ADR/number/design/comment/doc/diff checks exit 0, seven dispatch records complete. README unaffected because its named-CI-command guidance stays correct (validation-2/suite-summary.json, checks.json, doc-impact.json).
- DONE: Preserve implementation limits and the exact product candidate.
  Matching records at current tips do not prove approval timing or question content; chat/other-repository state remain outside scope. Native full-report length and unrelated observer prose are not certified; product remains clean on its dispatched branch (validation-2/README.md, identity.json).
- SKIPPED: Independently reproduce FO-owned RoboRev and hosted CI.
  roborev not run: FO owns the daemon review. Hosted CI cost per PR not measured; existing narrow triggers/job unchanged except one stdlib test step. Local CLI 0.27.2/plugin 0.27.3 checks do not prove the hosted pinned installation.
- DONE: Append cycle-2 evidence and report using the prescribed task-scoped state commit.
  New proof is confined to observer-lists-unasked-merges/validation-2/ plus this body append; prior failure and repair reports remain unchanged. No product push, PR edit or review request.
- F3 Polish: Fresh observer prose counts 13 state refs where the tool output has 12.
  Trigger: validation-2/observer-candidate.md Coverage versus native-execution.json; no ref identity, classification, finding token or exit status is lost. Material only if a missing/misidentified ref changes the conclusion; no repair or format rerun made.

### Summary

Cycle 2 independently recommends PASSED for a43b537cd12d69a5ccfde38bf964c6ea35cb0de0: the repair closes validation-1 F1 with an actual unpiped native execution and matching report, while deterministic replay, falsifiers, suite and guards pass again. Validation-1's rejection remains historical, F2 stays declined by FO, and F3 is a nonblocking count slip for FO disposition. FO retains acceptance replay, gate and delivery authority; this report does not authorize merge.
