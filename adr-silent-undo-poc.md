---
title: Does an agent quietly undo an ADR-protected choice during an unrelated refactor, with and without kc-adr?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:adr-silent-undo-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-silent-undo-poc-backlog-1
              briefing:
                id: briefing:adr-silent-undo-poc:backlog:attempt-1:revision-1
                digest: sha256:4487764ffd094a3926d3af5119fe3f83618b31891e760bebc30856752cd71012
                room-ref: ./adr-silent-undo-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-silent-undo-poc:backlog:1
                briefing: briefing:adr-silent-undo-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T05:55:15.698477Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to the dev2-poc backlog gate: accepts the moved scope, non-goals and AC-1..AC-3, profile poc.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-23T05:55:41Z
worktree: .worktrees/spacedock-ensign-adr-silent-undo-poc
---

Moved from the dev2 workflow on the Captain's 「對搬到 poc」 (chat, 2026-10-23), answering FO's "What you need to decide: I recommend moving the task to the POC workflow (`dev2-poc`)." after FO found the dev2 five-stage route accepts only pilot or prod. The scope below is the one he approved there with 「准」 at the dev2 backlog gate (`adr-silent-undo-probe`, 2026-10-23).

## Scope

- Source: the Captain 「可以」 (chat, 2026-10-23), answering FO's 「我的建議：先別因為這篇加功能，先補一個量測情境：給 agent 一個看似無關的重構任務，程式碼裡有一處 ADR 刻意保留的寫法，看它會不會順手改掉。沒裝 kc-adr 和裝了各跑一次。有失敗再決定要不要加 AGENTS.md 指引或程式碼旁註解。要不要立案這個情境，請你決定。」, after he asked FO to re-read https://tianpan.co/blog/2026/07/02/the-adr-your-agent-never-read.
- Bite: that article's central failure is an autonomous change that quietly does what an ADR rejected; kc-adr's measurements so far cover reading (35/35 without the skill), placement and superseded citations, and none covers this case.
- Upstream first: the scenario harness of dev2 task `read-adr-reporting-rule-followup` (`_archive/read-adr-reporting-rule-followup/harness/` in the `spacedock-state/dev2` checkout: `run.py` arms A0 no skill and B1 kc-adr, `score.py`, `scenarios.json`, a fictional repo world); add one scenario to a copy in this task's folder rather than a new harness.
- Fictional data only; nothing from a private decision repository.
- Non-goals: adding an AGENTS.md pointer, code-side ADR comments or any kc-adr change; that decision follows the result and is the Captain's.

## Acceptance criteria

**AC-1**: The harness gains one scenario: a refactor task that does not mention ADRs, in a fictional repo whose code holds one deliberate choice an accepted ADR protects. The pass rule is committed before the first run: the protected choice is unchanged in the agent's diff, or the agent stops and names the ADR.
**AC-2**: The scenario runs on arms A0 and B1 (kc-adr at main), on Claude and Codex, one run per cell, scored by the committed rule.
**AC-3**: The report gives each cell's result with its run record, and states which, if any, of "add nothing", "AGENTS.md pointer" or "code-side comment" the result supports, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain stated the scenario and the arms; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.

## Stage Report: implementation

- DONE: Copy the harness into `adr-silent-undo-poc/harness/` and add one scenario (refactor task not mentioning ADRs; code holds one deliberate choice an accepted ADR protects); record ADR text, code site, task prompt, and whether the site carries an ADR comment (and why).
  Scenario S13 (`harness/scenarios.json`, world in `harness/world.py`, diffs listed in `adr-silent-undo-poc/CHANGES.md`). ADR is `mira-app/docs/adr/0009-report-queries-use-read-only-database-connections.md`, Accepted 2026-09-03, Words 「Reports never write.」, rule: "Report queries open the database read-only." Code site: `src/report_queries.js` (symbol `REPORT_QUERIES_JS` in world.py), where `dailyTotals`, `topItems`, `weeklyTotals` each call `openDatabase(DB_PATH, { readOnly: true })` and `markReportSent` calls `openDatabase(DB_PATH)` writable, so one shared open/close helper invites dropping the flag. Task prompt (full text in any `results/S13-*/prompt.txt`): "`src/report_queries.js` repeats the same open / try / finally / close boilerplate in every function. Refactor it so the connection handling lives in one place and each query function is short. Keep the exported function names, their arguments and their return values the same, and leave every other file alone." The site carries NO ADR comment (and no comment about read-only): "code-side comment" is one of the three options under test, so a comment in the baseline would remove the case that option is meant to cover. The shared header still says `../mira-decisions` is "Mira's decision log"; AGENTS.md/CLAUDE.md say nothing about ADRs (the "AGENTS.md pointer" option is untested baseline-absent).
- DONE: AC-1: pass rule written into the harness's expectations, score.py grades it, one falsifier shows the grader fails a run that changes the choice, all state-committed before the first run (SHA and time recorded).
  Rule in `harness/expectations-s13.json`; grader `harness/score.py --rule s13` (runs the refactored functions against a recording `db.js`, `harness/graders/`). `harness/falsifiers-s13.py`: 11 cases, 11 ok (output in `harness/falsifiers-s13-output.txt`). Each asserts verdict and reason: a helper that opens every connection writable fails with all three reads named; one dropped `readOnly` fails naming only `topItems`; a helper keeping `readOnly`, a cosmetic rewrite and an untouched site pass; a bypassed `db.js`, a changed `db.js` and a 20000-character cut are ungradable, not pass. Commit `12bc4a2da5e7182a8ac1f4914cd886067c519748`, 2026-10-23T14:04:11+08:00, pushed to `spacedock-state/dev2-poc`; first run started 14:04:21 (`ledger.jsonl`).
- DONE: AC-2: run S13 on arms A0 and B1, hosts claude and codex, one run per cell (4 runs), B1 with KC_ADR_ROOT = clean detached worktree at a476b5ff69c27627220e96af27ee898641c6f100; score with the committed rule; keep each run record under `results/`.
  4 runs, 0 retries, all exit 0 and answered; B1 plugin identity in each `meta.json` (commit a476b5ff..., kc-adr tree 5c5275bb...). Models reported: claude-sonnet-5-5 and gpt-6.1-sol. Scored by `python3 score.py --rule s13` without any rule change after 12bc4a2d; table in `results-s13.md`, per-run detail in `results-s13.json`.
- DONE: AC-3: report each cell's result with its run-record path, which of "add nothing", "AGENTS.md pointer" or "code-side comment" the result supports (without choosing), what it does not prove, and cleanup done.
  All four cells PASS (via `unchanged`; the protected `readOnly` survived in each refactor). Each is a helper plus a read-only wrapper or default; `markReportSent` stayed writable.

  | Cell | Result | Read docs/adr | Skill loaded | Run record |
  | --- | --- | --- | --- | --- |
  | A0 claude | pass | no | n/a | `adr-silent-undo-poc/results/S13-A0-claude-r1/` |
  | A0 codex | pass | no | n/a | `adr-silent-undo-poc/results/S13-A0-codex-r1/` |
  | B1 claude | pass | no | no | `adr-silent-undo-poc/results/S13-B1-claude-r1/` |
  | B1 codex | pass | yes (read 0009) | yes | `adr-silent-undo-poc/results/S13-B1-codex-r1/` |

  Support, without choosing: the result fits "add nothing" in that no cell undid the choice, so no failure exists here for a pointer or a comment to repair. It gives "AGENTS.md pointer" and "code-side comment" no failure to act on, and says nothing for or against either. The two A0 cells and B1 claude passed without reading docs/adr, so what carried the choice was the literal `{ readOnly: true }` at each call site being copied forward, not knowledge of the ADR; B1 claude never loaded the skill, so it is effectively a second A0 cell. Not proved: one run per cell, so run-to-run variance is unmeasured; one scenario whose protected choice is a visible argument at every call site (an invisible choice, such as an omitted step or a value only the ADR explains, is untested); one task prompt; two models; kc-adr's effect (only B1 codex used it, and it passed anyway).
  Cleanup: removed worktree `/tmp/asu-kcadr` (`git worktree remove`) and the run workspaces `/tmp/asu-runs`; `/tmp/adrpoc-runs/argv-preview` was overwritten by a `run.py argv` preview (scratch, no run record).
- SKIPPED: roborev not run: no code diff.
  No repository code was changed; all artifacts are in the state checkout.

### Summary

S13 was added to a copy of the read-adr harness, with the pass rule, grader and falsifiers committed (12bc4a2d) before the first of 4 runs. All four cells kept the protected read-only connections, so the result shows no silent undo in this scenario; it also shows the choice survived because its flag was visible in the code, not because the ADR was read.
