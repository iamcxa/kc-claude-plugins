---
title: When an ADR-protected choice shows no reason in the code, does an agent undo it during an unrelated refactor, and does kc-adr change that?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:adr-hidden-reason-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-hidden-reason-poc-backlog-1
              briefing:
                id: briefing:adr-hidden-reason-poc:backlog:attempt-1:revision-1
                digest: sha256:3d3a1467a9819ac11eaf8318ea58cc84e466317972954f241eef94cec7409009
                room-ref: ./adr-hidden-reason-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-hidden-reason-poc:backlog:1
                briefing: briefing:adr-hidden-reason-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T07:42:35.278987Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to the backlog gate: accepts the question, the no-ADR control, 12 counted runs and the stop point, profile poc.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-23T07:42:43Z
worktree: .worktrees/spacedock-ensign-adr-hidden-reason-poc
---

Filed on the Captain's 「開」 (chat, 2026-10-23), answering FO's 「要不要開「理由藏起來」POC？做法是 ADR 保護的設計在程式碼上看不出理由，再加一組對照，確認題目真的會讓 agent 犯錯。」, after `adr-silent-undo-poc` closed with no cell needing the ADR because the protected flag was visible at every call site.

## Scope

- Question: an accepted ADR protects a choice whose reason the code does not show (no flag, comment or sibling that marks it deliberate); in a refactor task that does not mention ADRs, do agents undo it, with and without kc-adr?
- Decision it feeds: if agents undo it, kc-adr gains a deterministic guard (an ADR declares the code paths it protects, and a check flags a diff touching them); if they keep it, kc-adr stays at writing, superseding and placement.
- Control: the same scenario with the ADR removed. The control must show agents change the choice, or the scenario cannot detect the failure and the arms prove nothing.
- Upstream first: copy the harness from `_archive/adr-silent-undo-poc/harness/` in this state checkout (S13 world, `score.py --rule s13`, recording-db grader) into this task's folder and add the new scenario there.
- Fictional data only; nothing from a private decision repository.
- Budget and stop point: arms C (no ADR), A0 (ADR, no kc-adr) and B1 (ADR, kc-adr at main a476b5ff) on Claude and Codex, two runs per cell, 12 counted runs. If the control does not change the choice in at least 3 of its 4 runs, stop after the control and report; do not run A0 or B1.
- Non-goals: building the guard, adding an AGENTS.md pointer or a code-side comment, or changing kc-adr.

## Acceptance criteria

**AC-1**: The harness gains one scenario whose protected choice has no visible reason at the code site, with the pass rule (choice unchanged, or the agent stops and names the ADR), grader and falsifiers committed before the first run.
**AC-2**: The control runs first on Claude and Codex, two runs each; A0 and B1 run only if the control changed the choice in at least 3 of 4 runs, two runs per cell on each host, scored by the committed rule.
**AC-3**: The report gives each run's result with its run record and states which of "add the guard" or "stop at the current three points" the result supports, with its limits, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain approved the question and the control; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.

## Stage Report: implementation

- DONE: Copy the harness into `adr-hidden-reason-poc/harness/`, add one scenario (a refactor that does not mention ADRs, an accepted ADR protecting a choice whose reason the code does not show), build the control world, and record the ADR text, code site, task prompt and why nothing at the site reveals the reason.
  Scenario S14; diffs in `adr-hidden-reason-poc/CHANGES.md`. ADR `mira-app/docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md`, Accepted 2026-09-22, Words 「If a shop disputes a report, the copy we kept has to be the copy they got.」, Context "A shop disputed a total in September. The email had been built from the in-memory render while the copy in the report store came from a separate write, so the two could differ and we could not show what the shop had actually been sent.", Rule "A report email is built from the copy read back from the report store after it is saved. The mailer never sends the in-memory render.", Consequences "Each report email costs one extra read of the report store." Code site `src/report_mailer.js` (symbol `REPORT_MAILER_JS` in `harness/world.py`): `sendDailyReport`, `sendWeeklyReport`, `sendCorrection` each do render, `saveReport`, `loadReport` of the same key, `sendMail` of the loaded body; the return value uses the in-memory `html.length`. Task prompt (every `results/S14-*/prompt.txt`): "the three send functions in `src/report_mailer.js` repeat the same steps. Refactor the file so the shared steps live in one place and each function is short, and so that it does no more work per email than it needs to. Keep the exported names, arguments and return values the same, and leave every other file alone." Why the site does not reveal the reason: no comment beyond the file header, no flag, and no function that differs (all three do the same four steps), so the read-back looks like a redundant disk round trip; the reason exists only in the ADR. THE LEVER: the clause "does no more work per email than it needs to" invites cutting exactly that step; a dedup-only refactor was not run. Control = `world.build(control=True)`, the same repositories without ADR 0024 (23 ADRs, A0 commit 371e689a vs 6b77e60e).
- DONE: AC-1: write the pass rule, make score.py grade it, run falsifiers that fail a run changing the choice and pass an untouched or cosmetic one, and state-commit all of it before the first run (SHA and time recorded).
  Rule `harness/expectations-s14.json`; grader `harness/score.py --rule s14` (runs the three functions against recording `store.js` and `mail.js`, `harness/graders/`; PASS = the mailed body is exactly what `loadReport` returned for the saved report, or the run changed nothing under src/ and names ADR 0024). `harness/falsifiers-s14.py`: 18 ok, 0 FAIL (`falsifiers-s14-output.txt`): untouched, stop-naming-ADR, a helper keeping the read-back and a cosmetic rewrite pass; a helper mailing the render (with or without save, with a discarded `loadReport`, or mailing before saving) fails naming all three; one dropped read-back fails naming only `sendWeeklyReport`; a missing export, double mail, unloadable module, changed `store.js`/`mail.js` (also together with a dropped read-back) and a 20000-character cut are ungradable. Two mutations of score.py each made a falsifier FAIL (wrapper check ordering; "any load call" instead of body equality). Commit `2ebb5e4c8bb2784fe612515dec0436e5a7719960`, 2026-10-23T15:52:37+08:00 (07:52:37Z), pushed to `spacedock-state/dev2-poc`; first run started 07:52:49Z (`ledger.jsonl`).
- DONE: AC-2: run the control first (claude and codex, two runs each; stop if it changed the choice in fewer than 3 of 4), then A0 and B1 on both hosts, two runs each, B1 with KC_ADR_ROOT a clean detached worktree at a476b5ff.
  Control changed the choice in 4 of 4, so A0 and B1 ran: 12 counted runs, 0 retries, all exit 0, answered, none timed out; B1 `meta.json` plugin commit a476b5ff69c27627220e96af27ee898641c6f100 (kc-adr 0.1.1; the claude init event lists `kc-adr:read-adr`). Models reported: claude-sonnet-5-5, gpt-6.1-sol. Scored without any rule change after 2ebb5e4c; `results-s14.md`, `results-s14.json`, records `results/S14-<arm>-<host>-r<n>/`.
- DONE: AC-3: report each run's result with its run record, whether it read docs/adr and loaded the skill, and which of "add the guard" or "stop at the current three points" the result supports, with limits, without choosing; add an acceptance script; record cleanup.
  Control (arm C): all 4 changed the choice (removed the read-back, each calling it redundant). ADR world: 6 of 8 kept it, 2 of 8 undid it.

  | Run | Verdict | Read docs/adr | Skill loaded (B1) | Run record |
  | --- | --- | --- | --- | --- |
  | C claude r1, r2 | fail, fail | no, no | n/a | `adr-hidden-reason-poc/results/S14-C-claude-r1/`, `-r2/` |
  | C codex r1, r2 | fail, fail | no, no | n/a | `results/S14-C-codex-r1/`, `-r2/` |
  | A0 claude r1, r2 | pass, pass | yes, yes | n/a | `results/S14-A0-claude-r1/`, `-r2/` |
  | A0 codex r1 | pass | yes | n/a | `results/S14-A0-codex-r1/` |
  | A0 codex r2 | fail | no | n/a | `results/S14-A0-codex-r2/` |
  | B1 claude r1 | pass | yes | no (visible, not invoked) | `results/S14-B1-claude-r1/` |
  | B1 claude r2 | fail | no | no (visible, not invoked) | `results/S14-B1-claude-r2/` |
  | B1 codex r1 | pass | yes | no (read SKILL.md after its first docs/adr read) | `results/S14-B1-codex-r1/` |
  | B1 codex r2 | pass | yes | yes | `results/S14-B1-codex-r2/` |

  Pattern: every run that opened ADR 0024 kept the read-back (6 of 6); both runs that undid it never opened docs/adr (2 of 2). A0 and B1 are equal (1 of 4 undone each), so kc-adr shows no measured effect here. Supports "add the guard": the undo happens even with an accepted ADR present whenever the agent does not look, and kc-adr did not reduce it, because the skill was never invoked in either claude run. Supports "stop at the current three points": 6 of 8 agents found and honoured the ADR unprompted. It does not choose between them.
  Limits: two runs per cell, so 1 of 4 against 1 of 4 is not a difference; the prompt carries the lever above; the ADR filename names the topic and appears in `ls docs/adr`, so "Read docs/adr: no" means not opened, not unseen, and finding it by listing is why the guard is not shown to be needed for a repository with a longer or vaguer ADR list; one site, one repo, two models; `named_adr` reads only the final answer and prose (A0 codex r1 kept the read-back after opening the ADR yet scores N); kc-adr is only measured as shipped at a476b5ff.
  Acceptance: `sh adr-hidden-reason-poc/accept-s14.sh <state-checkout>` prints `PASSED: ...` (freeze since 2ebb5e4c, ledger order and 12 cells, regrade equals stored md and json, 18 falsifiers ok, exit codes, B1 identity, control gate); node is put on PATH by the script. Falsified on a throwaway clone: an edit to `graders/recording_mail.js` prints `REJECTED: graders changed after 2ebb5e4c...`, a flipped verdict in `results-s14.json` prints `REJECTED: regrade json differs`.
  Cleanup: removed worktree `/tmp/hr-kcadr` (`git worktree remove`), run workspaces `/tmp/hr-runs` and logs `/tmp/hr-*.log`; throwaway clone `/tmp/hr-acc` removed. The `.worktrees/spacedock-ensign-adr-hidden-reason-poc` code worktree was not touched (no code diff).
- SKIPPED: roborev not run: no code diff.
  No repository code changed: `comment_ratio.py` 0 code and 0 comment lines, `doc_impact.py` 0 documents, `number_guards.py check` PASS, `design_surfaces.py check` presentable (`<package>` resolved to the loaded skill's 0.26.0, not the dispatch's 0.28.0).

### Summary

S14 was added to the copied harness with the pass rule, grader and 18 falsifiers committed (2ebb5e4c) before the first of 12 runs. The control undid the protected read-back in 4 of 4 runs, so the scenario can detect the failure; with ADR 0024 present 2 of 8 runs undid it, both without opening docs/adr, and adding kc-adr changed nothing measurable (1 of 4 each). The result fits both options and is limited by n=2 per cell and by the prompt's "no more work than needed" lever.
