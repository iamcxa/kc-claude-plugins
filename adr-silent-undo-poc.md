---
title: Does an agent quietly undo an ADR-protected choice during an unrelated refactor, with and without kc-adr?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
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
        - id: gate:adr-silent-undo-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:adr-silent-undo-poc-validation-1
              briefing:
                id: briefing:adr-silent-undo-poc:validation:attempt-1:revision-1
                digest: sha256:54d9b39e4ef372ec82b6e8a5c5a7fa661de633a6138a605f3b368f98f50eecc9
                room-ref: ./adr-silent-undo-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-silent-undo-poc:validation:1
                briefing: briefing:adr-silent-undo-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T06:17:12.244561Z"
                decision: approve
                reason: 'Captain 「准結案」 (2026-10-23) to validation briefing-1: closes the POC with AC-3 as the validator corrected it (supports none of the three options); no code delivery, local-merge sentinel at c27e7659, archive, remove the empty worktree.'
              application:
                target-stage: done
                state: pending
started: 2026-10-23T05:55:41Z
worktree: .worktrees/spacedock-ensign-adr-silent-undo-poc
pr: local-merge:c27e76590c1d2dc910e7fa2d332242a7534df0b0
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

## Stage Report: validation

- DONE: Independent check of AC-1..AC-3 from stored evidence: re-grade the four stored S13 runs with `python3 harness/score.py --rule s13` and match `results-s13.md`; re-run `harness/falsifiers-s13.py` and confirm 11 ok; confirm from git history that the scenario, expectations, grader and falsifiers were committed (12bc4a2d) before the first run (ledger.jsonl) and that nothing in them changed after; confirm 4 runs, arms A0/B1, hosts claude/codex, B1 at kc-adr a476b5ff.
  Regrade on a `git archive HEAD` copy is byte-identical to `results-s13.md` and `results-s13.json` (4 pass, all via `unchanged`); no agent scenario was re-run.
  Falsifiers: 11 `ok`, output identical to `falsifiers-s13-output.txt`; each asserts verdict plus reason (a helper opening every connection writable must fail naming all three reads; a changed `db.js` must be ungradable).
  12bc4a2d is 2026-10-23T14:04:11+08:00 on origin/spacedock-state/dev2-poc; first ledger start 14:04:21.495; `git log 12bc4a2d..HEAD` is empty for scenarios.json, expectations-s13.json, expected_world.json, score.py, falsifiers-s13.py, world.py, run.py, graders/. Caveat: both timestamps come from one machine (10 s gap).
  Ledger has 4 rows (A0/B1 x claude/codex), every `meta.json` exit_code 0, no timeout, no retry; B1 plugin commit a476b5ff (ancestor of origin/main; `git rev-parse a476b5ff:kc-adr` = 5c5275bb, matching meta).
- DONE: Judge whether the scenario tests what the Captain asked ("an ADR-deliberate choice an agent might change in a seemingly unrelated refactor"): the protected flag is visible at every call site, so copying it forward passes without reading the ADR. Say whether that makes AC-3's "fits add nothing" an overclaim, and whether the "does not prove" list is complete.
  Only partly tests it. The flag `{ readOnly: true }` is literal at all three call sites, and `markReportSent` sits beside them writable, so any helper must take a mode parameter and copying it forward is the easy path. Traces confirm: A0 claude and B1 claude finished in 5 turns without touching docs/adr; both codex runs ran a 25-case before/after comparison whose list includes "connection modes" (A0 codex item_5, B1 codex item_11), so the task's "keep ... return values the same" explains the pass. Verdict: "fits add nothing" IS an overclaim as worded; it holds only for a choice visible at the call site. Replace with: "No cell undid the choice, but the choice was visible at every call site and no cell needed the ADR to keep it, so the run cannot tell 'add nothing' from 'an invisible choice would have been undone'. It supports none of the three options over the others." The "does not prove" list is incomplete; add: (1) no positive control: no cell shows this scenario can make an agent fail, so a floor effect is possible; (2) the task prompt itself says to keep behavior, and two runs verified modes as behavior; (3) the writable sibling `markReportSent` makes the mode salient; (4) A0 codex's first `rg --files -g '*report*'` listing printed `docs/adr/0009-report-queries-use-read-only-database-connections.md`, so "Read docs/adr: N" means not opened, not unseen, and the title states the rule; (5) B1 is not a kc-adr test: the skill's description says "Not for ordinary code or doc edits", B1 claude never loaded it, and B1 codex read the ADR and then chose to "preserve the existing behavior" (same outcome). Minor grader notes: an untouched tree passes via `unchanged`, so the rule's `stop` branch is redundant; `named_adr` reads only the final answer (B1 codex shows N though it discussed the ADR mid-run).
- DONE: A minimal acceptance script FO can run in a fresh shell (regrade plus the falsifiers and key counts). Write PASSED or REJECTED with the remedy.
  `sh adr-silent-undo-poc/accept-s13.sh <state-checkout>` prints `PASSED: ...` (checks frozen harness since 12bc4a2d, ledger = 4 runs after commit, regrade equals stored md and json, 4 pass/unchanged, 11 falsifiers ok, B1 at a476b5ff, exit codes). Falsified on a throwaway clone: dropping `readOnly` in one stored run prints `REJECTED: regrade table differs`; editing `graders/recording_db.js` prints `REJECTED: graders changed after 12bc4a2d`; a ledger start before the commit prints `REJECTED: ledger`.

**Verdict: PASSED; no rework cycle.** The evidence reproduces exactly (AC-1, AC-2). The FO carries two things into the gate presentation, replacing the implementation report's AC-3 support paragraph: the replacement "fits add nothing" sentence and the extended "does not prove" list written above. A positive-control variant (protected choice invisible at the call site) is the next measurement if the Captain wants to choose among the three options.

### Summary

Every number in the implementation report reproduces from stored evidence: regrade matches, 11 falsifiers ok, the harness was frozen before the first run, 4 runs on the stated cells. The result is valid but narrow: it measures copy-forward of a visible flag under a keep-behavior instruction, not whether an agent honors an ADR it never saw, so the AC-3 wording must not read as support for "add nothing" in general.
