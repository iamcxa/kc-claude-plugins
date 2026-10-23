---
title: Does a code-side pointer to the protecting ADR stop an agent from undoing a choice whose reason the code does not show?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:adr-code-pointer-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-code-pointer-poc-backlog-1
              briefing:
                id: briefing:adr-code-pointer-poc:backlog:attempt-1:revision-1
                digest: sha256:ce770ddd976f4aaef4a1e368d2a6e53504ca4d3f7f3d62d81fd5880bb6e209f9
                room-ref: ./adr-code-pointer-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-code-pointer-poc:backlog:1
                briefing: briefing:adr-code-pointer-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T08:26:09.734904Z"
                decision: approve
                reason: 'Captain 「可以，先測試這個，然後再考慮其他方案。」 (chat, 2026-10-23), answering FO''s question quoted in this briefing: accepts the comment arm, Claude and Codex x2, 4 runs, profile poc.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:adr-code-pointer-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:adr-code-pointer-poc-validation-1
              briefing:
                id: briefing:adr-code-pointer-poc:validation:attempt-1:revision-1
                digest: sha256:a6c20e79b55168cfbbb8a7e8e0a17f6a7f1331c71a79f8a6f98369c19816462a
                room-ref: ./adr-code-pointer-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-code-pointer-poc:validation:1
                briefing: briefing:adr-code-pointer-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T08:47:04.31858Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to validation briefing-1: closes the POC with the validator''s reading; no code delivery, local-merge sentinel at c27e7659, archive, remove the empty worktree.'
              application:
                target-stage: done
                state: pending
started: 2026-10-23T08:26:43Z
worktree: .worktrees/spacedock-ensign-adr-code-pointer-poc
---

Filed on the Captain's 「可以，先測試這個，然後再考慮其他方案。」 (chat, 2026-10-23), answering FO's 「我建議的下一步：撤回這道關卡，先開一個 POC。同一題，在程式碼旁加上那行註解，Claude 和 Codex 各跑 2 次，共 4 次。…要撤回這道關卡、改開註解 POC 嗎？」, after FO proposed a code-side comment as a cheaper alternative to an edit-time hook (dev2 task `adr-protected-path-guard`, its backlog gate withdrawn).

## Scope

- Question: in the archived S14 scenario of `adr-hidden-reason-poc`, add one line at the protected code site in `src/report_mailer.js` pointing at the protecting ADR (for example `// read-back is deliberate: see docs/adr/0024-…`), with the ADR present and kc-adr not installed; does the agent keep the choice?
- Comparison: the archived S14 A0 cells (ADR present, no comment, no kc-adr): 1 of 4 undone; the archived control (no ADR): 4 of 4 undone.
- Decision it feeds: if the comment holds, kc-adr's writing rule asks for a code-side pointer and the linter checks that each declared file carries it, with no hook; if it does not, the edit-time hook in `adr-protected-path-guard` is reconsidered with the other options the Captain named.
- Upstream first: copy `_archive/adr-hidden-reason-poc/harness/` in this state checkout into this task's folder; the pass rule, task prompt and grader stay as archived; the only world change is the comment line.
- Budget and stop point: one arm (comment), Claude and Codex, two runs each, 4 counted runs; an infrastructure failure gets one retry per cell, then stop and report.
- Fictional data only. Non-goals: building the linter check or a hook; changing kc-adr.

## Acceptance criteria

**AC-1**: The harness copy differs from the archived one only by the comment line at the protected site and the new arm's wiring; the diff is committed before the first run, and the archived falsifiers still pass.
**AC-2**: The comment arm runs on Claude and Codex, two runs each, scored by the archived pass rule.
**AC-3**: The report gives each run's result with its run record, whether the agent kept, moved or deleted the comment, and whether it read the ADR, and states which of "code-side pointer" or "reconsider the hook" the result supports, with limits, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain approved the arm and the run count in chat; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.

## Stage Report: implementation

- DONE: Copy the harness ... add one arm (S14 ADR world, ADR 0024 present, kc-adr not installed, one comment line at the protected read-back site pointing at the ADR's path); change nothing else; record the exact comment text and placement.
  Harness copied verbatim (f087b7ae), then arm `P` added (29fae059). Comment text, one line, indented two spaces: `// Reading the report back from the store before mailing is deliberate: see docs/adr/0024-report-emails-are-sent-from-the-stored-copy.md`. Placement: directly above `const body = await loadReport(...)` in `sendDailyReport`, the first of three read-backs; `sendWeeklyReport` and `sendCorrection` carry no comment (one line, three sites). I first built it as a file-header line and moved it before any run, because "at the read-back site" reads as adjacent.
- DONE: AC-1 commit the harness copy and the arm before the first run; diff against the archived harness; re-run the archived S14 falsifiers; record SHA and time.
  Frozen at 29fae05982e6fe5d45d97c5bb1e3d6ac05c09107, 2026-10-23T16:32:17+08:00; first run started after it (ledger). `diff -r` against `_archive/adr-hidden-reason-poc/harness`: only `world.py` (pointer variant + flag), `run.py` (arm P, one argument), `score.py` (`"P"` in the sort list), `expected_world.json` (`A0_pointer` bf505ff6...) differ; `world-diff.txt` shows the P world differs from A0 by that one line. `falsifiers-s14.py`: 18 ok, 0 FAIL, output identical to the archived output.
- DONE: AC-2 run the comment arm on claude and codex, two runs each (4 counted runs), scored by the archived pass rule; keep each run record under `adr-code-pointer-poc/results/`.
  4 runs, all exit 0, answered, no retry, no infrastructure failure: `results/S14-P-claude-r1`, `-claude-r2`, `-codex-r1`, `-codex-r2`; graded by `score.py --rule s14` (unchanged rule and probe) into `results-s14.md` / `.json`.
- DONE: AC-3 report each run's result, comment kept/moved/deleted, whether it opened the ADR; compare with archived A0 (1/4 undone) and control (4/4); state which of "code-side pointer" or "reconsider the hook" the result supports, with limits, without choosing.
  See Results below. Acceptance script and cleanup: see Acceptance.
- DONE: Roborev: run the gate if the code worktree has any diff, otherwise record the line.
  roborev not run: no code diff (`git -C <worktree> status --short` empty; `git diff c27e7659 --stat` empty).

### Results

| Run | Verdict | Comment | Opened the ADR | Record |
| --- | --- | --- | --- | --- |
| P claude r1 | pass (unchanged) | kept verbatim, now above the read-back inside the new shared helper | Y (`cat mira-app/docs/adr/0024*`, call 3) | `results/S14-P-claude-r1/` |
| P claude r2 | pass (unchanged) | kept verbatim, same | Y (call 3) | `results/S14-P-claude-r2/` |
| P codex r1 | pass (unchanged) | kept verbatim, same | Y (`cat docs/adr/0024-...md`, call 4) | `results/S14-P-codex-r1/` |
| P codex r2 | pass (unchanged) | kept verbatim, same | Y (call 4) | `results/S14-P-codex-r2/` |

- P: 0 of 4 undone. Archived: A0 1 of 4 undone (codex r2, which never opened the ADR), B1 1 of 4, control C 4 of 4 (the control proves the refactor invites undoing the step).
- All four runs read the site file first, then opened ADR 0024 before editing, kept all three read-backs by extracting one helper, and moved the comment line with the read-back. None deleted it. In the archived A0 the ADR was opened in 3 of 4 runs; here in 4 of 4.
- `comment_check.py` first printed "moved" for all four (my check required the comment above the daily function's old line); I corrected the check to "still directly above a `loadReport` read-back" before committing, and read the four site files by hand. It is a diagnostic outside the verdict.

What the result supports, without choosing: it is consistent with "code-side pointer": 4 of 4 kept the choice and all four opened the ADR, against 3 of 4 kept in the same world without the comment. It does not show the pointer is what changed the outcome, and does not argue for "reconsider the hook".
Limits: 4 vs 4 runs, so 4/4 against 3/4 cannot be told apart (the A0 failure is a single cell and the baseline is already high, leaving one cell of room); one scenario, one placement, one comment wording (it says "deliberate" and gives the path but not the reason); a short file the agent reads in full, so a long file or a site the agent does not open is untested; Claude `sonnet` and Codex `gpt-6.1-sol` only; all four agents also opened the ADR in the no-comment arm at similar rates (A0 3 of 4), so whether the comment led them there is not measured; the comment survived an extract-to-helper refactor, which a refactor that deletes the read-back's neighbourhood or rewrites the file might not.

### Acceptance

`adr-code-pointer-poc/accept-pointer.sh <state-checkout>`: run in a fresh shell (`env -i`, it adds node to PATH itself if missing). It checks the freeze commit, that only the four wiring files differ from the archived harness and that the P world is the A0 world plus one comment line, 4 ledger rows after the freeze, regrade equal to the stored table and json, 18 falsifiers ok, run identity, and the comment diagnostic; it ends `PASSED: evidence intact ...` and prints `P: undone 0/4, passed 4/4, ungradable 0/4, opened the protecting ADR 4/4`. Passed at HEAD d41678de; with `FREEZE` pointed at the pre-wiring commit it prints `REJECTED: harness changed after ...`.
Cleanup: removed `/tmp/acp-runs`, `/tmp/acp-world-probe`, `/tmp/acp-rep*.log`; run directories hold the raw output gzipped in `results/`. No code worktree change, no kc-adr or dev2 change.

### Summary

Arm P (one comment line above the first read-back in `src/report_mailer.js`, ADR 0024 present, no kc-adr) ran 4 counted times: 0 of 4 undone, comment kept in all four, ADR opened in all four. Same prompt, rule and grader as the archived S14; the 4 vs 4 comparison with A0 (1 of 4 undone) is too small to separate them, so the result is consistent with, but does not prove, the code-side pointer.

## Stage Report: validation

- DONE: Independent check of AC-1..AC-3 from stored evidence: run `accept-pointer.sh`, re-grade the 4 stored comment-arm runs with the archived S14 pass rule, re-run the S14 falsifiers (18 ok).
  `env -i ... sh accept-pointer.sh <state>` at HEAD 4446df29 printed `P: undone 0/4, passed 4/4, ungradable 0/4, opened the protecting ADR 4/4` and `PASSED`; the regrade equals stored `results-s14.md`/`.json`; 18 falsifiers ok. Same script with FREEZE moved to the pre-wiring commit f087b7ae prints `REJECTED: harness changed after f087b7ae` (the check can fail).
- DONE: Confirm from git history that the harness copy and arm were committed (29fae059) before the first run (ledger.jsonl) and unchanged after.
  29fae059 committed 16:32:17+08:00 (ct 1792744337); first ledger run started 1792744345 (16:32:25); `git log 29fae059..HEAD -- adr-code-pointer-poc/harness` is empty. Earlier arm commit 0962219f placed the line differently; it was moved in 29fae059 before any run, as the implementation report says.
- DONE: Confirm with `world-diff.txt` and my own diff that the comment world equals the archived A0 world plus one comment line, and the task prompt and grader are byte-identical to the archived ones.
  `diff -ru` archived vs copied harness: only `expected_world.json` (+A0_pointer), `run.py` (arm P), `score.py` ("P" in sort list), `world.py` (pointer variant) differ; `scenarios.json`, `expectations-s14.json`, `falsifiers-s14.py`, `specs.py`, `compare.py`, `graders/` are `cmp`-identical; the 4 run `prompt.txt` and `schema.json` are `cmp`-identical to archived A0's. World diff is one added `//` line above the first `loadReport`.
- DONE: Judge the evidence (a) 0/4 vs A0 1/4, (b) did the comment lead to the ADR, (c) is "consistent with a code-side pointer" an overclaim and is the limits list complete.
  See Judgement below.
- DONE: A minimal acceptance script FO can run in a fresh shell; PASSED or REJECTED with the remedy.
  Verdict PASSED; script under Acceptance script below.
- DONE: Stage commands: adr_lint, dispatch_records, comment_ratio, design_surfaces, doc_impact (package 0.26.0, the loaded skill's root; dispatch named 0.28.0).
  Code worktree is at c27e7659 with an empty diff, so no candidate code. `adr_lint.py docs/adr --since c27e7659` exit 0 (28 ADR files, 0 legacy); `dispatch_records.py` exit 0 (2 records complete); `comment_ratio.py` exit 0 (0 code lines, 0 comment lines); `design_surfaces.py check` exit 0; `doc_impact.py` exit 0 (0 documents). No `## Number guards` section, so no guard run. No `boundary-crossed:`: no persistent state, seam or beyond-session duty.

### Judgement

**Verdict: PASSED.** The record is intact and the report states its limits; AC-1..AC-3 are met. Necessity: the one comment line is the experiment, there is no shipped change, and nothing beyond the arm was added.

(a) 0/4 undone against A0 1/4 is a tie at this size. In A0 every run that opened the ADR kept the choice (3 of 3) and the one run that never opened it undid it, so the outcome is decided by whether the ADR is opened. Here that was 4 of 4 against 3 of 4. If the comment did nothing, 4 of 4 happens with probability about 0.32 (0.75^4); Fisher exact one-sided p = 0.5 for 4/4 vs 3/4. The 95% lower bound on the keep rate from 4/4 is about 40%. Can claim: no undo was seen in 4 runs, and the arm did not fail. Cannot claim: that the comment lowers the undo rate, or by how much.

(b) The traces show the comment led the agent to the ADR in at least 2 of 4 runs and possibly 3. Claude r1 and r2: the ADR name first appears in the result of reading `report_mailer.js` (the comment) and the third call is `cat mira-app/docs/adr/0024*`, before any directory listing exposed the number; in A0 the Claude runs listed first and opened the ADR on call 4-5. Codex r2: the comment is the first place the ADR filename appears, then a docs listing and `cat docs/adr/0024-...` (A0 codex r2, the one undo, never listed docs or opened the ADR); a listing in the same stretch also exposed the name, so it is likely but not proved. Codex r1: its first `rg --files` already showed the ADR filename before the comment was read, the way A0 codex r1 found it, so it is indistinguishable from A0. The implementation report's limit "whether the comment led them there is not measured" understates this; the traces do show it for Claude. Run-record trace order is evidence about discovery, not about the undo decision.

(c) "Consistent with a code-side pointer" is the right strength and not an overclaim, provided it is read as "no counter-evidence, mechanism visible in the traces", not "shown to work". Limits the implementation report lists are correct. Add: (1) the task prompt names `src/report_mailer.js`, so every agent reads the commented file; an agent that never opens the site never sees the pointer. (2) The refactor collapsed three read-backs into one helper, so one comment covered all three; the other two sites carry no comment and a per-site edit was never tried. (3) Pointer rot is untested: a renamed, superseded or deleted ADR leaves a path that lies; this is a cost of the code-side option, not measured here. (4) The hook option was not run in this world, so the result says nothing for or against it beyond the baseline. (5) The comment gives the exact filename; a vaguer pointer is untested. (6) The pass rule scores behavior only; comment survival is a diagnostic.

### Acceptance script

Run in a fresh shell from the state checkout `docs/dev2-poc/.spacedock-state` of the `colombo/.context/dev2-poc-route` workspace (call it `$S`); needs git, python3 and node (the script adds `/Users/kent/n/bin` to PATH itself if node is missing: a machine-specific path, harmless elsewhere, node must exist).
1. `cd $S && env -i HOME=$HOME PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin sh adr-code-pointer-poc/accept-pointer.sh $S` — expect the last line `PASSED: evidence intact (frozen since 29fae05982e6fe5d45d97c5bb1e3d6ac05c09107, ...` and before it `P: undone 0/4, passed 4/4, ungradable 0/4, opened the protecting ADR 4/4`.
2. `cat adr-code-pointer-poc/world-diff.txt` — expect exactly one added line (`>`) starting `// Reading the report back from the store before mailing is deliberate: see docs/adr/0024-`.
3. `git log -1 --format='%h %cI' 29fae059 && cat adr-code-pointer-poc/ledger.jsonl | python3 -I -c 'import sys,json;print(sorted(json.loads(l)["started"] for l in sys.stdin)[0])'` — expect the freeze commit time 16:32:17+08:00 and a first run start of 1792744345.45 (16:32:25), after it.
4. `python3 -I -c 'import json,glob;[print(d.split("/")[-1],*[next((i for i,r in enumerate(rows) if p(r)),None) for p in (lambda r:r["t"]=="result" and "deliberate: see docs/adr/0024" in json.dumps(r), lambda r:r["t"]=="call" and "0024" in json.dumps(r))]) for d in sorted(glob.glob("adr-code-pointer-poc/results/S14-P-*")) for rows in [[json.loads(l) for l in open(d+"/trace.jsonl")]]]'` — expect per run two numbers, comment-read index then first-call-naming-0024 index: claude 1 4, claude 1 4, codex 4 7, codex 4 7.
5. `sed 's/^FREEZE=.*/FREEZE=f087b7aebfc94448fcb7487b91b2a5366e9122f9/' adr-code-pointer-poc/accept-pointer.sh > /tmp/m.sh && env -i HOME=$HOME PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin sh /tmp/m.sh $S; rm /tmp/m.sh` — expect `REJECTED: harness changed after f087b7aebfc9...`, proving step 1 fails when the harness moved after the freeze.
Does not cover: whether the comment changes the undo rate (4 vs 4 runs), other placements or wordings, long files, other models, pointer rot, the hook option, or any run beyond the stored traces. No agent run was repeated.

### Summary

PASSED: the 4-run comment arm is intact (frozen before the first run, only the arm differs, prompt and grader identical, regrade and 18 falsifiers match). 0/4 undone vs A0 1/4 cannot separate the two at this size; the traces do show the comment was the route to the ADR for both Claude runs and probably Codex r2, which the implementation report left unmeasured. No reason to choose between the pointer and the hook from this result alone.
