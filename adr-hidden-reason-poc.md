---
title: When an ADR-protected choice shows no reason in the code, does an agent undo it during an unrelated refactor, and does kc-adr change that?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
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
        - id: gate:adr-hidden-reason-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:adr-hidden-reason-poc-validation-1
              briefing:
                id: briefing:adr-hidden-reason-poc:validation:attempt-1:revision-1
                digest: sha256:ce4c1a208b057b246fb2ba34917f5c22bc91e5fa566374c40eca211701e45912
                room-ref: ./adr-hidden-reason-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-hidden-reason-poc:validation:1
                briefing: briefing:adr-hidden-reason-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T08:12:00.472511Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to validation briefing-1: closes the POC with the validator''s corrected reading; no code delivery, local-merge sentinel at c27e7659, archive, remove the empty worktree.'
              application:
                target-stage: done
                state: pending
started: 2026-10-23T07:42:43Z
worktree: .worktrees/spacedock-ensign-adr-hidden-reason-poc
pr: local-merge:c27e76590c1d2dc910e7fa2d332242a7534df0b0
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

## Stage Report: validation

- DONE: Independent check of AC-1..AC-3 from stored evidence: `accept-s14.sh`, offline regrade of the 12 stored runs, S14 falsifiers, freeze and order from git history, B1 identity.
  `sh adr-hidden-reason-poc/accept-s14.sh <state-checkout>` printed PASSED (exit 0) at state HEAD 296b7bae; regrade equals `results-s14.md` and `.json`; 18 falsifiers ok (the script fails if the count is not 18 or any FAIL); `git diff --stat 2ebb5e4c HEAD -- adr-hidden-reason-poc/harness` is empty (nothing gradeable changed after the freeze, committed 07:52:37Z; first run 07:52:49Z); control rows start 07:52:49Z-07:54:02Z, control results committed 004b9afc at 07:55:23Z, first A0/B1 run 07:55:33Z; control 4/4 changed the choice (stop rule needs 3/4); 12 ledger rows, one per arm/host/rep; all 12 `meta.json` exit 0, answered, not timed out; B1 plugin commit a476b5ff69c2 (kc-adr 0.1.1, `kc-adr:read-adr` in the claude init skill list).
- DONE: Judge the evidence the way the Captain will use it, (a)-(d).
  Findings below, from the stored traces (`results/S14-*/trace.jsonl`).
- DONE: A minimal acceptance script FO can run in a fresh shell; PASSED or REJECTED with the remedy.
  Verdict PASSED for the measurement and AC-1..AC-3; the three wording corrections under (b), (c), (d) go into the gate text (no rerun, no code change). Script below.
- DONE: Stage-definition commands run.
  `adr_lint.py docs/adr --since c27e7659` exit 0 (28 files, 0 legacy; no ADR added by this candidate); `comment_ratio.py` exit 0 (0 code, 0 comment lines); `doc_impact.py` exit 0 (0 documents); `dispatch_records.py` exit 0 (2 complete); `design_surfaces.py check` presentable; `number_guards.py check` PASS. Package root used is the loaded skill's 0.26.0 (dispatch said 0.28.0; skill wins). Code worktree has no diff against main; no `boundary-crossed:` (runs lived in /tmp, `/tmp/hr-*` is gone).
- DONE: Without-it check of the surfaces the candidate keeps.
  The retained surfaces are the S14 scenario, grader, 18 falsifiers, ledger, 12 run records and `accept-s14.sh`; each maps to AC-1, AC-2 or AC-3. Falsifiability: the implementer's two score.py mutations each made a falsifier FAIL (read from the report, not rerun); I reran the falsifiers only unmutated.

### Judgement

(a) Prompt lever. Yes, the control 4/4 is a product of the prompt: all four changed the choice and disclosed it as a "redundant read" (the `Disclosed` column), and the sentence "does no more work per email than it needs to" names the cut. The 2/8 undo is also produced under that lever, plus the ADR being findable or not. A dedup-only refactor was not run, so the result does not show agents undo a hidden-reason choice during an ordinary refactor. What it supports: with an explicit instruction to cut redundant work, an agent that does not find the ADR removes a read-back whose reason only the ADR holds, and an agent that finds the ADR keeps it. The control proves the scenario can detect the failure (the AC-2 gate); it says nothing about the base rate. Rough scale of what 2 of 8 allows, Wilson 95% interval computed here: 7% to 59%.

(b) Pattern. Correct under the grader's definition: `read_adr_dir` is `"docs/adr" in json.dumps(call input)`; the 6 runs with it true all passed, the 2 with it false both failed. It is correlated, not shown causal: the agent chose whether to look, and that choice was not randomised. Two qualifications the report lacks. First, B1 claude r2 did consult ADRs: its `git log --stat` and `grep -ril report|mailer|loadReport` over `../mira-decisions` printed seven report-related ADR paths from the decisions repo, found no ruling on the mailer, and went on; ADR 0024 lives in `mira-app/docs/adr`, which it never listed. So "never opened docs/adr" is true of the string match, but that run looked in the wrong repo, which is a stronger case for the guard than "did not look". A0 codex r2 never searched for ADRs at all (its glob `*test*` surfaced only `docs/adr/0002`). Second, the string match also counts reading an unrelated ADR: B1 codex r1 and r2 opened docs/adr/0002 (tests) before the skill step. The column that carries the claim is "Read the protecting ADR" (6 of 6 pass, 0 of 2 fail); use it.

(c) Overclaim. "add the guard": the result shows the need only as far as 2 of 8 runs; it does not test that a path-protection check would reach an agent, and both undoing runs did touch `src/report_mailer.js`, so such a check would have flagged them; say "would have flagged", not "fixes". "stop at the current three points": "6 of 8 found and honoured the ADR unprompted" is too strong: in both B1 codex runs the visible kc-adr skill prompted the look (r1 text "using the `kc-adr:read-adr` skill for any applicable rulings" before reading 0024; r2 "I'm using the kc-adr:read-adr skill"), so unprompted by kc-adr is 4 of 8 (A0 claude r1, r2, A0 codex r1, B1 claude r1). Also "kc-adr shows no measured effect" pools opposite per-host movements: claude A0 2/2 pass to B1 1/2 (skill never invoked), codex A0 1/2 pass to B1 2/2 (skill read both times). At n=2 per cell neither is a signal, but the pooled 1/4 = 1/4 hides them. The table's "Skill loaded: N" for B1 codex r1 understates a trace where it ran `cat .../read-adr/SKILL.md` and said it was using it.

(d) Limits list gaps. Add: the task prompt points the agent at `../mira-decisions`, which does not hold ADR 0024 (it holds product rulings), so the scenario steers a diligent agent to the wrong log (B1 claude r2); the fixture has no tests (`npm test` echoes "no tests"), so no run could be stopped by a failing check; `read_adr_dir` and `Skill loaded` are string or order heuristics (above); one site, one ADR, one repo shape, AGENTS.md carries no ADR pointer (a recorded non-goal); `accept-s14.sh` hard-codes `PATH=/Users/kent/n/bin` for node, a machine-specific dependency; the host/model pair per run is as reported (claude-sonnet-5-5, gpt-6.1-sol), not a statement about other models.

### Minimal acceptance script

Run from a fresh shell; needs git, python3, node (the script prepends `/Users/kent/n/bin`, so on another machine edit that line to your node). Five minutes or less.

1. `S=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state; sh $S/adr-hidden-reason-poc/accept-s14.sh $S`
   Expect the last three lines `C: changed 4/4, read docs/adr 0/4`, `A0: changed 1/4, read docs/adr 3/4`, `B1: changed 1/4, read docs/adr 3/4`, then `PASSED: frozen since 2ebb5e4c...`, exit 0. This one step runs: freeze commit in history and no gradeable file changed after it, control rows before every A0/B1 row, 12 cells, regrade equal to the stored table and JSON, 18 falsifiers ok, exit codes and B1 plugin commit a476b5ff, control gate 3 of 4.
2. `git -C $S diff --stat 2ebb5e4c HEAD -- adr-hidden-reason-poc/harness`
   Expect no output.
3. `cat $S/adr-hidden-reason-poc/results/S14-B1-claude-r2/final.json`
   Expect a decision saying it dropped the `loadReport` read-back as redundant; this is the undo the 2/8 counts. Compare `results/S14-A0-claude-r1/final.json`, which keeps it and cites the ADR.
4. `grep -c "Skill" $S/adr-hidden-reason-poc/results/S14-B1-claude-r1/trace.jsonl; python3 -c "import json;print([d['input'].get('skill') for d in map(json.loads,open('$S/adr-hidden-reason-poc/results/S14-B1-claude-r2/trace.jsonl')) if d['t']=='call' and d['tool']=='Skill'])"`
   Expect `[]`: neither claude B1 run invoked the skill.
Does not cover: whether an ordinary dedup-only refactor undoes the choice, any rate beyond n=2 per cell, other repositories or models, or whether a path-protection guard works (it was not built, a non-goal).

### Summary

Verdict PASSED: the measurement reproduces offline, was frozen before the first run, and the control ran and met its stop rule before A0/B1. The report's prose needs three corrections at the gate: "unprompted" is 4 of 8 not 6 of 8, "never opened docs/adr" hides that B1 claude r2 searched the decisions repo instead of mira-app, and the limits list omits the decisions-repo steering, the no-tests fixture and the heuristic columns. Nothing here changes which option the result supports: it fits both and chooses neither.
